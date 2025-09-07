"""
Tests for CSV generation utilities used in testing.

These tests validate that our test data generation functions work correctly
and produce CSV files with the expected structure and content.
"""

import pytest
from pathlib import Path

from tests.fixtures.csv_generators import (
    generate_basic_csv,
    save_csv_file,
    TestScenarios,
    create_test_csv_pair,
)


class TestBasicCSVGeneration:
    """Test basic CSV generation functionality."""

    def test_generate_basic_csv_simple(self):
        """Test basic CSV generation with simple data."""
        headers = ["A", "B", "C"]
        data = [["1", "2", "3"], ["4", "5", "6"]]

        result = generate_basic_csv(data, headers)

        expected = "A,B,C\n1,2,3\n4,5,6\n"
        assert result == expected

    def test_generate_basic_csv_no_headers(self):
        """Test CSV generation without headers."""
        data = [["1", "2", "3"], ["4", "5", "6"]]

        result = generate_basic_csv(data)

        expected = "1,2,3\n4,5,6\n"
        assert result == expected

    def test_generate_basic_csv_custom_delimiter(self):
        """Test CSV generation with custom delimiter."""
        headers = ["A", "B", "C"]
        data = [["1", "2", "3"]]

        result = generate_basic_csv(data, headers, delimiter=";")

        expected = "A;B;C\n1;2;3\n"
        assert result == expected

    def test_generate_basic_csv_with_bom(self):
        """Test CSV generation with BOM marker."""
        headers = ["A", "B"]
        data = [["1", "2"]]

        result = generate_basic_csv(data, headers, add_bom=True)

        # Should start with BOM character
        assert result.startswith("\ufeff")
        assert "A,B\n1,2\n" in result

    def test_generate_basic_csv_with_page_selector(self):
        """Test CSV generation with Anaplan page selector."""
        headers = ["A", "B"]
        data = [["1", "2"]]

        result = generate_basic_csv(
            data, headers, anaplan_page_selector="Page Selector: All Items"
        )

        expected = "# Page Selector: All Items\nA,B\n1,2\n"
        assert result == expected


class TestCSVFileSaving:
    """Test CSV file saving functionality."""

    def test_save_csv_file(self, temp_dir):
        """Test saving CSV content to file."""
        content = "A,B,C\n1,2,3\n"
        file_path = temp_dir / "test.csv"

        save_csv_file(file_path, content)

        # Verify file was created and has correct content
        assert file_path.exists()
        assert file_path.read_text(encoding="utf-8") == content

    def test_save_csv_file_different_encoding(self, temp_dir):
        """Test saving CSV with different encoding."""
        content = "A,B,C\n1,2,3\n"
        file_path = temp_dir / "test.csv"

        save_csv_file(file_path, content, encoding="utf-8")

        assert file_path.exists()
        assert file_path.read_text(encoding="utf-8") == content


