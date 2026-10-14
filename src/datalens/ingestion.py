from os import PathLike
from typing import Any, IO
import pandas as pd 

def load_data(file: str | PathLike[str] | IO[Any]) -> pd.DataFrame:
    """
    Load a CSV file into a pandas DataFrame.

    Parameters
    ----------
    file : str, PathLike[str], or IO[Any]
        A filesystem path or a readable text stream containing CSV data.

    Returns
    -------
    pd.DataFrame
        The complete dataset, including all rows and columns.

    Raises
    ------
    ValueError
        If the file is empty or cannot be parsed as CSV.
    OSError
        If a filesystem-related error prevents reading the file.
    """

    try:
        return pd.read_csv(file)
    
    except pd.errors.EmptyDataError as exc:
        raise ValueError(
            "The uploaded file is empty or contains no readable data."
        ) from exc

    except pd.errors.ParserError as exc:
        raise ValueError(
            "The CSV could not be parsed. Check its structure and delimiters."
        ) from exc