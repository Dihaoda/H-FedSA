from __future__ import annotations

import csv
import json
import shutil
import time
from collections import OrderedDict
from datetime import datetime
from pathlib import Path

import numpy as np
import torch
import yaml
from torch import nn

from src.attacks.backdoor_scaling import apply_trigger
from src.data.datasets import FederatedData
from src.attacks.adaptive_feature_matched import apply_adaptive_feature_matched_attack
from src.defenses.factory import build_defense
from src.federated.client import Client
from src.federated.server_optimizers import build_server_optimizer
from src.federated.tensor_ops import StateDict, add_update, flatten_update, zeros_like_update
from src.models.simple_cnn import build_model


class FederatedExperiment:
    def __init__(self, config: dict, fed_data: FederatedData, logger) -> None:
        self.config = config
        self.fed_data = fed_data
        self.logger = logger
        self.device = self._resolve_device(config.get("device", "auto"))
        self.mixed_precision = bool(config.get("performance", {}).get("mixed_precision", False)) and self.device.type == "cuda"
        self.rng = np.random.default_rng(int(config["seed"]))
        self.run_dir = self._prepare_run_dir()
        self.model_factory = lambda: build_model(self.fed_data.num_classes, self.config.get("model", {}))
        self._asr_batch_cache: dict[tuple, list[tuple[torch.Tensor, int]]] = {}
        self._configure_torch_performance()
        self._write_data_metadata()

    def run(self) -> dict:
        started_at = time.perf_counter()
        self.logger.info("Dataset source: %s", self.fed_data.dataset_source)
        self.logger.info("Device: %s", self.device)
        defenses = self.config.get("defenses") or [self.config.get("defense", "fedavg")]
        all_rows: list[dict] = []
        summaries: dict[str, dict] = {}

        initial_state = self._initial_model_state()
        for defense_name in defenses:
            defense = build_defense(defense_name, self.config)
            self.logger.info("Starting defense: %s", defense.name)
            global_state = OrderedDict((name, tensor.clone()) for name, tensor in initial_state.items())
            rows, summary = self._run_single_defense(defense, global_state)
            all_rows.extend(rows)
            summaries[defense.name] = summary

        runtime_seconds = time.perf_counter() - started_at
        for summary in summaries.values():
            summary["runtime_seconds"] = runtime_seconds
            summary["config_path"] = self.config.get("_config_path", "")
            summary["output_dir"] = str(self.run_dir)
            summary["dataset_source"] = self.fed_data.dataset_source
            summary["cli_overrides"] = self.config.get("_cli_overrides", [])
            summary["final_config"] = self.config
        self._write_metrics(all_rows)
        self._write_summary(summaries)
        self._write_run_summary(summaries, runtime_seconds)
        self._write_hfedsa_diagnostic_summary()
        return {"run_dir": str(self.run_dir), "summaries": summaries}

    def _run_single_defense(self, defense, global_state: StateDict) -> tuple[list[dict], dict]:
        torch.manual_seed(int(self.config["seed"]))
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(int(self.config["seed"]))
        fed_cfg = self.config["federated"]
        attack_cfg = self.config.get("attack", {})
        rounds = int(fed_cfg["rounds"])
        clients_per_round = int(fed_cfg["clients_per_round"])
        local_epochs = int(fed_cfg["local_epochs"])
        base_learning_rate = float(fed_cfg["learning_rate"])
        optimizer_name = str(fed_cfg.get("optimizer", "sgd"))
        momentum = float(fed_cfg.get("momentum", 0.9))
        weight_decay = float(fed_cfg.get("weight_decay", 0.0))
        server_learning_rate = float(fed_cfg.get("server_learning_rate", 1.0))
        server_optimizer = build_server_optimizer(self.config, global_state)
        server_optimizer_name = str(fed_cfg.get("server_optimizer", "fedavg")).lower()
        server_lr = float(fed_cfg.get("server_lr", server_learning_rate))
        aggregation_weighting = str(fed_cfg.get("aggregation_weighting", "uniform")).lower()
        bn_buffer_strategy = str(fed_cfg.get("bn_buffer_strategy", "aggregate")).lower()
        aggregate_bn_buffers = bool(fed_cfg.get("aggregate_bn_buffers", bn_buffer_strategy == "aggregate"))
        attack_type = str(attack_cfg.get("type", "none"))
        scale_factor = float(attack_cfg.get("scale_factor", 1.0))
        rows: list[dict] = []
        debug_rows: list[dict] = []
        beta_trace_rows: list[dict] = []
        adaptive_trace_rows: list[dict] = []
        eval_every = max(1, int(fed_cfg.get("eval_every", self.config.get("evaluation", {}).get("eval_every", 1))))
        eval_last_k = max(1, int(fed_cfg.get("eval_last_k", self.config.get("evaluation", {}).get("eval_last_k", 5))))
        log_every = max(1, int(fed_cfg.get("log_every", self.config.get("logging", {}).get("round_log_every", 1))))
        final_accuracy = 0.0
        best_accuracy = 0.0
        last_train_eval: dict[str, float] | None = None
        last_test_eval: dict[str, float] | None = None
        last_attack_success_rate: float | str = "NA"
        rng = np.random.default_rng(int(self.config["seed"]))

        clients = [
            Client(
                client_id=client_id,
                dataloader=loader,
                model_factory=self.model_factory,
                device=self.device,
                num_classes=self.fed_data.num_classes,
                role=self.fed_data.client_roles[client_id],
            )
            for client_id, loader in enumerate(self.fed_data.client_loaders)
        ]
        client_sample_counts = {client.client_id: len(client.dataloader.dataset) for client in clients}
        root_client = Client(
            client_id="root",
            dataloader=self.fed_data.root_loader,
            model_factory=self.model_factory,
            device=self.device,
            num_classes=self.fed_data.num_classes,
            role="benign",
        )

        for round_idx in range(rounds):
            learning_rate = self._learning_rate_for_round(base_learning_rate, round_idx + 1, rounds)
            selected_ids = rng.choice(len(clients), size=clients_per_round, replace=False).tolist()
            selected_updates = []
            for client_id in selected_ids:
                client = clients[client_id]
                update = client.train(
                    global_state=global_state,
                    local_epochs=local_epochs,
                    learning_rate=learning_rate,
                    optimizer_name=optimizer_name,
                    momentum=momentum,
                    weight_decay=weight_decay,
                    aggregate_bn_buffers=aggregate_bn_buffers,
                    attack_type=attack_type,
                    scale_factor=scale_factor,
                    attack_cfg=attack_cfg,
                    mixed_precision=self.mixed_precision,
                )
                selected_updates.append((client_id, update))

            update_norms = {client_id: float(torch.linalg.norm(flatten_update(update)).item()) for client_id, update in selected_updates}
            selected_sample_counts = {client_id: int(client_sample_counts[client_id]) for client_id in selected_ids}
            if self._needs_root_update(defense.name, attack_type):
                root_update = root_client.train(
                    global_state=global_state,
                    local_epochs=local_epochs,
                    learning_rate=learning_rate,
                    optimizer_name=optimizer_name,
                    momentum=momentum,
                    weight_decay=weight_decay,
                    aggregate_bn_buffers=aggregate_bn_buffers,
                    attack_type="none",
                    scale_factor=1.0,
                    mixed_precision=self.mixed_precision,
                )
            else:
                root_update = zeros_like_update(selected_updates[0][1])
            if attack_type == "adaptive_feature_matched":
                selected_updates, adaptive_trace = apply_adaptive_feature_matched_attack(
                    updates=selected_updates,
                    root_update=root_update,
                    malicious_clients=self.fed_data.malicious_clients,
                    client_roles=self.fed_data.client_roles,
                    config=self.config,
                    round_number=round_idx + 1,
                )
                adaptive_trace_rows.extend(adaptive_trace)
            before_model_norm = self._model_state_norm(global_state)
            aggregated_update, diagnostics = defense.aggregate(
                selected_updates,
                root_update,
                sample_counts=selected_sample_counts,
            )
            diagnostics = self._augment_aggregation_diagnostics(diagnostics, selected_ids, selected_sample_counts, update_norms)
            aggregation_weights = {
                int(item["client_id"]): float(item["weight"])
                for item in diagnostics
                if str(item.get("client_id", "")).isdigit() and item.get("weight") not in {"", "NA", None}
            }
            aggregation_weight_sum = float(sum(aggregation_weights.values())) if aggregation_weights else 0.0
            aggregated_delta_norm = float(torch.linalg.norm(flatten_update(aggregated_update)).item())
            for item in diagnostics:
                item["aggregated_update_norm"] = aggregated_delta_norm
            fallback_reason = self._diagnostic_fallback_reason(diagnostics) or str(getattr(defense, "last_fallback_reason", "") or "")
            if fallback_reason:
                self.logger.info("%s round %d fallback: %s", defense.name, round_idx + 1, fallback_reason)
            server_update, server_optimizer_summary = server_optimizer.step(aggregated_update)
            global_state = add_update(global_state, server_update, scale=1.0)
            global_state = self._apply_bn_buffer_strategy(global_state, bn_buffer_strategy)
            after_model_norm = self._model_state_norm(global_state)
            should_eval = (
                eval_every <= 1
                or (round_idx + 1) % eval_every == 0
                or (round_idx + 1) > rounds - eval_last_k
                or round_idx == 0
                or round_idx + 1 == rounds
            )
            if should_eval or last_train_eval is None or last_test_eval is None:
                train_eval, test_eval, attack_success_rate = self._evaluate_round(global_state, attack_type, attack_cfg)
                last_train_eval = train_eval
                last_test_eval = test_eval
                last_attack_success_rate = attack_success_rate
            else:
                train_eval = dict(last_train_eval)
                test_eval = dict(last_test_eval)
                attack_success_rate = last_attack_success_rate
            final_accuracy = test_eval["accuracy"]
            best_accuracy = max(best_accuracy, final_accuracy)
            detection = self._detection_metrics(diagnostics)
            if hasattr(defense, "observe_round"):
                trace = defense.observe_round(train_eval["loss"], test_eval["loss"], test_eval["accuracy"], diagnostics)
                if trace:
                    beta_trace_rows.append({key: value for key, value in trace.items() if key != "state_vector"})
            row = {
                "round": round_idx + 1,
                "method": defense.name,
                "dataset": self.config.get("dataset", {}).get("name", "unknown"),
                "attack_type": attack_type,
                "seed": int(self.config["seed"]),
                "accuracy": final_accuracy,
                "error_rate": 100.0 - final_accuracy,
                "attack_success_rate": attack_success_rate,
                "num_clients": int(fed_cfg["num_clients"]),
                "malicious_ratio": float(fed_cfg["malicious_ratio"]),
                "defense": defense.name,
                "dataset_source": self.fed_data.dataset_source,
                "synthetic": self.fed_data.metadata.get("synthetic", False),
                "train_loss": train_eval["loss"],
                "train_accuracy": train_eval["accuracy"],
                "test_loss": test_eval["loss"],
                "test_accuracy": test_eval["accuracy"],
                "clients_per_round": clients_per_round,
                "learning_rate": learning_rate,
                "server_learning_rate": server_learning_rate,
                "server_optimizer": server_optimizer_name,
                "server_lr": server_lr,
                "bn_buffer_strategy": bn_buffer_strategy,
                "aggregation_weighting": aggregation_weighting,
                "iid": self.fed_data.metadata.get("iid", False),
                "non_iid_alpha": self.fed_data.metadata.get("non_iid_alpha", "NA"),
                "train_subset_size": self.fed_data.metadata.get("train_subset_size", "NA"),
                "test_subset_size": self.fed_data.metadata.get("test_subset_size", "NA"),
                "selected_clients": " ".join(str(idx) for idx in selected_ids),
                **detection,
            }
            rows.append(row)
            debug_rows.append(
                {
                    "round": round_idx + 1,
                    "method": defense.name,
                    "learning_rate": learning_rate,
                    "server_learning_rate": server_learning_rate,
                    "server_optimizer": server_optimizer_name,
                    "server_lr": server_lr,
                    "selected_clients": " ".join(str(idx) for idx in selected_ids),
                    "client_sample_counts_json": json.dumps(selected_sample_counts),
                    "client_update_norms_json": json.dumps(update_norms),
                    "aggregation_weights_json": json.dumps(aggregation_weights),
                    "aggregation_weight_sum": aggregation_weight_sum,
                    "aggregation_weighting": aggregation_weighting,
                    "min_update_norm": min(update_norms.values()) if update_norms else "NA",
                    "max_update_norm": max(update_norms.values()) if update_norms else "NA",
                    "mean_update_norm": float(np.mean(list(update_norms.values()))) if update_norms else "NA",
                    "aggregated_delta_norm": aggregated_delta_norm,
                    "server_update_norm": server_optimizer_summary.get("server_update_norm", "NA"),
                    "server_nan_flag": server_optimizer_summary.get("server_nan_flag", False),
                    "server_inf_flag": server_optimizer_summary.get("server_inf_flag", False),
                    "server_optimizer_state_json": json.dumps(server_optimizer_summary),
                    "model_norm_before": before_model_norm,
                    "model_norm_after": after_model_norm,
                    "train_accuracy": train_eval["accuracy"],
                    "test_accuracy": test_eval["accuracy"],
                }
            )
            if str(defense.name).startswith("hfedsa"):
                self._write_hfedsa_diagnostics(
                    round_idx + 1,
                    defense.name,
                    attack_type,
                    selected_ids,
                    diagnostics,
                    aggregated_delta_norm,
                    total_rounds=rounds,
                )
            if str(defense.name).lower() == "fltrust":
                self._write_fltrust_diagnostics(
                    round_idx + 1,
                    attack_type,
                    selected_ids,
                    diagnostics,
                    aggregated_delta_norm,
                    server_optimizer_summary.get("server_update_norm", "NA"),
                )
            if (round_idx + 1) % log_every == 0 or round_idx == 0 or round_idx + 1 == rounds:
                self.logger.info(
                    "%s round %d/%d | lr %.5f | train %.2f | test %.2f | agg_delta %.4f",
                    defense.name,
                    round_idx + 1,
                    rounds,
                    learning_rate,
                    train_eval["accuracy"],
                    final_accuracy,
                    aggregated_delta_norm,
                )

        self._write_aggregation_debug(defense.name, debug_rows)
        self._write_beta_trace(defense.name, beta_trace_rows)
        self._write_adaptive_attack_trace(defense.name, adaptive_trace_rows)
        self._write_final_model_state(defense.name, global_state)
        summary = {
            "final_accuracy": final_accuracy,
            "final_error_rate": 100.0 - final_accuracy,
            "best_accuracy": best_accuracy,
            "attack_type": attack_type,
            "scaling_factor": scale_factor,
        }
        if str(defense.name).startswith("hfedsa"):
            cfg = getattr(defense, "config", None)
            summary.update(
                {
                    "variant": defense.name,
                    "normalization_mode": getattr(cfg, "normalization_mode", "NA"),
                    "weight_ema_enabled": getattr(cfg, "weight_ema_enabled", "NA"),
                    "ddpg_enabled": bool(getattr(defense, "beta_agent", None) is not None),
                    "beta_mode": getattr(cfg, "beta_mode", "NA"),
                    "beta_explore": getattr(cfg, "beta_explore", "NA"),
                    "update_norm_clip_enabled": getattr(cfg, "update_norm_clip_enabled", "NA"),
                    "update_norm_clip_ratio": getattr(cfg, "update_norm_clip_ratio", "NA"),
                    "retention_floor_enabled": getattr(cfg, "retention_floor_enabled", "NA"),
                    "retention_floor": getattr(cfg, "retention_floor", "NA"),
                    "retention_mode": getattr(cfg, "retention_mode", "NA"),
                    "retention_pmal_threshold": getattr(cfg, "retention_pmal_threshold", "NA"),
                    "retention_topk": getattr(cfg, "retention_topk", "NA"),
                    "weight_bounds_enabled": getattr(cfg, "weight_bounds_enabled", "NA"),
                    "min_weight": getattr(cfg, "min_weight", "NA"),
                    "max_weight": getattr(cfg, "max_weight", "NA"),
                    "malicious_hard_gate_enabled": getattr(cfg, "malicious_hard_gate_enabled", "NA"),
                    "malicious_hard_gate_threshold": getattr(cfg, "malicious_hard_gate_threshold", "NA"),
                    "cluster_role_strategy": getattr(cfg, "cluster_role_strategy", "NA"),
                    "ddpg_security_penalty": getattr(cfg, "ddpg_security_penalty", "NA"),
                    "ddpg_residual_penalty": getattr(cfg, "ddpg_residual_penalty", "NA"),
                    "ddpg_aggregated_norm_penalty": getattr(cfg, "ddpg_aggregated_norm_penalty", "NA"),
                    "ddpg_beta_decay_enabled": getattr(cfg, "ddpg_beta_decay_enabled", "NA"),
                }
            )
        return rows, summary

    def evaluate(self, global_state: StateDict) -> float:
        return self.evaluate_metrics(global_state, self.fed_data.test_loader)["accuracy"]

    def _configure_torch_performance(self) -> None:
        perf_cfg = self.config.get("performance", {})
        if bool(perf_cfg.get("cudnn_benchmark", True)) and torch.cuda.is_available():
            torch.backends.cudnn.benchmark = True
        if bool(perf_cfg.get("allow_tf32", True)) and torch.cuda.is_available():
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True

    def _needs_root_update(self, defense_name: str, attack_type: str) -> bool:
        key = str(defense_name).lower()
        if attack_type == "adaptive_feature_matched":
            return True
        return key == "fltrust" or key.startswith("hfedsa")

    def _augment_aggregation_diagnostics(
        self,
        diagnostics: list[dict],
        selected_ids: list[int],
        sample_counts: dict[int, int],
        update_norms: dict[int, float],
    ) -> list[dict]:
        diagnostic_by_client = {
            int(item["client_id"]): dict(item)
            for item in diagnostics
            if str(item.get("client_id", "")).isdigit()
        }
        augmented = []
        for client_id in selected_ids:
            item = diagnostic_by_client.get(int(client_id), {"client_id": int(client_id)})
            item.setdefault("weight", 0.0)
            item["num_samples"] = int(sample_counts.get(int(client_id), 0))
            item["update_norm"] = float(update_norms.get(int(client_id), 0.0))
            augmented.append(item)
        return augmented

    def evaluate_metrics(self, global_state: StateDict, dataloader) -> dict[str, float]:
        model = self.model_factory().to(self.device)
        model.load_state_dict(global_state)
        model.eval()
        return self._evaluate_model_metrics(model, dataloader)

    def _evaluate_round(self, global_state: StateDict, attack_type: str, attack_cfg: dict) -> tuple[dict[str, float], dict[str, float], float | str]:
        model = self.model_factory().to(self.device)
        model.load_state_dict(global_state)
        model.eval()
        train_eval = self._evaluate_model_metrics(model, self.fed_data.train_eval_loader)
        test_eval = self._evaluate_model_metrics(model, self.fed_data.test_loader)
        attack_success_rate = self._attack_success_rate_for_model(model, attack_type, attack_cfg)
        return train_eval, test_eval, attack_success_rate

    def _evaluate_model_metrics(self, model, dataloader) -> dict[str, float]:
        criterion = nn.CrossEntropyLoss(reduction="sum")
        correct = 0
        total = 0
        loss_sum = 0.0
        with torch.no_grad():
            for features, labels in dataloader:
                features = features.to(self.device, non_blocking=True)
                labels = labels.to(self.device, non_blocking=True)
                if self.mixed_precision:
                    with torch.amp.autocast("cuda"):
                        logits = model(features)
                else:
                    logits = model(features)
                loss_sum += float(criterion(logits, labels).item())
                predictions = torch.argmax(logits, dim=1)
                correct += int((predictions == labels).sum().item())
                total += int(labels.numel())
        return {"loss": loss_sum / max(total, 1), "accuracy": 100.0 * correct / max(total, 1)}

    def _attack_success_rate(self, global_state: StateDict, attack_type: str, attack_cfg: dict) -> float | str:
        if attack_type != "backdoor_scaling":
            return "NA"
        model = self.model_factory().to(self.device)
        model.load_state_dict(global_state)
        model.eval()
        return self._attack_success_rate_for_model(model, attack_type, attack_cfg)

    def _attack_success_rate_for_model(self, model, attack_type: str, attack_cfg: dict) -> float | str:
        if attack_type != "backdoor_scaling":
            return "NA"
        target_label = int(attack_cfg.get("target_label", 0)) % int(self.fed_data.num_classes)
        total = 0
        target_hits = 0
        with torch.no_grad():
            for triggered_cpu, count in self._asr_batches(attack_cfg, target_label):
                triggered = triggered_cpu.to(self.device, non_blocking=True)
                if self.mixed_precision:
                    with torch.amp.autocast("cuda"):
                        logits = model(triggered)
                else:
                    logits = model(triggered)
                preds = torch.argmax(logits, dim=1)
                target_hits += int((preds == target_label).sum().item())
                total += int(count)
        return 100.0 * target_hits / max(total, 1)

    def _asr_batches(self, attack_cfg: dict, target_label: int) -> list[tuple[torch.Tensor, int]]:
        trigger_cfg = attack_cfg.get("trigger", {})
        key = (
            int(target_label),
            int(trigger_cfg.get("size", 4)),
            float(trigger_cfg.get("value", 2.5)),
            str(trigger_cfg.get("location", "bottom_right")),
            int(self.config.get("seed", 0)),
        )
        cached = self._asr_batch_cache.get(key)
        if cached is not None:
            return cached
        batches: list[tuple[torch.Tensor, int]] = []
        for features, labels in self.fed_data.test_loader:
            mask = labels != target_label
            if not bool(mask.any()):
                continue
            triggered = apply_trigger(features[mask], trigger_cfg).contiguous()
            batches.append((triggered, int(triggered.shape[0])))
        self._asr_batch_cache[key] = batches
        return batches

    def _initial_model_state(self) -> StateDict:
        model = self.model_factory()
        return OrderedDict((name, tensor.detach().cpu().clone()) for name, tensor in model.state_dict().items())

    def _model_state_norm(self, state: StateDict) -> float:
        return float(torch.linalg.norm(torch.cat([tensor.reshape(-1).float().cpu() for tensor in state.values()])).item())

    def _learning_rate_for_round(self, base_lr: float, round_number: int, total_rounds: int) -> float:
        schedule = self.config.get("federated", {}).get("lr_schedule", {})
        schedule_type = str(schedule.get("type", "constant")).lower()
        if schedule_type == "step":
            lr = base_lr
            milestones = schedule.get("milestones", [])
            gamma = float(schedule.get("gamma", 0.1))
            for milestone in milestones:
                if round_number >= int(milestone):
                    lr *= gamma
            return float(lr)
        if schedule_type == "cosine":
            min_lr = float(schedule.get("min_lr", 0.0))
            progress = min(max(round_number - 1, 0), max(total_rounds - 1, 1)) / float(max(total_rounds - 1, 1))
            return float(min_lr + 0.5 * (base_lr - min_lr) * (1.0 + np.cos(np.pi * progress)))
        return base_lr

    def _apply_bn_buffer_strategy(self, global_state: StateDict, strategy: str) -> StateDict:
        if strategy == "reset":
            return self._reset_bn_buffers(global_state)
        if strategy == "recompute_train_eval":
            return self._recompute_bn_buffers(global_state, self.fed_data.train_eval_loader)
        return global_state

    def _reset_bn_buffers(self, global_state: StateDict) -> StateDict:
        updated = OrderedDict((name, tensor.clone()) for name, tensor in global_state.items())
        for name, tensor in updated.items():
            if name.endswith("running_mean"):
                updated[name] = torch.zeros_like(tensor)
            elif name.endswith("running_var"):
                updated[name] = torch.ones_like(tensor)
            elif name.endswith("num_batches_tracked"):
                updated[name] = torch.zeros_like(tensor)
        return updated

    def _recompute_bn_buffers(self, global_state: StateDict, dataloader) -> StateDict:
        model = self.model_factory().to(self.device)
        model.load_state_dict(self._reset_bn_buffers(global_state))
        model.train()
        with torch.no_grad():
            for features, _ in dataloader:
                _ = model(features.to(self.device))
        return OrderedDict((name, tensor.detach().cpu().clone()) for name, tensor in model.state_dict().items())

    def _detection_metrics(self, diagnostics: list[dict]) -> dict:
        if not diagnostics or "predicted_malicious" not in diagnostics[0]:
            return {"detection_tpr": "", "detection_fpr": ""}
        tp = fp = tn = fn = 0
        for item in diagnostics:
            client_id = int(item["client_id"])
            predicted = bool(item["predicted_malicious"])
            actual = client_id in self.fed_data.malicious_clients
            if predicted and actual:
                tp += 1
            elif predicted and not actual:
                fp += 1
            elif not predicted and actual:
                fn += 1
            else:
                tn += 1
        tpr = tp / max(tp + fn, 1)
        fpr = fp / max(fp + tn, 1)
        return {"detection_tpr": tpr, "detection_fpr": fpr}

    def _write_hfedsa_diagnostics(
        self,
        round_number: int,
        defense_name: str,
        attack_type: str,
        selected_ids: list[int],
        diagnostics: list[dict],
        aggregated_update_norm: float,
        total_rounds: int,
    ) -> None:
        if not self._should_write_client_diagnostics(round_number, total_rounds):
            self._write_hfedsa_round_diagnostics(round_number, defense_name, diagnostics, aggregated_update_norm)
            return
        diagnostic_map = {int(item["client_id"]): item for item in diagnostics if str(item.get("client_id", "")).isdigit()}
        selected_set = set(selected_ids)
        write_all_clients = bool(self.config.get("diagnostics", {}).get("write_all_clients", True))
        client_ids_to_write = range(len(self.fed_data.client_loaders)) if write_all_clients else selected_ids
        fields = [
            "client_id",
            "round",
            "true_type",
            "selected",
            "f_dir",
            "f_int",
            "f_spa",
            "p_benign",
            "p_unseen",
            "p_malicious",
            "final_weight",
            "gmm_fallback_used",
            "gmm_fallback_reason",
            "raw_weight",
            "bounded_weight",
            "ema_weight",
            "posterior_clipped",
            "weight_clipped",
            "retention_applied",
            "effective_retention_floor",
            "retention_topk_eligible",
            "risk_weighted_contribution",
            "feature_nan_flag",
            "feature_inf_flag",
            "update_norm",
            "aggregated_update_norm",
            "num_effective_clients",
            "attack_type",
            "defense",
            "transformed_update_norm",
            "raw_update_norm",
            "normalized_update_norm",
            "root_update_norm",
            "update_scale",
            "update_norm_clipped",
            "normalization_mode",
            "formula_mode",
            "malicious_hard_gate_enabled",
            "retention_mode",
            "retention_pmal_threshold",
            "retention_topk",
            "normalize_update_to_root",
            "update_norm_clip_enabled",
        ]
        safe_defense = defense_name.replace("/", "_").replace("\\", "_")
        path = self.run_dir / f"client_diagnostics_{safe_defense}_round_{round_number:03d}.csv"
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for client_id in client_ids_to_write:
                item = diagnostic_map.get(client_id, {})
                writer.writerow(
                    {
                        "client_id": client_id,
                        "round": round_number,
                        "true_type": self.fed_data.client_roles.get(client_id, "benign"),
                        "selected": client_id in selected_set,
                        "f_dir": item.get("direction", "NA"),
                        "f_int": item.get("intensity", "NA"),
                        "f_spa": item.get("sparsity", "NA"),
                        "p_benign": item.get("p_benign", "NA"),
                        "p_unseen": item.get("p_unseen", "NA"),
                        "p_malicious": item.get("p_malicious", "NA"),
                        "final_weight": item.get("weight", "NA"),
                        "gmm_fallback_used": item.get("gmm_fallback_used", False),
                        "gmm_fallback_reason": item.get("gmm_fallback_reason", item.get("gmm_fallback", "")),
                        "raw_weight": item.get("raw_weight", "NA"),
                        "bounded_weight": item.get("bounded_weight", "NA"),
                        "ema_weight": item.get("ema_weight", "NA"),
                        "posterior_clipped": item.get("posterior_clipped", False),
                        "weight_clipped": item.get("weight_clipped", False),
                        "retention_applied": item.get("retention_applied", False),
                        "effective_retention_floor": item.get("effective_retention_floor", "NA"),
                        "retention_topk_eligible": item.get("retention_topk_eligible", "NA"),
                        "risk_weighted_contribution": item.get("risk_weighted_contribution", "NA"),
                        "feature_nan_flag": item.get("feature_nan_flag", False),
                        "feature_inf_flag": item.get("feature_inf_flag", False),
                        "update_norm": item.get("update_norm", "NA"),
                        "aggregated_update_norm": aggregated_update_norm,
                        "num_effective_clients": item.get("num_effective_clients", "NA"),
                        "attack_type": attack_type,
                        "defense": defense_name,
                        "transformed_update_norm": item.get("transformed_update_norm", "NA"),
                        "raw_update_norm": item.get("raw_update_norm", item.get("update_norm", "NA")),
                        "normalized_update_norm": item.get("normalized_update_norm", item.get("transformed_update_norm", "NA")),
                        "root_update_norm": item.get("root_update_norm", "NA"),
                        "update_scale": item.get("update_scale", "NA"),
                        "update_norm_clipped": item.get("update_norm_clipped", "NA"),
                        "normalization_mode": item.get("normalization_mode", "NA"),
                        "formula_mode": item.get("formula_mode", "NA"),
                        "malicious_hard_gate_enabled": item.get("malicious_hard_gate_enabled", "NA"),
                        "retention_mode": item.get("retention_mode", "NA"),
                        "retention_pmal_threshold": item.get("retention_pmal_threshold", "NA"),
                        "retention_topk": item.get("retention_topk", "NA"),
                        "normalize_update_to_root": item.get("normalize_update_to_root", "NA"),
                        "update_norm_clip_enabled": item.get("update_norm_clip_enabled", "NA"),
                    }
                )
        self.logger.info("Saved H-FedSA diagnostics: %s", path)
        self._write_hfedsa_round_diagnostics(round_number, defense_name, diagnostics, aggregated_update_norm)

    def _should_write_client_diagnostics(self, round_number: int, total_rounds: int) -> bool:
        diag_cfg = self.config.get("diagnostics", {})
        every = max(1, int(diag_cfg.get("client_detail_every", 1)))
        last_k = max(0, int(diag_cfg.get("client_detail_last_k", total_rounds)))
        return round_number == 1 or round_number == total_rounds or round_number % every == 0 or round_number > total_rounds - last_k

    def _write_fltrust_diagnostics(
        self,
        round_number: int,
        attack_type: str,
        selected_ids: list[int],
        diagnostics: list[dict],
        aggregated_update_norm: float,
        server_update_norm,
    ) -> None:
        fields = [
            "round",
            "client_id",
            "true_type",
            "selected",
            "trust_score",
            "cosine_similarity",
            "client_update_norm",
            "root_update_norm",
            "update_scale",
            "scaled_update_norm",
            "final_weight",
            "aggregated_update_norm",
            "server_update_norm",
            "attack_type",
            "defense",
        ]
        path = self.run_dir / "fltrust_scaling_diagnostics.csv"
        write_header = not path.exists()
        selected_set = set(selected_ids)
        with path.open("a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            if write_header:
                writer.writeheader()
            for item in diagnostics:
                client_id = int(item["client_id"])
                writer.writerow(
                    {
                        "round": round_number,
                        "client_id": client_id,
                        "true_type": self.fed_data.client_roles.get(client_id, "benign"),
                        "selected": client_id in selected_set,
                        "trust_score": item.get("trust_score", "NA"),
                        "cosine_similarity": item.get("cosine_similarity", "NA"),
                        "client_update_norm": item.get("client_update_norm", item.get("update_norm", "NA")),
                        "root_update_norm": item.get("root_update_norm", "NA"),
                        "update_scale": item.get("update_scale", "NA"),
                        "scaled_update_norm": item.get("scaled_update_norm", "NA"),
                        "final_weight": item.get("weight", "NA"),
                        "aggregated_update_norm": aggregated_update_norm,
                        "server_update_norm": server_update_norm,
                        "attack_type": attack_type,
                        "defense": "fltrust",
                    }
                )
        self.logger.info("Updated FLTrust diagnostics: %s", path)

    def _write_hfedsa_round_diagnostics(
        self,
        round_number: int,
        defense_name: str,
        diagnostics: list[dict],
        aggregated_update_norm: float,
    ) -> None:
        fields = [
            "round",
            "defense",
            "benign_mean_weight",
            "malicious_mean_weight",
            "unseen_mean_weight",
            "benign_mean_p_malicious",
            "malicious_mean_p_malicious",
            "unseen_mean_p_unseen",
            "aggregated_update_norm",
            "num_effective_clients",
            "gmm_fallback_count",
            "has_nan",
            "has_inf",
            "weight_collapse_flag",
            "weight_sum_before_normalization",
            "max_transformed_update_norm",
            "mean_transformed_update_norm",
            "formula_mode",
            "beta_explore",
            "cluster_role_strategy",
            "retention_floor_enabled",
            "retention_floor",
            "malicious_hard_gate_enabled",
            "malicious_hard_gate_threshold",
            "hard_gated_clients",
            "retention_mode",
            "retention_pmal_threshold",
            "retention_topk",
            "benign_retention_application_rate",
            "malicious_retention_application_rate",
            "mean_risk_weighted_contribution",
        ]
        by_role: dict[str, list[dict]] = {"benign": [], "malicious": [], "unseen": []}
        for item in diagnostics:
            client_id = int(item["client_id"])
            by_role.setdefault(self.fed_data.client_roles.get(client_id, "benign"), []).append(item)

        def mean_for(role: str, key: str):
            values = [float(item[key]) for item in by_role.get(role, []) if item.get(key) not in {"", "NA", None}]
            return float(np.mean(values)) if values else "NA"

        weights = np.asarray(
            [float(item["weight"]) for item in diagnostics if item.get("weight") not in {"", "NA", None}],
            dtype=float,
        ) if diagnostics else np.asarray([])
        raw_weights = np.asarray(
            [float(item["raw_weight"]) for item in diagnostics if item.get("raw_weight") not in {"", "NA", None}],
            dtype=float,
        ) if diagnostics else np.asarray([])
        transformed_norms = np.asarray(
            [float(item["transformed_update_norm"]) for item in diagnostics if item.get("transformed_update_norm") not in {"", "NA", None}],
            dtype=float,
        ) if diagnostics else np.asarray([])
        row = {
            "round": round_number,
            "defense": defense_name,
            "benign_mean_weight": mean_for("benign", "weight"),
            "malicious_mean_weight": mean_for("malicious", "weight"),
            "unseen_mean_weight": mean_for("unseen", "weight"),
            "benign_mean_p_malicious": mean_for("benign", "p_malicious"),
            "malicious_mean_p_malicious": mean_for("malicious", "p_malicious"),
            "unseen_mean_p_unseen": mean_for("unseen", "p_unseen"),
            "aggregated_update_norm": aggregated_update_norm,
            "num_effective_clients": max((int(item.get("num_effective_clients", 0)) for item in diagnostics), default=0),
            "gmm_fallback_count": sum(1 for item in diagnostics if bool(item.get("gmm_fallback_used", False))),
            "has_nan": any(bool(item.get("feature_nan_flag", False)) for item in diagnostics),
            "has_inf": any(bool(item.get("feature_inf_flag", False)) for item in diagnostics),
            "weight_collapse_flag": bool(weights.size > 0 and weights.sum() > 0 and weights.max() / weights.sum() > 0.8),
            "weight_sum_before_normalization": float(raw_weights.sum()) if raw_weights.size else "NA",
            "max_transformed_update_norm": float(np.max(transformed_norms)) if transformed_norms.size else "NA",
            "mean_transformed_update_norm": float(np.mean(transformed_norms)) if transformed_norms.size else "NA",
            "formula_mode": diagnostics[0].get("formula_mode", "NA") if diagnostics else "NA",
            "beta_explore": diagnostics[0].get("beta_explore", "NA") if diagnostics else "NA",
            "cluster_role_strategy": diagnostics[0].get("cluster_role_strategy", "NA") if diagnostics else "NA",
            "retention_floor_enabled": diagnostics[0].get("retention_floor_enabled", "NA") if diagnostics else "NA",
            "retention_floor": diagnostics[0].get("retention_floor", "NA") if diagnostics else "NA",
            "malicious_hard_gate_enabled": diagnostics[0].get("malicious_hard_gate_enabled", "NA") if diagnostics else "NA",
            "malicious_hard_gate_threshold": diagnostics[0].get("malicious_hard_gate_threshold", "NA") if diagnostics else "NA",
            "hard_gated_clients": sum(bool(item.get("hard_gated", False)) for item in diagnostics),
            "retention_mode": diagnostics[0].get("retention_mode", "NA") if diagnostics else "NA",
            "retention_pmal_threshold": diagnostics[0].get("retention_pmal_threshold", "NA") if diagnostics else "NA",
            "retention_topk": diagnostics[0].get("retention_topk", "NA") if diagnostics else "NA",
            "benign_retention_application_rate": mean_for("benign", "retention_applied"),
            "malicious_retention_application_rate": mean_for("malicious", "retention_applied"),
            "mean_risk_weighted_contribution": float(
                np.mean(
                    [
                        float(item["risk_weighted_contribution"])
                        for item in diagnostics
                        if item.get("risk_weighted_contribution") not in {"", "NA", None}
                    ]
                )
            ) if diagnostics else "NA",
        }
        safe_defense = defense_name.replace("/", "_").replace("\\", "_")
        path = self.run_dir / f"hfedsa_round_diagnostics_{safe_defense}.csv"
        write_header = not path.exists()
        with path.open("a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            if write_header:
                writer.writeheader()
            writer.writerow(row)
        self.logger.info("Updated H-FedSA round diagnostics: %s", path)

    def _diagnostic_fallback_reason(self, diagnostics: list[dict]) -> str:
        for item in diagnostics:
            reason = str(item.get("gmm_fallback", ""))
            if reason:
                return reason
        return ""

    def _prepare_run_dir(self) -> Path:
        base = Path(self.config.get("output_dir", "results/quick_dev"))
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_dir = base / f"{self.config.get('experiment_name', 'experiment')}_{timestamp}"
        run_dir.mkdir(parents=True, exist_ok=True)
        config_path = self.config.get("_config_path")
        if config_path:
            shutil.copy2(config_path, run_dir / "config.yaml")
        with (run_dir / "config_resolved.yaml").open("w", encoding="utf-8") as f:
            yaml.safe_dump(self.config, f, sort_keys=False)
        return run_dir

    def _write_data_metadata(self) -> None:
        metadata_path = self.run_dir / "data_diagnostics.json"
        with metadata_path.open("w", encoding="utf-8") as f:
            json.dump(self.fed_data.metadata, f, indent=2)
        self.logger.info("Saved data diagnostics: %s", metadata_path)
        label_distribution = self.fed_data.metadata.get("client_label_distribution", [])
        if label_distribution:
            path = self.run_dir / "client_label_distribution.csv"
            with path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=list(label_distribution[0].keys()))
                writer.writeheader()
                writer.writerows(label_distribution)
            self.logger.info("Saved client label distribution: %s", path)
        partition_summary = self.fed_data.metadata.get("partition_summary", {})
        if partition_summary:
            path = self.run_dir / "partition_summary.json"
            with path.open("w", encoding="utf-8") as f:
                json.dump(partition_summary, f, indent=2)
            self.logger.info("Saved partition summary: %s", path)

    def _write_aggregation_debug(self, defense_name: str, rows: list[dict]) -> None:
        if not rows:
            return
        debug_path = self.run_dir / f"aggregation_debug_{defense_name}.csv"
        with debug_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        self.logger.info("Saved aggregation debug: %s", debug_path)

    def _write_beta_trace(self, defense_name: str, rows: list[dict]) -> None:
        if not rows:
            return
        trace_path = self.run_dir / f"hfedsa_beta_trace_{defense_name}.csv"
        fieldnames = [
            "round",
            "defense",
            "beta_mode",
            "previous_beta",
            "beta_explore",
            "state_mean",
            "state_std",
            "reward",
            "actor_loss",
            "critic_loss",
            "replay_size",
            "predicted_malicious_mean_weight",
            "malicious_weighted_contribution",
            "aggregated_update_norm",
            "aggregated_norm_spike",
        ]
        with trace_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow({field: row.get(field, "NA") for field in fieldnames})
        self.logger.info("Saved H-FedSA beta trace: %s", trace_path)

    def _write_adaptive_attack_trace(self, defense_name: str, rows: list[dict]) -> None:
        if not rows:
            return
        trace_path = self.run_dir / f"adaptive_attack_trace_{defense_name}.csv"
        fieldnames = [
            "round",
            "client_id",
            "iteration",
            "objective",
            "f_dir",
            "f_int",
            "f_spa",
            "target_f_dir",
            "target_f_int",
            "target_f_spa",
        ]
        with trace_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        self.logger.info("Saved adaptive attack trace: %s", trace_path)

    def _write_final_model_state(self, defense_name: str, global_state: StateDict) -> None:
        safe_defense = defense_name.replace("/", "_").replace("\\", "_")
        path = self.run_dir / f"final_model_{safe_defense}.pt"
        torch.save({name: tensor.detach().cpu() for name, tensor in global_state.items()}, path)
        self.logger.info("Saved final model state: %s", path)

    def _write_metrics(self, rows: list[dict]) -> None:
        if not rows:
            return
        metrics_path = self.run_dir / "metrics.csv"
        fieldnames = [
            "round",
            "method",
            "dataset",
            "attack_type",
            "seed",
            "accuracy",
            "error_rate",
            "attack_success_rate",
            "num_clients",
            "malicious_ratio",
            "defense",
            "dataset_source",
            "synthetic",
            "train_loss",
            "train_accuracy",
            "test_loss",
            "test_accuracy",
            "clients_per_round",
            "learning_rate",
            "server_learning_rate",
            "server_optimizer",
            "server_lr",
            "bn_buffer_strategy",
            "aggregation_weighting",
            "iid",
            "non_iid_alpha",
            "train_subset_size",
            "test_subset_size",
            "selected_clients",
            "detection_tpr",
            "detection_fpr",
        ]
        with metrics_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        self.logger.info("Saved metrics: %s", metrics_path)

    def _write_summary(self, summaries: dict[str, dict]) -> None:
        summary_path = self.run_dir / "summary.json"
        with summary_path.open("w", encoding="utf-8") as f:
            json.dump(summaries, f, indent=2)
        self.logger.info("Saved summary: %s", summary_path)

    def _write_run_summary(self, summaries: dict[str, dict], runtime_seconds: float) -> None:
        run_summary = {
            "experiment_name": self.config.get("experiment_name", "experiment"),
            "config_path": self.config.get("_config_path", ""),
            "output_dir": str(self.run_dir),
            "dataset": self.config.get("dataset", {}).get("name", "unknown"),
            "dataset_source": self.fed_data.dataset_source,
            "synthetic": self.fed_data.metadata.get("synthetic", False),
            "iid": self.fed_data.metadata.get("iid", False),
            "partition_summary": self.fed_data.metadata.get("partition_summary", {}),
            "malicious_client_ids": self.fed_data.metadata.get("malicious_client_ids", []),
            "unseen_client_ids": self.fed_data.metadata.get("unseen_client_ids", []),
            "unseen_shift_type": self.fed_data.metadata.get("unseen_shift_type", "none"),
            "attack_type": self.config.get("attack", {}).get("type", "none"),
            "malicious_ratio": float(self.config.get("federated", {}).get("malicious_ratio", 0.0)),
            "scaling_factor": float(self.config.get("attack", {}).get("scale_factor", 1.0)),
            "seed": int(self.config["seed"]),
            "rounds": int(self.config.get("federated", {}).get("rounds", 0)),
            "local_epochs": int(self.config.get("federated", {}).get("local_epochs", 0)),
            "server_optimizer": self.config.get("federated", {}).get("server_optimizer", "fedavg"),
            "server_lr": float(self.config.get("federated", {}).get("server_lr", self.config.get("federated", {}).get("server_learning_rate", 1.0))),
            "aggregation_weighting": self.config.get("federated", {}).get("aggregation_weighting", "uniform"),
            "cli_overrides": self.config.get("_cli_overrides", []),
            "final_config": self.config,
            "runtime_seconds": runtime_seconds,
            "summaries": summaries,
        }
        path = self.run_dir / "run_summary.json"
        with path.open("w", encoding="utf-8") as f:
            json.dump(run_summary, f, indent=2)
        self.logger.info("Saved run summary: %s", path)

    def _write_hfedsa_diagnostic_summary(self) -> None:
        diagnostic_files = sorted(self.run_dir.glob("client_diagnostics_*_round_*.csv"))
        if not diagnostic_files:
            return
        rows = []
        for path in diagnostic_files:
            with path.open("r", encoding="utf-8", newline="") as f:
                selected = [row for row in csv.DictReader(f) if row.get("selected") == "True"]
            numeric = [row for row in selected if row.get("final_weight") not in {"", "NA", None}]
            benign = [row for row in numeric if row.get("true_type") == "benign"]
            malicious = [row for row in numeric if row.get("true_type") == "malicious"]
            weights = np.asarray([float(row["final_weight"]) for row in numeric], dtype=float) if numeric else np.asarray([])
            p_benign = np.asarray([float(row["p_benign"]) for row in numeric if row.get("p_benign") not in {"", "NA", None}], dtype=float)
            p_malicious = np.asarray([float(row["p_malicious"]) for row in numeric if row.get("p_malicious") not in {"", "NA", None}], dtype=float)
            benign_weights = np.asarray([float(row["final_weight"]) for row in benign], dtype=float) if benign else np.asarray([])
            malicious_weights = np.asarray([float(row["final_weight"]) for row in malicious], dtype=float) if malicious else np.asarray([])
            benign_mean = float(np.mean(benign_weights)) if benign_weights.size else "NA"
            malicious_mean = float(np.mean(malicious_weights)) if malicious_weights.size else "NA"
            downweight_threshold = (0.5 * benign_mean) if isinstance(benign_mean, float) else 0.0
            rows.append(
                {
                    "round": int(path.stem.split("_")[-1]),
                    "selected_clients": len(selected),
                    "benign_mean_final_weight": benign_mean,
                    "malicious_mean_final_weight": malicious_mean,
                    "malicious_downweighted": bool(isinstance(benign_mean, float) and isinstance(malicious_mean, float) and malicious_mean < benign_mean),
                    "mean_p_benign": float(np.mean(p_benign)) if p_benign.size else "NA",
                    "mean_p_malicious": float(np.mean(p_malicious)) if p_malicious.size else "NA",
                    "significantly_downweighted_clients": int(np.sum(weights < downweight_threshold)) if weights.size and isinstance(benign_mean, float) else 0,
                    "has_nan_or_inf": bool(weights.size and (not np.isfinite(weights).all())),
                    "all_weights_nearly_equal": bool(weights.size > 1 and np.std(weights) < 1e-6),
                    "collapsed_to_few_clients": bool(weights.size and weights.sum() > 0 and weights.max() / weights.sum() > 0.8),
                }
            )
        out_path = self.run_dir / "hfedsa_diagnostic_summary.csv"
        with out_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        self.logger.info("Saved H-FedSA diagnostic summary: %s", out_path)

    def _resolve_device(self, requested: str) -> torch.device:
        if requested == "auto":
            return torch.device("cuda" if torch.cuda.is_available() else "cpu")
        return torch.device(requested)
