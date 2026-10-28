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
