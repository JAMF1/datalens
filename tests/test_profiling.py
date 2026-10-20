import pandas as pd
from datalens.profiling import get_dataset_overview, get_column_profile

def test_normal_dataframe():
    df = pd.DataFrame({
        "calories": [420,380,390],
        "duration": [50.1, 40.5, 45.4]
        })

    result = get_dataset_overview(df)
    column_profile = get_column_profile(df)

    assert list(result.values()) == [3,2]
    assert column_profile == [{"name": "calories","data_type": "int64"},
                              {"name": "duration","data_type": "float64"}]


def test_dataframe_with_no_columns():
    df = pd.DataFrame(index=range(3))

    result = get_dataset_overview(df)

    assert result == {"row_count": 3, "column_count": 0}

def test_dataframe_with_no_rows():
    df = pd.DataFrame({
                "name": [],
                "age": [],
            })

    result = get_dataset_overview(df)
    column_profile = get_column_profile(df)

    assert list(result.values()) == [0,2]
    assert column_profile == [{"name": "name","data_type": "float"},
                              {"name": "age","data_type": "float64"}]

def test_empty_dataframe():
    df = pd.DataFrame()

    result = get_dataset_overview(df)

    assert list(result.values()) == [0,0]

def test_overview_does_not_modify_dataframe():
    df = pd.DataFrame({
        "name": ["Alice", "Bob"],
        "age": [25, 30],
    })

    original_df = df.copy(deep=True)

    get_dataset_overview(df)

    pd.testing.assert_frame_equal(df, original_df)