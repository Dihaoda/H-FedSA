#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from src.utils.results import attach_paper_target, read_final_rows, summarize_final_rows


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Aggregate every discovered final run; duplicate seeds are rejected."
    )
    parser.add_argument("paths", nargs="+", help="Run directories or metrics.csv files.")
    parser.add_argument("--target-file", type=Path)
    parser.add_argument("--attack", help="Target-manifest attack key, e.g. no_attack.")
    parser.add_argument("--method", help="Target-manifest method key, e.g. fedavg.")
    parser.add_argument(
        "--run-class",
        help=(
            "Only include this reporting class. Defaults to formal_measured when "
            "--target-file is supplied."
        ),
    )
    parser.add_argument("--output", type=Path, help="Optional JSON output path.")
    args = parser.parse_args()

    run_class = args.run_class or ("formal_measured" if args.target_file else None)
    summaries = summarize_final_rows(read_final_rows(args.paths, run_class=run_class))
    if args.target_file:
        if not args.attack or not args.method:
            parser.error("--target-file requires --attack and --method")
        target_doc = yaml.safe_load(args.target_file.read_text(encoding="utf-8"))
        target = target_doc["targets"][args.attack][args.method]
        required_runs = int(target_doc["evaluation_policy"]["required_runs"])
        aliases = target_doc.get("measured_attack_aliases", {})
        measured_attack_keys = {args.attack}
        measured_attack_keys.update(
            measured for measured, paper_key in aliases.items() if paper_key == args.attack
        )
        matching = [
            item
            for item in summaries
            if item["attack_type"] in measured_attack_keys and item["method"] == args.method
        ]
        if len(matching) != 1:
            raise ValueError(
                f"Expected one measured group for attack={args.attack}, method={args.method}; "
                f"found {len(matching)}"
            )
        payload: object = attach_paper_target(matching[0], target, required_runs)
    else:
        payload = summaries

    rendered = json.dumps(payload, indent=2, sort_keys=False)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

