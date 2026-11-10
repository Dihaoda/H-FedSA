from __future__ import annotations

import csv
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean, stdev
from typing import Iterable


GROUP_FIELDS = ("dataset", "attack_type", "method")


def discover_metrics(paths: Iterable[str | Path]) -> list[Path]:
    discovered: set[Path] = set()
    for value in paths:
        path = Path(value)
        if path.is_file() and path.name == "metrics.csv":
            discovered.add(path.resolve())
        elif path.is_dir():
            discovered.update(item.resolve() for item in path.rglob("metrics.csv"))
    return sorted(discovered)


def read_final_rows(paths: Iterable[str | Path]) -> list[dict[str, str]]:
    final_rows: list[dict[str, str]] = []
    for path in discover_metrics(paths):
        with path.open("r", encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream))
        by_run: dict[tuple[str, str, str, str], dict[str, str]] = {}
        for row in rows:
            key = tuple(row.get(field, "") for field in (*GROUP_FIELDS, "seed"))
            previous = by_run.get(key)
            if previous is None or int(row["round"]) > int(previous["round"]):
                by_run[key] = dict(row)
        for row in by_run.values():
            row["metrics_path"] = str(path)
            final_rows.append(row)
    return final_rows


def summarize_final_rows(rows: Iterable[dict[str, str]]) -> list[dict]:
    grouped: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[tuple(row.get(field, "") for field in GROUP_FIELDS)].append(row)

    summaries = []
    for key, group in sorted(grouped.items()):
        seeds = [int(row["seed"]) for row in group]
        if len(seeds) != len(set(seeds)):
            raise ValueError(f"Duplicate seeds in formal result group {key}: {seeds}")
        error_rates = [_number(row.get("error_rate")) for row in group]
        accuracies = [_number(row.get("accuracy", row.get("test_accuracy"))) for row in group]
        attack_success_rates = [_number(row.get("attack_success_rate")) for row in group]
        summaries.append(
            {
                "dataset": key[0],
                "attack_type": key[1],
                "method": key[2],
                "run_count": len(group),
                "seeds": sorted(seeds),
                "rounds": sorted(int(row["round"]) for row in group),
                "error_rate": _stats(error_rates),
                "accuracy": _stats(accuracies),
                "attack_success_rate": _stats(attack_success_rates),
                "metrics_paths": sorted(row["metrics_path"] for row in group),
            }
        )
    return summaries


def attach_paper_target(summary: dict, target: dict, required_runs: int) -> dict:
    result = dict(summary)
    result["required_runs"] = int(required_runs)
    result["complete"] = int(summary["run_count"]) == int(required_runs)
    result["paper_target"] = dict(target)
    measured_error = summary.get("error_rate", {}).get("mean")
    target_error = target.get("error_mean")
    result["error_mean_gap"] = (
        float(measured_error) - float(target_error)
        if measured_error is not None and target_error is not None
        else None
    )
    measured_asr = summary.get("attack_success_rate", {}).get("mean")
    target_asr = target.get("asr_mean")
    result["asr_mean_gap"] = (
        float(measured_asr) - float(target_asr)
        if measured_asr is not None and target_asr is not None
        else None
    )
    return result


def _number(value: object) -> float | None:
    if value in {None, "", "NA", "N/A"}:
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def _stats(values: Iterable[float | None]) -> dict:
    numeric = [float(value) for value in values if value is not None]
    return {
        "count": len(numeric),
        "mean": mean(numeric) if numeric else None,
        "sample_std": stdev(numeric) if len(numeric) > 1 else None,
        "min": min(numeric) if numeric else None,
        "max": max(numeric) if numeric else None,
    }

