from typing import Any, Literal, TypedDict

class AffectedValue(TypedDict):
    value: Any
    count: int

class DetectionResult(TypedDict):
    rule_id: str
    category: str
    issue_type: str 
    column: Any
    column_position: int 
    detection_type: Literal["deterministic", "heuristic"]
    description: str 
    recommendation: str 
    affected_count: int 
    affected_unit: Literal["cells", "records"]
    distinct_value_count: int 
    affected_values: list[AffectedValue]

class DataQualityFinding(DetectionResult):
    issue_id: str 

class DatasetQualitySummary(TypedDict):
    total_rows: int
    total_columns: int
    total_findings: int
    total_suggestions: int 

class DataQualityReport(TypedDict):
    dataset_summary: DatasetQualitySummary
    deterministic_findings: list[DataQualityFinding]
    heuristic_suggestions: list[DataQualityFinding]

class DetectionRule(TypedDict):
    rule_id: str
    category: str
    issue_type: str
    detection_type: Literal["deterministic", "heuristic"]
    description: str
    recommendation: str

class CategoricalColumnProfile(TypedDict):
    column: Any
    column_position: int
    data_type: str
    unique_count: int
    non_missing_count: int
    unique_ratio: float | None
    automatic_suggestion: bool
    user_selected: bool
    is_categorical: bool