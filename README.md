# Perovskite MPPT Curve Visualization Dataset

[English](README.md) | [简体中文](README_CN.md)

This dataset supports **visual learning for complex scientific curve figures**. It uses experimental perovskite solar-cell maximum power point tracking (MPPT) measurements to generate plots that reproduce four common difficulties in reading curves from research papers: auxiliary lines, overlap between the target curve and auxiliary lines, distracting background colors, and overlap among multiple curves. **Perovskite degradation/stability curves are the target application**; the broader figure-reading problems also occur across scientific literature. The long-term goal is to support training a dedicated multimodal large language model (vision-language model) to recognize and interpret these curves.

The repository contains processed MPPT data, plotting scripts, and generated images. The figures are rendered from the included measurements; they are not screenshots extracted from published papers.

<p align="center">
  <img src="figure/multi/A705P12_P101P04.png" alt="Example comparison of two perovskite stability datasets" width="820">
</p>

## Research Objective

The central task is to identify the **target degradation curve** despite visual elements that can obscure its path or make it easy to confuse with another line. The dataset focuses on four recurring challenges in scientific figures:

1. **Auxiliary lines are present:** grids, reference lines, or fitted trends appear near the target curve.
2. **The target and auxiliary lines overlap:** their crossings or shared segments make line identity ambiguous.
3. **The background varies in color:** gradients or colored regions reduce the reliability of simple color-based recognition.
4. **Multiple curves share one figure:** two or three series may cross or partially overlap, requiring the model to keep each curve distinct.

These challenges are represented through controlled renderings of perovskite MPPT time series. The intended learning path is to distinguish the target curve from non-target elements, follow it through difficult regions, and interpret degradation behavior. Model training and evaluation remain future work.

## Data-to-Figure Workflow

```text
Experimental perovskite MPPT data
                │
                ▼
  Elapsed-time calculation and Pmax normalization
                │
                ▼
         Processed curve CSV files
                │
                ├── assistline
                ├── assistline_overlap
                ├── colour
                └── multi
                         │
                         ▼
              Visual-learning image dataset
```

The current release includes:

- 30 processed perovskite device datasets.
- 73,242 normalized time-series points.
- 90 single-device figures across three categories.
- 12 multi-device figures in the fourth category.
- 102 high-resolution PNG figures in total.
- Scripts for preprocessing measurements and regenerating the visualizations.

## Four Figure Categories and Recognition Challenges

| Category | Figures | Recognition challenge | Rendering |
| --- | ---: | --- | --- |
| `figure/assistline/` | 30 | Identify the target curve when auxiliary elements are present | Single-device curve with markers, a reference grid, and a linear-fit line |
| `figure/assistline_overlap/` | 30 | Trace the target curve where it overlaps or crosses auxiliary lines | Single-device curve with dashed references and an overlapping fitted trend |
| `figure/colour/` | 30 | Recognize the curve despite a non-uniform colored background | Single-device curve with mixed markers and a brown-to-white gradient |
| `figure/multi/` | 12 | Keep multiple curves distinct through crossings and partial overlap | Two or three device curves shown in one plot |

The first three categories render individual experimental series. The `multi` category combines selected devices. The four categories isolate common visual ambiguities while retaining the underlying MPPT behavior.

## Repository Structure

```text
.
├── code/
│   ├── preprocess.py           # Converts raw perovskite MPPT exports to plotting metadata
│   ├── assistline.py           # Single-device plot with a linear fit
│   ├── assistline_overlap.py   # Single-device plot with grid and trend overlay
│   ├── colour.py               # Single-device tan/gradient style
│   ├── multi-2.py              # Two-device comparison plots
│   └── multi-3.py              # Two- and three-device comparison plots
├── data_csv/                   # 30 processed, flat CSV datasets
├── figure/
│   ├── assistline/             # Single-device figures with a fitted trend
│   ├── assistline_overlap/     # Single-device figures with grid/trend overlays
│   ├── colour/                 # Single-device color-style figures
│   └── multi/                  # Multi-device comparison figures
├── README.md                  # English
└── README_CN.md               # 简体中文
```

## Data Format

Each processed CSV contains the following columns:

| Column | Description |
| --- | --- |
| `ID` | Device or measurement identifier |
| `Figure` | Figure index |
| `Sub-figure` | Subfigure label |
| `Value_x` | Newline-separated elapsed-time values in hours |
| `Value_y` | Newline-separated normalized `Pmax` values used as the plotted stability signal |
| `Legend` | Device-structure or dataset label |
| `X-label` | Label for the x-axis |
| `Y-label` | Label for the y-axis |
| `Title` | Optional figure title |

