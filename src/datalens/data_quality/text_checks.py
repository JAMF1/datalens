import pandas as pd 
import re 
from collections import Counter
from pandas.api.types import is_object_dtype, is_string_dtype

from datalens.data_quality.models import DetectionResult, AffectedValue, DetectionRule

LEADING_WHITESPACE_RULE: DetectionRule = {
    "rule_id": "TEXT-WHITESPACE-001",
    "category": "text_formatting",
    "issue_type": "leading_whitespace",
    "detection_type": "deterministic",
    "description": "Leading whitespace detected.",
    "recommendation": "Remove unnecessary leading whitespace."
    }

TRAILING_WHITESPACE_RULE: DetectionRule = {
    "rule_id": "TEXT-WHITESPACE-002",
    "category": "text_formatting",
    "issue_type": "trailing_whitespace",
    "detection_type": "deterministic",
    "description": "Trailing whitespace detected.",
    "recommendation": "Remove unnecessary trailing whitespace."
    }
REPEATING_WHITESPACE_RULE: DetectionRule = {
    "rule_id": "TEXT-WHITESPACE-003",
    "category": "text_formatting",
    "issue_type": "repeated_whitespace",
    "detection_type": "deterministic",
    "description": "Repeated consecutive whitespace detected.",
    "recommendation": "Replace unnecesary consecutive whitespace with a single whitespace character"
    }

WHITESPACE_ONLY_RULE: DetectionRule = {
    "rule_id": "TEXT-WHITESPACE-004",
    "category": "text_formatting",
    "issue_type": "whitespace_only",
    "detection_type": "deterministic",
    "description": "Whitespace-only strings detected.",
    "recommendation": "Remove whitespace-only values or replace them with appropriate missing values."
    }

INCONSISTENT_CAPITALIZATION_RULE: DetectionRule = {
    "rule_id": "TEXT-CAPITALIZATION-001",
    "category": "text_formatting",
    "issue_type": "inconsistent_capitalization",
    "detection_type": "deterministic",
    "description": "Inconsistent capitalization detected.",
    "recommendation": "Standardize capitalization across equivalent text values."
    }

def _is_text_column(column: pd.Series) -> bool:
    return (is_object_dtype(column.dtype) or is_string_dtype(column.dtype))

def _build_text_detection_results(column: pd.Series, column_position: int, affected_values: list[str], rule: DetectionRule) -> DetectionResult:
    counts = Counter(affected_values)
    affected_value_details: list[AffectedValue] = [
        {"value": value, "count": count} 
        for value, count in counts.items()
        ]
    affected_count = sum(counts.values())
    distinct_value_count = len(counts)

    detection_results = DetectionResult(
        rule_id=rule["rule_id"],
        category=rule["category"],
        issue_type=rule["issue_type"],
        column=column.name,
        column_position=column_position,
        detection_type=rule["detection_type"],
        description=rule["description"],
        recommendation=rule["recommendation"],
        affected_count=affected_count,
        affected_unit="cells",
        distinct_value_count=distinct_value_count,
        affected_values=affected_value_details)
    return detection_results

def find_leading_whitespace(dataframe: pd.DataFrame) -> list[DetectionResult]:
    findings = []

    for position in range(len(dataframe.columns)):
        column = dataframe.iloc[:, position]

        if not _is_text_column(column):
            continue

        affected_values = []

        for value in column:
            if not isinstance(value, str):
                continue
            if value.lstrip() != value:
                affected_values.append(value)

        if affected_values:
            finding = _build_text_detection_results(
                column=column,
                column_position=position,
                affected_values=affected_values,
                rule=LEADING_WHITESPACE_RULE
                )

            findings.append(finding)

    return findings

def find_trailing_whitespace(dataframe: pd.DataFrame) -> list[DetectionResult]:
    findings = []

    for position in range(len(dataframe.columns)):
        column = dataframe.iloc[:, position]

        if not _is_text_column(column):
            continue

        affected_values = []

        for value in column:
            if not isinstance(value, str):
                continue

            if value.rstrip() != value:
                affected_values.append(value)

        if affected_values:
            finding = _build_text_detection_results(
                column=column,
                column_position=position,
                affected_values=affected_values,
                rule=TRAILING_WHITESPACE_RULE
                )

            findings.append(finding)

    return findings

def find_repeated_whitespace(dataframe: pd.DataFrame) -> list[DetectionResult]:
    findings = []

    for position in range(len(dataframe.columns)):
        column = dataframe.iloc[:, position]

        if not _is_text_column(column):
            continue

        affected_values = []

        for value in column:
            if not isinstance(value, str):
                continue

            if re.search(r"\s{2,}", value):
                affected_values.append(value)

        if affected_values:
            finding = _build_text_detection_results(
                column=column,
                column_position=position,
                affected_values=affected_values,
                rule=REPEATING_WHITESPACE_RULE
                )

            findings.append(finding)

    return findings

def find_whitespace_only_strings(dataframe: pd.DataFrame) -> list[DetectionResult]:
    findings = []

    for position in range(len(dataframe.columns)):
        column = dataframe.iloc[:, position]

        if not _is_text_column(column):
            continue

        affected_values = []

        for value in column:
            if not isinstance(value, str):
                continue

            if not value.isspace():
                continue
            
            if value.strip() != value:
                affected_values.append(value)

        if affected_values:
            finding = _build_text_detection_results(
                column=column,
                column_position=position,
                affected_values=affected_values,
                rule=WHITESPACE_ONLY_RULE
                )

            findings.append(finding)

    return findings

def find_inconsistent_capitalization(dataframe: pd.DataFrame) -> list[DetectionResult]:
    findings = []

    for position in range(len(dataframe.columns)):
        column = dataframe.iloc[:, position]

        if not _is_text_column(column):
            continue

        affected_values = []
        groupings = {}

        for value in column:
            if not isinstance(value, str):
                continue
            if value.isspace():
                continue
            
            lower_case_version = value.lower()
            if lower_case_version not in groupings:
                groupings[lower_case_version] = [value]
            else:
                groupings[lower_case_version].append(value)

        for group in groupings.values():
            if len(group) == 1: 
                continue
            elif len(set(group)) == 1:
                continue
            else: 
                affected_values.extend(group)

        if affected_values:
            finding = _build_text_detection_results(
                column=column,
                column_position=position,
                affected_values=affected_values,
                rule=INCONSISTENT_CAPITALIZATION_RULE
                )

            findings.append(finding)

    return findings
