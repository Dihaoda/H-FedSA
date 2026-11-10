from __future__ import annotations

from src.defenses.fedavg import FedAvg
from src.defenses.fltrust import FLTrust
from src.defenses.ddpg_beta_agent import DDPGBetaAgent, DDPGBetaConfig
from src.defenses.hfedsa import HFedSAConfig, HFedSAStatic
from src.defenses.rfa import RFA
from src.defenses.robust_baselines import MSGuard, SafeFLCompatible


def build_defense(name: str, config: dict):
    key = name.lower()
    if key == "fedavg":
        return FedAvg(aggregation_weighting=str(config.get("federated", {}).get("aggregation_weighting", "uniform")))
    if key == "fltrust":
        return FLTrust(min_trust_score=float(config.get("fltrust", {}).get("min_trust_score", 0.0)))
    if key in {"hfedsa", "hfedsa_static", "hfedsa_base", "hfedsa_ema", "hfedsa_ddpg", "hfedsa_ema_normroot", "hfedsa_ddpg_normroot", "hfedsa_ddpg_normroot_retention"}:
        hcfg = _hfedsa_config_for(key, config)
        agent = _build_ddpg_agent(hcfg, config) if str(hcfg.get("beta_mode", "")).lower() == "ddpg" or key == "hfedsa_ddpg" else None
        if key == "hfedsa_ddpg":
            hcfg["beta_mode"] = "ddpg"
        return HFedSAStatic(_build_hfedsa_config(hcfg), name=key if key != "hfedsa" else "hfedsa_static", beta_agent=agent)
    if key == "rfa":
        rcfg = config.get("rfa", {})
        return RFA(
            max_iter=int(rcfg.get("max_iter", 20)),
            tol=float(rcfg.get("tol", 1e-5)),
            eps=float(rcfg.get("eps", 1e-8)),
        )
    if key == "safefl":
        scfg = config.get("safefl", {})
        return SafeFLCompatible(
            rule=str(scfg.get("rule", "signguard")),
            seed=int(scfg.get("seed", config.get("seed", 0))),
            sign_fraction=float(scfg.get("sign_fraction", 0.1)),
            norm_lower=float(scfg.get("norm_lower", 0.1)),
            norm_upper=float(scfg.get("norm_upper", 3.0)),
        )
    if key == "msguard":
        mcfg = config.get("msguard", {})
        bandwidth = mcfg.get("bandwidth")
        return MSGuard(
            quantile=float(mcfg.get("quantile", 0.3)),
            bandwidth=None if bandwidth in {None, "", "auto"} else float(bandwidth),
            min_retained_fraction=float(mcfg.get("min_retained_fraction", 0.5)),
        )
    raise ValueError(f"Unknown defense: {name}")


def _hfedsa_config_for(key: str, config: dict) -> dict:
    if key == "hfedsa_ema":
        hcfg = dict(config.get("hfedsa", {}))
        hcfg.update(config.get("hfedsa_ema", {}))
        hcfg.setdefault("weight_ema_enabled", True)
        hcfg.setdefault("weight_ema_momentum", 0.8)
        return hcfg
    if key == "hfedsa_ema_normroot":
        hcfg = dict(config.get("hfedsa", {}))
        hcfg.update(config.get("hfedsa_ema", {}))
        hcfg.update(config.get("hfedsa_ema_normroot", {}))
        hcfg.setdefault("weight_ema_enabled", True)
        hcfg.setdefault("weight_ema_momentum", 0.8)
        hcfg.setdefault("normalization_mode", "root_norm")
        hcfg.setdefault("normalize_update_to_root", True)
        return hcfg
    if key == "hfedsa_base":
        hcfg = dict(config.get("hfedsa", {}))
        hcfg.update(config.get("hfedsa_base", {}))
        hcfg.setdefault("weight_ema_enabled", False)
        hcfg.setdefault("posterior_clip_enabled", False)
        hcfg.setdefault("weight_bounds_enabled", False)
        hcfg.setdefault("beta_decay_enabled", False)
        return hcfg
    if key == "hfedsa_ddpg":
        hcfg = dict(config.get("hfedsa", {}))
        hcfg.update(config.get("hfedsa_ddpg", {}))
        hcfg.setdefault("beta_mode", "ddpg")
        return hcfg
    if key == "hfedsa_ddpg_normroot":
        hcfg = dict(config.get("hfedsa", {}))
        hcfg.update(config.get("hfedsa_ddpg", {}))
        hcfg.update(config.get("hfedsa_ddpg_normroot", {}))
        hcfg.setdefault("beta_mode", "ddpg")
        hcfg.setdefault("weight_ema_enabled", True)
        hcfg.setdefault("weight_ema_momentum", 0.8)
        hcfg.setdefault("normalization_mode", "root_norm")
        hcfg.setdefault("normalize_update_to_root", True)
        return hcfg
    if key == "hfedsa_ddpg_normroot_retention":
        hcfg = dict(config.get("hfedsa", {}))
        hcfg.update(config.get("hfedsa_ddpg", {}))
        hcfg.update(config.get("hfedsa_ddpg_normroot", {}))
        hcfg.update(config.get("hfedsa_ddpg_normroot_retention", {}))
        hcfg.setdefault("beta_mode", "ddpg")
        hcfg.setdefault("weight_ema_enabled", True)
        hcfg.setdefault("weight_ema_momentum", 0.8)
        hcfg.setdefault("normalization_mode", "root_norm")
        hcfg.setdefault("normalize_update_to_root", True)
        hcfg.setdefault("retention_floor_enabled", True)
        hcfg.setdefault("retention_floor", 0.05)
        return hcfg
    return config.get("hfedsa", {})


