#!/usr/bin/env python3
"""
CLI Runner for Incremental Database Ingestion & Adaptive Cluster Scaling Benchmark.
Imports benchmark engine from src.benchmark.
"""

from __future__ import annotations

import argparse
import os
import sys

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.benchmark import (
    IncrementalScalingHarness,
    run_incremental_scaling_demonstration,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Incremental Database & Scaling Benchmark")
    parser.add_argument(
        "--steps",
        type=str,
        default="150,600,1998",
        help="Comma-separated sample steps (default: 150,600,1998)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="reports",
        help="Directory to save scaling report",
    )
    args = parser.parse_args()
    steps = [int(x.strip()) for x in args.steps.split(",") if x.strip()]
    sys.exit(run_incremental_scaling_demonstration(sample_steps=steps, output_dir=args.output_dir))


if __name__ == "__main__":
    main()
