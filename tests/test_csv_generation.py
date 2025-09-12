"""
Tests for CSV generation utilities used in testing.

These tests validate that our test data generation functions work correctly
and produce CSV files with the expected structure and content.
"""

import pytest

from tests.fixtures.csv_generators import (
    TestScenarios,
    create_test_csv_pair,
    generate_basic_csv,
    save_csv_file,
)


class TestBasicCSVGeneration:
    """Test essential CSV generation functionality."""

    def test_generate_basic_csv_simple(self):
        """Test basic CSV generation works."""
        headers = ["A", "B"]
        data = [["1", "2"]]
        result = generate_basic_csv(data, headers)
        assert "A,B" in result and "1,2" in result


class TestCSVFileSaving:
    """Test CSV file saving functionality."""

    def test_save_csv_file(self, temp_dir):
        """Test saving CSV content to file."""
        content = "A,B\n1,2\n"
        file_path = temp_dir / "test.csv"
        save_csv_file(file_path, content)
        assert file_path.exists() and file_path.read_text() == content


class TestScenarioGeneration:
    """Test that scenarios generate valid data."""

    def test_identical_files_scenario(self):
        """Test identical files scenario generates matching data."""
        baseline_csv, comparison_csv = TestScenarios.identical_files()
        assert baseline_csv == comparison_csv

    def test_single_value_change_scenario(self):
        """Test single value change scenario generates different data."""
        baseline_csv, comparison_csv = TestScenarios.single_value_change()
        assert baseline_csv != comparison_csv


class TestTestCsvPairCreation:
    """Test the create_test_csv_pair function."""

    def test_create_test_csv_pair(self, temp_dir):
        """Test creating a pair of CSV files."""
        baseline_path, comparison_path = create_test_csv_pair(
            "identical_files", temp_dir
        )
        assert baseline_path.exists() and comparison_path.exists()
        assert len(baseline_path.read_text()) > 0
