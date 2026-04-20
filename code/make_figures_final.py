"""
Generate IEEE-quality publication figures for LoRA rank scaling experiments.
"""
import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# IEEE quality settings
plt.rcParams.update({
    'font.size': 9,
    'font.family': 'serif',
    'font.serif': ['Times New Roman'],
    'axes.labelsize': 10,
    'axes.titlesize': 10,
    'xtick.labelsize': 8,
    'ytick.labelsize': 8,
    'legend.fontsize': 8,
    'figure.dpi': 100,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
})

# Color-blind safe palette (Okabe-Ito)
COLORS = {
    'blue': '#0072B2',
    'orange': '#D55E00',
    'green': '#009E73',
    'pink': '#CC79A7',
    'light_blue': '#56B4E9',
    'yellow': '#F0E442',
    'dark_blue': '#000000',
}

RESULTS_DIR = Path("/Users/conanssam-m4/autoresearch-paper/final_deliverables/03_experiments/results")
FIGURES_DIR = Path("/Users/conanssam-m4/autoresearch-paper/final_deliverables/02_full_paper/charts")
FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def load_metrics(path: Path) -> dict:
    """Load metrics.json file."""
    with open(path) as f:
        return json.load(f)


def fig_rank_scaling():
    """
    Figure 1: LoRA Rank Scaling - CER and trainable parameters.
    Dual-axis: line plot for CER, bar plot for trainable params.
    """
    # Load data
    baseline = load_metrics(RESULTS_DIR / "baseline_whisper_small" / "metrics.json")

    ranks = [4, 8, 16, 32, 64]
    cer_values = []
    param_values = []

    # Parameter counts (M) for Whisper Small LoRA
    # These are approximate based on Whisper Small's hidden dimension (768)
    # LoRA params = 2 * L * rank * hidden_dim where L is number of adapter layers
    param_map = {
        4: 1.62,
        8: 3.24,
        16: 6.49,
        32: 12.58,
        64: 25.17,
    }

    for rank in ranks:
        metrics = load_metrics(RESULTS_DIR / f"standard_lora_r{rank}" / "metrics.json")
        cer_values.append(metrics["cer"] * 100)
        param_values.append(param_map[rank])

    baseline_cer = baseline["cer"] * 100

    # Create figure - single column width (~3.5 inches)
    fig, ax1 = plt.subplots(figsize=(3.5, 2.5))

    # CER line plot (left y-axis)
    ax1.plot(ranks, cer_values, 'o-',
             color=COLORS['blue'], linewidth=1.8, markersize=5,
             label='CER', zorder=3)

    # Baseline dashed line
    ax1.axhline(y=baseline_cer, color=COLORS['orange'],
                linestyle='--', linewidth=1.2,
                label=f'Baseline ({baseline_cer:.2f}%)')

    ax1.set_xlabel('LoRA Rank (r)', fontsize=9)
    ax1.set_ylabel('CER (%)', fontsize=9, color=COLORS['blue'])
    ax1.tick_params(axis='y', labelcolor=COLORS['blue'])
    ax1.set_ylim(7, 14)
    ax1.set_xscale('log')  # Log scale for ranks
    ax1.set_xticks(ranks)
    ax1.set_xticklabels(['4', '8', '16', '32', '64'])
    ax1.grid(True, alpha=0.25, axis='y', linestyle='-')

    # Annotate CER values
    for rank, cer in zip(ranks, cer_values):
        ax1.annotate(f'{cer:.2f}', (rank, cer),
                    textcoords='offset points', xytext=(0, 8),
                    ha='center', fontsize=7, color=COLORS['blue'])

    # Trainable parameters bar plot (right y-axis)
    ax2 = ax1.twinx()
    bars = ax2.bar(ranks, param_values, alpha=0.25,
                   color=COLORS['orange'], width=5, label='Params (M)')
    ax2.set_ylabel('Trainable Parameters (M)', fontsize=9, color=COLORS['orange'])
    ax2.tick_params(axis='y', labelcolor=COLORS['orange'])
    ax2.set_ylim(0, 30)

    # Legend - combine both axes
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2,
               loc='upper right', frameon=False, numpoints=1,
               handletextpad=0.5, borderaxespad=0.3, fontsize=7)

    plt.tight_layout()

    # Save PNG
    png_path = FIGURES_DIR / "fig_rank_scaling.png"
    plt.savefig(png_path, dpi=300, bbox_inches='tight', pad_inches=0.05)

    # Save PDF (vector)
    pdf_path = FIGURES_DIR / "fig_rank_scaling.pdf"
    plt.savefig(pdf_path, dpi=300, bbox_inches='tight', pad_inches=0.05, format='pdf')

    plt.close()
    print(f"✓ Figure 1 saved: {png_path}")
    print(f"✓ Figure 1 saved: {pdf_path}")


