
import pandas as pd
import pytest
from datalens.profiling import get_dataset_overview, get_column_profile, get_descriptive_statistics, get_missing_value_profile


def test_normal_dataframe():
    df = pd.DataFrame({
        "calories": [420, 380, 390],
        "duration": [50.1, 40.5, 45.4],
    })

    result = get_dataset_overview(df)
    column_profile = get_column_profile(df)

    assert result == {"row_count": 3, "column_count": 2}
    assert column_profile == [
        {"name": "calories", "data_type": "int64"},
        {"name": "duration", "data_type": "float64"},
    ]


def test_dataframe_with_no_columns():
    df = pd.DataFrame(index=range(3))

    result = get_dataset_overview(df)
    column_profile = get_column_profile(df)

    assert result == {"row_count": 3, "column_count": 0}
    assert column_profile == []


def test_dataframe_with_no_rows():
    df = pd.DataFrame({
        "name": [],
        "age": [],
    })

    result = get_dataset_overview(df)
    column_profile = get_column_profile(df)

    assert result == {"row_count": 0, "column_count": 2}
    assert column_profile == [
        {"name": "name", "data_type": "float64"},
        {"name": "age", "data_type": "float64"},
    ]


def test_empty_dataframe():
    df = pd.DataFrame()

    assert get_dataset_overview(df) == {
        "row_count": 0,
        "column_count": 0,
    }
    assert get_column_profile(df) == []


def test_overview_does_not_modify_dataframe():
    df = pd.DataFrame({
        "name": ["Alice", "Bob"],
        "age": [25, 30],
    })
    original_df = df.copy(deep=True)

    get_dataset_overview(df)

    pd.testing.assert_frame_equal(df, original_df)


def test_column_profile_with_blank_names():
    df = pd.DataFrame(
        [[10, 20], [30, 40]],
        columns=["", ""],
    )

    result = get_column_profile(df)

    assert result == [
        {"name": "", "data_type": "int64"},
        {"name": "", "data_type": "int64"},
    ]


def test_column_profile_does_not_modify_dataframe():
    df = pd.DataFrame({
        "name": ["Alice", "Bob"],
        "age": [25, 30],
    })
    original_df = df.copy(deep=True)

    get_column_profile(df)

    pd.testing.assert_frame_equal(df, original_df)

def test_descriptive_statistics_for_numeric_columns():
    df = pd.DataFrame({
        "age": [20, 30, 40],
        "department": ["Sales", "IT", "HR"],
    })

    result = get_descriptive_statistics(df)

    assert len(result) == 1
    assert result[0]["name"] == "age"
    assert result[0]["position"] == 0
    assert result[0]["data_type"] == "int64"

    stats = result[0]["statistics"]

    assert stats["count"] == 3
    assert stats["mean"] == pytest.approx(30.0)
    assert stats["50%"] == pytest.approx(30.0)
    assert stats["min"] == 20
    assert stats["max"] == 40
    assert stats["unique_count"] == 3


def test_no_numeric_columns():
    df = pd.DataFrame({
        "name": ["Alice", "Bob"],
        "department": ["Sales", "IT"],
    })

    assert get_descriptive_statistics(df) == []


def test_empty_dataframe_for_descriptive_statistics():
    df = pd.DataFrame()

    assert get_descriptive_statistics(df) == []


def test_numeric_column_with_missing_values():
    df = pd.DataFrame({
        "score": [10.0, None, 30.0],
    })

    result = get_descriptive_statistics(df)
    stats = result[0]["statistics"]

    assert stats["count"] == 2
    assert stats["mean"] == pytest.approx(20.0)
    assert stats["unique_count"] == 2


def test_numeric_column_with_only_missing_values():
    df = pd.DataFrame({
        "score": pd.Series([None, None], dtype="float64"),
    })

    result = get_descriptive_statistics(df)
    stats = result[0]["statistics"]

    assert stats["count"] == 0
    assert stats["mean"] is None
    assert stats["min"] is None
    assert stats["max"] is None
    assert stats["unique_count"] == 0


def test_duplicate_column_names():
    df = pd.DataFrame(
        [[10, 100], [20, 200]],
        columns=["score", "score"],
    )

    result = get_descriptive_statistics(df)

    assert len(result) == 2
    assert result[0]["name"] == "score"
    assert result[1]["name"] == "score"
    assert result[0]["position"] == 0
    assert result[1]["position"] == 1

    assert result[0]["statistics"]["mean"] == pytest.approx(15.0)
    assert result[1]["statistics"]["mean"] == pytest.approx(150.0)


