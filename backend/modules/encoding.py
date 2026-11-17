import pandas as pd
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, OrdinalEncoder


def _to_pandas(df):
    if hasattr(df, "compute"):
        return df.compute()
    return df


def label_encode(df, columns=None):
    df = _to_pandas(df)
    target_columns = columns or df.select_dtypes(include=["object", "category"]).columns.tolist()
    for column in target_columns:
        encoder = LabelEncoder()
        df[column] = encoder.fit_transform(df[column].astype(str))
    return df


def one_hot_encode(df, columns=None):
    df = _to_pandas(df)
    target_columns = columns or df.select_dtypes(include=["object", "category"]).columns.tolist()
    return pd.get_dummies(df, columns=target_columns, dummy_na=False)


def ordinal_encode(df, columns, categories=None):
    df = _to_pandas(df)
    encoder = OrdinalEncoder(categories=categories)
    df[columns] = encoder.fit_transform(df[columns].astype(str))
    return df


def binary_encode(df, columns):
    df = _to_pandas(df)
    for column in columns:
        df[column] = df[column].astype("category").cat.codes
    return df
