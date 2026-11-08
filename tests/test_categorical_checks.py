
import pandas as pd

from datalens.data_quality.categorical_checks import (
    get_categorical_column_profile,
    )


def test_get_categorical_column_profile():
    dataframe = pd.DataFrame({
        "country": ["Mexico", "USA", "Canada", "Mexico", None],
        "department": ["Sales", "HR", "Sales", "IT", "HR"],
        "customer_id": [1, 2, 3, 4, 5],
        "comments": ["Good", None, "Bad", "Average", "Good"],
        "empty_column": [None, None, None, None, None]
    })

    result = get_categorical_column_profile(dataframe)

    assert len(result) == 4

    assert result[0]["column"] == "country"
    assert result[0]["column_position"] == 0
    assert result[0]["data_type"] == "str"
    assert result[0]["unique_count"] == 3
    assert result[0]["non_missing_count"] == 4
    assert result[0]["unique_ratio"] == 0.75

    assert result[1]["column"] == "department"
    assert result[1]["unique_count"] == 3
    assert result[1]["non_missing_count"] == 5
    assert result[1]["unique_ratio"] == 0.6

    assert result[2]["column"] == "comments"
    assert result[2]["unique_count"] == 3
    assert result[2]["non_missing_count"] == 4
    assert result[2]["unique_ratio"] == 0.75

    assert result[3]["column"] == "empty_column"
    assert result[3]["unique_count"] == 0
    assert result[3]["non_missing_count"] == 0
    assert result[3]["unique_ratio"] is None


def test_get_categorical_column_profile_ignores_non_string_values():
    dataframe = pd.DataFrame({
        "mixed": ["Apple", 123, None, True, "Apple", "Banana"]
    })

    result = get_categorical_column_profile(dataframe)

    assert len(result) == 1
    assert result[0]["unique_count"] == 2
    assert result[0]["non_missing_count"] == 3
    assert result[0]["unique_ratio"] == 2 / 3


def test_get_categorical_column_profile_empty_dataframe():
    dataframe = pd.DataFrame()

    result = get_categorical_column_profile(dataframe)

    assert result == []


def test_get_categorical_column_profile_only_numeric_columns():
    dataframe = pd.DataFrame({
        "age": [20, 30, 40],
        "salary": [1000, 2000, 3000]
    })

    result = get_categorical_column_profile(dataframe)

    assert result == []


def test_get_categorical_column_profile_all_missing_values():
    dataframe = pd.DataFrame({
        "category": [None, None, None]
    })

    result = get_categorical_column_profile(dataframe)

    assert len(result) == 1
    assert result[0]["unique_count"] == 0
    assert result[0]["non_missing_count"] == 0
    assert result[0]["unique_ratio"] is None


def test_get_categorical_column_profile_duplicate_values():
    dataframe = pd.DataFrame({
        "country": ["Mexico", "Mexico", "USA", "Mexico", "USA"]
    })

    result = get_categorical_column_profile(dataframe)

    assert result[0]["unique_count"] == 2
    assert result[0]["non_missing_count"] == 5
    assert result[0]["unique_ratio"] == 0.4


def test_get_categorical_column_profile_duplicate_column_names():
    dataframe = pd.DataFrame(
        [
            ["Mexico", "Sales"],
            ["USA", "HR"],
            ["Canada", "Sales"]
        ],
        columns=["category", "category"]
    )

    result = get_categorical_column_profile(dataframe)

    assert len(result) == 2
    assert [profile["column_position"] for profile in result] == [0, 1]
    assert [profile["unique_count"] for profile in result] == [3, 2]


def test_get_categorical_column_profile_pandas_string_dtype():
    dataframe = pd.DataFrame({
        "country": pd.Series(
            ["Mexico", "USA", "Mexico", None],
            dtype="string"
        )
    })

    result = get_categorical_column_profile(dataframe)

    assert len(result) == 1
    assert result[0]["data_type"] == "string"
    assert result[0]["unique_count"] == 2
    assert result[0]["non_missing_count"] == 3
    assert result[0]["unique_ratio"] == 2 / 3


def test_get_categorical_column_profile_does_not_modify_dataframe():
    dataframe = pd.DataFrame({
        "country": ["Mexico", "USA", None],
        "age": [20, 30, 40]
    })
    original_dataframe = dataframe.copy(deep=True)

    get_categorical_column_profile(dataframe)

    pd.testing.assert_frame_equal(dataframe, original_dataframe)


def test_get_categorical_column_profile_placeholder_fields():
    dataframe = pd.DataFrame({
        "country": ["Mexico", "USA", "Canada"]
    })

    result = get_categorical_column_profile(dataframe)

    assert result[0]["automatic_suggestion"] is False
    assert result[0]["user_selected"] is False
    assert result[0]["is_categorical"] is False
