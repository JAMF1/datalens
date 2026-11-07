import pandas as pd 
from datalens.data_quality.text_checks import (
    find_leading_whitespace, 
    find_trailing_whitespace, 
    find_repeated_whitespace, 
    find_whitespace_only_strings,
    find_inconsistent_capitalization
    )

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
    results_trailing = find_trailing_whitespace(df)

    assert results == [] 
    assert results_trailing == []

def test_empty_dataframe():
    df = pd.DataFrame()

    results = find_leading_whitespace(df)
    results_trailing = find_trailing_whitespace(df)

    assert results == []
    assert results_trailing == []

def test_original_dataframe_unchanged():
    df = pd.DataFrame({
        "Country": [" Mexico", "Canada", " Japan"]
        })

    original_df = df.copy(deep=True)

    find_leading_whitespace(df)

    pd.testing.assert_frame_equal(df, original_df)
    

def test_no_leading_whitespace():
    df = pd.DataFrame({
        "Country": ["Mexico", "Canada", "Mexico ", None, "Japan"],
        "Name": ["Alice", "Bob", "Charlie ", "David", "Eva"]
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

    ###################
def test_trailing_whitespace():
    df = pd.DataFrame({
        "Country": ["Mexico ", "Canada", "Japan "]
        })
    results = find_trailing_whitespace(df)

    assert len(results) == 1 
    assert results[0]["rule_id"] == "TEXT-WHITESPACE-002"
    assert results[0]["column"] == "Country"
    assert results[0]["affected_count"] == 2 
    assert results[0]["distinct_value_count"] == 2
    assert results[0]["affected_values"][0]["value"] == "Mexico "
    assert results[0]["affected_values"][1]["value"] == "Japan " 

def test_repeated_trailing_whitespace():
    df = pd.DataFrame({
        "Country": ["Mexico ", "Mexico ", "Canada", "Japan "]
        })
    results = find_trailing_whitespace(df)

    assert len(results) == 1 
    assert results[0]["rule_id"] == "TEXT-WHITESPACE-002"
    assert results[0]["column"] == "Country"
    assert results[0]["affected_count"] == 3 
    assert results[0]["distinct_value_count"] == 2

    assert results[0]["affected_values"] == [
    {"value": "Mexico ", "count": 2},
    {"value": "Japan ", "count": 1}
    ]

def test_multiple_columns_with_trailing_whitespace():
    df = pd.DataFrame({
        "Country": ["Mexico ", "Canada", "Mexico ", None, "Japan"],
        "Name": ["Alice ", "Bob", "Charlie", "David", "Eva"]
        })

    results = find_trailing_whitespace(df)

    assert len(results) == 2
    assert results[0]["column"] == "Country"
    assert results[0]["column_position"] == 0
    assert results[0]["affected_count"] == 2
    assert results[0]["distinct_value_count"] == 1

    assert results[1]["column"] == "Name"
    assert results[1]["column_position"] == 1
    assert results[1]["affected_count"] == 1
    assert results[1]["distinct_value_count"] == 1 

def test_ignore_non_string_values_trailing():
    df = pd.DataFrame({
        "Mixed": ["Mexico ", 25, None, 3.14, "Canada"]
        })

    results = find_trailing_whitespace(df) 

    assert len(results) == 1 
    assert results[0]["rule_id"] == "TEXT-WHITESPACE-002"
    assert results[0]["column"] == "Mixed"
    assert results[0]["affected_count"] == 1
    assert results[0]["distinct_value_count"] == 1
    assert results[0]["affected_values"][0]["value"] == "Mexico "
    assert results[0]["affected_values"][0]["count"] == 1


def test_no_trailing_whitespace():
    df = pd.DataFrame({
        "Country": [" Mexico", "Canada", " Mexico", None, "Japan"],
        "Name": ["Alice", " Bob", "Charlie", "David", "Eva"]
        })

    results = find_trailing_whitespace(df)

    assert results == [] 

def test_duplicate_trailing_column_names():
    df = pd.DataFrame(
        [["Mexico ", "Canada "]],
        columns=["Country", "Country"]
        )

    results = find_trailing_whitespace(df) 

    assert len(results) == 2

    assert results[0]["column"] == "Country"
    assert results[0]["column_position"] == 0
    assert results[0]["affected_count"] == 1 
    assert results[0]["affected_values"][0]["value"] == "Mexico "

    assert results[1]["column"] == "Country"
    assert results[1]["column_position"] == 1 
    assert results[1]["affected_count"] == 1 
    assert results[1]["affected_values"][0]["value"] == "Canada "

 #######
def test_find_repeated_whitespace():
    df = pd.DataFrame({
        "name": ["John  Smith", "Alice", "Robert   Brown"]
    })

    result = find_repeated_whitespace(df)

    assert len(result) == 1
    assert result[0]["issue_type"] == "repeated_whitespace"
    assert result[0]["affected_count"] == 2
    assert result[0]["distinct_value_count"] == 2
    assert result[0]["affected_values"] == [
        {"value": "John  Smith", "count": 1},
        {"value": "Robert   Brown", "count": 1}
    ]


def test_find_repeated_whitespace_counts_repeated_values():
    df = pd.DataFrame({
        "name": ["John  Smith", "John  Smith", "Robert   Brown"]
    })

    result = find_repeated_whitespace(df)

    assert result[0]["affected_count"] == 3
    assert result[0]["distinct_value_count"] == 2
    assert result[0]["affected_values"] == [
        {"value": "John  Smith", "count": 2},
        {"value": "Robert   Brown", "count": 1}
    ]


def test_find_repeated_whitespace_multiple_columns():
    dataframe = pd.DataFrame({
        "first_name": ["John  Smith", "Alice"],
        "last_name": ["Brown", "Robert   Jones"]
    })

    result = find_repeated_whitespace(dataframe)

    assert len(result) == 2
    assert [finding["column_position"] for finding in result] == [0, 1]


def test_find_repeated_whitespace_tabs_and_newlines():
    dataframe = pd.DataFrame({
        "text": ["John\t\tSmith", "Alice\n\nBrown", "Robert Smith"]
    })

    result = find_repeated_whitespace(dataframe)

    assert result[0]["affected_count"] == 2
    assert result[0]["affected_values"] == [
        {"value": "John\t\tSmith", "count": 1},
        {"value": "Alice\n\nBrown", "count": 1}
    ]


def test_find_repeated_whitespace_mixed_types():
    dataframe = pd.DataFrame({
        "mixed": ["John  Smith", 123, None, True, "Alice"]
    })

    result = find_repeated_whitespace(dataframe)

    assert result[0]["affected_count"] == 1
    assert result[0]["affected_values"] == [
        {"value": "John  Smith", "count": 1}
    ]


def test_find_repeated_whitespace_empty_dataframe():
    dataframe = pd.DataFrame()

    result = find_repeated_whitespace(dataframe)

    assert result == []


def test_find_repeated_whitespace_does_not_modify_dataframe():
    dataframe = pd.DataFrame({
        "name": ["John  Smith", "Alice"]
    })
    original_dataframe = dataframe.copy(deep=True)

    find_repeated_whitespace(dataframe)

    pd.testing.assert_frame_equal(dataframe, original_dataframe)


def test_find_repeated_whitespace_duplicate_column_names():
    dataframe = pd.DataFrame(
        [["John  Smith", "Alice"], ["Robert", "Jane   Doe"]],
        columns=["name", "name"]
    )

    result = find_repeated_whitespace(dataframe)

    assert len(result) == 2
    assert [finding["column_position"] for finding in result] == [0, 1]


def test_find_repeated_whitespace_no_matches():
    dataframe = pd.DataFrame({
        "name": ["John Smith", "Alice", "Robert Brown"]
    })

    result = find_repeated_whitespace(dataframe)

    assert result == []


def test_find_repeated_whitespace_pandas_string_dtype():
    dataframe = pd.DataFrame({
        "name": pd.Series(["John  Smith", "Alice"], dtype="string")
    })

    result = find_repeated_whitespace(dataframe)

    assert result[0]["affected_count"] == 1
    assert result[0]["affected_values"] == [
        {"value": "John  Smith", "count": 1}
    ]


###WHITESPACE ONLY####
def test_find_whitespace_only_strings():
    dataframe = pd.DataFrame({
        "name": ["Alice", "   ", "Bob", "\t", "   "]
    })

    result = find_whitespace_only_strings(dataframe)

    assert len(result) == 1
    assert result[0]["issue_type"] == "whitespace_only"
    assert result[0]["affected_count"] == 3
    assert result[0]["distinct_value_count"] == 2
    assert result[0]["affected_values"] == [
        {"value": "   ", "count": 2},
        {"value": "\t", "count": 1}
    ]


def test_find_whitespace_only_strings_multiple_whitespace_characters():
    dataframe = pd.DataFrame({
        "text": ["   ", "\t", "\n", "\t\n", "  Alice  "]
    })

    result = find_whitespace_only_strings(dataframe)

    assert result[0]["affected_count"] == 4
    assert result[0]["distinct_value_count"] == 4


def test_find_whitespace_only_strings_multiple_columns():
    dataframe = pd.DataFrame({
        "first_name": ["Alice", "   "],
        "last_name": ["\t", "Brown"]
    })

    result = find_whitespace_only_strings(dataframe)

    assert len(result) == 2
    assert [finding["column_position"] for finding in result] == [0, 1]


def test_find_whitespace_only_strings_mixed_types():
    dataframe = pd.DataFrame({
        "mixed": ["   ", 123, None, True, "Alice", "\t"]
    })

    result = find_whitespace_only_strings(dataframe)

    assert result[0]["affected_count"] == 2
    assert result[0]["affected_values"] == [
        {"value": "   ", "count": 1},
        {"value": "\t", "count": 1}
    ]


def test_find_whitespace_only_strings_empty_dataframe():
    dataframe = pd.DataFrame()

    result = find_whitespace_only_strings(dataframe)

    assert result == []


def test_find_whitespace_only_strings_does_not_modify_dataframe():
    dataframe = pd.DataFrame({
        "name": ["Alice", "   ", "Bob"]
    })
    original_dataframe = dataframe.copy(deep=True)

    find_whitespace_only_strings(dataframe)

    pd.testing.assert_frame_equal(dataframe, original_dataframe)


def test_find_whitespace_only_strings_duplicate_column_names():
    dataframe = pd.DataFrame(
        [["   ", "Alice"], ["Bob", "\t"]],
        columns=["name", "name"]
    )

    result = find_whitespace_only_strings(dataframe)

    assert len(result) == 2
    assert [finding["column_position"] for finding in result] == [0, 1]


def test_find_whitespace_only_strings_no_matches():
    dataframe = pd.DataFrame({
        "name": ["Alice", "Bob", "", "   Alice   "]
    })

    result = find_whitespace_only_strings(dataframe)

    assert result == []


def test_find_whitespace_only_strings_pandas_string_dtype():
    dataframe = pd.DataFrame({
        "name": pd.Series(["Alice", "   ", "\t"], dtype="string")
    })

    result = find_whitespace_only_strings(dataframe)

    assert result[0]["affected_count"] == 2
    assert result[0]["affected_values"] == [
        {"value": "   ", "count": 1},
        {"value": "\t", "count": 1}
    ]


def test_find_whitespace_only_strings_does_not_detect_empty_strings():
    dataframe = pd.DataFrame({
        "name": ["", "Alice", ""]
    })

    result = find_whitespace_only_strings(dataframe)

    assert result == []

####INCONSISTEN CAPITALIZATION####
def test_find_inconsistent_capitalization():
    dataframe = pd.DataFrame({
        "fruit": ["Apple", "apple", "APPLE", "Banana", "apple"]
    })

    result = find_inconsistent_capitalization(dataframe)

    assert len(result) == 1
    assert result[0]["issue_type"] == "inconsistent_capitalization"
    assert result[0]["affected_count"] == 4
    assert result[0]["distinct_value_count"] == 3
    assert result[0]["affected_values"] == [
        {"value": "Apple", "count": 1},
        {"value": "apple", "count": 2},
        {"value": "APPLE", "count": 1}
    ]


def test_find_inconsistent_capitalization_multiple_groups():
    dataframe = pd.DataFrame({
        "fruit": ["Apple", "APPLE", "Banana", "BANANA", "Orange"]
    })

    result = find_inconsistent_capitalization(dataframe)

    assert result[0]["affected_count"] == 4
    assert result[0]["distinct_value_count"] == 4
    assert result[0]["affected_values"] == [
        {"value": "Apple", "count": 1},
        {"value": "APPLE", "count": 1},
        {"value": "Banana", "count": 1},
        {"value": "BANANA", "count": 1}
    ]


def test_find_inconsistent_capitalization_multiple_columns():
    dataframe = pd.DataFrame({
        "fruit": ["Apple", "APPLE"],
        "city": ["London", "london"]
    })

    result = find_inconsistent_capitalization(dataframe)

    assert len(result) == 2
    assert [finding["column_position"] for finding in result] == [0, 1]


def test_find_inconsistent_capitalization_mixed_types():
    dataframe = pd.DataFrame({
        "mixed": ["Apple", "APPLE", 123, None, True, "Banana"]
    })

    result = find_inconsistent_capitalization(dataframe)

    assert result[0]["affected_count"] == 2
    assert result[0]["affected_values"] == [
        {"value": "Apple", "count": 1},
        {"value": "APPLE", "count": 1}
    ]


def test_find_inconsistent_capitalization_empty_dataframe():
    dataframe = pd.DataFrame()

    result = find_inconsistent_capitalization(dataframe)

    assert result == []


def test_find_inconsistent_capitalization_does_not_modify_dataframe():
    dataframe = pd.DataFrame({
        "fruit": ["Apple", "APPLE", "Banana"]
    })
    original_dataframe = dataframe.copy(deep=True)

    find_inconsistent_capitalization(dataframe)

    pd.testing.assert_frame_equal(dataframe, original_dataframe)


def test_find_inconsistent_capitalization_duplicate_column_names():
    dataframe = pd.DataFrame(
        [["Apple", "London"], ["APPLE", "london"]],
        columns=["value", "value"]
    )

    result = find_inconsistent_capitalization(dataframe)

    assert len(result) == 2
    assert [finding["column_position"] for finding in result] == [0, 1]


def test_find_inconsistent_capitalization_no_matches():
    dataframe = pd.DataFrame({
        "fruit": ["Apple", "Banana", "Orange"]
    })

    result = find_inconsistent_capitalization(dataframe)

    assert result == []


def test_find_inconsistent_capitalization_pandas_string_dtype():
    dataframe = pd.DataFrame({
        "fruit": pd.Series(["Apple", "APPLE", "Banana"], dtype="string")
    })

    result = find_inconsistent_capitalization(dataframe)

    assert result[0]["affected_count"] == 2
    assert result[0]["affected_values"] == [
        {"value": "Apple", "count": 1},
        {"value": "APPLE", "count": 1}
    ]


def test_find_inconsistent_capitalization_ignores_whitespace_only_strings():
    dataframe = pd.DataFrame({
        "text": ["   ", "APPLE", "apple", "\t"]
    })

    result = find_inconsistent_capitalization(dataframe)

    assert result[0]["affected_count"] == 2
    assert result[0]["affected_values"] == [
        {"value": "APPLE", "count": 1},
        {"value": "apple", "count": 1}
    ]


def test_find_inconsistent_capitalization_ignores_identical_repeated_values():
    dataframe = pd.DataFrame({
        "fruit": ["Apple", "Apple", "Banana", "Banana"]
    })

    result = find_inconsistent_capitalization(dataframe)

    assert result == []
