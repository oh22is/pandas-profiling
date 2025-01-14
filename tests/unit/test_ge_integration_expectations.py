from unittest.mock import Mock, patch

import pytest

from pandas_profiling.model.expectation_algorithms import (
    categorical_expectations,
    datetime_expectations,
    file_expectations,
    generic_expectations,
    image_expectations,
    numeric_expectations,
    path_expectations,
    url_expectations,
)
from pandas_profiling.model.schema import Monotonicity


@pytest.fixture(scope="function")
def batch():
    return Mock()


def test_generic_expectations(batch):
    generic_expectations("column", {"n_missing": 0, "p_unique": 1.0}, batch)
    batch.expect_column_to_exist.assert_called_once()
    batch.expect_column_values_to_not_be_null.assert_called_once()
    batch.expect_column_values_to_be_unique.assert_called_once()


def test_generic_expectations_min(batch):
    generic_expectations("column", {"n_missing": 1, "p_unique": 0.5}, batch)
    batch.expect_column_to_exist.assert_called_once()
    batch.expect_column_values_to_not_be_null.assert_not_called()
    batch.expect_column_values_to_be_unique.assert_not_called()


orig_import = __import__


def import_mock(name, *args):
    if name == "great_expectations.profile.base":
        mod = Mock()
        mod.ProfilerTypeMapping.INT_TYPE_NAMES = []
        mod.ProfilerTypeMapping.FLOAT_TYPE_NAMES = []
        return mod

    return orig_import(name, *args)


@patch("builtins.__import__", side_effect=import_mock)
def test_numeric_expectations(batch):
    numeric_expectations(
        "column",
        {
            "monotonic": Monotonicity.INCREASING_STRICT,
            "min": -1,
            "max": 5,
        },
        {"generic_expectations": batch},
    )
    batch.expect_column_values_to_be_in_type_list.assert_called_once()
    batch.expect_column_values_to_be_increasing.assert_called_once_with(
        "column", strictly=True
    )
    batch.expect_column_values_to_be_decreasing.assert_not_called()
    batch.expect_column_values_to_be_between.assert_called_once_with(
        "column",
        min_value=-1,
        max_value=5,
    )


@patch("builtins.__import__", side_effect=import_mock)
def test_numeric_expectations_min(batch):
    numeric_expectations(
        "column",
        {
            "monotonic": Monotonicity.NOT_MONOTONIC,
        },
        {"generic_expectations": batch},
    )
    batch.expect_column_values_to_be_in_type_list.assert_called_once()
    batch.expect_column_values_to_be_increasing.assert_not_called()
    batch.expect_column_values_to_be_decreasing.assert_not_called()
    batch.expect_column_values_to_be_between.assert_not_called()


def test_categorical_expectations(batch):
    categorical_expectations(
        "column",
        {
            "n_distinct": 1,
            "p_distinct": 0.1,
            "value_counts": {"val1": 1, "val2": 2},
        },
        batch,
    )
    batch.expect_column_values_to_be_in_set.assert_called_once_with(
        "column", {"val1", "val2"}
    )


def test_categorical_expectations_min(batch):
    categorical_expectations("column", {"n_distinct": 15, "p_distinct": 1.0}, batch)
    batch.expect_column_values_to_be_in_set.assert_not_called()


def test_path_expectations(batch):
    path_expectations("column", {}, batch)
    batch.expect_column_to_exist.assert_not_called()


def test_datetime_expectations(batch):
    datetime_expectations("column", {"min": 0, "max": 100}, batch)
    batch.expect_column_values_to_be_between.assert_called_once_with(
        "column",
        min_value=0,
        max_value=100,
        parse_strings_as_datetimes=True,
    )


def test_datetime_expectations_min(batch):
    datetime_expectations("column", {}, batch)
    batch.expect_column_values_to_be_between.assert_not_called()


def test_image_expectations(batch):
    image_expectations("column", {}, batch)
    batch.expect_column_to_exist.assert_not_called()


def test_url_expectations(batch):
    url_expectations("column", {}, batch)
    batch.expect_column_to_exist.assert_not_called()


def test_file_expectations(batch):
    file_expectations("column", {}, batch)
    batch.expect_file_to_exist.assert_called_once()
