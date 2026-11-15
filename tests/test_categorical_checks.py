import pandas as pd
import pytest

from datalens.data_quality.categorical_checks import (
    get_categorical_column_profile, suggest_categorical_columns, apply_categorical_selection
    )
from datalens.data_quality.models import CategoricalColumnProfile

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

## test suggest_categorical_columns ## 

def make_profile(
    unique_ratio=0.03,
    non_missing_count=100,
    automatic_suggestion=False,
    user_selected=False,
    is_categorical=False,
) -> CategoricalColumnProfile:
    return CategoricalColumnProfile(
        column="department",
        column_position=0,
        data_type="object",
        unique_count=3,
        non_missing_count=non_missing_count,
        unique_ratio=unique_ratio,
        automatic_suggestion=automatic_suggestion,
        user_selected=user_selected,
        is_categorical=is_categorical,
    )


# --- Basic classification behavior ---

def test_suggests_column_meeting_both_conditions():
    profiles = [make_profile(unique_ratio=0.03, non_missing_count=100)]

    result = suggest_categorical_columns(profiles)

    assert result[0]["automatic_suggestion"] is True
    assert result[0]["is_categorical"] is True


def test_does_not_suggest_column_exceeding_unique_ratio():
    profiles = [make_profile(unique_ratio=0.10, non_missing_count=100)]

    result = suggest_categorical_columns(profiles)

    assert result[0]["automatic_suggestion"] is False
    assert result[0]["is_categorical"] is False


def test_does_not_suggest_column_below_minimum_observations():
    profiles = [make_profile(unique_ratio=0.03, non_missing_count=10)]

    result = suggest_categorical_columns(profiles)

    assert result[0]["automatic_suggestion"] is False
    assert result[0]["is_categorical"] is False


def test_suggests_column_exactly_on_both_thresholds():
    profiles = [make_profile(unique_ratio=0.05, non_missing_count=20)]

    result = suggest_categorical_columns(profiles)

    assert result[0]["automatic_suggestion"] is True
    assert result[0]["is_categorical"] is True


def test_does_not_suggest_column_with_none_unique_ratio():
    profiles = [make_profile(unique_ratio=None, non_missing_count=100)]

    result = suggest_categorical_columns(profiles)

    assert result[0]["automatic_suggestion"] is False
    assert result[0]["is_categorical"] is False


def test_suggests_column_with_zero_unique_ratio():
    profiles = [make_profile(unique_ratio=0.0, non_missing_count=100)]

    result = suggest_categorical_columns(profiles)

    assert result[0]["automatic_suggestion"] is True
    assert result[0]["is_categorical"] is True


# --- Empty input and custom thresholds ---

def test_empty_profiles_returns_empty_list():
    result = suggest_categorical_columns([])

    assert result == []


def test_custom_thresholds_are_applied():
    profiles = [make_profile(unique_ratio=0.10, non_missing_count=50)]

    result = suggest_categorical_columns(
        profiles,
        max_unique_ratio=0.15,
        min_non_missing=40,
    )

    assert result[0]["automatic_suggestion"] is True
    assert result[0]["is_categorical"] is True


# --- Input validation ---

@pytest.mark.parametrize("invalid_ratio", ["0.05", None, [], True, False])
def test_rejects_invalid_max_unique_ratio_type(invalid_ratio):
    profiles = [make_profile()]

    with pytest.raises(ValueError, match="max_unique_ratio must be a number"):
        suggest_categorical_columns(
            profiles,
            max_unique_ratio=invalid_ratio,
        )


@pytest.mark.parametrize("invalid_ratio", [0, -0.1, 1.1, 2])
def test_rejects_max_unique_ratio_outside_valid_range(invalid_ratio):
    profiles = [make_profile()]

    with pytest.raises(ValueError, match="max_unique_ratio must be greater than 0"):
        suggest_categorical_columns(
            profiles,
            max_unique_ratio=invalid_ratio,
        )


@pytest.mark.parametrize("invalid_count", ["20", 20.0, None, [], True, False])
def test_rejects_invalid_min_non_missing_type(invalid_count):
    profiles = [make_profile()]

    with pytest.raises(ValueError, match="min_non_missing must be a positive integer"):
        suggest_categorical_columns(
            profiles,
            min_non_missing=invalid_count,
        )


@pytest.mark.parametrize("invalid_count", [0, -1])
def test_rejects_min_non_missing_below_one(invalid_count):
    profiles = [make_profile()]

    with pytest.raises(ValueError, match="min_non_missing must be at least 1"):
        suggest_categorical_columns(
            profiles,
            min_non_missing=invalid_count,
        )


