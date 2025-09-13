"""
Tests for non-numeric value support in the anaplan-diff tool.

Tests that the tool correctly handles string, boolean, and mixed data types
in both dimension and measure columns.
"""

import polars as pl
import pytest
from returns.result import Failure, Success

from anaplan_diff.comparator import compare_dataframes
from anaplan_diff.detector import analyze_file, detect_dimensions, load_dataframe
from tests.fixtures.csv_generators import save_csv_file


class TestNonNumericMeasures:
    """Test support for non-numeric values in measure columns."""

    def test_string_measures_comparison(self):
        """Test comparison of string measures (e.g., status values)."""
        baseline_df = pl.DataFrame(
            {
                "LineItem": ["Project A", "Project B", "Project C"],
                "Status": ["Complete", "In Progress", "Complete"],
            }
        )

        comparison_df = pl.DataFrame(
            {
                "LineItem": ["Project A", "Project B", "Project C"],
                "Status": ["Complete", "Complete", "Not Started"],
            }
        )

        result = compare_dataframes(
            baseline_df, comparison_df, dimension_columns=["LineItem"]
        )

        assert isinstance(result, Success)
        comparison_result = result.unwrap()

        # Project A unchanged (Complete -> Complete)
        assert len(comparison_result.unchanged_rows) == 1
        assert comparison_result.unchanged_rows["LineItem"][0] == "Project A"

        # Projects B and C changed
        assert len(comparison_result.changed_rows) == 2
        changed_items = comparison_result.changed_rows["LineItem"].to_list()
        assert "Project B" in changed_items
        assert "Project C" in changed_items

        # No change/change_percent columns for non-numeric data
        assert "change" not in comparison_result.changed_rows.columns
        assert "change_percent" not in comparison_result.changed_rows.columns

    def test_boolean_measures_comparison(self):
        """Test comparison of boolean measures."""
        baseline_df = pl.DataFrame(
            {
                "LineItem": ["Feature A", "Feature B", "Feature C"],
                "IsActive": [True, False, True],
            }
        )

        comparison_df = pl.DataFrame(
            {
                "LineItem": ["Feature A", "Feature B", "Feature C"],
                "IsActive": [True, True, False],
            }
        )

        result = compare_dataframes(
            baseline_df, comparison_df, dimension_columns=["LineItem"]
        )

        assert isinstance(result, Success)
        comparison_result = result.unwrap()

        # Feature A unchanged (True -> True)
        assert len(comparison_result.unchanged_rows) == 1
        assert comparison_result.unchanged_rows["LineItem"][0] == "Feature A"

        # Features B and C changed
        assert len(comparison_result.changed_rows) == 2

        # Should have baseline/comparison values but no arithmetic columns
        assert "baseline_value" in comparison_result.changed_rows.columns
        assert "comparison_value" in comparison_result.changed_rows.columns
        assert "change" not in comparison_result.changed_rows.columns
        assert "change_percent" not in comparison_result.changed_rows.columns

    def test_mixed_data_types_in_dimensions(self):
        """Test various data types in dimension columns."""
        baseline_df = pl.DataFrame(
            {
                "LineItem": ["Revenue", "Costs"],
                "Year": [2024, 2024],
                "Active": [True, False],
                "Category": ["Sales", "Operations"],
                "Value": [1000, 500],
            }
        )

        comparison_df = pl.DataFrame(
            {
                "LineItem": ["Revenue", "Costs"],
                "Year": [2024, 2024],
                "Active": [True, False],
                "Category": ["Sales", "Operations"],
                "Value": [1200, 500],
            }
        )

        dimensions = ["LineItem", "Year", "Active", "Category"]
        result = compare_dataframes(
            baseline_df, comparison_df, dimension_columns=dimensions
        )

        assert isinstance(result, Success)
        comparison_result = result.unwrap()

        # Revenue changed, Costs unchanged
        assert len(comparison_result.changed_rows) == 1
        assert len(comparison_result.unchanged_rows) == 1

        # Should have change calculations since Value is numeric
        assert "change" in comparison_result.changed_rows.columns
        assert "change_percent" in comparison_result.changed_rows.columns

    def test_string_measures_with_added_removed_rows(self):
        """Test string measures with added/removed rows."""
        baseline_df = pl.DataFrame(
            {
                "LineItem": ["Project A", "Project B"],
                "Status": ["Complete", "In Progress"],
            }
        )

        comparison_df = pl.DataFrame(
            {
                "LineItem": ["Project A", "Project C"],
                "Status": ["Complete", "Not Started"],
            }
        )

        result = compare_dataframes(
            baseline_df, comparison_df, dimension_columns=["LineItem"]
        )

        assert isinstance(result, Success)
        comparison_result = result.unwrap()

        # Project A unchanged
        assert len(comparison_result.unchanged_rows) == 1
        assert comparison_result.unchanged_rows["LineItem"][0] == "Project A"

        # Project B removed
        assert len(comparison_result.removed_rows) == 1
        assert comparison_result.removed_rows["LineItem"][0] == "Project B"

        # Project C added
        assert len(comparison_result.added_rows) == 1
        assert comparison_result.added_rows["LineItem"][0] == "Project C"


