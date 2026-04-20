"""Run additional experiments: r=8, r=32, and multi-seed r=16."""
import gc
import json
import sys
import time

sys.path.insert(0, "/Users/conanssam-m4/autoresearch-paper/jamo-lora/code")

from config import ExperimentConfig
from train import train_and_evaluate


def run_experiment(rank, seed=42, tag="standard_lora"):
    """Run a single LoRA experiment."""
    config = ExperimentConfig()
    config.lora_r = rank
    config.lora_alpha = rank * 2
    config.seed = seed

    if seed != 42:
        run_name = f"standard_lora_r{rank}_seed{seed}"
    else:
        run_name = f"standard_lora_r{rank}"

    # Check if already done
    metrics_path = config.results_dir / run_name / "metrics.json"
    if metrics_path.exists():
        print(f"[SKIP] {run_name} already exists")
        with open(metrics_path) as f:
            return json.load(f)

    # Override run_name in config
    original_run_name = config.run_name
    config.run_name = lambda t: run_name

    result = train_and_evaluate(config, experiment_type=tag)

    # Cleanup
    gc.collect()
    try:
        import torch
        if hasattr(torch.mps, "empty_cache"):
            torch.mps.empty_cache()
    except Exception:
        pass

    # Remove checkpoint to save disk
    import shutil
    ckpt_dir = config.checkpoint_dir / run_name
    if ckpt_dir.exists():
        shutil.rmtree(ckpt_dir)
        print(f"  Cleaned checkpoint: {run_name}")

    return result


def main():
    t0 = time.time()
    results = []

    # 1. r=8 (new)
    print("\n[1/5] LoRA r=8...")
    results.append(run_experiment(8))

    # 2. r=32 (new)
    print("\n[2/5] LoRA r=32...")
    results.append(run_experiment(32))

    # 3-5. Multi-seed r=16
    for i, seed in enumerate([123, 456, 789]):
        print(f"\n[{i+3}/5] LoRA r=16 seed={seed}...")
        results.append(run_experiment(16, seed=seed))

    total = time.time() - t0
    print(f"\nAll done in {total/60:.1f} minutes")

    # Print summary
    print(f"\n{'='*80}")
    print(f"{'Run':<30} {'CER':>8} {'WER':>8}")
    print(f"{'='*80}")
    for r in results:
        print(f"{r['run_name']:<30} {r['cer']:>8.4f} {r['wer']:>8.4f}")


if __name__ == "__main__":
    main()
