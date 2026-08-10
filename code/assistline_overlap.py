#!/usr/bin/env python3
"""
Plot perovskite solar cell stability data with 图片145.jpg style.
- Uses REAL data from CSV files
- Gray grid lines (full plot area) matching A613P02_MPPT001_Control_PCE.png
- Orange curve for visibility
"""

import os
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

warnings.filterwarnings("ignore")
matplotlib.use('Agg')

BASE_DIR = "/Users/shunhao/Desktop/1.曲线图-改图片形式"
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "assistline_overlap")

# Style parameters
DPI = 600
FIG_W = 8.0
FIG_H = 5.5
LINE_WIDTH = 2.0
MARKER_SIZE = 6.0
LABEL_FONTSIZE = 12
TICK_LABEL_FONTSIZE = 10
TITLE_FONTSIZE = 14

# Colors
CURVE_COLOR = '#0077CC'          # Blue curve
TREND_COLOR = '#E65C00'          # Orange dashed trend line (显眼的区别)
ASSIST_LINE_COLOR = '#999999'     # Gray assistant lines
BACKGROUND_COLOR = 'white'


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


def plot_device(device_name, output_dir):
    csv_path = os.path.join(DATA_DIR, device_name, "metadata_pv.csv")
    if not os.path.exists(csv_path):
        print(f"[SKIP] {csv_path} not found")
        return

    df = pd.read_csv(csv_path)
    if df.empty:
        print(f"[SKIP] Empty: {csv_path}")
        return

    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
    fig.set_dpi(DPI)

    xlabel = df["X-label"].iloc[0] if "X-label" in df.columns else "Time (h)"
    ylabel = df["Y-label"].iloc[0] if "Y-label" in df.columns else "Normalized PCE"
    legend_text = df["Legend"].iloc[0] if "Legend" in df.columns else "PCE"

    for _, row in df.iterrows():
        x_vals = parse_csv_values(row["Value_x"])
        y_vals = parse_csv_values(row["Value_y"])
        if len(x_vals) == 0 or len(y_vals) == 0:
            continue
        min_len = min(len(x_vals), len(y_vals))
        x_vals = x_vals[:min_len]
        y_vals = y_vals[:min_len]

        sort_idx = np.argsort(x_vals)
        x_vals = x_vals[sort_idx]
        y_vals = y_vals[sort_idx]

        # Axis ranges
        x_min, x_max = x_vals.min(), x_vals.max()
        y_min_d, y_max_d = y_vals.min(), y_vals.max()
        x_range = x_max - x_min if x_max > x_min else 1
        y_range = y_max_d - y_min_d if y_max_d > y_min_d else 0.1

        # Tight margins (curve close to axes)
        x_margin_left = x_range * 0.01
        x_margin_right = x_range * 0.02
        y_margin_bottom = max(y_range * 0.02, 0.01)
        y_margin_top = max(y_range * 0.05, 0.02)
        ax.set_xlim(max(0, x_min - x_margin_left), x_max + x_margin_right)
        ax.set_ylim(max(0, y_min_d - y_margin_bottom), min(1.2, y_max_d + y_margin_top))

        # X ticks based on data range
        x_range_plot = ax.get_xlim()[1] - ax.get_xlim()[0]
        if x_range_plot > 500:
            x_ticks_step = 100
        elif x_range_plot > 200:
            x_ticks_step = 50
        elif x_range_plot > 100:
            x_ticks_step = 20
        elif x_range_plot > 50:
            x_ticks_step = 10
        else:
            x_ticks_step = 5
        x_ticks = np.arange(0, ax.get_xlim()[1] + 1, x_ticks_step)
        x_ticks = x_ticks[x_ticks > 0]
        ax.set_xticks(x_ticks)

        # Y ticks
        ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])

        # ---- Gray vertical assistant lines at each X tick position ----
        for xt in x_ticks:
            ax.axvline(x=xt, color=ASSIST_LINE_COLOR, linestyle='--',
                       linewidth=0.8, alpha=0.6, zorder=1)

        # ---- Gray horizontal assistant lines at y = 0, 0.2, 0.4, 0.6, 0.8, 1.0 ----
        for yt in [0, 0.2, 0.4, 0.6, 0.8, 1.0]:
            ax.axhline(y=yt, color=ASSIST_LINE_COLOR, linestyle='--',
                       linewidth=0.8, alpha=0.6, zorder=1)

        # ---- Linear fit trend line (dashed, overlapping the curve) ----
        # Use numpy polyfit: y = slope * x + intercept
        slope, intercept = np.polyfit(x_vals, y_vals, 1)
        x_trend = np.array([x_min, x_max])
        y_trend = slope * x_trend + intercept
        ax.plot(x_trend, y_trend, color=TREND_COLOR, linewidth=1.5,
                linestyle='--', alpha=0.75, zorder=2)

        # ---- Plot data curve with markers ----
        markevery = max(1, len(x_vals) // 40)
        ax.plot(x_vals, y_vals, color=CURVE_COLOR, linewidth=LINE_WIDTH,
                linestyle='-', marker='o', markersize=MARKER_SIZE,
                markerfacecolor=CURVE_COLOR,
                markeredgecolor='white',
                markeredgewidth=0.8,
                markevery=markevery, alpha=0.90, zorder=3, label=legend_text)

        break  # one curve per device

    # ---- Labels ----
    ax.set_xlabel(xlabel, fontsize=LABEL_FONTSIZE, fontweight='bold')
    ax.set_ylabel(ylabel, fontsize=LABEL_FONTSIZE, fontweight='bold')
    ax.set_title(device_name, fontsize=TITLE_FONTSIZE, fontweight='bold', pad=10)

    # ---- Spine settings ----
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_linewidth(1.5)
    ax.spines['left'].set_linewidth(1.5)

    # ---- Tick settings ----
    ax.tick_params(axis='both', which='major', direction='in',
                   top=False, right=False, labelsize=TICK_LABEL_FONTSIZE)

    # ---- Background ----
    ax.set_facecolor(BACKGROUND_COLOR)

    # ---- Legend ----
    leg = ax.legend(loc='upper right', fontsize=10, frameon=True,
                    fancybox=False, edgecolor='gray')
    leg.get_frame().set_alpha(0.9)
    leg.get_frame().set_facecolor('white')

    plt.tight_layout()

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{device_name}.png")
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight', pad_inches=0.05,
                facecolor='white', edgecolor='none')
    plt.close()
    print(f"[OK] Saved: {output_path}")


def main():
    print("=" * 60)
    print("Perovskite Stability Plot")
    print("Using REAL data | Orange curve | Red dashed trend line")
    print("Gray vertical/horizontal assistant lines | Linear fit overlap")
    print("=" * 60)

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

    for i, device_name in enumerate(device_folders):
        print(f"[{i+1}/{len(device_folders)}] {device_name}")
        plot_device(device_name, OUTPUT_DIR)

    print(f"\n{'=' * 60}")
    print(f"Done! {len(device_folders)} images in {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
