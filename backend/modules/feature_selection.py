import numpy as np
from sklearn.feature_selection import VarianceThreshold, mutual_info_regression


def _to_pandas(df):
    if hasattr(df, "compute"):
        return df.compute()
    return df


def variance_threshold(df, threshold: float = 0.0):
    df = _to_pandas(df)
    selector = VarianceThreshold(threshold=threshold)
    numeric_df = df.select_dtypes(include=["number"])
    if numeric_df.shape[1] == 0:
        return []
    selector.fit(numeric_df)
    mask = selector.get_support()
    return numeric_df.columns[mask].tolist()


def correlation_filter(df, threshold: float = 0.95):
    df = _to_pandas(df)
    numeric_df = df.select_dtypes(include=["number"])
    if numeric_df.shape[1] < 2:
        return []

    corr = numeric_df.corr().abs()
    upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
    to_drop = [column for column in upper.columns if any(upper[column] > threshold)]
    return to_drop


def mutual_information(df, target_column: str = None, top_k: int = 20):
    df = _to_pandas(df)
    numeric_df = df.select_dtypes(include=["number"])
    if numeric_df.shape[1] < 2:
        return []

    results = []
    if target_column and target_column in numeric_df.columns:
        features = numeric_df.drop(columns=[target_column])
        target = numeric_df[target_column]
        if features.shape[1] == 0:
            return []
        scores = mutual_info_regression(features.fillna(0), target.fillna(0))
        for feature, score in zip(features.columns, scores):
            results.append({"target": target_column, "feature": feature, "score": float(score)})
    else:
        for target in numeric_df.columns:
            features = numeric_df.drop(columns=[target])
            if features.shape[1] == 0:
                continue
            scores = mutual_info_regression(features.fillna(0), numeric_df[target].fillna(0))
            for feature, score in zip(features.columns, scores):
                results.append({"target": target, "feature": feature, "score": float(score)})

    results.sort(key=lambda item: item["score"], reverse=True)
    return results[:top_k]
