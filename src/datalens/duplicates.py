import pandas as pd

def get_duplicate_profile(dataframe: pd.DataFrame) -> dict[str, int | float | None]:
    """
    Analyze a DataFrame and return summary statistics about duplicate rows.

    A row is considered a duplicate when all its values match a previous
    row. Only subsequent occurrences are counted; the first occurrence
    is treated as the original record.

    Parameters
    ----------
    dataframe : pd.DataFrame
        The DataFrame to inspect.

    Returns
    -------
        dict: A dictionary containing:
            - total_rows (int): Total number of rows in the DataFrame.
            - duplicate_count (int): Number of duplicate occurrences.
            - duplicate_percentage (float | None): Percentage of rows
              identified as duplicates. Returns None if the DataFrame
              contains zero rows.

    Notes:
        - Missing values in matching positions are considered equal
          for duplicate detection.
        - The original DataFrame is not modified.
    """
    total_rows = len(dataframe)
    duplicate_record = dataframe.duplicated(keep="first")

    #duplicate_count = int(duplicate_record.sum())
    duplicate_count = 0
    for row in duplicate_record:
        if row:
            duplicate_count += 1

    if total_rows == 0:
        duplicate_percentage = None
    else:
        duplicate_percentage = (duplicate_count / total_rows) * 100

    return {"total_rows": total_rows,
            "duplicate_count": duplicate_count,
            "duplicate_percentage": duplicate_percentage
            }

 