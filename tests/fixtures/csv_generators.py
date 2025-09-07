"""
CSV generation utilities for testing the anaplan-diff tool.

This module provides functions to generate CSV files with known differences
that can be used to test the CLI tool's functionality.
"""

import io
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


def generate_basic_csv(
    data: List[List[Any]],
    headers: Optional[List[str]] = None,
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
        before_data = [
            ["North", "Widget A", "1000", "10"],
            ["South", "Widget B", "2000", "20"],
            ["East", "Widget C", "1500", "15"],
        ]
        after_data = [
            ["North", "Widget A", "1000", "10"],
            ["South", "Widget B", "2500", "20"],  # Sales changed from 2000 to 2500
            ["East", "Widget C", "1500", "15"],
        ]

        before_csv = generate_basic_csv(before_data, headers)
        after_csv = generate_basic_csv(after_data, headers)
        return before_csv, after_csv

    @staticmethod
    def row_added() -> tuple[str, str]:
        """Generate CSV files where a row is added."""
        headers = ["Region", "Product", "Sales", "Quantity"]
        before_data = [
            ["North", "Widget A", "1000", "10"],
            ["South", "Widget B", "2000", "20"],
        ]
        after_data = [
            ["North", "Widget A", "1000", "10"],
            ["South", "Widget B", "2000", "20"],
            ["East", "Widget C", "1500", "15"],  # New row added
        ]

        before_csv = generate_basic_csv(before_data, headers)
        after_csv = generate_basic_csv(after_data, headers)
        return before_csv, after_csv

    @staticmethod
    def row_removed() -> tuple[str, str]:
        """Generate CSV files where a row is removed."""
        headers = ["Region", "Product", "Sales", "Quantity"]
        before_data = [
            ["North", "Widget A", "1000", "10"],
            ["South", "Widget B", "2000", "20"],
            ["East", "Widget C", "1500", "15"],
        ]
        after_data = [
            ["North", "Widget A", "1000", "10"],
            ["South", "Widget B", "2000", "20"],
            # East row removed
        ]

        before_csv = generate_basic_csv(before_data, headers)
        after_csv = generate_basic_csv(after_data, headers)
        return before_csv, after_csv

    @staticmethod
    def multiple_changes() -> tuple[str, str]:
        """Generate CSV files with multiple types of changes."""
        headers = ["Region", "Product", "Sales", "Quantity"]
        before_data = [
            ["North", "Widget A", "1000", "10"],
            ["South", "Widget B", "2000", "20"],
            ["East", "Widget C", "1500", "15"],
            ["West", "Widget D", "3000", "30"],
        ]
        after_data = [
            ["North", "Widget A", "1200", "10"],  # Sales changed
            ["South", "Widget B", "2000", "25"],  # Quantity changed
            # East row removed
            ["West", "Widget D", "3000", "30"],  # Unchanged
            ["Central", "Widget E", "2500", "25"],  # New row added
        ]

        before_csv = generate_basic_csv(before_data, headers)
        after_csv = generate_basic_csv(after_data, headers)
        return before_csv, after_csv

    @staticmethod
    def different_formats() -> tuple[str, str]:
        """Generate CSV files with different formatting (encoding, delimiters)."""
        headers = ["Region", "Product", "Sales", "Quantity"]
        data = [
            ["North", "Widget A", "1000", "10"],
            ["South", "Widget B", "2000", "20"],
        ]

        # UTF-8 with comma delimiter
        before_csv = generate_basic_csv(data, headers, delimiter=",")
        # UTF-8-BOM with semicolon delimiter
        after_csv = generate_basic_csv(data, headers, delimiter=";", add_bom=True)

        return before_csv, after_csv

    @staticmethod
    def with_anaplan_page_selector() -> tuple[str, str]:
        """Generate CSV files with Anaplan page selector lines."""
        headers = ["Region", "Product", "Sales", "Quantity"]
        data = [
            ["North", "Widget A", "1000", "10"],
            ["South", "Widget B", "2000", "20"],
        ]

        before_csv = generate_basic_csv(
            data, headers, anaplan_page_selector="Page Selector: All Regions"
        )
        after_csv = generate_basic_csv(
            data, headers, anaplan_page_selector="Page Selector: All Regions"
        )

        return before_csv, after_csv

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
        before_data = [
            ["1", "North", "WA", "Widget A", "1000.50", "10", "2024-01-01"],
            ["2", "South", "WB", "Widget B", "2000.75", "20", "2024-01-01"],
            ["3", "East", "WC", "Widget C", "1500.25", "15", "2024-01-01"],
        ]
        after_data = [
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

        before_csv = generate_basic_csv(before_data, headers)
        after_csv = generate_basic_csv(after_data, headers)
        return before_csv, after_csv


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
        Tuple of (before_file_path, after_file_path)
    """
    # Get the scenario method
    scenario_method = getattr(TestScenarios, scenario_name)
    before_content, after_content = scenario_method()

    # Create file paths
    before_path = temp_dir / f"{file_prefix}_before.csv"
    after_path = temp_dir / f"{file_prefix}_after.csv"

    # Save files
    save_csv_file(before_path, before_content)
    save_csv_file(after_path, after_content)

    return before_path, after_path
