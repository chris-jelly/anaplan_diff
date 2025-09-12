"""
Tests for dimension detection functionality.

This tests the core business logic for automatically identifying
dimension columns vs measure columns in CSV data.
"""

import polars as pl
import pytest
from returns.result import Failure, Success

from anaplan_diff.detector import detect_dimensions


class TestDimensionDetection:
    """Test automatic dimension column detection."""

    def test_detect_text_columns_as_dimensions(self):
        """Text columns should be identified as dimensions."""
        df = pl.DataFrame(
            {
                "Region": ["North", "South", "East"],
                "Product": ["Widget A", "Widget B", "Widget C"],
                "Sales": [1000, 2000, 1500],
            }
        )

        result = detect_dimensions(df)
        assert isinstance(result, Success)
        dimensions = result.unwrap()
        assert "Region" in dimensions
        assert "Product" in dimensions
        assert "Sales" not in dimensions

    def test_detect_low_cardinality_numeric_as_dimensions(self):
        """Low cardinality numeric columns should be identified as dimensions."""
        df = pl.DataFrame(
            {
                "Category_ID": [1, 2, 1, 2, 1],  # Low cardinality
                "Product_ID": [101, 102, 103, 104, 105],  # High cardinality
                "Revenue": [1000.5, 2000.7, 1500.3, 800.9, 1200.1],
            }
        )

        result = detect_dimensions(df)
        assert isinstance(result, Success)
        dimensions = result.unwrap()
        assert "Category_ID" in dimensions
        assert "Product_ID" not in dimensions  # High cardinality numeric
        assert "Revenue" not in dimensions

    def test_detect_anaplan_keywords_as_dimensions(self):
        """Columns with Anaplan-specific keywords should be dimensions."""
        df = pl.DataFrame(
            {
                "Time": ["2024-01", "2024-02", "2024-03"],
                "Location": ["NYC", "LA", "CHI"],
                "Account": ["Revenue", "Cost", "Profit"],
                "Amount": [1000, 2000, 1500],
            }
        )

        result = detect_dimensions(df)
        assert isinstance(result, Success)
        dimensions = result.unwrap()
        assert "Time" in dimensions
        assert "Location" in dimensions
        assert "Account" in dimensions
        assert "Amount" not in dimensions

    def test_mixed_column_types(self):
        """Test detection with mixed column types."""
        df = pl.DataFrame(
            {
                "ID": [1, 2, 3],  # Low cardinality numeric
                "Name": ["A", "B", "C"],  # Text
                "Active": [True, False, True],  # Boolean (should be dimension)
                "Score": [95.5, 87.2, 91.8],  # Numeric measure
                "Count": [100, 200, 150],  # Numeric measure
            }
        )

        result = detect_dimensions(df)
        assert isinstance(result, Success)
        dimensions = result.unwrap()
        assert "ID" in dimensions
        assert "Name" in dimensions
        assert "Active" in dimensions
        assert "Score" not in dimensions
        assert "Count" not in dimensions

    def test_empty_dataframe(self):
        """Empty DataFrame should return appropriate error."""
        df = pl.DataFrame()
        result = detect_dimensions(df)
        assert isinstance(result, Failure)

    def test_single_column_dataframe(self):
        """Single column DataFrame should be handled appropriately."""
        df = pl.DataFrame({"Only_Column": ["A", "B", "C"]})
        result = detect_dimensions(df)
        assert isinstance(result, Success)
        dimensions = result.unwrap()
        assert "Only_Column" in dimensions

    def test_all_numeric_high_cardinality(self):
        """DataFrame with all high-cardinality numeric columns."""
        df = pl.DataFrame(
            {
                "Value1": [1.1, 2.2, 3.3, 4.4, 5.5],
                "Value2": [10.1, 20.2, 30.3, 40.4, 50.5],
                "Value3": [100, 200, 300, 400, 500],
            }
        )

        result = detect_dimensions(df)
        assert isinstance(result, Success)
        dimensions = result.unwrap()
        # Should have some fallback behavior - perhaps treat first column as dimension
        # or use some other heuristic
        assert len(dimensions) >= 1  # Should identify at least one dimension

    def test_date_columns_as_dimensions(self):
        """Date/datetime columns should be identified as dimensions."""
        df = pl.DataFrame(
            {
                "Date": ["2024-01-01", "2024-01-02", "2024-01-03"],
                "Month": ["Jan", "Jan", "Jan"],
                "Sales": [1000, 1100, 1200],
            }
        )

        result = detect_dimensions(df)
        assert isinstance(result, Success)
        dimensions = result.unwrap()
        assert "Date" in dimensions
        assert "Month" in dimensions
        assert "Sales" not in dimensions

    def test_cardinality_threshold(self):
        """Test that cardinality threshold works correctly."""
        # High cardinality - each value unique
        high_card_df = pl.DataFrame(
            {
                "ID": list(range(100)),  # 100 unique values
                "Value": [i * 10 for i in range(100)],
            }
        )

        result = detect_dimensions(high_card_df)
        assert isinstance(result, Success)
        dimensions = result.unwrap()
        # With high cardinality, ID might not be detected as dimension
        # depending on threshold logic

        # Low cardinality - repeated values
        low_card_df = pl.DataFrame(
            {
                "Category": [1, 2, 1, 2] * 25,  # Only 2 unique values, 100 total rows
                "Value": list(range(100)),
            }
        )

        result = detect_dimensions(low_card_df)
        assert isinstance(result, Success)
        dimensions = result.unwrap()
        assert "Category" in dimensions
        assert "Value" not in dimensions


