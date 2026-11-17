import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler, RobustScaler, MaxAbsScaler


def _to_pandas(df):
    if hasattr(df, "compute"):
        return df.compute()
    return df


def get_numeric_columns(df):
    df = _to_pandas(df)
    return df.select_dtypes(include=["number"]).columns.tolist()


def scale_dataframe(df, method: str = "standard", columns=None):
    df = _to_pandas(df)
    numeric_columns = columns or get_numeric_columns(df)

    if len(numeric_columns) == 0:
        return df

    scaler_map = {
        "minmax": MinMaxScaler(),
        "standard": StandardScaler(),
        "robust": RobustScaler(),
        "maxabs": MaxAbsScaler(),
    }

    scaler = scaler_map.get(method, StandardScaler())
    values = df[numeric_columns].astype(float)
    scaled_values = scaler.fit_transform(values)
    df[numeric_columns] = scaled_values
    return df


def normalize_columns(df, columns=None):
    return scale_dataframe(df, method="minmax", columns=columns)
