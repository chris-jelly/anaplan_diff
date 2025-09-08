"""
Basic functionality tests for the anaplan-diff tool.
"""

import polars as pl
import pytest

from anaplan_diff.comparator import DataComparator
from anaplan_diff.detector import CSVInfo, DimensionDetector, FileAnalyzer
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


class TestFileAnalyzer:
    """Test the FileAnalyzer class."""

    def test_file_analyzer_creation(self):
        """Test creating a FileAnalyzer instance."""
        analyzer = FileAnalyzer()
        assert analyzer is not None


class TestDimensionDetector:
    """Test the DimensionDetector class."""

    def test_dimension_detector_creation(self):
        """Test creating a DimensionDetector instance."""
        detector = DimensionDetector()
        assert detector is not None


class TestDataComparator:
    """Test the DataComparator class."""

    def test_data_comparator_creation(self):
        """Test creating a DataComparator instance."""
        comparator = DataComparator()
        assert comparator is not None
        assert comparator.comparison_tolerance == 1e-10

    def test_data_comparator_custom_tolerance(self):
        """Test creating a DataComparator with custom tolerance."""
        comparator = DataComparator(comparison_tolerance=1e-5)
        assert comparator.comparison_tolerance == 1e-5

    def test_data_comparator_invalid_tolerance(self):
        """Test that invalid tolerance raises error."""
        with pytest.raises(ValueError, match="Comparison tolerance must be positive"):
            DataComparator(comparison_tolerance=-1)

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

        comparator = DataComparator()
        result = comparator.compare(
            before_df, after_df, dimension_columns=["Region", "Product"]
        )

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

        comparator = DataComparator()
        result = comparator.compare(
            before_df,
            after_df,
            dimension_columns=["Label"],
            format_type=AnaplanFormat.TABULAR_SINGLE_COLUMN,
        )

        # Check result structure
        assert result.format_type == AnaplanFormat.TABULAR_SINGLE_COLUMN
        assert result.dimension_columns == ["Label"]
        assert len(result.changed_rows) == 1  # One change

    def test_empty_dataframe_validation(self):
        """Test that empty DataFrames raise appropriate errors."""
        empty_df = pl.DataFrame()
        data_df = pl.DataFrame({"A": [1], "B": [2]})

        comparator = DataComparator()

        with pytest.raises(ValueError, match="Baseline DataFrame is empty"):
            comparator.compare(empty_df, data_df, ["A"])

        with pytest.raises(ValueError, match="Comparison DataFrame is empty"):
            comparator.compare(data_df, empty_df, ["A"])

    def test_mismatched_columns_validation(self):
        """Test that mismatched columns raise appropriate errors."""
        before_df = pl.DataFrame({"A": [1], "B": [2]})
        after_df = pl.DataFrame({"A": [1], "C": [3]})

        comparator = DataComparator()

        with pytest.raises(ValueError, match="Files have different column structures"):
            comparator.compare(before_df, after_df, ["A"])

    def test_missing_dimension_columns(self):
        """Test that missing dimension columns raise appropriate errors."""
        df = pl.DataFrame({"A": [1], "B": [2]})

        comparator = DataComparator()

        with pytest.raises(ValueError, match="Dimension column 'X' not found in data"):
            comparator.compare(df, df, ["X"])

    def test_no_measure_columns(self):
        """Test that DataFrames with only dimension columns raise appropriate errors."""
        df = pl.DataFrame({"A": ["x"], "B": ["y"]})

        comparator = DataComparator()

        with pytest.raises(ValueError, match="No measure columns found for comparison"):
            comparator.compare(df, df, ["A", "B"])

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

        comparator = DataComparator(comparison_tolerance=1.0)  # Large tolerance
        result = comparator.compare(before_df, after_df, ["Region"])

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