class TestDimensionDetectionEdgeCases:
    """Test edge cases in dimension detection."""

    def test_columns_with_nulls(self):
        """Columns with null values should still be processed."""
        df = pl.DataFrame(
            {
                "Region": ["North", None, "South"],
                "Sales": [1000, None, 2000],
            }
        )

        result = detect_dimensions(df)
        assert isinstance(result, Success)
        dimensions = result.unwrap()
        assert "Region" in dimensions

    def test_numeric_strings(self):
        """Numeric strings should be treated as text (dimensions)."""
        df = pl.DataFrame(
            {
                "Product_Code": ["001", "002", "003"],  # Numeric strings
                "Amount": [1000, 2000, 3000],  # Actual numbers
            }
        )

        result = detect_dimensions(df)
        assert isinstance(result, Success)
        dimensions = result.unwrap()
        assert "Product_Code" in dimensions
        assert "Amount" not in dimensions

    def test_very_long_text_values(self):
        """Very long text values should still be dimensions."""
        df = pl.DataFrame(
            {
                "Description": ["Very long product description " * 10] * 3,
                "Sales": [1000, 2000, 3000],
            }
        )

        result = detect_dimensions(df)
        assert isinstance(result, Success)
        dimensions = result.unwrap()
        assert "Description" in dimensions
        assert "Sales" not in dimensions


class TestDimensionDetectionConfiguration:
    """Test dimension detection with different configuration options."""

    def test_custom_cardinality_threshold(self):
        """Test detection with custom cardinality threshold."""
        df = pl.DataFrame(
            {
                "ID": [1, 2, 3, 4, 5],  # 5 unique values
                "Value": [100, 200, 300, 400, 500],
            }
        )

        # With high threshold, ID should be dimension
        result = detect_dimensions(df, cardinality_threshold=0.8)
        assert isinstance(result, Success)
        dimensions = result.unwrap()
        assert "ID" in dimensions

        # With low threshold, ID might not be dimension
        result = detect_dimensions(df, cardinality_threshold=0.2)
        assert isinstance(result, Success)
        dimensions = result.unwrap()
        # Behavior depends on implementation

    def test_custom_anaplan_keywords(self):
        """Test detection with custom Anaplan keyword list."""
        df = pl.DataFrame(
            {
                "CustomDimension": ["A", "B", "C"],
                "RegularColumn": ["X", "Y", "Z"],
                "Value": [1, 2, 3],
            }
        )

        custom_keywords = ["CustomDimension"]
        result = detect_dimensions(df, anaplan_keywords=custom_keywords)
        assert isinstance(result, Success)
        dimensions = result.unwrap()
        assert "CustomDimension" in dimensions