The included collection contains 73,242 time-series points across 30 device files. Measurement durations range from approximately 233 to 624 hours. A device identifier in `data_csv/` can be matched to figures with the same identifier under the single-device figure directories.

## Intended Use and Current Scope

- Develop visual-learning tasks that locate and follow the target curve in complex scientific figures.
- Study recognition under auxiliary lines, line overlap, background color variation, and multi-curve overlap.
- Support future training and evaluation of a perovskite degradation-curve-focused multimodal LLM / vision-language model.
- Compare degradation patterns among single-device and multi-device MPPT plots.

This repository provides generated figures, processed measurements, and plotting scripts. It does **not** yet include a trained model, task-specific annotations, or an official training/validation/test split. Additional labels or instruction data may be needed for supervised model training. When creating splits, group images by device ID so that different renderings of the same experimental curve do not leak across training and evaluation sets.

## Requirements

- Python 3.9 or later
- NumPy
- pandas
- Matplotlib

Install the dependencies in a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install numpy pandas matplotlib
```

On Windows, activate the environment with `.venv\Scripts\activate`.

## Configuration

The scripts currently contain a `BASE_DIR` constant inherited from the original local workflow. Before running a script, change this value to the absolute path of your cloned repository:

```python
BASE_DIR = "/absolute/path/to/perovskite-mppt-curve-visualization-dataset"
```

The two comparison scripts read the included flat files from `data_csv/` and write new images to `multi_csv/`.

The single-device scripts use the following nested input layout:

```text
data/
└── <device-name>/
    └── metadata_pv.csv
```

That nested source tree and the original instrument exports are not included in this repository. The corresponding pre-generated figures are available under `figure/`.

## Visualization Workflow

### Generate two-device comparisons

Edit the `PAIRS` list and, if necessary, `X_MAX_MAP` in `code/multi-2.py`, then run:

```bash
python code/multi-2.py
```

Each tuple in `PAIRS` must use a filename from `data_csv/` without the `.csv` extension.

### Generate two- and three-device comparisons

Edit the `PAIRS` list in `code/multi-3.py`, then run:

```bash
python code/multi-3.py
```

This script supports both two-item and three-item tuples and uses red, blue, and green curves.

### Run the archived preprocessing workflow

`code/preprocess.py` expects two upstream inputs that are not included here:

- `原始数据/`: raw MPPT exports, either standard timestamp-column CSVs or supported instrument-specific CSVs.
- `器件结构.csv`: a mapping from device IDs to legend labels.

The script calculates elapsed time, applies min–max normalization to `Pmax`, and writes plotting metadata. Review its input/output paths before using it with new data.

### Generate single-device figures

After preparing the nested `data/<device>/metadata_pv.csv` layout, update the relevant paths and run one of:

```bash
python code/assistline.py
python code/assistline_overlap.py
python code/colour.py
```

## Examples of the Four Figure Categories

| `assistline` | `assistline_overlap` |
| --- | --- |
| <img src="figure/assistline/A705P12_MPPT001_Control_PCE.png" alt="Single-device curve with an auxiliary fit line" width="440"> | <img src="figure/assistline_overlap/A705P12_MPPT001.png" alt="Single-device curve with overlapping fit and reference lines" width="440"> |
| `colour` | `multi` |
| <img src="figure/colour/A705P12_MPPT001.png" alt="Gradient-style single-device curve" width="440"> | <img src="figure/multi/A705P12_P101P04.png" alt="Multi-device comparison curve" width="440"> |

## Reproducibility and Dataset Notes

- All plotting scripts use Matplotlib's `Agg` backend and can run without a graphical display.
- Arial is requested for several styles; Matplotlib falls back to an available sans-serif font when Arial is unavailable.
- The plotting scripts sort samples by elapsed time and pair `Value_x` and `Value_y` entries up to their shared length.
- The preprocessor uses min–max normalization: `(Pmax - min(Pmax)) / (max(Pmax) - min(Pmax))`.
- Generated images are high resolution and may require additional memory when processing many devices.
- Multiple figure styles may originate from the same underlying experimental curve. Treat them as related samples when designing machine-learning splits.
- The generated figures are intended for visual-learning and scientific-visualization research; they are not device-lifetime certification results or figures extracted from papers.

## License and Data Use

No license is currently included. Before redistributing the code or experimental data, add an appropriate software license and confirm that the datasets may be shared publicly.
