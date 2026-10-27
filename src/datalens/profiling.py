
import pandas as pd

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
