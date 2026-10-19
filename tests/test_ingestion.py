from io import StringIO, BytesIO
import pandas as pd
import pytest

from datalens.ingestion import load_data


def test_load_valid_csv():
    file = StringIO("name,age\nAlice,25\nBob,30")
    

    result = load_data(file, "csv")

    assert isinstance(result, pd.DataFrame)
    assert result.shape == (2, 2)
    assert list(result.columns) == ["name", "age"]


def test_load_empty_csv():
    file = StringIO("")

    with pytest.raises(ValueError, match="empty"):
        load_data(file, "csv")


def test_load_malformed_csv():
    file = StringIO(
        "name,age\nAlice,25\nBob,30,extra"
    )

    with pytest.raises(ValueError, match="parsed"):
        load_data(file, "csv")
        

def test_load_valid_xlsx():
    # 1. Create an in-memory binary buffer.
    buffer = BytesIO()

    # 2. Generate a sample Excel workbook.
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        pd.DataFrame({
            "name": ["Alice", "Bob"],
            "age": [25, 30],
        }).to_excel(writer, index=False)

    # 3. Return the cursor to the beginning of the workbook.
    buffer.seek(0)

    # 4. Pass the workbook to the ingestion function.
    result = load_data(buffer, "xlsx")

    # 5. Verify the returned DataFrame.
    assert isinstance(result, pd.DataFrame)
    assert result.shape == (2, 2)
    assert list(result.columns) == ["name", "age"]
    assert result["name"].tolist() == ["Alice", "Bob"]
    assert result["age"].tolist() == [25, 30]
