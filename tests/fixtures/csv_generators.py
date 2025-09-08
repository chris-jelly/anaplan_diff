"""
CSV generation utilities for testing the anaplan-diff tool.

This module provides functions to generate CSV files with known differences
that can be used to test the CLI tool's functionality.
"""

import io
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Union


class AnaplanFormat(Enum):
    """Anaplan CSV export format types."""

    TABULAR_SINGLE_COLUMN = "tabular_single_column"
    TABULAR_MULTI_COLUMN = "tabular_multi_column"  # For future implementation


def generate_tabular_single_column_csv(
    dimension_data: dict[str, list[str]],
    measure_data: dict[str, list[float | int | str]],
    encoding: str = "utf-8",
    delimiter: str = ",",
    add_bom: bool = False,
    anaplan_page_selector: Optional[str] = None,
) -> str:
    """
    Generate CSV content in Anaplan Tabular Single Column format.

    In this format, each dimension is on a separate row, followed by measures.
    Example output:
    Region,North,South,East
    Product,Widget A,Widget B,Widget C
    Sales,1000,2000,1500
    Quantity,10,20,15

    Args:
        dimension_data: Dict mapping dimension names to their values across columns
        measure_data: Dict mapping measure names to their values across columns
        encoding: Text encoding to use
        delimiter: CSV delimiter character
        add_bom: Whether to add UTF-8 BOM
        anaplan_page_selector: Optional Anaplan page selector line

    Returns:
        CSV content as string in Tabular Single Column format
    """
    output = io.StringIO()

    # Add BOM if requested
    if add_bom and encoding.lower() in ("utf-8", "utf-8-sig"):
        output.write("\ufeff")

    # Add Anaplan page selector if provided
    if anaplan_page_selector:
        output.write(f"# {anaplan_page_selector}\n")

    # Write dimension rows
    for dim_name, dim_values in dimension_data.items():
        row = [dim_name] + dim_values
        output.write(delimiter.join(str(cell) for cell in row) + "\n")

    # Write measure rows
    for measure_name, measure_values in measure_data.items():
        row = [measure_name] + measure_values
        output.write(delimiter.join(str(cell) for cell in row) + "\n")

    return output.getvalue()


def generate_csv_with_format(
    format_type: AnaplanFormat,
    data: dict[str, Any],
    encoding: str = "utf-8",
    delimiter: str = ",",
    add_bom: bool = False,
    anaplan_page_selector: Optional[str] = None,
) -> str:
    """
    Generate CSV content based on the specified Anaplan format.

    Args:
        format_type: The Anaplan export format to use
        data: Format-specific data structure
        encoding: Text encoding to use
        delimiter: CSV delimiter character
        add_bom: Whether to add UTF-8 BOM
        anaplan_page_selector: Optional Anaplan page selector line

    Returns:
        CSV content as string

    Raises:
        ValueError: If format_type is not supported
    """
    if format_type == AnaplanFormat.TABULAR_SINGLE_COLUMN:
        return generate_tabular_single_column_csv(
            dimension_data=data["dimensions"],
            measure_data=data["measures"],
            encoding=encoding,
            delimiter=delimiter,
            add_bom=add_bom,
            anaplan_page_selector=anaplan_page_selector,
        )
    elif format_type == AnaplanFormat.TABULAR_MULTI_COLUMN:
        # Future implementation - for now fall back to basic format
        return generate_basic_csv(
            data=data.get("rows", []),
            headers=data.get("headers"),
            encoding=encoding,
            delimiter=delimiter,
            add_bom=add_bom,
            anaplan_page_selector=anaplan_page_selector,
        )
    else:
        raise ValueError(f"Unsupported format type: {format_type}")


