def detect_duplicates(df):
    if hasattr(df, "duplicated"):
        duplicate_mask = df.duplicated()
        return int(duplicate_mask.sum())
    return 0


def remove_duplicates(df):
    if hasattr(df, "drop_duplicates"):
        return df.drop_duplicates()
    return df
