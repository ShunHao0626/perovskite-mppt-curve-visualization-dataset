# Perovskite Stability Curve Dataset

A paired numerical and visual dataset of perovskite solar-cell stability curves for visual learning research. The repository contains processed maximum power point tracking (MPPT) measurements, multiple image renderings of normalized power conversion efficiency (PCE) curves, multi-device comparison figures, and the Python scripts used to create them.

<p align="center">
  <img src="figure/multi/A705P12_P101P04.png" alt="Example comparison of two perovskite stability datasets" width="820">
</p>

## Project Purpose

This project was created to support visual learning from perovskite stability curves. It preserves the numerical measurements alongside different visual representations of the same degradation behavior, allowing researchers to explore tasks such as curve-pattern recognition, visual representation learning, figure understanding, and stability-trend comparison.

The current release includes:

- 30 processed perovskite device datasets.
- 73,242 normalized time-series points.
- 90 single-device figures in three visual styles.
- 12 multi-device comparison figures.
- 102 high-resolution PNG figures in total.
- Scripts for preprocessing measurements and regenerating the visualizations.

This repository is a dataset collection rather than a finalized machine-learning benchmark. It does not currently provide class annotations, predefined tasks, or official training, validation, and test splits.

## Dataset Design

- Each single-device CSV is paired with visualizations derived from the same MPPT stability curve.
- Multiple rendering styles introduce controlled visual variation, including different colors, markers, grids, backgrounds, and fitted trend lines.
- Multi-device figures combine two or three curves to represent comparative stability patterns.
- Elapsed time is represented in hours, and measured maximum power (`Pmax`) is normalized to the range 0–1.
- Device identifiers and legend values preserve the link between numerical records and generated figures.

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
└── README.md
```

## Data Format

Each processed CSV contains the following columns:

| Column | Description |
| --- | --- |
| `ID` | Device or measurement identifier |
| `Figure` | Figure index |
| `Sub-figure` | Subfigure label |
| `Value_x` | Newline-separated elapsed-time values in hours |
| `Value_y` | Newline-separated normalized PCE values |
| `Legend` | Device-structure or dataset label |
| `X-label` | Label for the x-axis |
| `Y-label` | Label for the y-axis |
| `Title` | Optional figure title |

The included collection contains 73,242 time-series points across 30 device files. Measurement durations range from approximately 233 to 624 hours. A device identifier in `data_csv/` can be matched to figures with the same identifier under the single-device figure directories.

## Potential Research Uses

- Visual representation learning from scientific curves.
- Recognition or retrieval of perovskite degradation patterns.
- Numerical-to-visual and visual-to-numerical alignment studies.
- Scientific figure understanding and curve interpretation.
- Comparison of visual styles and their effect on model behavior.
- Prototyping future stability classification or regression tasks after adding suitable labels.

Researchers should define task-specific labels and use device-level data splitting to prevent different renderings of the same device from leaking across training and evaluation sets.

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
BASE_DIR = "/absolute/path/to/photovoltaic-mppt-stability-plots"
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

## Example Outputs

| Gradient style | Trend and reference-grid style |
| --- | --- |
| <img src="figure/colour/A705P12_MPPT001.png" alt="Gradient-style single-device plot" width="440"> | <img src="figure/assistline_overlap/A705P12_MPPT001.png" alt="Single-device plot with trend and reference lines" width="440"> |

## Reproducibility and Dataset Notes

- All plotting scripts use Matplotlib's `Agg` backend and can run without a graphical display.
- Arial is requested for several styles; Matplotlib falls back to an available sans-serif font when Arial is unavailable.
- The plotting scripts sort samples by elapsed time and pair `Value_x` and `Value_y` entries up to their shared length.
- The preprocessor uses min–max normalization: `(Pmax - min(Pmax)) / (max(Pmax) - min(Pmax))`.
- Generated images are high resolution and may require additional memory when processing many devices.
- Multiple figures may originate from the same underlying device curve. Treat them as related samples when designing machine-learning splits.
- The dataset is intended for research and visualization experiments; model performance should not be interpreted as a clinical, industrial, or lifetime-certification result.

## License and Data Use

No license is currently included. Before redistributing the code or experimental data, add an appropriate software license and confirm that the datasets may be shared publicly.
