"""Run LoRA r=64 with 3 additional random seeds (123, 456, 789).

Seed 42 already exists at results/standard_lora_r64/metrics.json.
This script produces standard_lora_r64_seed{123,456,789}/metrics.json.
"""
import gc
import json
import sys
import time
import shutil

sys.path.insert(0, "/Users/conanssam-m4/autoresearch-paper/jamo-lora/code")

from config import ExperimentConfig
from train import train_and_evaluate


def run_experiment(rank, seed):
    config = ExperimentConfig()
    config.lora_r = rank
    config.lora_alpha = rank * 2
    config.seed = seed

    run_name = f"standard_lora_r{rank}_seed{seed}"
    metrics_path = config.results_dir / run_name / "metrics.json"
    if metrics_path.exists():
        print(f"[SKIP] {run_name} already exists")
        with open(metrics_path) as f:
            return json.load(f)

    # Override run_name in config (monkey-patch)
    config.run_name = lambda t: run_name

    result = train_and_evaluate(config, experiment_type="standard_lora")

    # Cleanup MPS + checkpoint dir
    gc.collect()
    try:
        import torch
        if hasattr(torch, "mps") and hasattr(torch.mps, "empty_cache"):
            torch.mps.empty_cache()
    except Exception:
        pass

    ckpt_dir = config.checkpoint_dir / run_name
    if ckpt_dir.exists():
        shutil.rmtree(ckpt_dir, ignore_errors=True)
        print(f"  Cleaned checkpoint: {run_name}")

    return result


def main():
    t0 = time.time()
    results = []

    seeds = [123, 456, 789]
    for i, seed in enumerate(seeds, 1):
        print(f"\n[{i}/{len(seeds)}] LoRA r=64 seed={seed}...")
        results.append(run_experiment(64, seed))

    total = time.time() - t0
    print(f"\nAll done in {total/60:.1f} minutes")

    print(f"\n{'='*80}")
    print(f"{'Run':<35} {'CER':>8} {'WER':>8}")
    print(f"{'='*80}")
    for r in results:
        print(f"{r['run_name']:<35} {r['cer']:>8.4f} {r['wer']:>8.4f}")


if __name__ == "__main__":
    main()
