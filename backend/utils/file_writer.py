import os
from pathlib import Path

import pandas as pd

try:
    import polars as pl
except ImportError:
    pl = None

try:
    import dask.dataframe as dd
except ImportError:
    dd = None

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import landscape, letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import LongTable, Paragraph, SimpleDocTemplate, TableStyle
except ImportError:
    colors = None
    landscape = None
    letter = None
    getSampleStyleSheet = None
    LongTable = None
    Paragraph = None
    SimpleDocTemplate = None
    TableStyle = None

from xml.sax.saxutils import escape


def build_processed_filename(original_filename: str, suffix: str = "cleaned") -> str:
    name, ext = os.path.splitext(Path(original_filename).name)
    if not ext:
        ext = ".csv"
    return f"{suffix}_{name}{ext}"


def _save_pdf(df, output_path: str):
    if SimpleDocTemplate is None:
        raise RuntimeError("PDF export requires reportlab. Install backend requirements.")

    if dd is not None and hasattr(df, "compute") and hasattr(df, "to_parquet"):
        df = df.compute()
    elif pl is not None and isinstance(df, pl.DataFrame):
        df = df.to_pandas()
    if len(df.columns) == 0:
        df = pd.DataFrame({"message": ["No columns are available in this dataset."]})

    styles = getSampleStyleSheet()
    cell_style = styles["BodyText"]
    cell_style.fontName = "Helvetica"
    cell_style.fontSize = 7
    cell_style.leading = 8
    header_style = styles["BodyText"]
    header_style.fontName = "Helvetica-Bold"
    header_style.fontSize = 7
    header_style.leading = 8

    def cell(value, style):
        if pd.isna(value):
            value = ""
        return Paragraph(escape(str(value)), style)

    rows = [[cell(column, header_style) for column in df.columns]]
    rows.extend(
        [cell(value, cell_style) for value in row]
        for row in df.itertuples(index=False, name=None)
    )
    column_width = landscape(letter)[0] / max(len(df.columns), 1)
    table = LongTable(rows, colWidths=[column_width] * len(df.columns), repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dbeafe")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cbd5e1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))

    document = SimpleDocTemplate(output_path, pagesize=landscape(letter))
    document.build([table])
    return output_path


def save_dataframe(df, output_path: str):
    extension = Path(output_path).suffix.lower().lstrip(".")
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)

    if extension == "pdf":
        return _save_pdf(df, output_path)

    if dd is not None and hasattr(df, "to_parquet") and hasattr(df, "compute") and extension in {"csv", "parquet"}:
        if extension == "csv":
            df.to_csv(output_path, single_file=True, index=False)
            return output_path
        df.to_parquet(output_path, engine="pyarrow")
        return output_path

    if pl is not None and isinstance(df, pl.DataFrame):
        if extension == "csv":
            df.write_csv(output_path)
        elif extension in {"parquet", "parq"}:
            df.write_parquet(output_path)
        elif extension in {"json"}:
            df.write_json(output_path)
        elif extension in {"xlsx", "xls"}:
            df.write_excel(output_path)
        else:
            df.write_csv(output_path)
        return output_path

    if extension == "csv":
        df.to_csv(output_path, index=False)
    elif extension in {"xlsx", "xls"}:
        df.to_excel(output_path, index=False, engine="openpyxl")
    elif extension == "json":
        df.to_json(output_path, orient="records", lines=True)
    elif extension == "parquet":
        df.to_parquet(output_path, engine="pyarrow", index=False)
    else:
        df.to_csv(output_path, index=False)

    return output_path
