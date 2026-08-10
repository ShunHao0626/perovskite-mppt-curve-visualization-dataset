#!/usr/bin/env python3
"""
Batch plot generator using the Advanced Materials journal style.
Applies to ALL devices in data/ folder.
Saves output to pub_style_all/ folder.
"""

import os
os.environ.setdefault("MPLCONFIGDIR", os.path.join(os.path.dirname(__file__), ".mplconfig"))

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.colors import LinearSegmentedColormap
import warnings

warnings.filterwarnings("ignore")

BASE_DIR = "/Users/shunhao/Desktop/1.曲线图-改图片形式"
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "pub_style_all")


def parse_csv_values(value_str):
    lines = str(value_str).strip().split('\n')
    values = []
    for line in lines:
        line = line.strip()
        if line:
            try:
                values.append(float(line))
            except ValueError:
                continue
    return np.array(values)


def get_xticks_for_range(x_max):
    """Dynamically set x ticks based on data range."""
    if x_max <= 50:
        return list(range(0, int(x_max) + 1, 10))
    elif x_max <= 100:
        return list(range(0, int(x_max) + 1, 20))
    elif x_max <= 200:
        return list(range(0, int(x_max) + 1, 50))
    elif x_max <= 400:
        return list(range(0, int(x_max) + 1, 100))
    elif x_max <= 800:
        return list(range(0, int(x_max) + 1, 200))
    else:
        return list(range(0, int(x_max) + 1, 500))


