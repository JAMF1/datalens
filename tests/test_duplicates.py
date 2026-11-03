import pandas as pd
from datalens.duplicates import get_duplicate_profile

def test_ordinary_duplicates():
    df = pd.DataFrame({
        "Name": ["Alice", "Bob", "Alice", "Charlie", "Bob"],
        "Age": [25,30,25,35,30]
    })

    result = get_duplicate_profile(df)

    assert result == {
        "total_rows": 5,
        "duplicate_count": 2,
        "duplicate_percentage": 40.0
    }

def test_multiple_ocurrences():
    df = pd.DataFrame({
        "Name": ["Alice", "Alice", "Alice", "Alice", "Bob", "Bob", "Bob", "Bob", "Charlie", "Charlie"],
        "Age": [25, 25, 25, 25, 30, 30, 30, 30, 20, 20]
    })

    result = get_duplicate_profile(df)

    assert result == {
        "total_rows": 10,
        "duplicate_count": 7,
        "duplicate_percentage": 70.0
    }

def test_missing_values():
    df = pd.DataFrame({
        "Name": ["Alice", "Alice", "Alice", None, None, None, None, None],
        "Age": [None, None, None, 30, 30, 30, None, None]
    })

    result = get_duplicate_profile(df)

    assert result == {
        "total_rows": 8,
        "duplicate_count": 5,
        "duplicate_percentage": 62.5
    }

def test_no_duplicates():
    df = pd.DataFrame({
        "Name": ["Alice", "Bob", "Charlie"],
        "Age": [25,30,35]
    })

    result = get_duplicate_profile(df)

    assert result == {
        "total_rows": 3,
        "duplicate_count": 0,
        "duplicate_percentage": 0.0
    }

def test_empty_dataframe():
    df = pd.DataFrame()

    result = get_duplicate_profile(df)

    assert result == {
        "total_rows": 0,
        "duplicate_count": 0,
        "duplicate_percentage": None
    }

def test_original_dataframe_unchanged():
    df = pd.DataFrame({
        "Name": ["Alice", "Bob", "Alice"],
        "Age": [25, 30, 25]
    })

    original_df = df.copy(deep=True)

    get_duplicate_profile(df)

    pd.testing.assert_frame_equal(df, original_df)