def generate_basic_csv(
    data: list[list[Any]],
    headers: Optional[list[str]] = None,
    encoding: str = "utf-8",
    delimiter: str = ",",
    add_bom: bool = False,
    anaplan_page_selector: Optional[str] = None,
) -> str:
    """
    Generate a CSV string with the specified parameters.

    Args:
        data: List of rows, where each row is a list of values
        headers: Optional list of column headers
        encoding: Text encoding to use
        delimiter: CSV delimiter character
        add_bom: Whether to add UTF-8 BOM
        anaplan_page_selector: Optional Anaplan page selector line

    Returns:
        CSV content as string
    """
    output = io.StringIO()

    # Add BOM if requested
    if add_bom and encoding.lower() in ("utf-8", "utf-8-sig"):
        output.write("\ufeff")

    # Add Anaplan page selector if provided
    if anaplan_page_selector:
        output.write(f"# {anaplan_page_selector}\n")

    # Write headers if provided
    if headers:
        output.write(delimiter.join(str(h) for h in headers) + "\n")

    # Write data rows
    for row in data:
        output.write(delimiter.join(str(cell) for cell in row) + "\n")

    return output.getvalue()


def save_csv_file(
    file_path: Union[str, Path], content: str, encoding: str = "utf-8"
) -> None:
    """
    Save CSV content to a file.

    Args:
        file_path: Path where to save the file
        content: CSV content string
        encoding: File encoding
    """
    Path(file_path).write_text(content, encoding=encoding)


