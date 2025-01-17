from pandas_profiling.config import Settings
from pandas_profiling.report.presentation.frequency_table_utils import (
    extreme_obs_table,
    freq_table,
)


def render_common(config: Settings, summary: dict) -> dict:
    n_extreme_obs = config.n_extreme_obs
    n_freq_table_max = config.n_freq_table_max

    template_variables = {
        # TODO: with nan
        "freq_table_rows": freq_table(
            freqtable=summary["value_counts"],
            n=summary["n"],
            max_number_to_print=n_freq_table_max,
        ),
        "firstn_expanded": extreme_obs_table(
            freqtable=summary["values"],
            number_to_print=n_extreme_obs,
            n=summary["n"],
        ),
        "lastn_expanded": extreme_obs_table(
            freqtable=summary["values"][::-1],
            number_to_print=n_extreme_obs,
            n=summary["n"],
        ),
    }

    return template_variables
