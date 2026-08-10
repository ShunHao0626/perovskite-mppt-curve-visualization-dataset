#!/usr/bin/env python3
"""预处理脚本：将原始CSV数据整理并分发到各器件文件夹"""

import os
import pandas as pd
from datetime import datetime

BASE = "/Users/shunhao/Desktop/1.曲线图-改图片形式"
RAW = os.path.join(BASE, "原始数据")
STRUCT_CSV = os.path.join(BASE, "器件结构.csv")

# ── 1. 读取器件结构映射表 ──────────────────────────────────────
struct_df = pd.read_csv(STRUCT_CSV)
struct_map = dict(zip(struct_df["ID"].str.strip(), struct_df["器件结构"].str.strip()))

id_to_folder = {
    "A613P02": "A613P02_MPPT001",
    "A613P05": "A613P05_MPPT001",
    "A613P06": "A613P06_MPPT001",
    "A615P15": "A615P15_MPPT001",
    "A615P19": "A615P19_MPPT001",
    "A705P12": "A705P12_MPPT001",
    "A705P13": "A705P13_MPPT001",
    "A706P02": "A706P02_MPPT001",
    "AY04P29": "AY04P29-Test001一MPPT一Channel4",
    "AZ30P22": "AZ30P22_MPPT001",
    "BZ15P02": "BZ15P02-Test001一MPPT一Channel14",
    "GRHQ6303P0008": "GRHQ6303P0008_MPPT001",
    "GRHQ6303P0009": "GRHQ6303P0009_MPPT001",
    "GRHQ6303P0010": "GRHQ6303P0010_MPPT001",
    "GRHQ6304P0003": "GRHQ6304P0003_MPPT001",
    "GRPI6309P0008": "GRPI6309P0008-Test001一MPPT一Channel2",
    "GRPI6309P0009": "GRPI6309P0009-Test001一MPPT一Channel3",
    "GRPI6311P0027": "GRPI6311P0027-Test001一MPPT一Channel4",
    "K211P18": "K211P18_MPPT001",
    "K211P20": "K211P20-Test001一MPPT一Channel8",
    "K403P09": "K403P09一MPPT一Channel1",
    "KY29P01": "KY29P01-Test001一MPPT一Channel1",
    "L925P01": "L925P01_MPPT001",
    "P101P04": "P101P04_MPPT001",
    "P101P16": "P101P16_MPPT001",
    "P210P03": "P210P03_MPPT001",
    "PY29P06": "PY29P06-Test001一MPPT一Channel13",
    "R403P15": "R403P15-Test001一MPPT一Channel4",
    "S210P02": "S210P02_MPPT001",
    "T926P07": "T926P07_MPPT001",
}


def parse_special_csv(path):
    """解析特殊格式 CSV（中文元数据头，第13行为列头，第14行起为数据）"""
    for enc in ["gbk", "gb18030"]:
        try:
            df = pd.read_csv(path, encoding=enc, skiprows=13)
            break
        except Exception:
            continue
    else:
        return None
    df.columns = df.columns.str.strip()
    df["Pmax"] = pd.to_numeric(df["Pmax"], errors="coerce")
    df["datetime"] = pd.to_datetime(df["RecordTime"], format="%Y/%m/%d %H:%M", errors="coerce")
    if df["datetime"].isna().all():
        df["datetime"] = pd.to_datetime(df["RecordTime"], errors="coerce")
    df = df.dropna(subset=["datetime", "Pmax"])
    return df


def parse_standard_csv(path):
    """解析标准 CSV（Year/Month/Day/Hour/Minute 列）"""
    for enc in ["utf-8", "latin-1"]:
        try:
            df = pd.read_csv(path, encoding=enc, on_bad_lines="skip")
            break
        except UnicodeDecodeError:
            continue
    else:
        return None
    if "Year" not in df.columns:
        return None
    df.columns = df.columns.str.strip()
    # 只保留 Year 列全为数字的行
    df = df[pd.to_numeric(df["Year"], errors="coerce").notna()].copy()
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    df["Month"] = pd.to_numeric(df["Month"], errors="coerce")
    df["Day"] = pd.to_numeric(df["Day"], errors="coerce")
    df["Hour"] = pd.to_numeric(df["Hour"], errors="coerce")
    df["Minute"] = pd.to_numeric(df["Minute"], errors="coerce")
    df["Pmax"] = pd.to_numeric(df["Pmax"], errors="coerce")
    df = df.dropna(subset=["Year", "Month", "Day", "Hour", "Minute", "Pmax"])
    df["datetime"] = pd.to_datetime(
        df[["Year", "Month", "Day", "Hour", "Minute"]], errors="coerce"
    )
    return df