def _build_hfedsa_config(hcfg: dict) -> HFedSAConfig:
    return HFedSAConfig(
        beta_explore=float(hcfg.get("beta_explore", 0.35)),
        malicious_penalty=float(hcfg.get("malicious_penalty", 0.8)),
        detection_threshold=float(hcfg.get("detection_threshold", 0.5)),
        gmm_reg_covar=float(hcfg.get("gmm_reg_covar", 1e-6)),
        gmm_covariance_type=str(hcfg.get("gmm_covariance_type", "full")).lower(),
        gmm_max_iter=int(hcfg.get("gmm_max_iter", 100)),
        gmm_n_init=int(hcfg.get("gmm_n_init", 3)),
        gmm_random_state=int(hcfg.get("gmm_random_state", 0)),
        weight_ema_enabled=bool(hcfg.get("weight_ema_enabled", False)),
        weight_ema_momentum=float(hcfg.get("weight_ema_momentum", 0.8)),
        posterior_clip_enabled=bool(hcfg.get("posterior_clip_enabled", False)),
        posterior_min=float(hcfg.get("posterior_min", 0.001)),
        posterior_max=float(hcfg.get("posterior_max", 0.999)),
        weight_bounds_enabled=bool(hcfg.get("weight_bounds_enabled", False)),
        min_weight=float(hcfg.get("min_weight", 0.0)),
        max_weight=float(hcfg.get("max_weight", 1.0)),
        retention_floor_enabled=bool(hcfg.get("retention_floor_enabled", False)),
        retention_floor=float(hcfg.get("retention_floor", hcfg.get("min_weight", 0.0))),
        retention_mode=str(hcfg.get("retention_mode", "global")).lower(),
        retention_risk_gamma=float(hcfg.get("retention_risk_gamma", 1.0)),
        retention_pmal_threshold=float(hcfg.get("retention_pmal_threshold", 0.3)),
        retention_topk=int(hcfg.get("retention_topk", 10)),
        beta_decay_enabled=bool(hcfg.get("beta_decay_enabled", False)),
        beta_initial=float(hcfg.get("beta_initial", hcfg.get("beta_explore", 0.35))),
        beta_final=float(hcfg.get("beta_final", 0.10)),
        beta_decay_rounds=int(hcfg.get("beta_decay_rounds", 20)),
        ddpg_beta_decay_enabled=bool(hcfg.get("ddpg_beta_decay_enabled", False)),
        ddpg_beta_final_max=float(hcfg.get("ddpg_beta_final_max", 0.05)),
        ddpg_beta_decay_rounds=int(hcfg.get("ddpg_beta_decay_rounds", 100)),
        beta_mode=str(hcfg.get("beta_mode", "static")).lower(),
        normalization_mode=str(hcfg.get("normalization_mode", "none")).lower(),
        feature_mode=str(hcfg.get("feature_mode", "paper")).lower(),
        formula_mode=str(hcfg.get("formula_mode", "paper")).lower(),
        cluster_role_strategy=str(hcfg.get("cluster_role_strategy", "intensity_order")).lower(),
        malicious_hard_gate_enabled=bool(hcfg.get("malicious_hard_gate_enabled", False)),
        malicious_hard_gate_threshold=float(hcfg.get("malicious_hard_gate_threshold", 0.9)),
        ddpg_security_penalty=float(hcfg.get("ddpg_security_penalty", 0.2)),
        ddpg_smoothness_penalty=float(hcfg.get("ddpg_smoothness_penalty", 0.05)),
        ddpg_residual_penalty=float(hcfg.get("ddpg_residual_penalty", 0.0)),
        ddpg_aggregated_norm_penalty=float(hcfg.get("ddpg_aggregated_norm_penalty", 0.0)),
        ddpg_aggregated_norm_target=float(hcfg.get("ddpg_aggregated_norm_target", 1.0)),
        normalize_update_to_root=bool(hcfg.get("normalize_update_to_root", False)),
        update_norm_clip_enabled=bool(hcfg.get("update_norm_clip_enabled", False)),
        update_norm_clip_ratio=float(hcfg.get("update_norm_clip_ratio", hcfg.get("norm_clip_multiple", 1.0))),
    )


def _build_ddpg_agent(hcfg: dict, config: dict) -> DDPGBetaAgent:
    dcfg = dict(config.get("ddpg", {}))
    dcfg.update(hcfg.get("ddpg", {}))
    agent_cfg = DDPGBetaConfig(
        state_dim=int(dcfg.get("state_dim", 39)),
        hidden_dim=int(dcfg.get("hidden_dim", 64)),
        actor_lr=float(dcfg.get("actor_lr", 1e-3)),
        critic_lr=float(dcfg.get("critic_lr", 1e-3)),
        gamma=float(dcfg.get("gamma", 0.95)),
        tau=float(dcfg.get("tau", 0.02)),
        replay_capacity=int(dcfg.get("replay_capacity", 1000)),
        batch_size=int(dcfg.get("batch_size", 16)),
        exploration_noise=float(dcfg.get("exploration_noise", 0.05)),
        min_beta=float(dcfg.get("min_beta", 0.0)),
        max_beta=float(dcfg.get("max_beta", 1.0)),
    )
    return DDPGBetaAgent(agent_cfg, seed=int(config.get("seed", 0)))

