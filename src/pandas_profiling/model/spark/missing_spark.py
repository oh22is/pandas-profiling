from pyspark.sql import DataFrame

from pandas_profiling.config import Settings
from pandas_profiling.model.missing import (
    missing_bar,
    missing_dendrogram,
    missing_heatmap,
    missing_matrix,
)
from pandas_profiling.visualisation.missing import (
    plot_missing_bar,
    plot_missing_dendrogram,
    plot_missing_heatmap,
    plot_missing_matrix,
)


class MissingnoBarSparkPatch:
    """
    Technical Debt :
    This is a monkey patching object that allows usage of the library missingno as is for spark dataframes.
    This is because missingno library's bar function always applies a isnull().sum() on dataframes in the visualisation
    function, instead of allowing just values counts as an entry point. Thus, in order to calculate the
    missing values dataframe in spark, we compute it first, then wrap it in this MissingnoBarSparkPatch object which
    will be unwrapped by missingno and return the pre-computed value counts.
    The best fix to this currently terrible patch is to submit a PR to missingno to separate preprocessing function
    (compute value counts from df) and visualisation functions such that we can call the visualisation directly.
    Unfortunately, the missingno library people have not really responded to our issues on gitlab.
    See https://github.com/ResidentMario/missingno/issues/119.
    We could also fork the missingno library and implement some of the code in our database, but that feels
    like bad practice as well.
    """

    def __init__(self, df, columns, original_df_size=None):
        self.df = df
        self.columns = columns
        self.original_df_size = original_df_size

    def isnull(self):
        """
        This patches the .isnull().sum() function called by missingno library
        """
        return self  # return self to patch .sum() function

    def sum(self):
        """
        This patches the .sum() function called by missingno library
        """
        return self.df  # return unwrapped dataframe

    def __len__(self):
        """
        This patches the len(df) function called by missingno library
        """
        return self.original_df_size


@missing_bar.register
def spark_missing_bar(config: Settings, df: DataFrame) -> str:
    import pyspark.sql.functions as F

    # FIXME: move to univariate
    data_nan_counts = (
        df.agg(
            *[F.count(F.when(F.isnull(c) | F.isnan(c), c)).alias(c) for c in df.columns]
        )
        .toPandas()
        .squeeze(axis="index")
    )

    return plot_missing_bar(
        config,
        MissingnoBarSparkPatch(
            df=data_nan_counts, columns=df.columns, original_df_size=df.count()
        ),
    )


@missing_matrix.register
def spark_missing_matrix(config: Settings, df: DataFrame) -> str:
    return plot_missing_matrix(config, MissingnoBarSparkPatch(df))


@missing_heatmap.register
def spark_missing_heatmap(config: Settings, df: DataFrame) -> str:
    return plot_missing_heatmap(config, MissingnoBarSparkPatch(df))


@missing_dendrogram.register
def spark_missing_dendrogram(config: Settings, df: DataFrame) -> str:
    return plot_missing_dendrogram(config, MissingnoBarSparkPatch(df))
