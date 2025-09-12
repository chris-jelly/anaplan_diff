"""
Basic functionality tests for the anaplan-diff tool.
"""

import polars as pl
from returns.result import Failure, Success

from anaplan_diff.comparator import compare_dataframes
from tests.fixtures.csv_generators import AnaplanFormat


class TestDataComparison:
    """Test the functional data comparison."""

    def test_compare_dataframes_invalid_tolerance(self):
        """Test that invalid tolerance is rejected."""
        df = pl.DataFrame({"A": [1], "B": [2]})
        result = compare_dataframes(
            df, df, dimension_columns=["A"], comparison_tolerance=-1
        )
        assert isinstance(result, Failure)

    def test_traditional_tabular_comparison(self):
        """Test basic comparison of traditional tabular data."""
        # Create test data
        before_data = {
            "Region": ["North", "South", "East"],
            "Product": ["Widget A", "Widget B", "Widget C"],
            "Sales": [1000, 2000, 1500],
            "Quantity": [10, 20, 15],
        }
        after_data = {
            "Region": ["North", "South", "East"],
            "Product": ["Widget A", "Widget B", "Widget C"],
            "Sales": [1200, 2000, 1500],  # North changed
            "Quantity": [10, 25, 15],  # South changed
        }

        before_df = pl.DataFrame(before_data)
        after_df = pl.DataFrame(after_data)

        result = compare_dataframes(
            before_df, after_df, dimension_columns=["Region", "Product"]
        )
        assert isinstance(result, Success)
        result = result.unwrap()

        # Check result structure
        assert result.dimension_columns == ["Region", "Product"]
        assert set(result.measure_columns) == {"Sales", "Quantity"}
        assert result.total_baseline == 3
        assert result.total_comparison == 3

        # Should have 1 unchanged row (East)
        assert len(result.unchanged_rows) == 1
        assert result.unchanged_rows["Region"].to_list() == ["East"]

        # Should have 2 changed rows (North and South)
        assert len(result.changed_rows) == 2

    def test_tabular_single_column_comparison(self):
        """Test comparison of Tabular Single Column format."""
        # Create test data in standard tabular format (simplified test)
        before_data = {
            "Label": ["A", "B", "C"],
            "Value": [1000, 2000, 1500],
        }
        after_data = {
            "Label": ["A", "B", "C"],
            "Value": [1200, 2000, 1500],  # A changed
        }

        before_df = pl.DataFrame(before_data)
        after_df = pl.DataFrame(after_data)

        result = compare_dataframes(
            before_df,
            after_df,
            dimension_columns=["Label"],
            format_type=AnaplanFormat.TABULAR_SINGLE_COLUMN,
        )
        assert isinstance(result, Success)
        result = result.unwrap()

        # Check result structure
        assert result.format_type == AnaplanFormat.TABULAR_SINGLE_COLUMN
        assert result.dimension_columns == ["Label"]
        assert len(result.changed_rows) == 1  # One change

    def test_empty_dataframe_validation(self):
        """Test that empty DataFrames are rejected."""
        empty_df = pl.DataFrame()
        data_df = pl.DataFrame({"A": [1], "B": [2]})

        result = compare_dataframes(empty_df, data_df, dimension_columns=["A"])
        assert isinstance(result, Failure)

        result = compare_dataframes(data_df, empty_df, dimension_columns=["A"])
        assert isinstance(result, Failure)

    def test_mismatched_columns_validation(self):
        """Test that mismatched columns are rejected."""
        before_df = pl.DataFrame({"A": [1], "B": [2]})
        after_df = pl.DataFrame({"A": [1], "C": [3]})

        result = compare_dataframes(before_df, after_df, dimension_columns=["A"])
        assert isinstance(result, Failure)

    def test_missing_dimension_columns(self):
        """Test that missing dimension columns are rejected."""
        df = pl.DataFrame({"A": [1], "B": [2]})

        result = compare_dataframes(df, df, dimension_columns=["X"])
        assert isinstance(result, Failure)

    def test_no_measure_columns(self):
        """Test that DataFrames with only dimension columns are rejected."""
        df = pl.DataFrame({"A": ["x"], "B": ["y"]})

        result = compare_dataframes(df, df, dimension_columns=["A", "B"])
        assert isinstance(result, Failure)

    def test_numeric_vs_text_measures(self):
        """Test handling of mixed numeric and text measures."""
        before_data = {
            "Region": ["North", "South"],
            "Sales": [1000.0, 2000.0],  # Numeric
            "Status": ["Active", "Pending"],  # Text
        }
        after_data = {
            "Region": ["North", "South"],
            "Sales": [1000.5, 2000.0],  # Small numeric change
            "Status": ["Inactive", "Pending"],  # Text change
        }

        before_df = pl.DataFrame(before_data)
        after_df = pl.DataFrame(after_data)

        result = compare_dataframes(
            before_df, after_df, ["Region"], comparison_tolerance=1.0
        )
        assert isinstance(result, Success)
        result = result.unwrap()

        # North should be unchanged (within tolerance) but Status changed
        # South should be unchanged completely
        assert len(result.changed_rows) >= 1  # At least North due to status change
