"""Comparison logic for CSV data."""

from typing import List, Optional

import attrs
import polars as pl
from returns.result import Failure, Result, Success

try:
    from tests.fixtures.csv_generators import AnaplanFormat
except ImportError:
    from enum import Enum

    class AnaplanFormat(Enum):
        TABULAR_SINGLE_COLUMN = "tabular_single_column"
        TABULAR_MULTI_COLUMN = "tabular_multi_column"


@attrs.frozen
class ComparisonResult:
    """Immutable structured results of CSV comparison."""

    unchanged_rows: pl.DataFrame
    changed_rows: pl.DataFrame
    added_rows: pl.DataFrame
    removed_rows: pl.DataFrame
    dimension_columns: List[str]
    measure_columns: List[str]
    total_baseline: int
    total_comparison: int
    format_type: Optional[AnaplanFormat] = None

    @property
    def has_changes(self) -> bool:
        """Check if there are any changes."""
        return (
            len(self.changed_rows) > 0
            or len(self.added_rows) > 0
            or len(self.removed_rows) > 0
        )

    @property
    def total_changes(self) -> int:
        """Get total number of changes."""
        return len(self.changed_rows) + len(self.added_rows) + len(self.removed_rows)


def compare_dataframes(
    baseline_df: pl.DataFrame,
    comparison_df: pl.DataFrame,
    dimension_columns: List[str],
    format_type: Optional[AnaplanFormat] = None,
    comparison_tolerance: float = 1e-10,
) -> Result[ComparisonResult, str]:
    """Compare two DataFrames and identify changes."""
    if comparison_tolerance <= 0:
        return Failure("Comparison tolerance must be positive")

    return _validate_dataframes(baseline_df, comparison_df, dimension_columns).bind(
        lambda _: _perform_comparison(
            baseline_df,
            comparison_df,
            dimension_columns,
            format_type,
            comparison_tolerance,
        )
    )


def _validate_dataframes(
    baseline_df: pl.DataFrame,
    comparison_df: pl.DataFrame,
    dimension_columns: List[str],
) -> Result[None, str]:
    """Validate DataFrames have compatible structure."""
    if not dimension_columns:
        return Failure("At least one dimension column is required")

    if baseline_df.shape[0] == 0:
        return Failure("Baseline DataFrame is empty")
    if comparison_df.shape[0] == 0:
        return Failure("Comparison DataFrame is empty")

    if baseline_df.columns != comparison_df.columns:
        missing_in_comparison = set(baseline_df.columns) - set(comparison_df.columns)
        missing_in_baseline = set(comparison_df.columns) - set(baseline_df.columns)
        error_msg = "Files have different column structures"
        if missing_in_comparison:
            error_msg += f". Missing in comparison: {missing_in_comparison}"
        if missing_in_baseline:
            error_msg += f". Missing in baseline: {missing_in_baseline}"
        return Failure(error_msg)

    for col in dimension_columns:
        if col not in baseline_df.columns:
            return Failure(f"Dimension column '{col}' not found in data")

    return Success(None)


def _perform_comparison(
    baseline_df: pl.DataFrame,
    comparison_df: pl.DataFrame,
    dimension_columns: List[str],
    format_type: Optional[AnaplanFormat],
    comparison_tolerance: float,
) -> Result[ComparisonResult, str]:
    """Perform the actual comparison."""
    try:
        # Get measure columns
        measure_columns = [
            col for col in baseline_df.columns if col not in dimension_columns
        ]
        if not measure_columns:
            return Failure("No measure columns found for comparison")

        # Add composite keys
        baseline_with_key = _add_composite_key(baseline_df, dimension_columns)
        comparison_with_key = _add_composite_key(comparison_df, dimension_columns)

        # Perform comparisons
        unchanged_rows = _find_unchanged_rows(
            baseline_with_key,
            comparison_with_key,
            dimension_columns,
            measure_columns,
            comparison_tolerance,
        )
        changed_rows = _find_changed_rows(
            baseline_with_key,
            comparison_with_key,
            dimension_columns,
            measure_columns,
            comparison_tolerance,
        )
        added_rows = _find_added_rows(
            baseline_with_key, comparison_with_key, dimension_columns
        )
        removed_rows = _find_removed_rows(
            baseline_with_key, comparison_with_key, dimension_columns
        )

        return Success(
            ComparisonResult(
                unchanged_rows=unchanged_rows,
                changed_rows=changed_rows,
                added_rows=added_rows,
                removed_rows=removed_rows,
                dimension_columns=dimension_columns,
                measure_columns=measure_columns,
                total_baseline=len(baseline_df),
                total_comparison=len(comparison_df),
                format_type=format_type or AnaplanFormat.TABULAR_MULTI_COLUMN,
            )
        )
    except Exception as e:
        return Failure(f"Comparison failed: {e}")


