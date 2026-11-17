import pandas as pd


def _to_pandas(df):
    if hasattr(df, "compute"):
        return df.compute()
    return df


def detect_missing_values(df):
    df = _to_pandas(df)
    return df.isnull().sum().to_dict()


def fill_missing(df, strategy: str = "median", constant_value=None):
    df = _to_pandas(df)

    if strategy == "constant":
        fill_value = "Unknown" if constant_value is None else constant_value
        for column in df.columns:
            if isinstance(df[column].dtype, pd.CategoricalDtype):
                df[column] = df[column].astype(object)
        return df.fillna(fill_value)

    if strategy in {"mean", "median", "mode"}:
        for column in df.columns:
            series = df[column]
            if not series.isna().any():
                continue

            if pd.api.types.is_numeric_dtype(series.dtype):
                if strategy == "mean":
                    fill_value = series.mean()
                elif strategy == "median":
                    fill_value = series.median()
                else:
                    mode = series.mode(dropna=True)
                    fill_value = mode.iloc[0] if not mode.empty else 0
                if pd.isna(fill_value):
                    fill_value = 0
            else:
                mode = series.mode(dropna=True)
                fill_value = mode.iloc[0] if not mode.empty else "Unknown"
                if isinstance(series.dtype, pd.CategoricalDtype) and fill_value not in series.cat.categories:
                    df[column] = series.astype(object)

            df[column] = df[column].fillna(fill_value)
    elif strategy == "ffill":
        df = df.ffill()
    elif strategy == "bfill":
        df = df.bfill()
    elif strategy == "drop_rows":
        df = df.dropna(axis=0, how="any")
    elif strategy == "drop_columns":
        df = df.dropna(axis=1, how="any")

    return df
