"""
Test configuration and shared fixtures for anaplan-diff tests.
"""

import subprocess
import tempfile
from pathlib import Path
from typing import Any

import pytest
from typer.testing import CliRunner

from anaplan_diff.cli import app
from tests.fixtures.csv_generators import create_test_csv_pair


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def cli_runner():
    """Create a CLI runner for testing the typer application."""
    return CliRunner()


@pytest.fixture
def csv_file_pair(temp_dir):
    """Create a basic pair of CSV test files."""
    return create_test_csv_pair("identical_files", temp_dir, "basic")


class CLITestHelper:
    """Helper class for CLI testing operations."""

    def __init__(self, temp_dir: Path, cli_runner: CliRunner):
        self.temp_dir = temp_dir
        self.cli_runner = cli_runner

    def run_cli_command(
        self, baseline_file: Path, comparison_file: Path, expected_exit_code: int = 0
    ) -> subprocess.CompletedProcess:
        """
        Run the anaplan-diff CLI command and return the result.

        Args:
            baseline_file: Path to the 'baseline' CSV file
            comparison_file: Path to the 'comparison' CSV file
            expected_exit_code: Expected exit code (0 for success)

        Returns:
            CliRunner result object
        """
        result = self.cli_runner.invoke(app, [str(baseline_file), str(comparison_file)])

        # Store the result for debugging
        self.last_result = result

        return result

    def create_scenario_files(self, scenario_name: str, prefix: str = "test") -> tuple[Path, Path]:
        """
        Create CSV files for a specific test scenario.

        Args:
            scenario_name: Name of the test scenario
            prefix: File prefix for generated files

        Returns:
            Tuple of (baseline_file_path, comparison_file_path)
        """
        return create_test_csv_pair(scenario_name, self.temp_dir, prefix)

    def assert_cli_output_contains(self, result: Any, expected_texts: list[str]) -> None:
        """
        Assert that CLI output contains all expected text fragments.

        Args:
            result: CLI runner result
            expected_texts: List of text fragments that should be in output
        """
        output = result.stdout
        for expected_text in expected_texts:
            assert expected_text in output, f"Expected '{expected_text}' in output: {output}"

    def assert_cli_success(self, result: Any) -> None:
        """Assert that CLI command executed successfully."""
        assert result.exit_code == 0, (
            f"CLI failed with exit code {result.exit_code}. Output: {result.stdout}"
        )

    def assert_cli_failure(self, result: Any, expected_exit_code: int = 1) -> None:
        """Assert that CLI command failed as expected."""
        assert result.exit_code == expected_exit_code, (
            f"Expected exit code {expected_exit_code}, got {result.exit_code}"
        )


@pytest.fixture
def cli_helper(temp_dir, cli_runner):
    """Create a CLI test helper instance."""
    return CLITestHelper(temp_dir, cli_runner)


class CSVValidationHelper:
    """Helper class for validating CSV content and structure."""

    @staticmethod
    def validate_csv_content(file_path: Path, expected_rows: int, expected_columns: int) -> bool:
        """
        Validate that a CSV file has expected structure.

        Args:
            file_path: Path to CSV file
            expected_rows: Expected number of data rows (excluding header)
            expected_columns: Expected number of columns

        Returns:
            True if validation passes
        """
        try:
            import polars as pl

            df = pl.read_csv(file_path)
            return df.height == expected_rows and df.width == expected_columns
        except Exception:
            return False

    @staticmethod
    def get_csv_info(file_path: Path) -> dict[str, Any]:
        """
        Get basic information about a CSV file.

        Args:
            file_path: Path to CSV file

        Returns:
            Dictionary with CSV file information
        """
        try:
            import polars as pl

            df = pl.read_csv(file_path)
            return {
                "rows": df.height,
                "columns": df.width,
                "column_names": df.columns,
                "dtypes": dict(zip(df.columns, df.dtypes, strict=False)),
                "has_nulls": df.null_count().sum_horizontal().item() > 0,
            }
        except Exception as e:
            return {"error": str(e)}


@pytest.fixture
def csv_validator():
    """Create a CSV validation helper instance."""
    return CSVValidationHelper()


# Test data constants for reuse across tests
TEST_SCENARIOS = [
    "identical_files",
    "single_value_change",
    "row_added",
    "row_removed",
    "multiple_changes",
    "different_formats",
    "with_anaplan_page_selector",
    "dimension_detection_test",
]


@pytest.fixture(params=TEST_SCENARIOS)
def scenario_name(request):
    """Parametrize tests to run against all test scenarios."""
    return request.param
