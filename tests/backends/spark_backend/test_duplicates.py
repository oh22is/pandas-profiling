import pandas as pd
import pytest

from pandas_profiling.config import Settings
from pandas_profiling.model.spark.duplicates_spark import spark_get_duplicates


@pytest.fixture
def duplicates_data(spark_session):
    correlation_testdata = pd.DataFrame(
        {
            "test_num_1": [1, 2, 3, 5, 7, 8, 9, 1],
            "test_num_2": [11, 12, 13, 15, 17, 18, 4, 11],
        }
    )

    return spark_session.createDataFrame(correlation_testdata)


def test_spark_get_duplicates_disabled(duplicates_data):
    cfg = Settings()
    cfg.duplicates.head = 0

    stats, df = spark_get_duplicates(cfg, duplicates_data, duplicates_data.columns)
    assert stats.n_duplicates is None
    assert df is None


def test_spark_get_duplicates(duplicates_data):
    cfg = Settings()
    cfg.duplicates.head = 3
    cfg.duplicates.key = "my_name"

    stats, df = spark_get_duplicates(cfg, duplicates_data, duplicates_data.columns)
    assert stats.n_duplicates == 1
    assert df.head(1)["my_name"][0] == 2
    assert df.head(1).test_num_1[0] == 1
    assert df.head(1).test_num_2[0] == 11
    assert "count" not in df.head(1)
