#!/usr/bin/env python3
"""
Advanced Materials journal-style plot for photovoltaic stability data.

Uses REAL data from data/{device}/metadata_pv.csv.
Features:
- Clean, publication-ready, flat minimal design
- White background, monochrome black-gray palette
- 4K resolution (3840×2160), 16:9 landscape
- Arial bold labels and title
- Light gray grid behind data
- Thin black border around entire plot
- Blue (#0077CC) data curve with scatter points
- Gray dashed linear fit trend line
- No legends, no extra decorations
"""

import os
os.environ.setdefault("MPLCONFIGDIR", os.path.join(os.path.dirname(__file__), ".mplconfig"))

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import warnings

warnings.filterwarnings("ignore")

BASE_DIR = "/Users/shunhao/Desktop/1.曲线图-改图片形式"
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "pub_style")


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

    x_min, x_max = 0.0, all_x.max()
    y_min, y_max = 0.0, all_y.max()

    x_range = x_max if x_max > 0 else 1
    y_range = y_max if y_max > 0 else 0.1

    ax.set_xlim(0, x_max + x_range * 0.02)
    ax.set_ylim(0, y_max + y_range * 0.08)

    # X axis tick every 100
    x_tick_max = x_max + x_range * 0.02
    ax.set_xticks(np.arange(0, x_tick_max + 1, 100))
    ax.set_yticks(np.arange(0, y_max + y_range * 0.08 + 0.01, 0.2))

    ax.set_xlabel(xlabel, fontsize=18, fontweight="bold",
                  fontname=font_name, color="black")
    ax.set_ylabel(ylabel, fontsize=18, fontweight="bold",
                  fontname=font_name, color="black")

    ax.set_title(device_name, fontsize=20, fontweight="bold",
                 fontname=font_name, color="black",
                 pad=18, loc="center")

    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(1.0)
        spine.set_edgecolor("black")

    ax.spines["left"].set_position(("outward", 0))
    ax.spines["bottom"].set_position(("outward", 0))
    ax.spines["right"].set_position(("outward", 0))
    ax.spines["top"].set_position(("outward", 0))

    ax.tick_params(axis="both", direction="in", length=5, width=0.8,
                   top=True, right=True, labelsize=14,
                   labelcolor="black", color="black")

    ax.grid(True, color="#D0D0D0", linestyle="-", linewidth=0.5, zorder=0)
    ax.set_axisbelow(True)

    slope, intercept = np.polyfit(all_x, all_y, 1)
    x_fit = np.array([x_min, x_max])
    y_fit = np.clip(slope * x_fit + intercept, 0, 1.5)
    ax.plot(x_fit, y_fit,
            color="#808080",
            linewidth=1.8,
            linestyle="--",
            dashes=[8, 4],
            zorder=2,
            solid_capstyle="round")

    ax.plot(all_x, all_y,
            color="#0077CC",
            linewidth=2.2,
            linestyle="-",
            zorder=3,
            solid_capstyle="round")

    scatter_step = max(1, len(all_x) // 40)
    scatter_idx = list(range(0, len(all_x), scatter_step))
    if scatter_idx and scatter_idx[-1] != len(all_x) - 1:
        scatter_idx.append(len(all_x) - 1)
    ax.scatter(all_x[scatter_idx], all_y[scatter_idx],
               color="#0077CC",
               s=35,
               zorder=4,
               marker="o",
               linewidths=0)

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{device_name}.png")
    fig.savefig(output_path, dpi=dpi, bbox_inches="tight",
                pad_inches=0.1, facecolor="white", edgecolor="none")
    plt.close()
    print(f"[OK] {device_name} → {output_path}")
    return True


def main():
    print("=" * 60)
    print("Advanced Materials Journal Style Plot Generator")
    print("Using REAL data | Monochrome | No legends")
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

    success = 0
    for i, device_name in enumerate(device_folders):
        print(f"[{i+1}/{len(device_folders)}] {device_name}", end=" ... ")
        if plot_device(device_name, OUTPUT_DIR):
            success += 1

    print(f"\n{'=' * 60}")
    print(f"Done! {success}/{len(device_folders)} images saved to {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
