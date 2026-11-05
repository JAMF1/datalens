import pandas as pd 
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

def find_leading_whitespace(dataframe: pd.DataFrame) -> list[DetectionResult]:
    findings = []

    for position in range(len(dataframe.columns)):
        column = dataframe.iloc[:, position]

        if not (is_object_dtype(column.dtype) or is_string_dtype(column.dtype)):
            continue

        affected_values = []

        for value in column:
            if not isinstance(value, str):
                continue
            if value.lstrip() != value:
                affected_values.append(value)

        if affected_values:
            counts = Counter(affected_values)
        
            affected_value_details: list[AffectedValue] = [
                {"value": value, "count": count} 
                for value, count in counts.items()
            ]
            affected_count = sum(counts.values())
            distinct_value_count = len(counts)

            detection_results = DetectionResult(rule_id=LEADING_WHITESPACE_RULE["rule_id"],
                                    category=LEADING_WHITESPACE_RULE["category"],
                                    issue_type=LEADING_WHITESPACE_RULE["issue_type"],
                                    column=column.name,
                                    column_position=position,
                                    detection_type=LEADING_WHITESPACE_RULE["detection_type"],
                                    description=LEADING_WHITESPACE_RULE["description"],
                                    recommendation=LEADING_WHITESPACE_RULE["recommendation"],
                                    affected_count=affected_count,
                                    affected_unit="cells",
                                    distinct_value_count=distinct_value_count,
                                    affected_values=affected_value_details
                                    )
            findings.append(detection_results)

    return findings
