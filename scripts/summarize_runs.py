#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

from src.utils.results import attach_paper_target, read_final_rows, summarize_final_rows


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Aggregate every discovered final run; duplicate seeds are rejected."
    )
    parser.add_argument("paths", nargs="+", help="Run directories or metrics.csv files.")
    parser.add_argument("--target-file", type=Path)
    parser.add_argument("--attack", help="Target-manifest attack key, e.g. no_attack.")
    parser.add_argument("--method", help="Target-manifest method key, e.g. fedavg.")
    parser.add_argument("--output", type=Path, help="Optional JSON output path.")
    args = parser.parse_args()

    summaries = summarize_final_rows(read_final_rows(args.paths))
    if args.target_file:
        if not args.attack or not args.method:
            parser.error("--target-file requires --attack and --method")
        target_doc = yaml.safe_load(args.target_file.read_text(encoding="utf-8"))
        target = target_doc["targets"][args.attack][args.method]
        required_runs = int(target_doc["evaluation_policy"]["required_runs"])
        matching = [
            item
            for item in summaries
            if item["attack_type"] == args.attack and item["method"] == args.method
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

