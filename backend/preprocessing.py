import os
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pandas as pd

from .config import PROCESSED_FOLDER
from .modules.duplicates import detect_duplicates, remove_duplicates
from .modules.encoding import binary_encode, label_encode, one_hot_encode, ordinal_encode
from .modules.feature_selection import correlation_filter, mutual_information as mutual_information_score, variance_threshold
from .modules.missing_values import detect_missing_values, fill_missing
from .modules.outliers import (
    detect_outliers_iqr,
    detect_outliers_isolation_forest,
    detect_outliers_zscore,
)
from .modules.scaling import scale_dataframe
from .utils.file_reader import (
    get_column_names,
    get_memory_usage,
    get_preview,
    get_row_count,
    safe_filename,
    to_pandas,
)
from .utils.file_writer import build_processed_filename, save_dataframe


def inspect_dataset(df, file_path: str = None) -> Dict:
    rows = get_row_count(df)
    columns = get_column_names(df)
    preview = get_preview(df, rows=min(rows, 20))
    missing_values = detect_missing_values(df)

    data_types = {}
    if hasattr(df, "dtypes"):
        dtypes = df.dtypes
        if hasattr(dtypes, "items"):
            data_types = {str(key): str(value) for key, value in dtypes.items()}
        else:
            data_types = dict(dtypes)

    numeric_columns = [col for col, dtype in data_types.items() if "int" in dtype or "float" in dtype]
    categorical_columns = [col for col, dtype in data_types.items() if dtype in {"object", "category", "string"}]
    date_columns = [col for col, dtype in data_types.items() if "datetime" in dtype.lower()]
    boolean_columns = [col for col, dtype in data_types.items() if "bool" in dtype.lower()]

    pandas_df = to_pandas(df)
    unique_values = {col: int(pandas_df[col].nunique(dropna=False)) for col in columns}
    null_percentage = {
        col: round(100.0 * (missing_values.get(col, 0) / rows), 2) if rows else 0.0
        for col in columns
    }

    metadata = {
        "rows": rows,
        "columns": len(columns),
        "column_names": columns,
        "data_types": data_types,
        "numeric_columns": numeric_columns,
        "categorical_columns": categorical_columns,
        "date_columns": date_columns,
        "boolean_columns": boolean_columns,
        "missing_values": missing_values,
        "null_percentage": null_percentage,
        "unique_values": unique_values,
        "duplicate_rows": detect_duplicates(df),
        "preview": preview,
        "memory_usage_bytes": get_memory_usage(df),
    }

    if file_path:
        metadata["file_path"] = file_path

    return metadata


def generate_recommendations(inspect_report: Dict) -> List[str]:
    recommendations = []
    if inspect_report.get("duplicate_rows", 0) > 0:
        recommendations.append("Remove duplicate rows")
    if sum(inspect_report.get("missing_values", {}).values()) > 0:
        recommendations.append("Fill missing values using median or mode")
    if inspect_report.get("numeric_columns"):
        recommendations.append("Normalize numeric features")
    if inspect_report.get("categorical_columns") and inspect_report.get("numeric_columns"):
        recommendations.append("Encode categorical features")
    return recommendations


def _normalize_options(options: Any) -> Dict[str, Any]:
    if hasattr(options, "dict"):
        normalized = options.dict()
    elif isinstance(options, dict):
        normalized = options.copy()
    else:
        normalized = dict(options)

    normalized["output_format"] = str(normalized.get("output_format", "csv")).lstrip(".")
    normalized["missing_strategy"] = normalized.get("missing_strategy", "median")
    normalized["constant_value"] = normalized.get("constant_value")
    normalized["remove_duplicates"] = bool(normalized.get("remove_duplicates", True))
    normalized["remove_empty_rows"] = bool(normalized.get("remove_empty_rows", False))
    normalized["remove_empty_columns"] = bool(normalized.get("remove_empty_columns", False))
    normalized["trim_spaces"] = bool(normalized.get("trim_spaces", True))
    normalized["remove_duplicate_columns"] = bool(normalized.get("remove_duplicate_columns", False))
    normalized["convert_to_numeric"] = bool(normalized.get("convert_to_numeric", False))
    normalized["convert_to_float"] = bool(normalized.get("convert_to_float", False))
    normalized["convert_to_integer"] = bool(normalized.get("convert_to_integer", False))
    normalized["convert_to_boolean"] = bool(normalized.get("convert_to_boolean", False))
    normalized["convert_to_datetime"] = bool(normalized.get("convert_to_datetime", False))
    normalized["encoding"] = normalized.get("encoding")
    normalized["scaling"] = normalized.get("scaling")
    normalized["outlier_method"] = normalized.get("outlier_method")
    normalized["variance_threshold"] = float(normalized.get("variance_threshold", 0.0) or 0.0)
    normalized["correlation_threshold"] = float(normalized.get("correlation_threshold", 0.95) or 0.95)
    normalized["mutual_information"] = bool(normalized.get("mutual_information", False))
    normalized["target_column"] = normalized.get("target_column")
    return normalized


