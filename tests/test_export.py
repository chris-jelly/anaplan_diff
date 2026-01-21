"""
Tests for CSV export functionality.
"""

import polars as pl
import pytest
from returns.result import Failure, Success

from anaplan_diff.comparator import ComparisonResult
from anaplan_diff.formatter import export_to_csv
from anaplan_diff.types import AnaplanFormat


class TestCSVExport:
    """Test CSV export functionality."""

    def test_export_changed_rows_only(self, temp_dir):
        """Test exporting only changed rows."""
        # Create sample data
        changed_df = pl.DataFrame(
            {
                "Region": ["North", "South"],
                "baseline_value": [100.0, 200.0],
                "comparison_value": [150.0, 180.0],
                "change": [50.0, -20.0],
                "change_percent": [50.0, -10.0],
            }
        )

        result = ComparisonResult(
            unchanged_rows=pl.DataFrame(),
            changed_rows=changed_df,
            added_rows=pl.DataFrame(),
            removed_rows=pl.DataFrame(),
            dimension_columns=["Region"],
            measure_columns=["Value"],
            total_baseline=2,
            total_comparison=2,
            format_type=AnaplanFormat.TABULAR_SINGLE_COLUMN,
        )

        output_path = temp_dir / "export_changed.csv"
        export_result = export_to_csv(result, str(output_path))

        assert isinstance(export_result, Success)
        assert output_path.exists()

        # Verify content
        exported_df = pl.read_csv(output_path)
        assert len(exported_df) == 2
        assert "change_type" in exported_df.columns
        assert all(exported_df["change_type"] == "CHANGED")

    def test_export_added_rows_only(self, temp_dir):
        """Test exporting only added rows."""
        added_df = pl.DataFrame({"Region": ["East", "West"], "Value": [300.0, 400.0]})

        result = ComparisonResult(
            unchanged_rows=pl.DataFrame(),
            changed_rows=pl.DataFrame(),
            added_rows=added_df,
            removed_rows=pl.DataFrame(),
            dimension_columns=["Region"],
            measure_columns=["Value"],
            total_baseline=0,
            total_comparison=2,
            format_type=AnaplanFormat.TABULAR_SINGLE_COLUMN,
        )

        output_path = temp_dir / "export_added.csv"
        export_result = export_to_csv(result, str(output_path))

        assert isinstance(export_result, Success)
        assert output_path.exists()

        # Verify content
        exported_df = pl.read_csv(output_path)
        assert len(exported_df) == 2
        assert "change_type" in exported_df.columns
        assert all(exported_df["change_type"] == "ADDED")

    def test_export_removed_rows_only(self, temp_dir):
        """Test exporting only removed rows."""
        removed_df = pl.DataFrame({"Region": ["Old1", "Old2"], "Value": [500.0, 600.0]})

        result = ComparisonResult(
            unchanged_rows=pl.DataFrame(),
            changed_rows=pl.DataFrame(),
            added_rows=pl.DataFrame(),
            removed_rows=removed_df,
            dimension_columns=["Region"],
            measure_columns=["Value"],
            total_baseline=2,
            total_comparison=0,
            format_type=AnaplanFormat.TABULAR_SINGLE_COLUMN,
        )

        output_path = temp_dir / "export_removed.csv"
        export_result = export_to_csv(result, str(output_path))

        assert isinstance(export_result, Success)
        assert output_path.exists()

        # Verify content
        exported_df = pl.read_csv(output_path)
        assert len(exported_df) == 2
        assert "change_type" in exported_df.columns
        assert all(exported_df["change_type"] == "REMOVED")

    def test_export_all_change_types(self, temp_dir):
        """Test exporting all types of changes together."""
        changed_df = pl.DataFrame(
            {
                "Region": ["North"],
                "baseline_value": [100.0],
                "comparison_value": [150.0],
                "change": [50.0],
                "change_percent": [50.0],
            }
        )
        added_df = pl.DataFrame({"Region": ["East"], "Value": [300.0]})
        removed_df = pl.DataFrame({"Region": ["West"], "Value": [400.0]})

        result = ComparisonResult(
            unchanged_rows=pl.DataFrame(),
            changed_rows=changed_df,
            added_rows=added_df,
            removed_rows=removed_df,
            dimension_columns=["Region"],
            measure_columns=["Value"],
            total_baseline=2,
            total_comparison=2,
            format_type=AnaplanFormat.TABULAR_SINGLE_COLUMN,
        )

        output_path = temp_dir / "export_all.csv"
        export_result = export_to_csv(result, str(output_path))

        assert isinstance(export_result, Success)
        assert output_path.exists()

        # Verify content
        exported_df = pl.read_csv(output_path)
        assert len(exported_df) == 3
        assert "change_type" in exported_df.columns

        # Check all change types are present
        change_types = set(exported_df["change_type"].to_list())
        assert change_types == {"CHANGED", "ADDED", "REMOVED"}

    def test_export_no_changes(self, temp_dir):
        """Test export fails gracefully when there are no changes."""
        result = ComparisonResult(
            unchanged_rows=pl.DataFrame({"Region": ["North"], "Value": [100.0]}),
            changed_rows=pl.DataFrame(),
            added_rows=pl.DataFrame(),
            removed_rows=pl.DataFrame(),
            dimension_columns=["Region"],
            measure_columns=["Value"],
            total_baseline=1,
            total_comparison=1,
            format_type=AnaplanFormat.TABULAR_SINGLE_COLUMN,
        )

        output_path = temp_dir / "export_none.csv"
        export_result = export_to_csv(result, str(output_path))

        assert isinstance(export_result, Failure)
        assert "No changes to export" in export_result.failure()

    def test_export_with_multiple_dimensions(self, temp_dir):
        """Test exporting with multiple dimension columns."""
        changed_df = pl.DataFrame(
            {
                "Region": ["North"],
                "Product": ["Widget"],
                "baseline_value": [100.0],
                "comparison_value": [150.0],
                "change": [50.0],
                "change_percent": [50.0],
            }
        )

        result = ComparisonResult(
            unchanged_rows=pl.DataFrame(),
            changed_rows=changed_df,
            added_rows=pl.DataFrame(),
            removed_rows=pl.DataFrame(),
            dimension_columns=["Region", "Product"],
            measure_columns=["Value"],
            total_baseline=1,
            total_comparison=1,
            format_type=AnaplanFormat.TABULAR_SINGLE_COLUMN,
        )

        output_path = temp_dir / "export_multi_dim.csv"
        export_result = export_to_csv(result, str(output_path))

        assert isinstance(export_result, Success)
        assert output_path.exists()

        # Verify content
        exported_df = pl.read_csv(output_path)
        assert "Region" in exported_df.columns
        assert "Product" in exported_df.columns


