"""
Tests for dimension detection functionality.

Tests the position-based logic for identifying dimension columns in
Tabular Single Column format where:
- First column: ALWAYS line item name (dimension)
- Last column: ALWAYS value (measure)
- Middle columns: ALWAYS dimensions
"""

import polars as pl
from returns.result import Failure, Success

from anaplan_diff.detector import detect_dimensions


class TestDimensionDetection:
    """Test position-based dimension detection for Tabular Single Column format."""

    def test_basic_three_column_structure(self):
        """Test basic 3-column structure: Line Item | Dimension | Value."""
        df = pl.DataFrame(
            {
                "Line_Item": ["Revenue", "Costs", "Profit"],
                "Region": ["North", "South", "East"],
                "Value": [1000, 2000, 1500],
            }
        )

        result = detect_dimensions(df)
        assert isinstance(result, Success)
        dimensions = result.unwrap()
        assert "Line_Item" in dimensions  # First column always dimension
        assert "Region" in dimensions  # Middle column always dimension
        assert "Value" not in dimensions  # Last column never dimension

    def test_multiple_dimension_columns(self):
        """Test structure with multiple dimension columns."""
        df = pl.DataFrame(
            {
                "Line_Item": ["Revenue", "Costs"],
                "Time": ["2024-01", "2024-01"],
                "Product": ["Widget A", "Widget A"],
                "Region": ["North", "South"],
                "Value": [1000.5, 800.9],
            }
        )

        result = detect_dimensions(df)
        assert isinstance(result, Success)
        dimensions = result.unwrap()
        assert "Line_Item" in dimensions  # First column
        assert "Time" in dimensions  # Middle column
        assert "Product" in dimensions  # Middle column
        assert "Region" in dimensions  # Middle column
        assert "Value" not in dimensions  # Last column (measure)

    def test_two_column_structure(self):
        """Test minimum 2-column structure: Line Item | Value."""
        df = pl.DataFrame(
            {
                "Line_Item": ["Revenue", "Costs", "Profit"],
                "Value": [1000, 500, 500],
            }
        )

        result = detect_dimensions(df)
        assert isinstance(result, Success)
        dimensions = result.unwrap()
        assert "Line_Item" in dimensions  # First column always dimension
        assert "Value" not in dimensions  # Last column never dimension
        assert len(dimensions) == 1  # Only one dimension

    def test_data_types_irrelevant_to_position(self):
        """Test that data types don't affect position-based detection."""
        df = pl.DataFrame(
            {
                "LineItem": [1, 2, 3],  # Numeric line item (still dimension)
                "TextDim": ["A", "B", "C"],  # Text dimension
                "NumericDim": [100, 200, 300],  # Numeric dimension
                "BoolDim": [True, False, True],  # Boolean dimension
                "Measure": [95.5, 87.2, 91.8],  # Final measure column
            }
        )

        result = detect_dimensions(df)
        assert isinstance(result, Success)
        dimensions = result.unwrap()
        assert "LineItem" in dimensions  # First column (even though numeric)
        assert "TextDim" in dimensions  # Middle column
        assert "NumericDim" in dimensions  # Middle column (even though numeric)
        assert "BoolDim" in dimensions  # Middle column
        assert "Measure" not in dimensions  # Last column (never dimension)

    def test_empty_dataframe(self):
        """Empty DataFrame should return appropriate error."""
        df = pl.DataFrame()
        result = detect_dimensions(df)
        assert isinstance(result, Failure)

    def test_single_column_dataframe(self):
        """Single column DataFrame should return Failure (invalid format)."""
        df = pl.DataFrame({"Only_Column": ["A", "B", "C"]})
        result = detect_dimensions(df)
        assert isinstance(result, Failure)

    def test_all_numeric_columns(self):
        """All numeric columns still follow position-based rules."""
        df = pl.DataFrame(
            {
                "LineItem_ID": [1, 2, 3, 4, 5],  # First = dimension (even numeric)
                "Category_ID": [
                    10,
                    20,
                    30,
                    40,
                    50,
                ],  # Middle = dimension (even numeric)
                "Amount": [100, 200, 300, 400, 500],  # Last = measure
            }
        )

        result = detect_dimensions(df)
        assert isinstance(result, Success)
        dimensions = result.unwrap()
        assert "LineItem_ID" in dimensions  # First column always dimension
        assert "Category_ID" in dimensions  # Middle column always dimension
        assert "Amount" not in dimensions  # Last column never dimension

    def test_various_data_types_in_guaranteed_positions(self):
        """Various data types in their guaranteed positions."""
        df = pl.DataFrame(
            {
                "LineItem": ["Revenue", "Costs", "Profit"],  # Text line item
                "Date": ["2024-01-01", "2024-01-02", "2024-01-03"],  # Date dimension
                "Active": [True, False, True],  # Boolean dimension
                "Amount": [1000, 1100, 1200],  # Numeric measure
            }
        )

        result = detect_dimensions(df)
        assert isinstance(result, Success)
        dimensions = result.unwrap()
        assert "LineItem" in dimensions  # First column
        assert "Date" in dimensions  # Middle column
        assert "Active" in dimensions  # Middle column
        assert "Amount" not in dimensions  # Last column

    def test_large_dataset_structure(self):
        """Test position-based detection works with large datasets."""
        # Create larger dataset to ensure position logic is robust
        df = pl.DataFrame(
            {
                "LineItem": ["Revenue", "Costs"] * 50,  # 100 rows, repeated line items
                "Time": [f"2024-{i:02d}" for i in range(1, 13)] * 8 + ["2024-01"] * 4,
                "Value": list(range(100)),  # 100 unique values
            }
        )

        result = detect_dimensions(df)
        assert isinstance(result, Success)
        dimensions = result.unwrap()
        assert "LineItem" in dimensions  # First column always dimension
        assert "Time" in dimensions  # Middle column always dimension
        assert "Value" not in dimensions  # Last column never dimension