class TestScenarioGeneration:
    """Test pre-defined scenario generation."""

    def test_identical_files_scenario(self):
        """Test identical files scenario generation."""
        before_csv, after_csv = TestScenarios.identical_files()

        # Should be exactly the same
        assert before_csv == after_csv

        # Should have proper structure
        lines = before_csv.strip().split("\n")
        assert len(lines) >= 2  # At least header + 1 data row
        assert "Region" in lines[0]  # Header should contain Region
        assert "," in before_csv  # Should use comma delimiter

    def test_single_value_change_scenario(self):
        """Test single value change scenario."""
        before_csv, after_csv = TestScenarios.single_value_change()

        # Should be different
        assert before_csv != after_csv

        # Should have same number of lines
        before_lines = before_csv.strip().split("\n")
        after_lines = after_csv.strip().split("\n")
        assert len(before_lines) == len(after_lines)

        # Should have same headers
        assert before_lines[0] == after_lines[0]

        # Should have exactly one different line
        different_lines = 0
        for i in range(1, len(before_lines)):
            if before_lines[i] != after_lines[i]:
                different_lines += 1
        assert different_lines == 1

    def test_row_added_scenario(self):
        """Test row added scenario."""
        before_csv, after_csv = TestScenarios.row_added()

        before_lines = before_csv.strip().split("\n")
        after_lines = after_csv.strip().split("\n")

        # After should have one more line
        assert len(after_lines) == len(before_lines) + 1

        # Headers should be the same
        assert before_lines[0] == after_lines[0]

    def test_row_removed_scenario(self):
        """Test row removed scenario."""
        before_csv, after_csv = TestScenarios.row_removed()

        before_lines = before_csv.strip().split("\n")
        after_lines = after_csv.strip().split("\n")

        # Before should have one more line
        assert len(before_lines) == len(after_lines) + 1

        # Headers should be the same
        assert before_lines[0] == after_lines[0]

    def test_multiple_changes_scenario(self):
        """Test multiple changes scenario."""
        before_csv, after_csv = TestScenarios.multiple_changes()

        # Should be different
        assert before_csv != after_csv

        # Should have proper CSV structure
        assert "Region" in before_csv
        assert "Region" in after_csv

    def test_different_formats_scenario(self):
        """Test different formats scenario."""
        before_csv, after_csv = TestScenarios.different_formats()

        # Should have different delimiters
        assert "," in before_csv
        assert ";" in after_csv

        # After should have BOM
        assert after_csv.startswith("\ufeff")
        assert not before_csv.startswith("\ufeff")

    def test_with_anaplan_page_selector_scenario(self):
        """Test Anaplan page selector scenario."""
        before_csv, after_csv = TestScenarios.with_anaplan_page_selector()

        # Both should have page selector
        assert before_csv.startswith("#")
        assert after_csv.startswith("#")
        assert "Page Selector" in before_csv
        assert "Page Selector" in after_csv

    def test_dimension_detection_test_scenario(self):
        """Test dimension detection scenario."""
        before_csv, after_csv = TestScenarios.dimension_detection_test()

        # Should have various column types for testing dimension detection
        assert "ID" in before_csv
        assert "Region" in before_csv
        assert "Product_Code" in before_csv
        assert "Sales_Amount" in before_csv


class TestTestCsvPairCreation:
    """Test the create_test_csv_pair function."""

    def test_create_test_csv_pair(self, temp_dir):
        """Test creating a pair of CSV files."""
        before_path, after_path = create_test_csv_pair(
            "identical_files", temp_dir, "test_scenario"
        )

        # Files should exist
        assert before_path.exists()
        assert after_path.exists()

        # Files should have expected names
        assert before_path.name == "test_scenario_before.csv"
        assert after_path.name == "test_scenario_after.csv"

        # Files should be in the temp directory
        assert before_path.parent == temp_dir
        assert after_path.parent == temp_dir

        # Files should have content
        assert len(before_path.read_text()) > 0
        assert len(after_path.read_text()) > 0

    def test_create_test_csv_pair_different_scenario(self, temp_dir):
        """Test creating CSV pair with different scenario."""
        before_path, after_path = create_test_csv_pair("single_value_change", temp_dir)

        before_content = before_path.read_text()
        after_content = after_path.read_text()

        # Should be different (single value change)
        assert before_content != after_content

        # Should have same structure (same number of lines)
        before_lines = before_content.strip().split("\n")
        after_lines = after_content.strip().split("\n")
        assert len(before_lines) == len(after_lines)


class TestCSVContentValidation:
    """Test validation of generated CSV content."""

    @pytest.mark.parametrize(
        "scenario_name",
        [
            "identical_files",
            "single_value_change",
            "row_added",
            "row_removed",
            "multiple_changes",
            "dimension_detection_test",
        ],
    )
    def test_all_scenarios_generate_valid_csv(
        self, scenario_name, temp_dir, csv_validator
    ):
        """Test that all scenarios generate valid CSV files."""
        before_path, after_path = create_test_csv_pair(scenario_name, temp_dir)

        # Both files should be valid CSV
        before_info = csv_validator.get_csv_info(before_path)
        after_info = csv_validator.get_csv_info(after_path)

        # Should not have errors
        assert "error" not in before_info, (
            f"Before file error: {before_info.get('error')}"
        )
        assert "error" not in after_info, f"After file error: {after_info.get('error')}"

        # Should have data
        assert before_info["rows"] > 0, f"Before file has no data rows"
        assert after_info["columns"] > 0, f"After file has no columns"

        # Should have reasonable structure
        assert before_info["columns"] >= 2, "Should have at least 2 columns"
        assert after_info["columns"] >= 2, "Should have at least 2 columns"
