from typing import Optional, Sequence, Tuple

import pandas as pd

from pandas_profiling.config import Settings
from pandas_profiling.model.duplicates import get_duplicates
from pandas_profiling.model.schema import DuplicateResult


@get_duplicates.register(Settings, pd.DataFrame, Sequence)
def pandas_get_duplicates(
    config: Settings, df: pd.DataFrame, supported_columns: Sequence
) -> Tuple[DuplicateResult, Optional[pd.DataFrame]]:
    """Obtain the most occurring duplicate rows in the DataFrame.

    Args:
        config: report Settings object
        df: the Pandas DataFrame.
        supported_columns: the columns to consider

    Returns:
        A subset of the DataFrame, ordered by occurrence.
    """
    n_head = config.duplicates.head

    metrics = DuplicateResult()
    if n_head == 0:
        return metrics, None

    if not supported_columns or len(df) == 0:
        metrics.n_duplicates = 0
        metrics.p_duplicates = 0.0
        return metrics, None

    duplicates_key = config.duplicates.key
    if duplicates_key in df.columns:
        raise ValueError(
            f"Duplicates key ({duplicates_key}) may not be part of the DataFrame. Either change the "
            f" column name in the DataFrame or change the 'duplicates.key' parameter."
        )

    duplicated_rows = df.duplicated(subset=supported_columns, keep=False)
    duplicated_rows = (
        df[duplicated_rows]
        .groupby(supported_columns)
        .size()
        .reset_index(name=duplicates_key)
    )

    metrics.n_duplicates = len(duplicated_rows[duplicates_key])
    metrics.p_duplicates = metrics.n_duplicates / len(df)

    return (
        metrics,
        duplicated_rows.nlargest(n_head, duplicates_key),
    )
