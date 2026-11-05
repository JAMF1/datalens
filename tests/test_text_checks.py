import pandas as pd 
from datalens.data_quality.text_checks import find_leading_whitespace

def test_leading_whitespace():
    df = pd.DataFrame({
        "Country": [" Mexico", "Canada", " Japan"]
        })
    results = find_leading_whitespace(df)

    assert len(results) == 1 
    assert results[0]["rule_id"] == "TEXT-WHITESPACE-001"
    assert results[0]["column"] == "Country"
    assert results[0]["affected_count"] == 2 
    assert results[0]["distinct_value_count"] == 2
    assert results[0]["affected_values"][0]["value"] == " Mexico"
    assert results[0]["affected_values"][1]["value"] == " Japan" 

def test_repeated_leading_whitespace():
    df = pd.DataFrame({
        "Country": [" Mexico", " Mexico", "Canada", " Japan"]
        })
    results = find_leading_whitespace(df)

    assert len(results) == 1 
    assert results[0]["rule_id"] == "TEXT-WHITESPACE-001"
    assert results[0]["column"] == "Country"
    assert results[0]["affected_count"] == 3 
    assert results[0]["distinct_value_count"] == 2

    assert results[0]["affected_values"] == [
    {"value": " Mexico", "count": 2},
    {"value": " Japan", "count": 1}
    ]

def test_multiple_columns_with_whitespace():
    df = pd.DataFrame({
        "Country": [" Mexico", "Canada", " Mexico", None, "Japan"],
        "Name": [" Alice", "Bob", "Charlie", "David", "Eva"]
        })

    results = find_leading_whitespace(df)

    assert len(results) == 2
    assert results[0]["column"] == "Country"
    assert results[0]["column_position"] == 0
    assert results[0]["affected_count"] == 2
    assert results[0]["distinct_value_count"] == 1

    assert results[1]["column"] == "Name"
    assert results[1]["column_position"] == 1
    assert results[1]["affected_count"] == 1
    assert results[1]["distinct_value_count"] == 1 

def test_ignore_non_string_values():
    df = pd.DataFrame({
        "Mixed": [" Mexico", 25, None, 3.14, "Canada"]
        })

    results = find_leading_whitespace(df) 

    assert len(results) == 1 
    assert results[0]["rule_id"] == "TEXT-WHITESPACE-001"
    assert results[0]["column"] == "Mixed"
    assert results[0]["affected_count"] == 1
    assert results[0]["distinct_value_count"] == 1
    assert results[0]["affected_values"][0]["value"] == " Mexico"
    assert results[0]["affected_values"][0]["count"] == 1

def test_ignore_non_text_columns():
    df = pd.DataFrame({
        "Age": [25, 30, 35],
        "Score": [90.5, 85.0, 92.0]
        })

    results = find_leading_whitespace(df) 

    assert results == [] 

def test_empty_dataframe():
    df = pd.DataFrame()

    results = find_leading_whitespace(df)

    assert results == []

def test_original_dataframe_unchanged():
    df = pd.DataFrame({
        "Country": [" Mexico", "Canada", " Japan"]
        })

    original_df = df.copy(deep=True)

    find_leading_whitespace(df)

    pd.testing.assert_frame_equal(df, original_df)

def test_no_leading_whitespace():
    df = pd.DataFrame({
        "Country": ["Mexico", "Canada", "Mexico", None, "Japan"],
        "Name": ["Alice", "Bob", "Charlie", "David", "Eva"]
        })

    results = find_leading_whitespace(df)

    assert results == [] 

def test_duplicate_column_names():
    df = pd.DataFrame(
        [[" Mexico", " Canada"]],
        columns=["Country", "Country"]
        )

    results = find_leading_whitespace(df) 

    assert len(results) == 2

    assert results[0]["column"] == "Country"
    assert results[0]["column_position"] == 0
    assert results[0]["affected_count"] == 1 
    assert results[0]["affected_values"][0]["value"] == " Mexico"

    assert results[1]["column"] == "Country"
    assert results[1]["column_position"] == 1 
    assert results[1]["affected_count"] == 1 
    assert results[1]["affected_values"][0]["value"] == " Canada"