def preprocess_dataset(df, filename: str, options: Any) -> Tuple[Any, str, Dict]:
    options = _normalize_options(options)
    df = to_pandas(df)

    original_rows = get_row_count(df)
    original_columns = len(get_column_names(df))
    report = {
        "original_rows": original_rows,
        "original_columns": original_columns,
        "output_format": options["output_format"],
        "missing_strategy": options["missing_strategy"],
    }

    report["duplicate_rows_before"] = detect_duplicates(df)
    if options["remove_duplicates"]:
        df = remove_duplicates(df)
    report["duplicates_removed"] = report["duplicate_rows_before"] - detect_duplicates(df)

    if options["trim_spaces"]:
        string_columns = df.select_dtypes(include=["object", "string", "category"]).columns.tolist()
        for column in string_columns:
            df[column] = df[column].map(
                lambda value: value.strip() if isinstance(value, str) else value
            )

    if options["remove_duplicate_columns"]:
        df = df.loc[:, ~df.columns.duplicated()]

    if options["remove_empty_rows"]:
        df = df.dropna(axis=0, how="all")

    if options["remove_empty_columns"]:
        df = df.dropna(axis=1, how="all")

    report["missing_values_before"] = detect_missing_values(df)
    df = fill_missing(
        df,
        strategy=options["missing_strategy"],
        constant_value=options.get("constant_value"),
    )
    report["missing_values_after"] = detect_missing_values(df)

    report["numeric_columns_before_encoding"] = df.select_dtypes(include=["number"]).columns.tolist()
    report["categorical_columns_before_encoding"] = df.select_dtypes(include=["object", "category", "string"]).columns.tolist()

    if options["encoding"] == "label":
        df = label_encode(df)
    elif options["encoding"] == "onehot":
        df = one_hot_encode(df)
    elif options["encoding"] == "ordinal":
        categorical_cols = df.select_dtypes(include=["object", "category", "string"]).columns.tolist()
        if categorical_cols:
            df = ordinal_encode(df, columns=categorical_cols)

    if options["convert_to_numeric"]:
        for column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="ignore")

    if options["convert_to_float"]:
        numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()
        df[numeric_columns] = df[numeric_columns].astype(float)

    if options["convert_to_integer"]:
        numeric_columns = df.select_dtypes(include=["number"]).columns.tolist()
        df[numeric_columns] = df[numeric_columns].astype("Int64")

    if options["convert_to_boolean"]:
        df = df.applymap(lambda value: bool(value) if pd.notna(value) else value)

    if options["convert_to_datetime"]:
        for column in df.columns:
            try:
                df[column] = pd.to_datetime(df[column], errors="ignore")
            except Exception:
                pass

    if options["scaling"]:
        df = scale_dataframe(df, method=options["scaling"])

    if options["outlier_method"] == "iqr":
        report["outlier_summary"] = detect_outliers_iqr(df)
    elif options["outlier_method"] == "zscore":
        report["outlier_summary"] = detect_outliers_zscore(df)
    elif options["outlier_method"] == "isolation_forest":
        report["outlier_summary"] = detect_outliers_isolation_forest(df)
    else:
        report["outlier_summary"] = {}

    if options["variance_threshold"] > 0.0:
        report["variance_selected_features"] = variance_threshold(df, threshold=options["variance_threshold"])

    report["high_correlation_columns"] = correlation_filter(df, threshold=options["correlation_threshold"])

    if options["mutual_information"]:
        report["mutual_information"] = mutual_information_score(df, target_column=options.get("target_column"))

    final_rows = get_row_count(df)
    final_columns = len(get_column_names(df))
    report["final_rows"] = final_rows
    report["final_columns"] = final_columns

    processed_filename = build_processed_filename(filename, suffix="cleaned")
    processed_filename = Path(processed_filename).with_suffix(f".{options['output_format']}").name
    output_path = os.path.join(PROCESSED_FOLDER, safe_filename(processed_filename))
    save_dataframe(df, output_path)

    report["processed_file"] = processed_filename
    report["processed_path"] = output_path

    return df, processed_filename, report