def test_statistics_do_not_modify_dataframe():
    df = pd.DataFrame({
        "age": [20, 30, 40],
        "name": ["Alice", "Bob", "Charlie"],
    })

    original_df = df.copy(deep=True)

    get_descriptive_statistics(df)

    pd.testing.assert_frame_equal(df, original_df)

def test_missing_value_profile_normal_dataframe():
    df = pd.DataFrame({
        "name": ["Alice", "Bob", None, "David"],
        "age": [25, None, 35, 40],
        "salary": [40000, 50000, 60000, 70000]
    })

    result = get_missing_value_profile(df)

    assert result["columns"] == [
        {
            "position": 0,
            "name": "name",
            "missing_count": 1,
            "non_missing_count": 3,
            "missing_percentage": 25.0
        },
        {
            "position": 1,
            "name": "age",
            "missing_count": 1,
            "non_missing_count": 3,
            "missing_percentage": 25.0
        },
        {
            "position": 2,
            "name": "salary",
            "missing_count": 0,
            "non_missing_count": 4,
            "missing_percentage": 0.0
        }
    ]

    assert result["dataset"] == {
        "row_count": 4,
        "column_count": 3,
        "total_missing": 2,
        "total_cells": 12,
        "missing_percentage": pytest.approx(16.6666666667)
    }

def test_missing_value_profile_no_missing_values():
    df = pd.DataFrame({
        "name": ["Alice", "Bob"],
        "age": [25, 30]
    })

    result = get_missing_value_profile(df)

    assert result["dataset"]["total_missing"] == 0
    assert result["dataset"]["missing_percentage"] == 0.0

    for column in result["columns"]:
        assert column["missing_count"] == 0
        assert column["missing_percentage"] == 0.0

def test_missing_value_profile_all_values_missing():
    df = pd.DataFrame({
        "name": [None, None],
        "age": [None, None]
    })

    result = get_missing_value_profile(df)

    assert result["dataset"]["total_missing"] == 4
    assert result["dataset"]["total_cells"] == 4
    assert result["dataset"]["missing_percentage"] == 100.0

    for column in result["columns"]:
        assert column["missing_count"] == 2
        assert column["non_missing_count"] == 0
        assert column["missing_percentage"] == 100.0
    
def test_missing_value_profile_zero_rows():
    df = pd.DataFrame(columns=["name", "age"])

    result = get_missing_value_profile(df)

    assert len(result["columns"]) == 2

    for column in result["columns"]:
        assert column["missing_count"] == 0
        assert column["non_missing_count"] == 0
        assert column["missing_percentage"] is None

    assert result["dataset"] == {
        "row_count": 0,
        "column_count": 2,
        "total_missing": 0,
        "total_cells": 0,
        "missing_percentage": None
    }

def test_missing_value_profile_zero_columns():
    df = pd.DataFrame(index=range(3))

    result = get_missing_value_profile(df)

    assert result["columns"] == []

    assert result["dataset"] == {
        "row_count": 3,
        "column_count": 0,
        "total_missing": 0,
        "total_cells": 0,
        "missing_percentage": None
    }

def test_missing_value_profile_empty_dataframe():
    df = pd.DataFrame()

    result = get_missing_value_profile(df)

    assert result["columns"] == []

    assert result["dataset"] == {
        "row_count": 0,
        "column_count": 0,
        "total_missing": 0,
        "total_cells": 0,
        "missing_percentage": None
    }

def test_missing_value_profile_duplicate_column_names():
    df = pd.DataFrame(
        [["Alice", None], ["Bob", "Smith"]],
        columns=["name", "name"]
    )

    result = get_missing_value_profile(df)

    assert len(result["columns"]) == 2

    assert result["columns"][0] == {
        "position": 0,
        "name": "name",
        "missing_count": 0,
        "non_missing_count": 2,
        "missing_percentage": 0.0
    }

    assert result["columns"][1] == {
        "position": 1,
        "name": "name",
        "missing_count": 1,
        "non_missing_count": 1,
        "missing_percentage": 50.0
    }
    
def test_missing_value_profile_does_not_modify_dataframe():
    df = pd.DataFrame({
        "name": ["Alice", None],
        "age": [25, 30]
    })

    original_df = df.copy(deep=True)

    get_missing_value_profile(df)

    pd.testing.assert_frame_equal(df, original_df)