class TestScenarios:
    """Pre-defined test scenarios for common comparison cases."""

    @staticmethod
    def identical_files() -> tuple[str, str]:
        """Generate two identical CSV files."""
        headers = ["Region", "Product", "Sales", "Quantity"]
        data = [
            ["North", "Widget A", "1000", "10"],
            ["South", "Widget B", "2000", "20"],
            ["East", "Widget C", "1500", "15"],
        ]

        csv_content = generate_basic_csv(data, headers)
        return csv_content, csv_content

    @staticmethod
    def single_value_change() -> tuple[str, str]:
        """Generate CSV files with one changed value."""
        headers = ["Region", "Product", "Sales", "Quantity"]
        baseline_data = [
            ["North", "Widget A", "1000", "10"],
            ["South", "Widget B", "2000", "20"],
            ["East", "Widget C", "1500", "15"],
        ]
        comparison_data = [
            ["North", "Widget A", "1000", "10"],
            ["South", "Widget B", "2500", "20"],  # Sales changed from 2000 to 2500
            ["East", "Widget C", "1500", "15"],
        ]

        baseline_csv = generate_basic_csv(baseline_data, headers)
        comparison_csv = generate_basic_csv(comparison_data, headers)
        return baseline_csv, comparison_csv

    @staticmethod
    def row_added() -> tuple[str, str]:
        """Generate CSV files where a row is added."""
        headers = ["Region", "Product", "Sales", "Quantity"]
        baseline_data = [
            ["North", "Widget A", "1000", "10"],
            ["South", "Widget B", "2000", "20"],
        ]
        comparison_data = [
            ["North", "Widget A", "1000", "10"],
            ["South", "Widget B", "2000", "20"],
            ["East", "Widget C", "1500", "15"],  # New row added
        ]

        baseline_csv = generate_basic_csv(baseline_data, headers)
        comparison_csv = generate_basic_csv(comparison_data, headers)
        return baseline_csv, comparison_csv

    @staticmethod
    def row_removed() -> tuple[str, str]:
        """Generate CSV files where a row is removed."""
        headers = ["Region", "Product", "Sales", "Quantity"]
        baseline_data = [
            ["North", "Widget A", "1000", "10"],
            ["South", "Widget B", "2000", "20"],
            ["East", "Widget C", "1500", "15"],
        ]
        comparison_data = [
            ["North", "Widget A", "1000", "10"],
            ["South", "Widget B", "2000", "20"],
            # East row removed
        ]

        baseline_csv = generate_basic_csv(baseline_data, headers)
        comparison_csv = generate_basic_csv(comparison_data, headers)
        return baseline_csv, comparison_csv

    @staticmethod
    def multiple_changes() -> tuple[str, str]:
        """Generate CSV files with multiple types of changes."""
        headers = ["Region", "Product", "Sales", "Quantity"]
        baseline_data = [
            ["North", "Widget A", "1000", "10"],
            ["South", "Widget B", "2000", "20"],
            ["East", "Widget C", "1500", "15"],
            ["West", "Widget D", "3000", "30"],
        ]
        comparison_data = [
            ["North", "Widget A", "1200", "10"],  # Sales changed
            ["South", "Widget B", "2000", "25"],  # Quantity changed
            # East row removed
            ["West", "Widget D", "3000", "30"],  # Unchanged
            ["Central", "Widget E", "2500", "25"],  # New row added
        ]

        baseline_csv = generate_basic_csv(baseline_data, headers)
        comparison_csv = generate_basic_csv(comparison_data, headers)
        return baseline_csv, comparison_csv

    @staticmethod
    def different_formats() -> tuple[str, str]:
        """Generate CSV files with different formatting (encoding, delimiters)."""
        headers = ["Region", "Product", "Sales", "Quantity"]
        data = [
            ["North", "Widget A", "1000", "10"],
            ["South", "Widget B", "2000", "20"],
        ]

        # UTF-8 with comma delimiter
        baseline_csv = generate_basic_csv(data, headers, delimiter=",")
        # UTF-8-BOM with semicolon delimiter
        comparison_csv = generate_basic_csv(data, headers, delimiter=";", add_bom=True)

        return baseline_csv, comparison_csv

    @staticmethod
    def with_anaplan_page_selector() -> tuple[str, str]:
        """Generate CSV files with Anaplan page selector lines."""
        headers = ["Region", "Product", "Sales", "Quantity"]
        data = [
            ["North", "Widget A", "1000", "10"],
            ["South", "Widget B", "2000", "20"],
        ]

        baseline_csv = generate_basic_csv(
            data, headers, anaplan_page_selector="Page Selector: All Regions"
        )
        comparison_csv = generate_basic_csv(
            data, headers, anaplan_page_selector="Page Selector: All Regions"
        )

        return baseline_csv, comparison_csv

    @staticmethod
    def dimension_detection_test() -> tuple[str, str]:
        """Generate CSV files designed to test dimension detection logic."""
        headers = [
            "ID",
            "Region",
            "Product_Code",
            "Product_Name",
            "Sales_Amount",
            "Quantity",
            "Date",
        ]
        baseline_data = [
            ["1", "North", "WA", "Widget A", "1000.50", "10", "2024-01-01"],
            ["2", "South", "WB", "Widget B", "2000.75", "20", "2024-01-01"],
            ["3", "East", "WC", "Widget C", "1500.25", "15", "2024-01-01"],
        ]
        comparison_data = [
            [
                "1",
                "North",
                "WA",
                "Widget A",
                "1200.50",
                "10",
                "2024-01-02",
            ],  # Sales and Date changed
            [
                "2",
                "South",
                "WB",
                "Widget B",
                "2000.75",
                "25",
                "2024-01-02",
            ],  # Quantity and Date changed
            [
                "3",
                "East",
                "WC",
                "Widget C",
                "1500.25",
                "15",
                "2024-01-02",
            ],  # Date changed
        ]

        baseline_csv = generate_basic_csv(baseline_data, headers)
        comparison_csv = generate_basic_csv(comparison_data, headers)
        return baseline_csv, comparison_csv

    @staticmethod
    def tabular_single_column_identical() -> tuple[str, str]:
        """Generate two identical CSV files in Tabular Single Column format."""
        dimensions = {
            "Region": ["North", "South", "East"],
            "Product": ["Widget A", "Widget B", "Widget C"],
        }
        measures = {
            "Sales": [1000, 2000, 1500],
            "Quantity": [10, 20, 15],
        }

        data = {"dimensions": dimensions, "measures": measures}
        csv_content = generate_csv_with_format(
            AnaplanFormat.TABULAR_SINGLE_COLUMN, data
        )
        return csv_content, csv_content

    @staticmethod
    def tabular_single_column_value_change() -> tuple[str, str]:
        """Generate CSV files in Tabular Single Column format with one changed value."""
        dimensions = {
            "Region": ["North", "South", "East"],
            "Product": ["Widget A", "Widget B", "Widget C"],
        }

        baseline_measures = {
            "Sales": [1000, 2000, 1500],
            "Quantity": [10, 20, 15],
        }
        comparison_measures = {
            "Sales": [1000, 2500, 1500],  # South sales changed from 2000 to 2500
            "Quantity": [10, 20, 15],
        }

        baseline_data = {"dimensions": dimensions, "measures": baseline_measures}
        comparison_data = {"dimensions": dimensions, "measures": comparison_measures}

        baseline_csv = generate_csv_with_format(
            AnaplanFormat.TABULAR_SINGLE_COLUMN, baseline_data
        )
        comparison_csv = generate_csv_with_format(
            AnaplanFormat.TABULAR_SINGLE_COLUMN, comparison_data
        )
        return baseline_csv, comparison_csv

    @staticmethod
    def tabular_single_column_column_added() -> tuple[str, str]:
        """Generate CSV files in Tabular Single Column format where a column is added."""
        baseline_dimensions = {
            "Region": ["North", "South"],
            "Product": ["Widget A", "Widget B"],
        }
        comparison_dimensions = {
            "Region": ["North", "South", "East"],
            "Product": ["Widget A", "Widget B", "Widget C"],
        }

        baseline_measures = {
            "Sales": [1000, 2000],
            "Quantity": [10, 20],
        }
        comparison_measures = {
            "Sales": [1000, 2000, 1500],  # East column added
            "Quantity": [10, 20, 15],
        }

        baseline_data = {
            "dimensions": baseline_dimensions,
            "measures": baseline_measures,
        }
        comparison_data = {
            "dimensions": comparison_dimensions,
            "measures": comparison_measures,
        }

        baseline_csv = generate_csv_with_format(
            AnaplanFormat.TABULAR_SINGLE_COLUMN, baseline_data
        )
        comparison_csv = generate_csv_with_format(
            AnaplanFormat.TABULAR_SINGLE_COLUMN, comparison_data
        )
        return baseline_csv, comparison_csv

    @staticmethod
    def tabular_single_column_multiple_changes() -> tuple[str, str]:
        """Generate CSV files in Tabular Single Column format with multiple types of changes."""
        baseline_dimensions = {
            "Region": ["North", "South", "East", "West"],
            "Product": ["Widget A", "Widget B", "Widget C", "Widget D"],
        }
        comparison_dimensions = {
            "Region": [
                "North",
                "South",
                "West",
                "Central",
            ],  # East removed, Central added
            "Product": [
                "Widget A",
                "Widget B",
                "Widget D",
                "Widget E",
            ],  # Widget C -> Widget E
        }

        baseline_measures = {
            "Sales": [1000, 2000, 1500, 3000],
            "Quantity": [10, 20, 15, 30],
        }
        comparison_measures = {
            "Sales": [
                1200,
                2000,
                3000,
                2500,
            ],  # North changed, East removed, Central added
            "Quantity": [10, 25, 30, 25],  # South changed, East removed, Central added
        }

        baseline_data = {
            "dimensions": baseline_dimensions,
            "measures": baseline_measures,
        }
        comparison_data = {
            "dimensions": comparison_dimensions,
            "measures": comparison_measures,
        }

        baseline_csv = generate_csv_with_format(
            AnaplanFormat.TABULAR_SINGLE_COLUMN, baseline_data
        )
        comparison_csv = generate_csv_with_format(
            AnaplanFormat.TABULAR_SINGLE_COLUMN, comparison_data
        )
        return baseline_csv, comparison_csv


def create_test_csv_pair(
    scenario_name: str, temp_dir: Path, file_prefix: str = "test"
) -> tuple[Path, Path]:
    """
    Create a pair of CSV test files for a given scenario.

    Args:
        scenario_name: Name of the test scenario method
        temp_dir: Directory to save the files
        file_prefix: Prefix for the generated filenames

    Returns:
        Tuple of (baseline_file_path, comparison_file_path)
    """
    # Get the scenario method
    scenario_method = getattr(TestScenarios, scenario_name)
    baseline_content, comparison_content = scenario_method()

    # Create file paths
    baseline_path = temp_dir / f"{file_prefix}_baseline.csv"
    comparison_path = temp_dir / f"{file_prefix}_comparison.csv"

    # Save files
    save_csv_file(baseline_path, baseline_content)
    save_csv_file(comparison_path, comparison_content)

    return baseline_path, comparison_path
