from __future__ import annotations

from pathlib import Path
import json
from typing import Any

import numpy as np
import pandas as pd

def _format_number(value: Any, col: str = "") -> str:
    if value is None:
        return ""
    if isinstance(value, (bool, np.bool_)):
        return "True" if bool(value) else "False"
    if isinstance(value, (int, np.integer)) and not isinstance(value, bool):
        return str(int(value))
    if isinstance(value, (float, np.floating)):
        if np.isnan(value):
            return "NaN"
        if "p" in col.lower():
            if value < 0.001:
                return "< .001"
            s = f"{value:.3f}"
            return s[1:] if s.startswith("0") else s
        if abs(value) < 0.001 and value != 0:
            return f"{value:.3g}"
        return f"{value:.3f}"
    return str(value)

def render_apa_table(df: pd.DataFrame, title: str, table_number: int | str | None = None) -> str:
    view = df.copy()
    for col in view.columns:
        view[col] = view[col].map(lambda x, c=col: _format_number(x, c))

    headers = [str(c) for c in view.columns]
    rows = view.astype(str).values.tolist()

    widths = []
    for idx, header in enumerate(headers):
        col_width = len(header)
        for row in rows:
            col_width = max(col_width, len(row[idx]))
        widths.append(col_width)

    def row_line(items):
        return "  ".join(item.ljust(widths[i]) for i, item in enumerate(items))

    lines = []
    if table_number is not None:
        lines.append(f"Table {table_number}")
    if title:
        lines.append(title)
    total_width = sum(widths) + 2 * (len(widths) - 1)
    lines.append("=" * max(20, total_width))
    lines.append(row_line(headers))
    lines.append("-" * max(20, total_width))
    for row in rows:
        lines.append(row_line(row))
    lines.append("=" * max(20, total_width))
    return "\n".join(lines)

def print_apa_table(df: pd.DataFrame, table_number: int | str | None, title: str) -> None:
    print()
    print(render_apa_table(df, title=title, table_number=table_number))

def save_table(df: pd.DataFrame, out_dir: Path, stem: str, title: str | None = None, table_number: int | str | None = None) -> dict[str, str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / f"{stem}.csv"
    txt_path = out_dir / f"{stem}.txt"
    df.to_csv(csv_path, index=False)
    txt_path.write_text(render_apa_table(df, title=title or stem, table_number=table_number), encoding="utf-8")
    return {"csv": str(csv_path), "txt": str(txt_path)}

def save_json(obj: Any, out_dir: Path, stem: str) -> str:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{stem}.json"
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, default=str)
    return str(path)
