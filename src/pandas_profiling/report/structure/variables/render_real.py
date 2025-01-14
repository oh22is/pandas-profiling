from pandas_profiling.config import Settings
from pandas_profiling.report.formatters import (
    fmt,
    fmt_bytesize,
    fmt_monotonic,
    fmt_numeric,
    fmt_percent,
)
from pandas_profiling.report.presentation.core import (
    Container,
    FrequencyTable,
    Image,
    Table,
    VariableInfo,
)
from pandas_profiling.report.structure.variables.render_common import render_common
from pandas_profiling.visualisation.plot import histogram, mini_histogram


def render_real(config: Settings, summary: dict) -> dict:
    varid = summary["varid"]
    template_variables = render_common(config, summary)
    image_format = config.plot.image_format

    if summary["min"] >= 0:
        name = "Real number (&Ropf;<sub>&ge;0</sub>)"
    else:
        name = "Real number (&Ropf;)"

    # Top
    info = VariableInfo(
        summary["varid"],
        summary["varname"],
        name,
        summary["alerts"],
        summary["description"],
    )

    table1 = Table(
        [
            {
                "name": "Distinct",
                "value": fmt(summary["n_distinct"]),
                "alert": "n_distinct" in summary["alert_fields"],
            },
            {
                "name": "Distinct (%)",
                "value": fmt_percent(summary["p_distinct"]),
                "alert": "p_distinct" in summary["alert_fields"],
            },
            {
                "name": "Missing",
                "value": fmt(summary["n_missing"]),
                "alert": "n_missing" in summary["alert_fields"],
            },
            {
                "name": "Missing (%)",
                "value": fmt_percent(summary["p_missing"]),
                "alert": "p_missing" in summary["alert_fields"],
            },
            {
                "name": "Infinite",
                "value": fmt(summary["n_infinite"]),
                "alert": "n_infinite" in summary["alert_fields"],
            },
            {
                "name": "Infinite (%)",
                "value": fmt_percent(summary["p_infinite"]),
                "alert": "p_infinite" in summary["alert_fields"],
            },
            {
                "name": "Mean",
                "value": fmt_numeric(
                    summary["mean"], precision=config.report.precision
                ),
                "alert": False,
            },
        ]
    )

    res = [
        {
            "name": "Minimum",
            "value": fmt_numeric(summary["min"], precision=config.report.precision),
            "alert": False,
        },
        {
            "name": "Maximum",
            "value": fmt_numeric(summary["max"], precision=config.report.precision),
            "alert": False,
        },
        {
            "name": "Zeros",
            "value": fmt(summary["n_zeros"]),
            "alert": "n_zeros" in summary["alert_fields"],
        },
        {
            "name": "Zeros (%)",
            "value": fmt_percent(summary["p_zeros"]),
            "alert": "p_zeros" in summary["alert_fields"],
        },
        {
            "name": "Negative",
            "value": fmt(summary["n_negative"]),
            "alert": False,
        },
        {
            "name": "Negative (%)",
            "value": fmt_percent(summary["p_negative"]),
            "alert": False,
        },
    ]

    if summary["memory_size"] is not None:
        res.append(
            {
                "name": "Memory size",
                "value": fmt_bytesize(summary["memory_size"]),
                "alert": False,
            }
        )

    table2 = Table(res)

    mini_histo = Image(
        "",  # mini_histogram(config, *summary["histogram"]),
        image_format=image_format,
        alt="Mini histogram",
    )

    template_variables["top"] = Container(
        [info, table1, table2, mini_histo], sequence_type="grid"
    )

    quantile_statistics = Table(
        [
            {
                "name": "Minimum",
                "value": fmt_numeric(summary["min"], precision=config.report.precision),
            },
            {
                "name": "5-th percentile",
                "value": fmt_numeric(
                    summary["quantiles"]["5%"], precision=config.report.precision
                ),
            },
            {
                "name": "Q1",
                "value": fmt_numeric(
                    summary["quantiles"]["25%"], precision=config.report.precision
                ),
            },
            {
                "name": "median",
                "value": fmt_numeric(
                    summary["quantiles"]["50%"], precision=config.report.precision
                ),
            },
            {
                "name": "Q3",
                "value": fmt_numeric(
                    summary["quantiles"]["75%"], precision=config.report.precision
                ),
            },
            {
                "name": "95-th percentile",
                "value": fmt_numeric(
                    summary["quantiles"]["95%"], precision=config.report.precision
                ),
            },
            {
                "name": "Maximum",
                "value": fmt_numeric(summary["max"], precision=config.report.precision),
            },
            {
                "name": "Range",
                "value": fmt_numeric(
                    summary["range"], precision=config.report.precision
                ),
            },
            {
                "name": "Interquartile range (IQR)",
                "value": fmt_numeric(summary["iqr"], precision=config.report.precision),
            },
        ],
        name="Quantile statistics",
    )

    stats = [
        {
            "name": "Standard deviation",
            "value": fmt_numeric(summary["std"], precision=config.report.precision),
        },
        {
            "name": "Coefficient of variation (CV)",
            "value": fmt_numeric(summary["cv"], precision=config.report.precision),
        },
        {
            "name": "Mean",
            "value": fmt_numeric(summary["mean"], precision=config.report.precision),
        },
        {
            "name": "Median Absolute Deviation (MAD)",
            "value": fmt_numeric(summary["mad"], precision=config.report.precision),
        },
        {
            "name": "Sum",
            "value": fmt_numeric(summary["sum"], precision=config.report.precision),
        },
        {
            "name": "Variance",
            "value": fmt_numeric(
                summary["variance"], precision=config.report.precision
            ),
        },
    ]

    if summary["monotonic"] is not None:
        stats.append(
            {
                "name": "Monotonicity",
                "value": fmt_monotonic(summary["monotonic"]),
            }
        )

    if summary["kurtosis"] is not None:
        stats.append(
            {
                "name": "Kurtosis",
                "value": fmt_numeric(
                    summary["kurtosis"], precision=config.report.precision
                ),
            }
        )

    if summary["skewness"] is not None:
        stats.append(
            {
                "name": "Skewness",
                "value": fmt_numeric(
                    summary["skewness"], precision=config.report.precision
                ),
                "class": "alert" if "skewness" in summary["alert_fields"] else "",
            }
        )

    descriptive_statistics = Table(
        stats,
        name="Descriptive statistics",
    )

    statistics = Container(
        [quantile_statistics, descriptive_statistics],
        anchor_id=f"{varid}statistics",
        name="Statistics",
        sequence_type="grid",
    )

    hist = Image(
        "",  # histogram(config, *summary["histogram"]),
        image_format=image_format,
        alt="Histogram",
        caption="",  # f"<strong>Histogram with fixed size bins</strong> (bins={len(summary['histogram'][1]) - 1})",
        name="Histogram",
        anchor_id=f"{varid}histogram",
    )

    fq = FrequencyTable(
        template_variables["freq_table_rows"],
        name="Common values",
        anchor_id=f"{varid}common_values",
        redact=False,
    )

    evs = Container(
        [
            FrequencyTable(
                template_variables["firstn_expanded"],
                name=f"Minimum {config.n_extreme_obs} values",
                anchor_id=f"{varid}firstn",
                redact=False,
            ),
            FrequencyTable(
                template_variables["lastn_expanded"],
                name=f"Maximum {config.n_extreme_obs} values",
                anchor_id=f"{varid}lastn",
                redact=False,
            ),
        ],
        sequence_type="tabs",
        name="Extreme values",
        anchor_id=f"{varid}extreme_values",
    )

    template_variables["bottom"] = Container(
        [statistics, hist, fq, evs],
        sequence_type="tabs",
        anchor_id=f"{varid}bottom",
    )

    return template_variables
