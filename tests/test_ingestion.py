from io import StringIO, BytesIO
import pandas as pd
import pytest

from datalens.ingestion import load_data
example_csv = "tests/Social_media_impact_on_life.csv"
example_excel = "tests/coffeeOrdersData.xlsx"

def test_load_valid_csv():
    file = StringIO("name,age\nAlice,25\nBob,30")
    file2 = StringIO("name,age,gender\nRose,30,F\nHenry,28,M")
    
    result = load_data(file, "csv")
    result2 = load_data(file2, "csv")
    result3 = load_data(example_csv, "csv")

    assert isinstance(result, pd.DataFrame)
    assert result.shape == (2, 2)
    assert list(result.columns) == ["name", "age"]

    assert isinstance(result2, pd.DataFrame)
    assert result2.shape == (2,3)
    assert list(result2.columns) == ["name", "age", "gender"]

    assert isinstance(result3, pd.DataFrame)
    assert result3.shape == (4500,16)


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

def test_load_csv_with_headers_only():
    buffer = StringIO("name,age\n")

    result = load_data(buffer, "csv")

    assert isinstance(result, pd.DataFrame)
    assert result.empty
    assert list(result.columns) == ["name", "age"]

def test_load_csv_from_path(tmp_path):
    file_path = tmp_path / "people.csv"
    file_path.write_text("name,age\nAlice,25\n", encoding="utf-8")

    result = load_data(file_path, "csv")

    assert result.shape == (1, 2)
    assert result.iloc[0]["name"] == "Alice"

def test_load_valid_xlsx():
    buffer = BytesIO()

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        pd.DataFrame({
            "name": ["Alice", "Bob"],
            "age": [25, 30],
        }).to_excel(writer, index=False)

    buffer.seek(0)

    result = load_data(buffer, "xlsx")
    result2 = load_data(example_excel, "xlsx")

    assert isinstance(result, pd.DataFrame)
    assert result.shape == (2, 2)
    assert list(result.columns) == ["name", "age"]
    assert result["name"].tolist() == ["Alice", "Bob"]
    assert result["age"].tolist() == [25, 30]

    assert isinstance(result2, pd.DataFrame)
    assert result2.shape == (1000, 13)

def test_load_xlsx_with_headers_only():
    buffer = BytesIO()

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        pd.DataFrame({
            "name": [],
            "age": [],
        }).to_excel(writer, index=False)

    buffer.seek(0)

    result = load_data(buffer, "xlsx")

    assert isinstance(result, pd.DataFrame)
    assert result.empty
    assert list(result.columns) == ["name", "age"]

def test_load_empty_xlsx():
    buffer = BytesIO()

    # Create a workbook containing a blank worksheet.
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        pd.DataFrame().to_excel(writer, index=False)

    buffer.seek(0)

    result = load_data(buffer, "xlsx")

    assert isinstance(result, pd.DataFrame)
    assert result.empty

def test_unsupported_file_type():
    with pytest.raises(ValueError, match="Unsupported file format"):
        load_data(BytesIO(b"sample"), "json")

