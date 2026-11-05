import pandas as pd 
from collections import Counter
from pandas.api.types import is_object_dtype, is_string_dtype

from datalens.data_quality.models import DetectionResult


def find_leading_whitespace(dataframe: pd.DataFrame) -> list[DetectionResult]:
    findings = []

    for position in range(len(dataframe.columns)):
        column = dataframe.iloc[:, position]

        if not is_object_dtype(column.dtype) or is_string_dtype(column.dtype):
            continue

        affected_values = []

        for value in column:
            if pd.isna(value):
                continue
            if value.lstrip() != value:
                affected_values.append

        if affected_values:
            counts = Counter(affected_values)
            

        # statistics.append({
        #     "position": position,
        #     "name": dataframe.columns[position],
        #     "data_type": str(column.dtype),
        #     "statistics": clean_summary,
        # })

    return findings