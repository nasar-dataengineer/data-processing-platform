import numpy as np


def histogram_data(df, column, bins: int = 20):
    if hasattr(df, "compute"):
        df = df.compute()

    values = df[column].dropna().astype(float)
    hist, bin_edges = np.histogram(values, bins=bins)
    return {
        "labels": [f"{round(bin_edges[i], 2)} - {round(bin_edges[i+1], 2)}" for i in range(len(bin_edges) - 1)],
        "counts": hist.tolist(),
    }


def missing_value_summary(df):
    if hasattr(df, "compute"):
        df = df.compute()

    missing = df.isnull().sum()
    return {
        "labels": missing.index.tolist(),
        "values": missing.astype(int).tolist(),
    }


def correlation_matrix(df):
    if hasattr(df, "compute"):
        df = df.compute()

    numeric_df = df.select_dtypes(include=["number"])
    corr = numeric_df.corr()
    return {
        "columns": corr.columns.tolist(),
        "matrix": corr.fillna(0).round(4).values.tolist(),
    }
