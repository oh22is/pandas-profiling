from typing import Tuple

import numpy as np
import pyspark.sql.functions as F
from pyspark.sql import DataFrame

from pandas_profiling.config import Settings
from pandas_profiling.model.schema import NumericColumnResult
from pandas_profiling.model.summary_algorithms import describe_numeric_1d


def numeric_stats_spark(df: DataFrame, summary: dict) -> dict:
    column = df.columns[0]

    expr = [
        F.mean(F.col(column)).alias("mean"),
        F.stddev(F.col(column)).alias("std"),
        F.variance(F.col(column)).alias("variance"),
        F.min(F.col(column)).alias("min"),
        F.max(F.col(column)).alias("max"),
        F.kurtosis(F.col(column)).alias("kurtosis"),
        F.skewness(F.col(column)).alias("skewness"),
        F.sum(F.col(column)).alias("sum"),
    ]
    return df.agg(*expr).first().asDict()


@describe_numeric_1d.register
def describe_numeric_1d_spark(
    config: Settings, df: DataFrame, summary: dict
) -> Tuple[Settings, DataFrame, NumericColumnResult]:
    """Describe a boolean series.

    Args:
        series: The Series to describe.
        summary: The dict containing the series description so far.

    Returns:
        A dict containing calculated series description values.
    """

    result = NumericColumnResult()

    stats = numeric_stats_spark(df, summary)
    # summary.update(numeric_stats)
    result.min = stats["min"]
    result.max = stats["max"]
    result.mean = stats["mean"]
    result.std = stats["std"]
    result.variance = stats["variance"]
    result.skewness = stats["skewness"]
    result.kurtosis = stats["kurtosis"]
    result.sum = stats["sum"]

    value_counts = summary["describe_counts"].value_counts

    n_infinite = (
        value_counts.where(F.col(df.columns[0]).isin([np.inf, -np.inf]))
        .agg(F.sum(F.col("count")).alias("count"))
        .first()
    )
    if n_infinite is None or n_infinite["count"] is None:
        n_infinite = 0
    else:
        n_infinite = n_infinite["count"]
    result.n_infinite = n_infinite

    n_zeros = value_counts.where(f"{df.columns[0]} = 0").first()
    if n_zeros is None:
        n_zeros = 0
    else:
        n_zeros = n_zeros["count"]
    result.n_zeros = n_zeros

    n_negative = (
        value_counts.where(f"{df.columns[0]} < 0")
        .agg(F.sum(F.col("count")).alias("count"))
        .first()
    )
    if n_negative is None or n_negative["count"] is None:
        n_negative = 0
    else:
        n_negative = n_negative["count"]
    result.n_negative = n_negative

    quantiles = config.vars.num.quantiles
    quantile_threshold = 0.05

    result.quantiles = {
        f"{percentile:.0%}": value
        for percentile, value in zip(
            quantiles,
            df.stat.approxQuantile(
                f"{df.columns[0]}",
                quantiles,
                quantile_threshold,
            ),
        )
    }

    median = result.quantiles["50%"]

    result.mad = df.select(
        (F.abs(F.col(f"{df.columns[0]}").cast("int") - median)).alias("abs_dev")
    ).stat.approxQuantile("abs_dev", [0.5], quantile_threshold)[0]

    # FIXME: move to fmt
    result.p_negative = result.n_negative / summary["describe_generic"].n
    result.range = result.max - result.min
    result.iqr = result.quantiles["75%"] - result.quantiles["25%"]
    result.cv = result.std / result.mean if result.mean else np.NaN
    result.p_zeros = result.n_zeros / summary["describe_generic"].n
    result.p_infinite = result.n_infinite / summary["describe_generic"].n

    # TODO - enable this feature
    # because spark doesn't have an indexing system, there isn't really the idea of monotonic increase/decrease
    # [feature enhancement] we could implement this if the user provides an ordinal column to use for ordering
    # ... https://stackoverflow.com/questions/60221841/how-to-detect-monotonic-decrease-in-pyspark
    # summary["monotonic"] =

    # this function only displays the top N (see config) values for a histogram.
    # This might be confusing if there are a lot of values of equal magnitude, but we cannot bring all the values to
    # display in pandas display
    # the alternative is to do this in spark natively, but it is not trivial
    # summary.update(
    #     histogram_compute(
    #         value_counts.index.values,
    #         summary["n_distinct"],
    #         weights=value_counts.values,
    #     )
    # )

    # buckets = config.plot.histogram.bins
    # if not isinstance(buckets, int):
    #     buckets = 50
    # print('histogram', value_counts.rdd.values().histogram(buckets=None))

    return config, df, result
