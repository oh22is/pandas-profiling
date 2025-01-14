from typing import Tuple

from pyspark.sql import DataFrame

from pandas_profiling.config import Settings
from pandas_profiling.model.schema import BooleanColumnResult
from pandas_profiling.model.summary_algorithms import describe_boolean_1d


@describe_boolean_1d.register
def describe_boolean_1d_spark(
    config: Settings, df: DataFrame, summary: dict
) -> Tuple[Settings, DataFrame, BooleanColumnResult]:
    """Describe a boolean series.

    Args:
        series: The Series to describe.
        summary: The dict containing the series description so far.

    Returns:
        A dict containing calculated series description values.
    """

    value_counts = summary["value_counts"]

    result = BooleanColumnResult()
    result.top = value_counts.index[0]
    result.freq = value_counts.iloc[0]

    return config, df, result