def fig_multiseed_variance():
    """
    Figure 2: Multi-seed variance comparison - r=16 vs r=64.
    Box plots with individual seed points and mean markers.
    """
    # Load multi-seed data for r=16
    r16_cers = [
        load_metrics(RESULTS_DIR / "standard_lora_r16" / "metrics.json")["cer"] * 100,  # 8.45 (main run)
        load_metrics(RESULTS_DIR / "standard_lora_r16_seed123" / "metrics.json")["cer"] * 100,  # 9.33
        load_metrics(RESULTS_DIR / "standard_lora_r16_seed456" / "metrics.json")["cer"] * 100,  # 9.29
        load_metrics(RESULTS_DIR / "standard_lora_r16_seed789" / "metrics.json")["cer"] * 100,  # 9.54
    ]

    # Load multi-seed data for r=64
    r64_cers = [
        load_metrics(RESULTS_DIR / "standard_lora_r64" / "metrics.json")["cer"] * 100,  # 8.04 (main run)
        load_metrics(RESULTS_DIR / "standard_lora_r64_seed123" / "metrics.json")["cer"] * 100,  # 7.94
        load_metrics(RESULTS_DIR / "standard_lora_r64_seed456" / "metrics.json")["cer"] * 100,  # 7.98
        load_metrics(RESULTS_DIR / "standard_lora_r64_seed789" / "metrics.json")["cer"] * 100,  # 8.10
    ]

    # Statistics
    r16_mean = np.mean(r16_cers)
    r16_std = np.std(r16_cers)
    r64_mean = np.mean(r64_cers)
    r64_std = np.std(r64_cers)

    # Create figure - single column width
    fig, ax = plt.subplots(figsize=(3.5, 2.5))

    # Positions
    x_pos = [1, 2]
    box_width = 0.5

    # Box plots
    bp = ax.boxplot([r16_cers, r64_cers],
                    positions=x_pos,
                    widths=box_width,
                    patch_artist=True,
                    showmeans=True,
                    meanline=True,
                    showfliers=False,
                    boxprops=dict(facecolor='none', edgecolor=COLORS['blue'], linewidth=1.2),
                    whiskerprops=dict(color=COLORS['blue'], linewidth=1.2),
                    capprops=dict(color=COLORS['blue'], linewidth=1.2),
                    medianprops=dict(color=COLORS['orange'], linewidth=1.2),
                    meanprops=dict(color=COLORS['green'], linewidth=1.2, linestyle='-'),
                    )

    # Color the boxes
    bp['boxes'][0].set_facecolor(plt.cm.Blues(0.2))
    bp['boxes'][1].set_facecolor(plt.cm.Blues(0.4))

    # Individual seed points (jittered)
    for i, (cers, x) in enumerate([(r16_cers, 1), (r64_cers, 2)]):
        jitter = np.random.normal(0, 0.05, size=len(cers))
        ax.scatter(x + jitter, cers,
                   color=COLORS['dark_blue'],
                   s=15, alpha=0.6, zorder=3,
                   edgecolors='white', linewidths=0.5)

    # Annotate statistics
    ax.annotate(f'μ={r16_mean:.2f}%\nσ={r16_std:.2f}', (1, r16_mean),
               textcoords='offset points', xytext=(0, 15),
               ha='center', fontsize=7,
               bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=COLORS['blue'], linewidth=0.5))

    ax.annotate(f'μ={r64_mean:.2f}%\nσ={r64_std:.2f}', (2, r64_mean),
               textcoords='offset points', xytext=(0, -25),
               ha='center', fontsize=7,
               bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=COLORS['blue'], linewidth=0.5))

    # Labels
    ax.set_xticks(x_pos)
    ax.set_xticklabels(['r=16', 'r=64'], fontsize=9)
    ax.set_ylabel('CER (%)', fontsize=10)
    ax.set_xlabel('LoRA Rank', fontsize=10)
    ax.set_title('Multi-Seed Variance Analysis', fontsize=10, pad=5)

    # Grid
    ax.grid(True, alpha=0.25, axis='y', linestyle='-')
    ax.set_ylim(7, 10)

    # Legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor=COLORS['dark_blue'],
               markersize=5, label='Individual seed', markeredgecolor='white', markeredgewidth=0.5),
        Line2D([0], [0], color=COLORS['blue'], linewidth=1.2, label='Box (IQR)'),
        Line2D([0], [0], color=COLORS['orange'], linewidth=1.2, label='Median'),
        Line2D([0], [0], color=COLORS['green'], linewidth=1.2, label='Mean'),
    ]
    ax.legend(handles=legend_elements, loc='upper right',
              frameon=False, fontsize=6,
              handletextpad=0.5, borderaxespad=0.3)

    plt.tight_layout()

    # Save PNG
    png_path = FIGURES_DIR / "fig_multiseed_variance.png"
    plt.savefig(png_path, dpi=300, bbox_inches='tight', pad_inches=0.05)

    # Save PDF (vector)
    pdf_path = FIGURES_DIR / "fig_multiseed_variance.pdf"
    plt.savefig(pdf_path, dpi=300, bbox_inches='tight', pad_inches=0.05, format='pdf')

    plt.close()
    print(f"✓ Figure 2 saved: {png_path}")
    print(f"✓ Figure 2 saved: {pdf_path}")

    # Print statistics
    print("\n📊 Multi-seed Statistics:")
    print(f"   r=16:  mean={r16_mean:.2f}%, std={r16_std:.2f}%, values={r16_cers}")
    print(f"   r=64:  mean={r64_mean:.2f}%, std={r64_std:.2f}%, values={r64_cers}")
    print(f"   Improvement: {((r16_mean - r64_mean) / r16_mean * 100):.2f}%")


if __name__ == "__main__":
    print("=" * 60)
    print("Generating IEEE-quality publication figures...")
    print("=" * 60)

    fig_rank_scaling()
    print()
    fig_multiseed_variance()

    print("\n" + "=" * 60)
    print("✓ All figures generated successfully!")
    print("=" * 60)
