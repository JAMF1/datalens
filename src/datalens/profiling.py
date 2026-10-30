import pandas as pd
from pandas.api.types import is_bool_dtype, is_numeric_dtype

def get_dataset_overview(dataframe: pd.DataFrame) -> dict[str, int]:
    """
    Return the number of rows and columns in a DataFrame.

    Parameters
    ----------
    dataframe : pd.DataFrame
        The DataFrame to inspect.

    Returns
    -------
    dict[str, int]
        A dictionary containing row_count and column_count.
    """
    return {
        "row_count": len(dataframe),
        "column_count": len(dataframe.columns),
    }

def get_column_profile(dataframe: pd.DataFrame) -> list[dict]:
    """
    Return a list of dictionaries containing column name and column data type.

    Parameters
    ----------
    dataframe : pd.DataFrame
        The DataFrame to inspect.

    Returns
    -------
    list[dict]
        A list of dictionaries.
    """
    column_info  = []

    for position, column in enumerate(dataframe.columns):
        column_dict = {
            "name": column,
            "data_type": str(dataframe.dtypes.iloc[position])
        }
        column_info.append(column_dict)
    return column_info

def get_descriptive_statistics(dataframe: pd.DataFrame) -> list[dict]:
    """
    Return descriptive statistics for numeric columns.

    Each column is represented by a dictionary containing its
    position, name, data type, and descriptive statistics.

    Boolean columns are excluded from numerical statistics.
    Missing values are ignored by pandas' statistical calculations.
    Unavailable statistical results are represented as None.

    Parameters
    ----------
    dataframe : pd.DataFrame
        The DataFrame to inspect.

    Returns
    -------
    list[dict]
        A list containing the descriptive statistics for each
        numeric column.
    """
    statistics = []
    for position in range(len(dataframe.columns)):
        column = dataframe.iloc[:, position]

        if not is_numeric_dtype(column.dtype) or is_bool_dtype(column.dtype):
            continue

        summary = column.describe().to_dict()
        summary["unique_count"] = int(column.nunique(dropna=True))

        clean_summary = {}

        for statistic, value in summary.items():
            if pd.isna(value):
                clean_summary[statistic] = None
            elif hasattr(value, "item"):
                clean_summary[statistic] = value.item()
            else:
                clean_summary[statistic] = value

        statistics.append({
            "position": position,
            "name": dataframe.columns[position],
            "data_type": str(column.dtype),
            "statistics": clean_summary,
        })

    return statistics

def get_missing_value_profile(dataframe: pd.DataFrame) -> dict:
    """
    Generate a missing-value profile for each column and the entire dataset.

    Calculates missing and non-missing value counts, missing-value
    percentages, and overall dataset statistics. Missing values are
    identified using pandas' isna() method.

    Column positions are included to distinguish columns with duplicate
    names. Percentages are represented as None when they cannot be
    calculated due to zero rows or zero total cells.

    The original DataFrame is not modified.

    Parameters
    ----------
    dataframe : pd.DataFrame
        The DataFrame to analyze.

    Returns
    -------
    dict
        A dictionary containing:
        - columns: A list of dictionaries with each column's position,
          name, missing count, non-missing count, and missing percentage.
        - dataset: A dictionary containing row count, column count,
          total missing values, total cells, and overall missing percentage.
    """
    missing_value_profiles = {}
    column_profile = []

    for position in range(len(dataframe.columns)):
        column = dataframe.iloc[:, position]
        missing_count = int(column.isna().sum())
        non_missing_count = int(column.notna().sum())

        if len(dataframe) == 0:
            column_missing_percentage = None
        else: 
            column_missing_percentage = float((missing_count / len(dataframe)) * 100)

        column_profile.append({
            "position": position,
            "name": column.name,
            "missing_count": missing_count,
            "non_missing_count": non_missing_count,
            "missing_percentage": column_missing_percentage
        })
    total_missing = int(dataframe.isna().sum().sum())
    total_cells = dataframe.size 
    if total_cells == 0:
        dataset_missing_percentage = None
    else:
        dataset_missing_percentage = float((total_missing / total_cells) * 100)

    missing_value_profiles["columns"] = column_profile
    missing_value_profiles["dataset"] = {
        "row_count": len(dataframe),
        "column_count": len(dataframe.columns),
        "total_missing": total_missing,
        "total_cells": total_cells,
        "missing_percentage": dataset_missing_percentage
    }

    return missing_value_profiles