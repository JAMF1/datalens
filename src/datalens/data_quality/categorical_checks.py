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

dataframe = pd.DataFrame({
        "country": ["Mexico", "USA", "Canada", "Mexico", None],
        "department": ["Sales", "HR", "Sales", "IT", "HR"],
        "customer_id": [1, 2, 3, 4, 5],
        "comments": ["Good", None, "Bad", "Average", "Good"],
        "empty_column": [None, None, None, None, None]
    })

# results = get_categorical_column_profile(dataframe=dataframe)

# for column_profile in results:
#     print(column_profile["column"],
#           column_profile["unique_count"],
#           column_profile["non_missing_count"],
#           column_profile["unique_ratio"])

print(pd.__version__)

#print(dataframe["country"].dtype)