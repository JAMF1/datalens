from datalens.data_quality.models import CategoricalColumnProfile
from pandas.api.types import is_object_dtype, is_string_dtype
import pandas as pd 


def _is_text_column(column: pd.Series) -> bool:
    return (is_object_dtype(column.dtype) or is_string_dtype(column.dtype))

def get_categorical_column_profile(dataframe: pd.DataFrame) -> list[CategoricalColumnProfile]:
    categorical_profile = []

    for position in range(len(dataframe.columns)):
        column = dataframe.iloc[:, position]
        filter = []

        if not _is_text_column(column):
            continue

        for value in column:
            if not isinstance(value,str):
                continue
            if value.isspace():
                continue
            filter.append(value)

        filterered = pd.Series(filter)
        unique_count = filterered.nunique(dropna=True)
        non_missing_count = int(filterered.notna().sum())

        if non_missing_count == 0:
            unique_ratio = None
        else:
            unique_ratio = unique_count / non_missing_count

        column_profile = CategoricalColumnProfile(
            column=column.name,
            column_position=position,
            data_type=str(column.dtype),
            unique_count=unique_count,
            non_missing_count=non_missing_count,
            unique_ratio=unique_ratio,
            automatic_suggestion=False,
            user_selected=False,
            is_categorical=False
            )
        categorical_profile.append(column_profile)

    return categorical_profile

def suggest_categorical_columns(profiles: list[CategoricalColumnProfile], max_unique_ratio: float = 0.05, min_non_missing: int = 20) -> list[CategoricalColumnProfile]:
    if isinstance(max_unique_ratio, bool) or not isinstance(max_unique_ratio, (int, float)):
        raise ValueError("max_unique_ratio must be a number between 0 and 1.")

    if isinstance(min_non_missing, bool) or not isinstance(min_non_missing, int):
        raise ValueError("min_non_missing must be a positive integer.")

    if not (0 < max_unique_ratio <= 1):
        raise ValueError("max_unique_ratio must be greater than 0 and less than or equal to 1.")

    if min_non_missing < 1:
        raise ValueError("min_non_missing must be at least 1.")

    updated = []

    for profile in profiles:
        if profile['unique_ratio'] is not None:
            suggestion = (profile['unique_ratio'] <= max_unique_ratio) and (profile['non_missing_count'] >= min_non_missing)
        else:
            suggestion = False

        updated_profile = {
            **profile,
            "automatic_suggestion": suggestion,
            "is_categorical": suggestion or profile["user_selected"]
        }

        updated.append(updated_profile)

    return updated

def apply_categorical_selection(profiles: list[CategoricalColumnProfile], selected_positions: list[int]) -> list[CategoricalColumnProfile]:
    if not isinstance(profiles, list):
        raise ValueError("Profiles must be a list")
    if not isinstance(selected_positions, list):
        raise ValueError("Selected positions must be a list containing selected values")
    if not all(isinstance(position, int) and not isinstance(position, bool)
           for position in selected_positions):
        raise ValueError("Every selected position must be an integer.")

    valid_positions = {profile["column_position"] for profile in profiles}

    if not set(selected_positions).issubset(valid_positions):
        raise ValueError("Selected positions must correspond to existing column profiles.")
    
    updated = []

    for profile in profiles:
        if profile["column_position"] in selected_positions:
            user_selected = True
        else:
            user_selected = False

        updated_profile = {
            **profile,
            "user_selected": user_selected,
            "is_categorical": user_selected or profile["automatic_suggestion"]
        }

        updated.append(updated_profile)

    return updated