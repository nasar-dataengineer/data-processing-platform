import os
from pathlib import Path

import pandas as pd

try:
    import dask.dataframe as dd
except ImportError:
    dd = None

try:
    import polars as pl
except ImportError:
    pl = None

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

from ..config import ALLOWED_EXTENSIONS

LARGE_FILE_THRESHOLD = 200 * 1024 * 1024
CHUNK_SIZE = 200_000


def get_extension(filepath: str) -> str:
    return Path(filepath).suffix.lower().lstrip(".")


def is_allowed_file(filename: str) -> bool:
    return get_extension(filename) in ALLOWED_EXTENSIONS


def safe_filename(filename: str) -> str:
    cleaned = Path(filename).name
    return cleaned.replace(" ", "_").replace("..", "")


def is_dask(df) -> bool:
    return dd is not None and hasattr(df, "__dask_scheduler__")


def is_polars(df) -> bool:
    return pl is not None and isinstance(df, pl.DataFrame)


def get_memory_usage(df):
    if is_dask(df):
        try:
            return int(df.map_partitions(lambda partition: partition.memory_usage(deep=True).sum()).compute())
        except Exception:
            return 0
    if is_polars(df):
        return int(df.estimated_size())
    return int(df.memory_usage(deep=True).sum())


def read_csv_in_chunks(filepath: str, chunk_size: int = CHUNK_SIZE):
    for chunk in pd.read_csv(filepath, chunksize=chunk_size, low_memory=False):
        yield chunk


def _read_pdf(filepath: str):
    if pdfplumber is None:
        raise ValueError("PDF support requires pdfplumber. Install backend requirements.")

    tables = []
    text_rows = []
    with pdfplumber.open(filepath) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            page_text = page.extract_text() or ""
            text_rows.extend(
                {"page": page_number, "line": line_number, "text": line.strip()}
                for line_number, line in enumerate(page_text.splitlines(), start=1)
                if line.strip()
            )

            for table in page.extract_tables() or []:
                rows = [
                    [cell.strip().replace("\n", " ") if cell else "" for cell in row]
                    for row in table
                    if row and any(cell and cell.strip() for cell in row)
                ]
                if len(rows) < 2:
                    continue

                width = max(len(row) for row in rows)
                header_row = rows[0] + [""] * (width - len(rows[0]))
                headers = []
                used_headers = set()
                for index, value in enumerate(header_row, start=1):
                    base_name = value or f"column_{index}"
                    name = base_name
                    suffix = 2
                    while name in used_headers:
                        name = f"{base_name}_{suffix}"
                        suffix += 1
                    used_headers.add(name)
                    headers.append(name)

                data_rows = []
                for row in rows[1:]:
                    values = row + [""] * (width - len(row))
                    if values == header_row:
                        continue
                    data_rows.append([value if value else pd.NA for value in values])
                if data_rows:
                    tables.append(pd.DataFrame(data_rows, columns=headers))

    if tables:
        return pd.concat(tables, ignore_index=True, sort=False).dropna(how="all")
    if text_rows:
        return pd.DataFrame(text_rows)
    raise ValueError(
        "No readable text or tables were found in this PDF. Scanned PDFs require OCR and are not supported."
    )


def load_file(filepath: str, sample_rows: int = 20):
    extension = get_extension(filepath)
    file_size = os.path.getsize(filepath)

    if extension in {"csv", "txt"}:
        if file_size > LARGE_FILE_THRESHOLD and dd is not None:
            df = dd.read_csv(filepath, assume_missing=True, blocksize="64MB")
        elif extension == "txt":
            df = pd.read_csv(filepath, sep=None, engine="python")
        else:
            df = pd.read_csv(filepath, low_memory=False)

    elif extension in {"xlsx", "xls"}:
        engine = "openpyxl" if extension == "xlsx" else "xlrd"
        df = pd.read_excel(filepath, engine=engine)

    elif extension == "json":
        with open(filepath, "r", encoding="utf-8") as handle:
            first_char = ""
            while True:
                char = handle.read(1)
                if not char:
                    break
                if not char.isspace():
                    first_char = char
                    break

        if file_size > LARGE_FILE_THRESHOLD and dd is not None:
            lines = first_char != "["
            df = dd.read_json(filepath, orient="records", lines=lines)
        else:
            lines = first_char != "["
            df = pd.read_json(filepath, orient="records", lines=lines)

    elif extension == "parquet":
        if pl is not None:
            df = pl.read_parquet(filepath)
        else:
            df = pd.read_parquet(filepath)

    elif extension == "pdf":
        df = _read_pdf(filepath)

    else:
        raise ValueError(f"Unsupported file type: {extension}")

    return df


def get_preview(df, rows: int = 20):
    if is_dask(df):
        preview_df = df.head(rows)
        return preview_df.fillna("", inplace=False).to_dict(orient="records")

    if is_polars(df):
        return df.head(rows).to_dicts()

    return df.head(rows).fillna("", inplace=False).to_dict(orient="records")


def get_row_count(df):
    if is_dask(df):
        return int(df.shape[0].compute())
    if is_polars(df):
        return df.height
    return len(df)


def get_column_names(df):
    if is_dask(df):
        return list(df.columns)
    if is_polars(df):
        return df.columns
    return list(df.columns)


def to_pandas(df):
    if is_dask(df):
        return df.compute()
    if is_polars(df):
        return df.to_pandas()
    return df


def to_polars(df):
    if is_polars(df):
        return df
    if is_dask(df):
        return pl.from_pandas(df.compute()) if pl is not None else df.compute()
    return pl.from_pandas(df) if pl is not None else df
