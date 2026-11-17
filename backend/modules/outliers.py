import numpy as np
from sklearn.ensemble import IsolationForest


def _to_pandas(df):
    if hasattr(df, "compute"):
        return df.compute()
    return df


def detect_outliers_iqr(df, columns=None):
    df = _to_pandas(df)
    numeric_columns = columns or df.select_dtypes(include=["number"]).columns.tolist()
    outliers = {}

    for column in numeric_columns:
        q1 = df[column].quantile(0.25)
        q3 = df[column].quantile(0.75)
        iqr = q3 - q1
        outliers[column] = int(((df[column] < q1 - 1.5 * iqr) | (df[column] > q3 + 1.5 * iqr)).sum())

    return outliers


def detect_outliers_zscore(df, columns=None, threshold: float = 3.0):
    df = _to_pandas(df)
    numeric_columns = columns or df.select_dtypes(include=["number"]).columns.tolist()
    outliers = {}

    for column in numeric_columns:
        series = df[column].astype(float)
        z_scores = (series - series.mean()) / series.std(ddof=0)
        outliers[column] = int((np.abs(z_scores) > threshold).sum())

    return outliers


def detect_outliers_isolation_forest(df, columns=None, contamination=0.01):
    df = _to_pandas(df)
    numeric_columns = columns or df.select_dtypes(include=["number"]).columns.tolist()
    if len(numeric_columns) == 0:
        return {}

    model = IsolationForest(contamination=contamination, random_state=42)
    model.fit(df[numeric_columns].astype(float))
    preds = model.predict(df[numeric_columns].astype(float))
    mask = preds == -1
    return {"isolation_forest": int(mask.sum())}