# ── 2. 遍历原始数据，分发到各文件夹 ───────────────────────────
skipped = []
for item in sorted(os.listdir(RAW)):
    src = os.path.join(RAW, item)
    if item.startswith("."):
        continue

    if item.endswith(".csv"):
        csv_path = src
        base_id = item.replace(".csv", "")
    elif os.path.isdir(src):
        csv_path = os.path.join(src, "Data.csv")
        base_id = item
    else:
        continue

    if not os.path.exists(csv_path):
        skipped.append(f"{item} [无数据文件]")
        continue

    # 判断格式：特殊格式有中文元数据头，标准格式首行为 Year,...
    first_line = open(csv_path, "rb").read(20).decode("utf-8", errors="replace").strip()
    if first_line.startswith("样品名称") or first_line.startswith("Year"):
        df = parse_special_csv(csv_path) if "样品名称" in first_line else parse_standard_csv(csv_path)
    else:
        # 尝试检测
        raw = open(csv_path, "rb").read(5)
        try:
            raw.decode("utf-8")
            test_df = pd.read_csv(csv_path, encoding="utf-8", nrows=1)
            if "Year" in test_df.columns:
                df = parse_standard_csv(csv_path)
            else:
                df = parse_special_csv(csv_path)
        except UnicodeDecodeError:
            df = parse_special_csv(csv_path)

    if df is None or df.empty:
        skipped.append(f"{item} [解析失败]")
        continue

    if "datetime" not in df.columns or df["datetime"].isna().all():
        skipped.append(f"{item} [时间列解析失败]")
        continue

    # ── 3. 时间 → 相对小时，保留3位小数 ────────────────────
    t0 = df["datetime"].iloc[0]
    df["t"] = ((df["datetime"] - t0).dt.total_seconds() / 3600).round(3)

    # ── 4. Pmax 归一化到 [0, 1] ────────────────────────────
    pcol = "Pmax" if "Pmax" in df.columns else None
    if pcol is None:
        skipped.append(f"{item} [无Pmax列]")
        continue

    pmin, pmax_val = df[pcol].min(), df[pcol].max()
    if pmax_val - pmin == 0:
        df["Pmax_norm"] = 1.0
    else:
        df["Pmax_norm"] = ((df[pcol] - pmin) / (pmax_val - pmin)).round(6)

    # ── 5. 器件结构 → Legend ───────────────────────────────
    short_id = base_id.split("_")[0].split("-")[0]
    if short_id in struct_map:
        legend_label = struct_map[short_id]
    else:
        legend_label = short_id

    # 构造绘图 DataFrame（强制 Title 为空字符串避免 nan）
    rec = {
        "ID":         base_id,
        "Figure":     1,
        "Sub-figure": "a",
        "Value_x":    "\n".join([f"{x:.3f}" for x in df["t"]]),
        "Value_y":    "\n".join([f"{y:.6f}" for y in df["Pmax_norm"]]),
        "Legend":     legend_label,
        "X-label":    "Time (h)",
        "Y-label":    "Normalized PCE",
        "Title":      "",
    }
    plot_df = pd.DataFrame([rec])

    # ── 7. 写入对应文件夹 ─────────────────────────────────
    folder_name = id_to_folder.get(base_id, base_id)
    out_dir = os.path.join(BASE, folder_name)
    out_csv = os.path.join(out_dir, "metadata_pv.csv")

    # 确保文件夹存在
    os.makedirs(out_dir, exist_ok=True)
    plot_df.to_csv(out_csv, index=False)
    print(f"[OK] {folder_name} ({len(df)} rows) → {out_csv}")

# ── 8. 报告 ──────────────────────────────────────────────────
if skipped:
    print(f"\n跳过 {len(skipped)} 项：")
    for s in skipped:
        print(f"  - {s}")
else:
    print("\n全部 30 个器件处理完成。")