class TestCLIExportOption:
    """Test the CLI --output option."""

    def test_cli_export_with_changes(self, cli_helper, temp_dir):
        """Test CLI export functionality with changes."""
        baseline_file, comparison_file = cli_helper.create_scenario_files(
            "single_value_change"
        )

        output_file = temp_dir / "cli_export.csv"
        result = cli_helper.cli_runner.invoke(
            cli_helper.cli_runner.app
            if hasattr(cli_helper.cli_runner, "app")
            else __import__("anaplan_diff.cli", fromlist=["app"]).app,
            [str(baseline_file), str(comparison_file), "--output", str(output_file)],
        )

        cli_helper.assert_cli_success(result)
        assert output_file.exists()
        assert "Results exported to" in result.stdout

        # Verify the exported file has content
        exported_df = pl.read_csv(output_file)
        assert len(exported_df) > 0
        assert "change_type" in exported_df.columns

    def test_cli_export_with_identical_files(self, cli_helper, temp_dir):
        """Test CLI export with identical files (no changes)."""
        baseline_file, comparison_file = cli_helper.create_scenario_files(
            "identical_files"
        )

        output_file = temp_dir / "cli_export_empty.csv"
        result = cli_helper.cli_runner.invoke(
            __import__("anaplan_diff.cli", fromlist=["app"]).app,
            [str(baseline_file), str(comparison_file), "--output", str(output_file)],
        )

        # Should fail gracefully since there are no changes
        assert result.exit_code == 1
        assert "No changes to export" in result.stdout

    def test_cli_export_short_option(self, cli_helper, temp_dir):
        """Test CLI export with -o short option."""
        baseline_file, comparison_file = cli_helper.create_scenario_files(
            "single_value_change"
        )

        output_file = temp_dir / "cli_export_short.csv"
        result = cli_helper.cli_runner.invoke(
            __import__("anaplan_diff.cli", fromlist=["app"]).app,
            [str(baseline_file), str(comparison_file), "-o", str(output_file)],
        )

        cli_helper.assert_cli_success(result)
        assert output_file.exists()