class TestNonNumericFileDetection:
    """Test file detection with non-numeric measures."""

    def test_string_measure_file_detection(self, tmp_path):
        """Test that files with string measures are accepted."""
        csv_content = """LineItem,Region,Status
Revenue,North,Complete
Costs,South,In Progress
Profit,East,Not Started"""

        file_path = tmp_path / "test_string_measures.csv"
        save_csv_file(file_path, csv_content)

        # Should successfully analyze file
        result = analyze_file(str(file_path))
        assert isinstance(result, Success)

        csv_info = result.unwrap()
        assert csv_info.format_type == "tabular_single_column"

        # Should successfully load dataframe
        df_result = load_dataframe(str(file_path), csv_info)
        assert isinstance(df_result, Success)

        df = df_result.unwrap()
        assert len(df) == 3
        assert df.columns == ["LineItem", "Region", "Status"]

    def test_boolean_measure_file_detection(self, tmp_path):
        """Test that files with boolean measures are accepted."""
        csv_content = """LineItem,Category,IsActive
Feature A,Core,True
Feature B,Optional,False
Feature C,Core,True"""

        file_path = tmp_path / "test_boolean_measures.csv"
        save_csv_file(file_path, csv_content)

        result = analyze_file(str(file_path))
        assert isinstance(result, Success)

        csv_info = result.unwrap()
        df_result = load_dataframe(str(file_path), csv_info)
        assert isinstance(df_result, Success)

        df = df_result.unwrap()
        # Boolean values should be properly loaded
        assert df["IsActive"].dtype == pl.Boolean

    def test_mixed_measure_types_file_detection(self, tmp_path):
        """Test files with mixed data types throughout."""
        csv_content = """LineItem,Year,IsCore,Priority,Budget
Revenue,2024,True,High,1000000
Costs,2024,False,Medium,500000
Profit,2024,True,Low,500000"""

        file_path = tmp_path / "test_mixed_types.csv"
        save_csv_file(file_path, csv_content)

        result = analyze_file(str(file_path))
        assert isinstance(result, Success)

        csv_info = result.unwrap()
        df_result = load_dataframe(str(file_path), csv_info)
        assert isinstance(df_result, Success)


class TestNonNumericDimensionDetection:
    """Test dimension detection with non-numeric data."""

    def test_detect_dimensions_with_string_measures(self):
        """Test dimension detection when measure is string."""
        df = pl.DataFrame(
            {
                "LineItem": ["A", "B", "C"],
                "Category": ["X", "Y", "Z"],
                "Status": ["Complete", "In Progress", "Not Started"],
            }
        )

        result = detect_dimensions(df)
        assert isinstance(result, Success)

        dimensions = result.unwrap()
        assert "LineItem" in dimensions
        assert "Category" in dimensions
        assert "Status" not in dimensions  # Last column never dimension

    def test_detect_dimensions_with_boolean_measures(self):
        """Test dimension detection when measure is boolean."""
        df = pl.DataFrame(
            {"LineItem": ["Feature A", "Feature B"], "IsActive": [True, False]}
        )

        result = detect_dimensions(df)
        assert isinstance(result, Success)

        dimensions = result.unwrap()
        assert "LineItem" in dimensions
        assert "IsActive" not in dimensions  # Last column never dimension

    def test_all_text_columns_follow_position_rules(self):
        """Test that all text columns still follow position rules."""
        df = pl.DataFrame(
            {
                "Product": ["Widget A", "Widget B"],
                "Category": ["Electronics", "Tools"],
                "Region": ["North", "South"],
                "Status": ["Active", "Inactive"],
            }
        )

        result = detect_dimensions(df)
        assert isinstance(result, Success)

        dimensions = result.unwrap()
        assert "Product" in dimensions  # First column
        assert "Category" in dimensions  # Middle column
        assert "Region" in dimensions  # Middle column
        assert "Status" not in dimensions  # Last column (measure)


class TestNonNumericEdgeCases:
    """Test edge cases with non-numeric data."""

    def test_null_values_in_string_measures(self):
        """Test handling of null values in string measures."""
        baseline_df = pl.DataFrame(
            {"LineItem": ["A", "B", "C"], "Status": ["Complete", None, "In Progress"]}
        )

        comparison_df = pl.DataFrame(
            {"LineItem": ["A", "B", "C"], "Status": ["Complete", "Complete", None]}
        )

        result = compare_dataframes(
            baseline_df, comparison_df, dimension_columns=["LineItem"]
        )

        assert isinstance(result, Success)
        comparison_result = result.unwrap()

        # A unchanged, B and C changed
        assert len(comparison_result.unchanged_rows) == 1
        assert len(comparison_result.changed_rows) == 2

    def test_empty_string_measures(self):
        """Test handling of empty string measures."""
        baseline_df = pl.DataFrame({"LineItem": ["A", "B"], "Status": ["Complete", ""]})

        comparison_df = pl.DataFrame(
            {"LineItem": ["A", "B"], "Status": ["", "Complete"]}
        )

        result = compare_dataframes(
            baseline_df, comparison_df, dimension_columns=["LineItem"]
        )

        assert isinstance(result, Success)
        comparison_result = result.unwrap()

        # Both rows changed
        assert len(comparison_result.changed_rows) == 2
        assert len(comparison_result.unchanged_rows) == 0