# --- User selection and input preservation ---

def test_preserves_existing_user_selection():
    profiles = [make_profile(
        unique_ratio=0.50,
        non_missing_count=100,
        user_selected=True,
    )]

    result = suggest_categorical_columns(profiles)

    assert result[0]["automatic_suggestion"] is False
    assert result[0]["user_selected"] is True
    assert result[0]["is_categorical"] is True


def test_user_selection_remains_false_when_not_selected():
    profiles = [make_profile(user_selected=False)]

    result = suggest_categorical_columns(profiles)

    assert result[0]["user_selected"] is False


def test_does_not_modify_original_profiles_suggest():
    profiles = [make_profile()]

    original_profile = profiles[0].copy()

    suggest_categorical_columns(profiles)

    assert profiles[0] == original_profile


def test_returns_new_profile_dictionaries_suggest():
    profiles = [make_profile()]

    result = suggest_categorical_columns(profiles)

    assert result is not profiles
    assert result[0] is not profiles[0]


# --- User selection behavior ---

def test_selects_column_not_automatically_suggested():
    profiles = [make_profile(
        unique_ratio=0.50,
        non_missing_count=100,
        automatic_suggestion=False,
    )]

    result = apply_categorical_selection(profiles, [0])

    assert result[0]["user_selected"] is True
    assert result[0]["is_categorical"] is True


def test_preserves_automatically_suggested_column():
    profiles = [make_profile(
        automatic_suggestion=True,
        user_selected=False,
    )]

    result = apply_categorical_selection(profiles, [])

    assert result[0]["automatic_suggestion"] is True
    assert result[0]["user_selected"] is False
    assert result[0]["is_categorical"] is True


def test_selects_multiple_columns():
    profiles = [
        make_profile(),
        make_profile(),
        make_profile(),
    ]

    profiles[1]["column_position"] = 1
    profiles[2]["column_position"] = 2

    result = apply_categorical_selection(profiles, [0, 2])

    assert result[0]["user_selected"] is True
    assert result[1]["user_selected"] is False
    assert result[2]["user_selected"] is True


def test_empty_selection_deselects_all_columns():
    profiles = [
        make_profile(user_selected=True),
        make_profile(user_selected=True),
    ]

    profiles[1]["column_position"] = 1

    result = apply_categorical_selection(profiles, [])

    assert result[0]["user_selected"] is False
    assert result[1]["user_selected"] is False


def test_selection_preserves_automatic_suggestions():
    profiles = [
        make_profile(automatic_suggestion=True),
        make_profile(automatic_suggestion=False),
    ]

    profiles[1]["column_position"] = 1

    result = apply_categorical_selection(profiles, [1])

    assert result[0]["automatic_suggestion"] is True
    assert result[1]["automatic_suggestion"] is False
    assert result[1]["is_categorical"] is True


def test_duplicate_selected_positions_do_not_change_result():
    profiles = [make_profile()]

    result = apply_categorical_selection(profiles, [0, 0, 0])

    assert result[0]["user_selected"] is True


# --- Position validation ---

@pytest.mark.parametrize("invalid_position", ["0", 1.5, None, True, False])
def test_rejects_non_integer_positions(invalid_position):
    profiles = [make_profile()]

    with pytest.raises(ValueError, match="Every selected position must be an integer"):
        apply_categorical_selection(profiles, [invalid_position])


@pytest.mark.parametrize("invalid_position", [1, 5, 999, -1])
def test_rejects_positions_not_present_in_profiles(invalid_position):
    profiles = [make_profile()]

    with pytest.raises(ValueError, match="Selected positions must correspond to existing column profiles"):
        apply_categorical_selection(profiles, [invalid_position])


def test_rejects_non_list_profiles():
    with pytest.raises(ValueError, match="Profiles must be a list"):
        apply_categorical_selection("invalid", [])


def test_rejects_non_list_selected_positions():
    profiles = [make_profile()]

    with pytest.raises(ValueError, match="Selected positions must be a list"):
        apply_categorical_selection(profiles, 0)


# --- Data integrity ---

def test_does_not_modify_original_profiles():
    profiles = [
        make_profile(user_selected=False),
        make_profile(user_selected=False),
    ]

    profiles[1]["column_position"] = 1
    original_profiles = [profile.copy() for profile in profiles]

    apply_categorical_selection(profiles, [0])

    assert profiles == original_profiles


def test_returns_new_profile_dictionaries():
    profiles = [make_profile()]

    result = apply_categorical_selection(profiles, [0])

    assert result is not profiles
    assert result[0] is not profiles[0]
