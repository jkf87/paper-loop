"""Generate publication-quality figures from experimental results."""
import json
import sys
from pathlib import Path

sys.path.insert(0, "/Users/conanssam-m4/autoresearch-paper/jamo-lora/code")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

RESULTS_DIR = Path("/Users/conanssam-m4/autoresearch-paper/jamo-lora/results")
FIGURES_DIR = Path("/Users/conanssam-m4/autoresearch-paper/deliverables/charts")
FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def load_all_results():
    """Load all metrics.json files."""
    results = []
    for d in sorted(RESULTS_DIR.iterdir()):
        m = d / "metrics.json"
        if m.exists():
            with open(m) as f:
                results.append(json.load(f))
    return results


def fig_rank_scaling():
    """Figure 1: CER and trainable params vs LoRA rank."""
    results = load_all_results()

    # Filter standard LoRA (seed=42) + baseline
    standard = [r for r in results if "seed" not in r["run_name"] and "jamo" not in r["run_name"]]

    # Map to rank values
    data = []
    for r in standard:
        name = r["run_name"]
        if "baseline" in name:
            data.append((0, r["cer"] * 100, 0))
        elif "r4" in name and "r64" not in name:
            data.append((4, r["cer"] * 100, 1.62))
        elif "r8" in name:
            data.append((8, r["cer"] * 100, 3.24))
        elif "r16" in name and "r16_seed" not in name:
            data.append((16, r["cer"] * 100, 6.49))
        elif "r32" in name:
            data.append((32, r["cer"] * 100, 12.58))
        elif "r64" in name:
            data.append((64, r["cer"] * 100, 25.17))

    data.sort(key=lambda x: x[0])
    ranks, cers, params = zip(*data)

    fig, ax1 = plt.subplots(figsize=(8, 5))

    # CER line
    color1 = "#2563eb"
    ax1.plot(ranks, cers, "o-", color=color1, linewidth=2.5, markersize=10, label="CER (%)", zorder=3)
    ax1.set_xlabel("LoRA Rank (r)", fontsize=13)
    ax1.set_ylabel("CER (%)", fontsize=13, color=color1)
    ax1.tick_params(axis="y", labelcolor=color1)
    ax1.set_ylim(6, 15)
    ax1.grid(True, alpha=0.3)

    # Annotate CER values
    for x, y in zip(ranks, cers):
        ax1.annotate(f"{y:.2f}%", (x, y), textcoords="offset points",
                    xytext=(0, 12), ha="center", fontsize=10, color=color1, fontweight="bold")

    # Params bar
    ax2 = ax1.twinx()
    color2 = "#dc2626"
    bar_width = [0.5] + [max(0.5, r * 0.08) for r in ranks[1:]]
    ax2.bar(ranks, params, alpha=0.3, color=color2, width=bar_width, label="Trainable Params (M)")
    ax2.set_ylabel("Trainable Parameters (M)", fontsize=13, color=color2)
    ax2.tick_params(axis="y", labelcolor=color2)

    # Title
    ax1.set_title("LoRA Rank Scaling: CER vs Parameter Count", fontsize=14, fontweight="bold", pad=15)

    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right", fontsize=11)

    plt.tight_layout()
    path = FIGURES_DIR / "fig_rank_scaling.png"
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")


def fig_efficiency():
    """Figure 2: Parameter efficiency (CER reduction per M params)."""
    results = load_all_results()
    standard = [r for r in results if "seed" not in r["run_name"] and "jamo" not in r["run_name"] and "baseline" not in r["run_name"]]

    baseline_cer = 13.18
    data = []
    for r in standard:
        name = r["run_name"]
        cer_reduction = baseline_cer - r["cer"] * 100
        if "r4" in name and "r64" not in name:
            data.append(("r=4", 1.62, cer_reduction))
        elif "r8" in name:
            data.append(("r=8", 3.24, cer_reduction))
        elif "r16" in name:
            data.append(("r=16", 6.49, cer_reduction))
        elif "r32" in name:
            data.append(("r=32", 12.58, cer_reduction))
        elif "r64" in name:
            data.append(("r=64", 25.17, cer_reduction))

    data.sort(key=lambda x: x[1])

    fig, ax = plt.subplots(figsize=(8, 5))
    names, params, reductions = zip(*data)

    colors = ["#3b82f6", "#2563eb", "#16a34a", "#eab308", "#dc2626"][:len(data)]
    scatter = ax.scatter(params, reductions, c=colors, s=200, zorder=3, edgecolors="black", linewidth=1.5)

    for name, p, red in data:
        ax.annotate(name, (p, red), textcoords="offset points",
                   xytext=(10, 5), fontsize=11, fontweight="bold")

    # Highlight r=16 as optimal
    r16_data = [d for d in data if d[0] == "r=16"]
    if r16_data:
        _, p16, r16 = r16_data[0]
        ax.annotate("optimal\ntrade-off", (p16, r16), textcoords="offset points",
                   xytext=(-50, -30), fontsize=10, color="#16a34a",
                   arrowprops=dict(arrowstyle="->", color="#16a34a", lw=1.5))

    ax.set_xlabel("Trainable Parameters (M)", fontsize=13)
    ax.set_ylabel("CER Reduction from Baseline (%p)", fontsize=13)
    ax.set_title("Parameter Efficiency: CER Improvement vs Model Complexity", fontsize=14, fontweight="bold", pad=15)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    path = FIGURES_DIR / "fig_efficiency.png"
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")


def fig_multiseed():
    """Figure 3: Multi-seed r=16 with error bars (if available)."""
    results = load_all_results()

    # Find all r=16 results (including multi-seed)
    r16_results = [r for r in results if "r16" in r["run_name"]]
    if len(r16_results) < 2:
        print("Not enough multi-seed results yet, skipping fig_multiseed")
        return

    cers = [r["cer"] * 100 for r in r16_results]
    wers = [r["wer"] * 100 for r in r16_results]
    names = [r["run_name"].replace("standard_lora_", "") for r in r16_results]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))

    # CER
    bars1 = ax1.bar(names, cers, color="#2563eb", alpha=0.8, edgecolor="black")
    ax1.axhline(y=np.mean(cers), color="red", linestyle="--", linewidth=1.5,
               label=f"Mean: {np.mean(cers):.2f}% (SD: {np.std(cers):.2f})")
    ax1.set_ylabel("CER (%)", fontsize=12)
    ax1.set_title("CER across seeds (r=16)", fontsize=13, fontweight="bold")
    ax1.legend(fontsize=10)
    ax1.tick_params(axis="x", rotation=30)

    # WER
    bars2 = ax2.bar(names, wers, color="#dc2626", alpha=0.8, edgecolor="black")
    ax2.axhline(y=np.mean(wers), color="blue", linestyle="--", linewidth=1.5,
               label=f"Mean: {np.mean(wers):.2f}% (SD: {np.std(wers):.2f})")
    ax2.set_ylabel("WER (%)", fontsize=12)
    ax2.set_title("WER across seeds (r=16)", fontsize=13, fontweight="bold")
    ax2.legend(fontsize=10)
    ax2.tick_params(axis="x", rotation=30)

    plt.suptitle("Statistical Validation: Multi-Seed Evaluation at r=16", fontsize=14, fontweight="bold")
    plt.tight_layout()

    path = FIGURES_DIR / "fig_multiseed.png"
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")


if __name__ == "__main__":
    print("Generating figures from available results...")
    fig_rank_scaling()
    fig_efficiency()
    fig_multiseed()
    print("Done!")
