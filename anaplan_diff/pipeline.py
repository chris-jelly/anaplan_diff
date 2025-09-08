"""Pipeline for CSV comparison operations."""

from pathlib import Path
from typing import Tuple

from returns.result import Failure, Result, Success

from .comparator import ComparisonResult, compare_dataframes
from .detector import CSVInfo, analyze_file, detect_dimensions, load_dataframe


def validate_file_paths(
    baseline_path: str, comparison_path: str
) -> Result[Tuple[Path, Path], str]:
    """Validate that both file paths exist."""
    baseline = Path(baseline_path)
    comparison = Path(comparison_path)

    if not baseline.exists():
        return Failure(f"Could not find '{baseline_path}'")
    if not comparison.exists():
        return Failure(f"Could not find '{comparison_path}'")

    return Success((baseline, comparison))


def analyze_csv_files(paths: Tuple[Path, Path]) -> Result[Tuple[CSVInfo, CSVInfo], str]:
    """Analyze both CSV files (I/O operation)."""
    baseline_path, comparison_path = paths

    return analyze_file(str(baseline_path)).bind(
        lambda baseline_info: analyze_file(str(comparison_path)).bind(
            lambda comparison_info: Success((baseline_info, comparison_info))
        )
    )


def load_csv_dataframes(
    file_infos: Tuple[CSVInfo, CSVInfo], paths: Tuple[Path, Path]
) -> Result[Tuple[object, object], str]:
    """Load both CSV files as DataFrames (I/O operation)."""
    baseline_info, comparison_info = file_infos
    baseline_path, comparison_path = paths

    return load_dataframe(str(baseline_path), baseline_info).bind(
        lambda baseline_df: load_dataframe(str(comparison_path), comparison_info).bind(
            lambda comparison_df: Success((baseline_df, comparison_df))
        )
    )


def detect_comparison_dimensions(
    dataframes: Tuple[object, object],
) -> Result[Tuple[object, object, list], str]:
    """Detect dimension columns from the baseline DataFrame."""
    baseline_df, comparison_df = dataframes

    return detect_dimensions(baseline_df).bind(
        lambda dimensions: Success((baseline_df, comparison_df, dimensions))
    )


def execute_comparison(
    data: Tuple[object, object, list],
) -> Result[ComparisonResult, str]:
    """Execute the DataFrame comparison."""
    baseline_df, comparison_df, dimension_columns = data

    return compare_dataframes(
        baseline_df, comparison_df, dimension_columns, comparison_tolerance=1e-10
    )


def run_csv_diff_pipeline(
    baseline_path: str, comparison_path: str
) -> Result[ComparisonResult, str]:
    """Execute the complete CSV diff pipeline."""
    return (
        validate_file_paths(baseline_path, comparison_path)
        .bind(
            lambda paths: analyze_csv_files(paths).bind(
                lambda infos: load_csv_dataframes(infos, paths)
            )
        )
        .bind(detect_comparison_dimensions)
        .bind(execute_comparison)
    )
