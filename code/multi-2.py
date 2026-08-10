#!/usr/bin/env python3
"""
Multi-device photovoltaic stability comparison plot generator.

Style: Advanced Materials journal standard
- Clean, publication-ready, flat minimal design
- White background, high resolution 4K 16:9 landscape
- Red/blue/black color palette
- No title, no grid lines
- No brown gradient background
- Hollow-circle scatter markers (white fill, colored border)
- Legend box at top-right with light gray border
- Bold Arial labels, tick direction in

All data from data_csv/{device}.csv (flat CSV files).
Output naming: {device1_short}_{device2_short}.png
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
DATA_DIR = os.path.join(BASE_DIR, "data_csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "multi_csv")

# Color palette: red-blue-black
COLORS = ['#d62728', '#1f77b4']


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


def short_name(device_full):
    """Extract short device name from full folder name."""
    # Remove common suffixes: _MPPT001, -Test001一MPPT一ChannelN
    name = device_full
    for suffix in [
        "_MPPT001", "_MPPT002", "_MPPT003",
        "-Test001一MPPT一Channel1", "-Test001一MPPT一Channel2",
        "-Test001一MPPT一Channel3", "-Test001一MPPT一Channel4",
        "-Test001一MPPT一Channel8", "-Test001一MPPT一Channel13",
        "-Test001一MPPT一Channel14",
    ]:
        if name.endswith(suffix):
            name = name[:-len(suffix)]
            break
    return name


def load_device_data(device_name):
    """Load first group of data for a device from flat CSV."""
    csv_path = os.path.join(DATA_DIR, f"{device_name}.csv")
    if not os.path.exists(csv_path):
        return None, None, None

    df = pd.read_csv(csv_path)
    if df.empty:
        return None, None, None

    first_idx = df[["ID", "Figure", "Sub-figure"]].drop_duplicates().iloc[0]
    group = df[(df["ID"] == first_idx["ID"]) &
               (df["Figure"] == first_idx["Figure"]) &
               (df["Sub-figure"] == first_idx["Sub-figure"])]

    legend_label = None
    if "Legend" in group.columns:
        val = group["Legend"].iloc[0]
        if val and str(val).strip():
            legend_label = str(val).strip()

    all_x, all_y = [], []
    for _, row in group.iterrows():
        x_vals = parse_csv_values(row["Value_x"])
        y_vals = parse_csv_values(row["Value_y"])
        if len(x_vals) == 0 or len(y_vals) == 0:
            continue
        min_len = min(len(x_vals), len(y_vals))
        all_x.extend(x_vals[:min_len])
        all_y.extend(y_vals[:min_len])

    if not all_x:
        return None, None, None

    all_x = np.array(all_x)
    all_y = np.array(all_y)
    sort_idx = np.argsort(all_x)
    all_x = all_x[sort_idx]
    all_y = all_y[sort_idx]
    return all_x, all_y, legend_label


def _smart_x_ticks(x_max):
    """Return dynamic X tick positions based on data range."""
    candidates = [100, 200, 300, 400, 500, 600, 700, 800, 1000]
    nice_max = next((c for c in candidates if c >= x_max), candidates[-1])
    step = 100
    ticks = list(range(0, nice_max + 1, step))
    return ticks, nice_max


def _smart_y_ticks(y_max):
    """Return dynamic Y tick positions based on data range."""
    if y_max <= 0.5:
        return sorted(set([0.0, 0.2, 0.4, 0.6, 0.8, 1.0]))
    elif y_max <= 1.0:
        return [0.2, 0.4, 0.6, 0.8, 1.0]
    else:
        n_ticks = 6
        step = y_max / (n_ticks - 1)
        return [round(i * step, 2) for i in range(1, n_ticks)]


def _compute_legend_bbox(ax, all_data):
    """Compute legend anchor position away from curve overlap."""
    xlim, ylim = ax.get_xlim(), ax.get_ylim()
    w_range = xlim[1] - xlim[0]
    h_range = ylim[1] - ylim[0]

    candidates = [
        (0.99, 0.99),
        (0.99, 0.90),
        (0.75, 0.99),
        (0.75, 0.90),
    ]

    for xa, ya in candidates:
        x_px = xlim[0] + xa * w_range
        y_px = ylim[0] + ya * h_range
        y_btm = y_px - h_range * 0.12
        y_top = y_px + h_range * 0.03
        occupied = False
        for _, x, y, _ in all_data:
            for xi, yi in zip(x, y):
                if x_px - w_range * 0.22 <= xi <= x_px + w_range * 0.22:
                    if y_btm <= yi <= y_top:
                        occupied = True
                        break
            if occupied:
                break
        if not occupied:
            return xa, ya

    return 0.75, 0.90


def plot_multi(combination, output_dir, x_axis_max=None):
    """
    Plot multiple devices on a single figure.

    Style: Advanced Materials journal standard
    - No title
    - X/Y: dynamic range based on data
    - Thick black spines (left+bottom only)
    - No grid
    - Red (#d62728) and Blue (#1f77b4) curves
    - ALL hollow-circle scatter (white fill, colored border)
    - Legend at top-right, light gray border
    - Red/blue/black palette
    """
    devices = combination
    n = len(devices)

    all_data = []
    for dev in devices:
        x, y, legend_label = load_device_data(dev)
        if x is None:
            print(f"  [SKIP] {dev} - no data found")
            return False
        all_data.append((dev, x, y, legend_label))

    if len(all_data) != n:
        print(f"  [SKIP] not all devices loaded")
        return False

    all_x = np.concatenate([d[1] for d in all_data])
    all_y = np.concatenate([d[2] for d in all_data])
    x_max_data = all_x.max()
    y_max_data = all_y.max()

    # Compute dynamic X axis
    xticks, x_fig_max = _smart_x_ticks(x_max_data)
    if x_axis_max is not None:
        x_fig_max = x_axis_max
        max_tick = int(x_fig_max)
        xticks = list(range(0, max_tick, 100))
        if max_tick % 100 != 0:
            xticks.append(max_tick)

    # Figure: 4K 16:9 landscape
    fig_w = 16.0
    fig_h = 9.0
    dpi = 240

    fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi)
    ax = fig.add_axes([0.10, 0.10, 0.85, 0.83])

    font_name = "Arial"
    try:
        arial_prop = fm.FontProperties(family=font_name)
        _ = fm.fontManager.findfont(arial_prop)
    except Exception:
        font_name = "DejaVu Sans"

    # Axis limits
    ax.set_xlim(0, x_fig_max)
    ax.set_ylim(0.0, y_max_data)

    # X ticks
    ax.set_xticks(xticks)

    ax.set_yticks(_smart_y_ticks(y_max_data))

    # Axis labels (bold Arial, large)
    ax.set_xlabel("Time (h)", fontsize=22, fontweight="bold",
                  fontname=font_name, color="black")
    ax.set_ylabel("Normalized PCE", fontsize=22, fontweight="bold",
                  fontname=font_name, color="black")

    # NO title
    ax.set_title("")

    # Spines: thick black, only left and bottom visible
    for spine_name in ['top', 'right']:
        ax.spines[spine_name].set_visible(False)
    ax.spines['bottom'].set_visible(True)
    ax.spines['left'].set_visible(True)
    ax.spines['bottom'].set_linewidth(2.0)
    ax.spines['left'].set_linewidth(2.0)
    ax.spines['bottom'].set_edgecolor('black')
    ax.spines['left'].set_edgecolor('black')
    ax.spines['bottom'].set_position(('outward', 0))
    ax.spines['left'].set_position(('outward', 0))

    # Tick style: direction in, large bold
    ax.tick_params(axis='both', direction='in', length=6, width=1.2,
                   top=False, right=False, labelsize=16,
                   labelcolor="black", color="black")

    # No grid at all
    ax.grid(False)

    # Build handles and labels for legend
    handles = []
    labels = []

    for i, (dev, x, y, legend_label) in enumerate(all_data):
        color = COLORS[i % len(COLORS)]

        # Thick continuous curve
        ax.plot(x, y,
                color=color,
                linewidth=2.5,
                linestyle='-',
                zorder=3,
                solid_capstyle='round',
                solid_joinstyle='round')

        # Hollow-circle scatter points (ALL hollow, white fill, colored border)
        n_total = len(x)
        n_samples = 45
        step = max(1, n_total // n_samples)
        sample_idx = list(range(0, n_total, step))
        if sample_idx and sample_idx[-1] != n_total - 1:
            sample_idx.append(n_total - 1)

        for idx in sample_idx:
            ax.scatter(x[idx], y[idx],
                       facecolors='white',
                       edgecolors=color,
                       s=55,
                       zorder=5,
                       marker='o',
                       linewidths=1.8)

        # Legend handle: line + hollow circle
        handle = plt.Line2D([0], [0],
                            color=color, linewidth=3.0,
                            marker='o', markersize=8,
                            markerfacecolor='white',
                            markeredgecolor=color,
                            markeredgewidth=1.8,
                            linestyle='-')
        handles.append(handle)

        # Label: use data legend or default
        lbl = legend_label if legend_label else f"Dataset {i+1}"
        labels.append(lbl)

    # Compute dynamic legend position (avoid curve overlap)
    xa, ya = _compute_legend_bbox(ax, all_data)

    # Legend box, light gray border
    leg = ax.legend(handles, labels,
                    loc='upper right',
                    bbox_to_anchor=(xa, ya),
                    frameon=True,
                    fancybox=False,
                    edgecolor='#AAAAAA',
                    framealpha=0.95,
                    borderpad=0.6,
                    labelspacing=0.4,
                    handlelength=2.5,
                    handletextpad=0.6)

    for text in leg.get_texts():
        text.set_fontsize(14)
        text.set_color('black')
        text.set_fontweight('bold')
        text.set_fontname(font_name)

    leg.get_frame().set_linewidth(1.0)

    # Save
    os.makedirs(output_dir, exist_ok=True)
    short_names = [short_name(d) for d in devices]
    filename = "_".join(short_names) + ".png"
    output_path = os.path.join(output_dir, filename)
    fig.savefig(output_path, dpi=dpi, bbox_inches='tight',
                pad_inches=0.15, facecolor='white', edgecolor='none')
    plt.close()
    print(f"[OK] {filename}")
    return True


def main():
    print("=" * 60)
    print("Multi-Device Stability Plot Generator")
    print("Advanced Materials Journal Style")
    print(f"Output: {OUTPUT_DIR}")
    print("=" * 60)

    PAIRS = [
        ('A705P12_MPPT001', 'P101P04_MPPT001'),
        ('A705P12_MPPT001', 'P101P16_MPPT001'),
        ('A705P12_MPPT001', 'P210P03_MPPT001'),
        ('A615P15_MPPT001', 'P101P16_MPPT001'),
        ('AY04P29-Test001一MPPT一Channel4', 'P210P03_MPPT001'),
        ('L925P01_MPPT001', 'P101P16_MPPT001'),
        ('A615P15_MPPT001', 'A613P06_MPPT001'),
        ('A706P02_MPPT001', 'K211P20-Test001一MPPT一Channel8'),
    ]
    # Per-pair X axis upper limit: None = auto (round up to nearest 100)
    X_MAX_MAP = {
        'A705P12_P101P04':   500,
        'A705P12_P101P16':   500,
        'A705P12_P210P03':   650,
        'A615P15_P101P16':   500,
        'AY04P29_P210P03':   650,
        'L925P01_P101P16':   400,
        'A615P15_A613P06':   500,
        'A706P02_K211P20':   500,
    }

    success = 0
    for combo in PAIRS:
        short_names = [short_name(d) for d in combo]
        key = '_'.join(short_names)
        x_max = X_MAX_MAP.get(key)
        if plot_multi(combo, OUTPUT_DIR, x_axis_max=x_max):
            success += 1

    print(f"\n{'=' * 60}")
    print(f"Done! {success}/{len(PAIRS)} images saved to {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