def plot_pub_style_all(device_name, output_dir):
    csv_path = os.path.join(DATA_DIR, device_name, "metadata_pv.csv")
    if not os.path.exists(csv_path):
        print(f"[SKIP] {csv_path} not found")
        return False

    df = pd.read_csv(csv_path)
    if df.empty:
        print(f"[SKIP] Empty: {csv_path}")
        return False

    first_idx = df[["ID", "Figure", "Sub-figure"]].drop_duplicates().iloc[0]
    group = df[(df["ID"] == first_idx["ID"]) &
               (df["Figure"] == first_idx["Figure"]) &
               (df["Sub-figure"] == first_idx["Sub-figure"])]

    xlabel = group["X-label"].iloc[0] if "X-label" in group.columns else "Time (h)"
    ylabel = group["Y-label"].iloc[0] if "Y-label" in group.columns else "Normalized PCE"

    all_x = []
    all_y = []
    for _, row in group.iterrows():
        x_vals = parse_csv_values(row["Value_x"])
        y_vals = parse_csv_values(row["Value_y"])
        if len(x_vals) == 0 or len(y_vals) == 0:
            continue
        min_len = min(len(x_vals), len(y_vals))
        all_x.extend(x_vals[:min_len])
        all_y.extend(y_vals[:min_len])

    if len(all_x) == 0:
        print(f"[SKIP] No valid data: {device_name}")
        return False

    all_x = np.array(all_x)
    all_y = np.array(all_y)
    sort_idx = np.argsort(all_x)
    all_x = all_x[sort_idx]
    all_y = all_y[sort_idx]

    # ── Figure: 4K 16:9 landscape ────────────────────────────────
    fig_w = 16.0
    fig_h = 9.0
    dpi = 240

    fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi)
    ax = fig.add_axes([0.08, 0.10, 0.87, 0.83])

    font_name = "Arial"
    try:
        arial_prop = fm.FontProperties(family=font_name)
        _ = fm.fontManager.findfont(arial_prop)
    except Exception:
        font_name = "DejaVu Sans"

    # ── Axis limits ───────────────────────────────────────────────
    x_max_data = all_x.max()
    y_max_data = all_y.max()

    ax.set_xlim(0, x_max_data)
    ax.set_ylim(0, 1.0)

    # ── Ticks ─────────────────────────────────────────────────────
    ax.set_xticks(get_xticks_for_range(x_max_data))
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])

    # ── Axis labels (bold Arial) ─────────────────────────────────
    ax.set_xlabel(xlabel, fontsize=22, fontweight="bold",
                  fontname=font_name, color="black")
    ax.set_ylabel(ylabel, fontsize=22, fontweight="bold",
                  fontname=font_name, color="black")

    # ── Title: device name centered (bold Arial) ─────────────────
    ax.set_title(device_name, fontsize=24, fontweight="bold",
                 fontname=font_name, color="black",
                 pad=18, loc="center")

    # ── Spines: only left and bottom visible ─────────────────────
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_linewidth(1.5)
    ax.spines['left'].set_linewidth(1.5)
    ax.spines['bottom'].set_position(('outward', 0))
    ax.spines['left'].set_position(('outward', 0))

    # ── Tick style ────────────────────────────────────────────────
    ax.tick_params(axis='both', direction='in', length=6, width=1.0,
                   top=False, right=False, labelsize=16,
                   labelcolor="black", color="black")

    # ── NO grid lines ─────────────────────────────────────────────
    ax.grid(False)

    # ── Brown gradient background on left side (0-80h region) ─────
    grad_x1 = min(80.0, x_max_data * 0.22)

    gradient_colors = ['#3D1A0A', '#7B3A1A', '#B06030', '#D08050', '#F0C090', '#FFFFFF']
    grad_cmap = LinearSegmentedColormap.from_list('brown_grad', gradient_colors)

    grad_data = np.linspace(0, 1, 256).reshape(1, -1)
    ax.imshow(grad_data, extent=[0, grad_x1, 0, 1.0],
              origin='lower', aspect='auto', cmap=grad_cmap,
              alpha=0.35, zorder=0)

    # ── Tan curve data ────────────────────────────────────────────
    tan_color = '#C4956A'

    ax.plot(all_x, all_y,
            color=tan_color,
            linewidth=2.5,
            linestyle='-',
            zorder=3,
            solid_capstyle='round',
            solid_joinstyle='round')

    # ── Scatter points: periodic sampling ─────────────────────────
    n_total = len(all_x)
    n_samples = 45
    step = max(1, n_total // n_samples)
    sample_idx = list(range(0, n_total, step))
    if sample_idx and sample_idx[-1] != n_total - 1:
        sample_idx.append(n_total - 1)

    solid_freq = 5
    for i, idx in enumerate(sample_idx):
        is_solid = (i % solid_freq == 0)
        if is_solid:
            ax.scatter(all_x[idx], all_y[idx],
                       color=tan_color,
                       s=55,
                       zorder=5,
                       marker='o',
                       linewidths=0,
                       edgecolors='none')
        else:
            ax.scatter(all_x[idx], all_y[idx],
                       facecolors='white',
                       edgecolors=tan_color,
                       s=55,
                       zorder=5,
                       marker='o',
                       linewidths=1.8)

    # ── Legend box at bottom left ───────────────────────────────
    # Extract legend label from data if available
    legend_label = "6-2"
    if "Legend" in group.columns:
        val = group["Legend"].iloc[0]
        if val and str(val).strip():
            legend_label = str(val).strip()

    leg = ax.legend(
        [plt.Line2D([0], [0], color=tan_color, linewidth=3.0,
                     marker='o', markersize=8,
                     markerfacecolor=tan_color,
                     markeredgecolor=tan_color,
                     linestyle='-')],
        [legend_label],
        loc='lower left',
        bbox_to_anchor=(0.01, 0.05),
        frameon=True,
        fancybox=False,
        edgecolor='#AAAAAA',
        framealpha=0.9,
        borderpad=0.5,
        labelspacing=0.4,
        handlelength=2.5,
        handletextpad=0.6,
    )

    for text in leg.get_texts():
        text.set_fontsize(14)
        text.set_color('red')
        text.set_fontweight('bold')
        text.set_fontname(font_name)

    leg.get_frame().set_linewidth(1.0)

    # ── Save ─────────────────────────────────────────────────────
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{device_name}.png")
    fig.savefig(output_path, dpi=dpi, bbox_inches='tight',
                pad_inches=0.15, facecolor='white', edgecolor='none')
    plt.close()
    print(f"[OK] {device_name} -> {output_path}")
    return True


def main():
    print("=" * 60)
    print("Batch Plot: Advanced Materials Journal Style")
    print("All devices from data/ -> pub_style_all/")
    print("=" * 60)

    # Collect all device folders
    device_folders = []
    for item in sorted(os.listdir(DATA_DIR)):
        item_path = os.path.join(DATA_DIR, item)
        if os.path.isdir(item_path):
            csv_path = os.path.join(item_path, "metadata_pv.csv")
            if os.path.exists(csv_path):
                device_folders.append(item)

    print(f"\nFound {len(device_folders)} devices")
    print(f"Output: {OUTPUT_DIR}")
    print()

    success = 0
    for i, device_name in enumerate(device_folders):
        print(f"[{i+1}/{len(device_folders)}] {device_name}", end=" ... ")
        if plot_pub_style_all(device_name, OUTPUT_DIR):
            success += 1

    print(f"\n{'=' * 60}")
    print(f"Done! {success}/{len(device_folders)} images saved to {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
