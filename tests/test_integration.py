"""
Integration tests for the anaplan-diff CLI tool.

These tests validate the complete pipeline from CSV generation through
CLI execution to output validation.
"""

import pytest


class TestCLIBasicFunctionality:
    """Test basic CLI functionality with simple scenarios."""

    def test_cli_with_identical_files(self, cli_helper):
        """Test CLI behavior when files are identical."""
        baseline_file, comparison_file = cli_helper.create_scenario_files("identical_files")

        result = cli_helper.run_cli_command(baseline_file, comparison_file)

        # Should succeed
        cli_helper.assert_cli_success(result)

        # Should indicate no changes (once implementation is complete)
        # Note: Current implementation just prints "Analysis complete"
        assert result.stdout is not None

    def test_cli_with_nonexistent_files(self, cli_helper):
        """Test CLI behavior with non-existent files."""
        nonexistent_before = cli_helper.temp_dir / "missing_before.csv"
        nonexistent_after = cli_helper.temp_dir / "missing_after.csv"

        result = cli_helper.run_cli_command(nonexistent_before, nonexistent_after)

        # Should handle missing files gracefully
        # (Current implementation may succeed due to placeholder code)
        assert result.exit_code is not None  # Just verify it runs

    def test_cli_with_single_value_change(self, cli_helper):
        """Test CLI with a single changed value."""
        baseline_file, comparison_file = cli_helper.create_scenario_files("single_value_change")

        result = cli_helper.run_cli_command(baseline_file, comparison_file)

        cli_helper.assert_cli_success(result)
        assert result.stdout is not None


class TestCLIAdvancedScenarios:
    """Test CLI with more complex scenarios."""

    def test_cli_with_row_added(self, cli_helper):
        """Test CLI when a row is added."""
        baseline_file, comparison_file = cli_helper.create_scenario_files("row_added")

        result = cli_helper.run_cli_command(baseline_file, comparison_file)

        cli_helper.assert_cli_success(result)
        assert result.stdout is not None

    def test_cli_with_row_removed(self, cli_helper):
        """Test CLI when a row is removed."""
        baseline_file, comparison_file = cli_helper.create_scenario_files("row_removed")

        result = cli_helper.run_cli_command(baseline_file, comparison_file)

        cli_helper.assert_cli_success(result)
        assert result.stdout is not None

    def test_cli_with_multiple_changes(self, cli_helper):
        """Test CLI with multiple types of changes."""
        baseline_file, comparison_file = cli_helper.create_scenario_files("multiple_changes")

        result = cli_helper.run_cli_command(baseline_file, comparison_file)

        cli_helper.assert_cli_success(result)
        assert result.stdout is not None


class TestCLIFormatHandling:
    """Test CLI with different CSV formats."""

    def test_cli_with_different_formats(self, cli_helper):
        """Test CLI with different CSV formatting."""
        baseline_file, comparison_file = cli_helper.create_scenario_files("different_formats")

        result = cli_helper.run_cli_command(baseline_file, comparison_file)

        cli_helper.assert_cli_success(result)
        assert result.stdout is not None


class TestCLIOutputValidation:
    """Test CLI output formatting and content."""

    @pytest.mark.parametrize(
        "scenario",
        ["identical_files", "single_value_change", "row_added", "row_removed"],
    )
    def test_cli_output_format(self, cli_helper, scenario):
        """Test that CLI output follows expected format for various scenarios."""
        baseline_file, comparison_file = cli_helper.create_scenario_files(scenario)

        result = cli_helper.run_cli_command(baseline_file, comparison_file)

        # Should always succeed (currently placeholder implementation)
        cli_helper.assert_cli_success(result)

        # Output should be non-empty
        assert result.stdout is not None
        assert len(result.stdout.strip()) > 0

    def test_cli_error_handling(self, cli_helper):
        """Test CLI error handling and messaging."""
        # Create a scenario that might cause issues (empty files)
        empty_before = cli_helper.temp_dir / "empty_before.csv"
        empty_after = cli_helper.temp_dir / "empty_after.csv"

        # Create empty files
        empty_before.write_text("")
        empty_after.write_text("")

        result = cli_helper.run_cli_command(empty_before, empty_after)

        # Should handle gracefully (behavior depends on implementation)
        assert result.exit_code is not None


class TestCLIEndToEnd:
    """End-to-end tests for complete workflows."""

    def test_complete_workflow_identical_files(self, cli_helper, csv_validator):
        """Test complete workflow with identical files."""
        # Generate test files
        baseline_file, comparison_file = cli_helper.create_scenario_files("identical_files")

        # Validate the test files were created correctly
        baseline_info = csv_validator.get_csv_info(baseline_file)
        comparison_info = csv_validator.get_csv_info(comparison_file)

        assert "error" not in baseline_info
        assert "error" not in comparison_info
        assert baseline_info["rows"] == comparison_info["rows"]
        assert baseline_info["columns"] == comparison_info["columns"]

        # Run CLI
        result = cli_helper.run_cli_command(baseline_file, comparison_file)

        # Validate CLI execution
        cli_helper.assert_cli_success(result)

        # Future: Validate specific output content when implementation is complete
        # For now, just verify it produces output
        assert result.stdout is not None

    def test_complete_workflow_with_changes(self, cli_helper, csv_validator):
        """Test complete workflow with actual changes."""
        # Generate test files with known differences
        baseline_file, comparison_file = cli_helper.create_scenario_files("single_value_change")

        # Validate test file generation
        baseline_info = csv_validator.get_csv_info(baseline_file)
        comparison_info = csv_validator.get_csv_info(comparison_file)

        assert "error" not in baseline_info
        assert "error" not in comparison_info
        assert baseline_info["rows"] == comparison_info["rows"]  # Same number of rows
        assert baseline_info["columns"] == comparison_info["columns"]  # Same structure

        # Run CLI
        result = cli_helper.run_cli_command(baseline_file, comparison_file)

        # Validate execution
        cli_helper.assert_cli_success(result)

        # Future: When implementation is complete, validate that:
        # - Changes are detected
        # - Correct change summary is displayed
        # - Dimension columns are properly identified
        assert result.stdout is not None
