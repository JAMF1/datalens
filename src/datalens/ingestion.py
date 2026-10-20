from os import PathLike
from typing import Any, IO
from zipfile import BadZipFile
from xml.etree.ElementTree import ParseError

import pandas as pd
from openpyxl.utils.exceptions import InvalidFileException


def load_data(file: str | PathLike[str] | IO[Any], file_type: str) -> pd.DataFrame:
    """
    Load a CSV or XLSX file into a pandas DataFrame.

    Parameters
    ----------
    file : str, PathLike[str], or IO[Any]
        A filesystem path or readable stream containing the file.
    file_type : str
            The file format: "csv" or "xlsx".

        Returns
        -------
        pd.DataFrame
            The loaded dataset.

        Raises
        ------
        ValueError
            If the format is unsupported or the file is empty,
            malformed, or unreadable.
        OSError
            If a filesystem-related error prevents reading the file.
        """
    
    file_type = file_type.lower().lstrip(".")

    if file_type not in {"csv", "xlsx"}:
        raise ValueError("Unsupported file format. Please use 'csv' or 'xlsx'.")

    if file_type == "csv":
        try:
            return pd.read_csv(file)
        
        except pd.errors.EmptyDataError as exc:
            raise ValueError("The uploaded file is empty or contains no readable data.") from exc
        
        except pd.errors.ParserError as exc:
            raise ValueError("The CSV could not be parsed. "
                             "Check its structure and delimiters.") from exc

    try:
        return pd.read_excel(file, sheet_name=0)
    
    except (
        ValueError,
        BadZipFile,
        InvalidFileException,
        ParseError,
        pd.errors.EmptyDataError
    ) as exc:
        raise ValueError(
            "The XLSX file could not be read. "
            "Check that it is a valid, uncorrupted Excel workbook."
        ) from exc
