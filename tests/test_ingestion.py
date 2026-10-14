from io import StringIO

import pandas as pd
import pytest

from datalens.ingestion import load_data


def test_load_valid_csv():
    file = StringIO("name,age\nAlice,25\nBob,30")

    result = load_data(file)

    assert isinstance(result, pd.DataFrame)
    assert result.shape == (2, 2)
    assert list(result.columns) == ["name", "age"]


def test_load_empty_csv():
    file = StringIO("")

    with pytest.raises(ValueError, match="empty"):
        load_data(file)


def test_load_malformed_csv():
    file = StringIO(
        "name,age\nAlice,25\nBob,30,extra"
    )

    with pytest.raises(ValueError, match="parsed"):
        load_data(file)