def _add_composite_key(df: pl.DataFrame, dimension_columns: List[str]) -> pl.DataFrame:
    """Add composite key column."""
    key_expr = pl.concat_str(
        [pl.col(col).cast(pl.Utf8) for col in dimension_columns], separator="||"
    )
    return df.with_columns(key_expr.alias("_composite_key"))


def _find_unchanged_rows(
    baseline_df: pl.DataFrame,
    comparison_df: pl.DataFrame,
    dimension_columns: List[str],
    measure_columns: List[str],
    comparison_tolerance: float,
) -> pl.DataFrame:
    """Find unchanged rows."""
    joined = baseline_df.join(
        comparison_df, on="_composite_key", how="inner", suffix="_comparison"
    )

    # Check all measures for equality
    equality_conditions = []
    for measure in measure_columns:
        measure_comparison = f"{measure}_comparison"
        if joined[measure].dtype.is_numeric():
            condition = (
                pl.col(measure) - pl.col(measure_comparison)
            ).abs() < comparison_tolerance
        else:
            condition = pl.col(measure) == pl.col(measure_comparison)
        equality_conditions.append(condition)

    if equality_conditions:
        unchanged = joined.filter(pl.all_horizontal(equality_conditions))
    else:
        unchanged = joined.filter(pl.lit(False))

    return unchanged.select(dimension_columns + measure_columns)


def _find_changed_rows(
    baseline_df: pl.DataFrame,
    comparison_df: pl.DataFrame,
    dimension_columns: List[str],
    measure_columns: List[str],
    comparison_tolerance: float,
) -> pl.DataFrame:
    """Find changed rows."""
    joined = baseline_df.join(
        comparison_df, on="_composite_key", how="inner", suffix="_comparison"
    )

    # Check which measures differ
    difference_conditions = []
    for measure in measure_columns:
        measure_comparison = f"{measure}_comparison"
        if joined[measure].dtype.is_numeric():
            condition = (
                pl.col(measure) - pl.col(measure_comparison)
            ).abs() >= comparison_tolerance
        else:
            condition = pl.col(measure) != pl.col(measure_comparison)
        difference_conditions.append(condition)

    if difference_conditions:
        changed = joined.filter(pl.any_horizontal(difference_conditions))
    else:
        return pl.DataFrame()

    # Build result with baseline/comparison values - simplified for single measure case
    if len(measure_columns) == 1:
        measure = measure_columns[0]
        measure_comparison = f"{measure}_comparison"

        result_columns = dimension_columns + [
            pl.col(measure).alias("baseline_value"),
            pl.col(measure_comparison).alias("comparison_value"),
            (pl.col(measure_comparison) - pl.col(measure)).alias("change"),
            (
                (pl.col(measure_comparison) - pl.col(measure))
                / pl.when(pl.col(measure) != 0)
                .then(pl.col(measure))
                .otherwise(pl.lit(None))
                * 100
            ).alias("change_percent"),
        ]
        return changed.select(result_columns)

    # For multi-measure, return simplified format
    return changed.select(dimension_columns + measure_columns)


def _find_added_rows(
    baseline_df: pl.DataFrame,
    comparison_df: pl.DataFrame,
    dimension_columns: List[str],
) -> pl.DataFrame:
    """Find added rows."""
    added = comparison_df.join(
        baseline_df.select(["_composite_key"]), on="_composite_key", how="anti"
    )
    all_columns = [col for col in comparison_df.columns if col != "_composite_key"]
    return added.select(all_columns)


def _find_removed_rows(
    baseline_df: pl.DataFrame,
    comparison_df: pl.DataFrame,
    dimension_columns: List[str],
) -> pl.DataFrame:
    """Find removed rows."""
    removed = baseline_df.join(
        comparison_df.select(["_composite_key"]), on="_composite_key", how="anti"
    )
    all_columns = [col for col in baseline_df.columns if col != "_composite_key"]
    return removed.select(all_columns)


# Compatibility wrapper for tests
class DataComparator:
    """Compatibility wrapper for functional comparator."""

    def __init__(self, comparison_tolerance: float = 1e-10):
        if comparison_tolerance <= 0:
            raise ValueError("Comparison tolerance must be positive")
        self.comparison_tolerance = comparison_tolerance

    def compare(self, baseline_df, comparison_df, dimension_columns, format_type=None):
        result = compare_dataframes(
            baseline_df,
            comparison_df,
            dimension_columns,
            format_type,
            self.comparison_tolerance,
        )
        if isinstance(result, Success):
            return result.unwrap()
        else:
            raise ValueError(result.failure())
