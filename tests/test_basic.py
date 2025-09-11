"""
Basic functionality tests for the anaplan-diff tool.
"""

import polars as pl
import pytest
from returns.result import Success, Failure

from anaplan_diff.comparator import compare_dataframes
from anaplan_diff.detector import CSVInfo
from anaplan_diff.formatter import TerminalFormatter
from tests.fixtures.csv_generators import AnaplanFormat


class TestCSVInfo:
    """Test the CSVInfo dataclass."""

    def test_csv_info_creation(self):
        """Test creating a CSVInfo instance."""
        csv_info = CSVInfo(
            encoding="utf-8", delimiter=",", has_header=True, skip_rows=0
        )
        assert csv_info.encoding == "utf-8"
        assert csv_info.delimiter == ","
        assert csv_info.has_header is True
        assert csv_info.skip_rows == 0


class TestDataComparison:
    """Test the functional data comparison."""

    def test_compare_dataframes_invalid_tolerance(self):
        """Test that invalid tolerance returns failure."""
        df = pl.DataFrame({"A": [1], "B": [2]})
        result = compare_dataframes(df, df, ["A"], comparison_tolerance=-1)
        assert isinstance(result, Failure)
        assert "Comparison tolerance must be positive" in result.failure()

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
        """Test that empty DataFrames raise appropriate errors."""
        empty_df = pl.DataFrame()
        data_df = pl.DataFrame({"A": [1], "B": [2]})

        result = compare_dataframes(empty_df, data_df, ["A"])
        assert isinstance(result, Failure)
        assert "Baseline DataFrame is empty" in result.failure()

        result = compare_dataframes(data_df, empty_df, ["A"])
        assert isinstance(result, Failure)
        assert "Comparison DataFrame is empty" in result.failure()

    def test_mismatched_columns_validation(self):
        """Test that mismatched columns raise appropriate errors."""
        before_df = pl.DataFrame({"A": [1], "B": [2]})
        after_df = pl.DataFrame({"A": [1], "C": [3]})

        result = compare_dataframes(before_df, after_df, ["A"])
        assert isinstance(result, Failure)
        assert "Files have different column structures" in result.failure()

    def test_missing_dimension_columns(self):
        """Test that missing dimension columns raise appropriate errors."""
        df = pl.DataFrame({"A": [1], "B": [2]})

        result = compare_dataframes(df, df, ["X"])
        assert isinstance(result, Failure)
        assert "Dimension column 'X' not found in data" in result.failure()

    def test_no_measure_columns(self):
        """Test that DataFrames with only dimension columns raise appropriate errors."""
        df = pl.DataFrame({"A": ["x"], "B": ["y"]})

        result = compare_dataframes(df, df, ["A", "B"])
        assert isinstance(result, Failure)
        assert "No measure columns found for comparison" in result.failure()

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


class TestTerminalFormatter:
    """Test the TerminalFormatter class."""

    def test_terminal_formatter_creation(self):
        """Test creating a TerminalFormatter instance."""
        formatter = TerminalFormatter()
        assert formatter is not None
        assert formatter.console is not None

    def test_error_message_formatting(self):
        """Test that error messages are properly formatted."""
        formatter = TerminalFormatter()
        # Test that methods exist - actual output testing would require mocking
        assert hasattr(formatter, "print_error")
        assert hasattr(formatter, "print_success")