class TestDimensionDetectionEdgeCases:
    """Test edge cases in dimension detection."""

    def test_columns_with_nulls(self):
        """Columns with null values should still be processed based on position."""
        df = pl.DataFrame(
            {
                "LineItem": ["Revenue", None, "Costs"],
                "Region": ["North", None, "South"],
                "Value": [1000, None, 2000],
            }
        )

        result = detect_dimensions(df)
        assert isinstance(result, Success)
        dimensions = result.unwrap()
        assert "LineItem" in dimensions  # First column always dimension
        assert "Region" in dimensions  # Middle column always dimension
        assert "Value" not in dimensions  # Last column never dimension

    def test_numeric_strings_follow_position_rules(self):
        """Numeric strings follow position rules regardless of content."""
        df = pl.DataFrame(
            {
                "Product_Code": ["001", "002", "003"],  # First column = dimension
                "Category_Code": ["100", "200", "300"],  # Middle column = dimension
                "Amount": [1000, 2000, 3000],  # Last column = measure
            }
        )

        result = detect_dimensions(df)
        assert isinstance(result, Success)
        dimensions = result.unwrap()
        assert "Product_Code" in dimensions  # First column
        assert "Category_Code" in dimensions  # Middle column
        assert "Amount" not in dimensions  # Last column

    def test_very_long_text_values_follow_position_rules(self):
        """Very long text values follow position rules."""
        df = pl.DataFrame(
            {
                "Description": ["Very long product description " * 10] * 3,
                "Category": ["A", "B", "C"],
                "Sales": [1000, 2000, 3000],
            }
        )

        result = detect_dimensions(df)
        assert isinstance(result, Success)
        dimensions = result.unwrap()
        assert "Description" in dimensions  # First column
        assert "Category" in dimensions  # Middle column
        assert "Sales" not in dimensions  # Last column

    def test_mixed_null_patterns(self):
        """Mixed null patterns don't affect position-based detection."""
        df = pl.DataFrame(
            {
                "LineItem": [None, "Revenue", None],  # First = dimension (with nulls)
                "Time": ["2024-01", None, "2024-03"],  # Middle = dimension (with nulls)
                "Region": [None, None, "North"],  # Middle = dimension (mostly nulls)
                "Value": [None, 1000, 2000],  # Last = measure (with nulls)
            }
        )

        result = detect_dimensions(df)
        assert isinstance(result, Success)
        dimensions = result.unwrap()
        assert "LineItem" in dimensions  # First column
        assert "Time" in dimensions  # Middle column
        assert "Region" in dimensions  # Middle column
        assert "Value" not in dimensions  # Last column


class TestDimensionDetectionExactColumnCount:
    """Test that exact column counts work correctly."""

    def test_minimum_columns_exactly_two(self):
        """Exactly 2 columns: first is dimension, last is measure."""
        df = pl.DataFrame(
            {
                "LineItem": ["A", "B"],
                "Measure": [1, 2],
            }
        )

        result = detect_dimensions(df)
        assert isinstance(result, Success)
        dimensions = result.unwrap()
        assert len(dimensions) == 1
        assert dimensions[0] == "LineItem"

    def test_three_columns_exactly(self):
        """Exactly 3 columns: first and middle are dimensions."""
        df = pl.DataFrame(
            {
                "LineItem": ["A", "B"],
                "Dimension": ["X", "Y"],
                "Measure": [1, 2],
            }
        )

        result = detect_dimensions(df)
        assert isinstance(result, Success)
        dimensions = result.unwrap()
        assert len(dimensions) == 2
        assert "LineItem" in dimensions
        assert "Dimension" in dimensions

    def test_many_columns(self):
        """Many columns: all except last are dimensions."""
        df = pl.DataFrame(
            {
                "LineItem": ["A"],
                "Dim1": ["X"],
                "Dim2": ["Y"],
                "Dim3": ["Z"],
                "Dim4": ["W"],
                "Dim5": ["V"],
                "Measure": [1],
            }
        )

        result = detect_dimensions(df)
        assert isinstance(result, Success)
        dimensions = result.unwrap()
        assert len(dimensions) == 6  # All except last
        assert "Measure" not in dimensions
        assert all(
            col in dimensions
            for col in ["LineItem", "Dim1", "Dim2", "Dim3", "Dim4", "Dim5"]
        )
