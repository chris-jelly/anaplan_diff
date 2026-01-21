"""
Terminal output formatting using Rich library.
"""

import polars as pl
from returns.result import Failure, Result, Success
from rich.console import Console
from rich.table import Table

from .comparator import ComparisonResult


# Pure helper functions


def _format_number(value) -> str:
    """Format numeric values for display (pure function)."""
    if value is None:
        return "N/A"

    # Handle very large numbers
    if abs(value) >= 1e6:
        return f"{value:,.0f}"
    elif abs(value) >= 1000:
        return f"{value:,.1f}"
    elif abs(value) >= 1:
        return f"{value:.2f}"
    else:
        return f"{value:.4f}"


# Direct console I/O functions (functional approach)


def print_progress_message(console: Console, message: str) -> None:
    """Print progress message (I/O operation)."""
    console.print(message)


def print_error_message(console: Console, message: str) -> None:
    """Print formatted error message (I/O operation)."""
    console.print(f"❌ Error: {message}", style="red")


def print_success_message(console: Console, message: str) -> None:
    """Print formatted success message (I/O operation)."""
    console.print(f"✅ {message}", style="green")


def display_comparison_results(console: Console, result: ComparisonResult) -> None:
    """Display formatted comparison results directly to console (I/O operation)."""
    _display_summary_direct(console, result)

    if len(result.changed_rows) > 0:
        _display_changes_direct(console, result)

    if len(result.added_rows) > 0:
        _display_additions_direct(console, result)

    if len(result.removed_rows) > 0:
        _display_removals_direct(console, result)

    _display_overall_status_direct(console, result)


def _display_summary_direct(console: Console, result: ComparisonResult) -> None:
    """Display summary statistics directly to console (I/O operation)."""
    unchanged_count = len(result.unchanged_rows)
    changed_count = len(result.changed_rows)
    added_count = len(result.added_rows)
    removed_count = len(result.removed_rows)

    # Create summary table
    summary_table = Table(show_header=False, box=None, padding=(0, 2))
    summary_table.add_column("Category", style="bold")
    summary_table.add_column("Count", justify="right")

    summary_table.add_row("Total Baseline:", str(result.total_baseline))
    summary_table.add_row("Total Comparison:", str(result.total_comparison))
    summary_table.add_row("Unchanged:", f"[green]{unchanged_count}[/green]")
    summary_table.add_row("Changed:", f"[yellow]{changed_count}[/yellow]")
    summary_table.add_row("Added:", f"[blue]{added_count}[/blue]")
    summary_table.add_row("Removed:", f"[red]{removed_count}[/red]")

    # Direct output to console
    console.print()
    console.print("📊 [bold]Comparison Summary[/bold]", style="blue")
    console.print("=" * 40)
    console.print(summary_table)


def _display_changes_direct(console: Console, result: ComparisonResult) -> None:
    """Display changed rows directly to console (I/O operation)."""
    console.print(
        f"\n🔄 [bold yellow]Changed Rows ({len(result.changed_rows)})[/bold yellow]"
    )
    console.print("-" * 40)

    if len(result.changed_rows) == 0:
        return

    # Create changes table
    table = Table(box=None, show_edge=False)

    # Add dimension columns
    for dim_col in result.dimension_columns:
        table.add_column(dim_col, style="dim")

    # Add value columns
    table.add_column("Baseline", justify="right", style="red")
    table.add_column("Comparison", justify="right", style="green")
    table.add_column("Change", justify="right", style="yellow")
    table.add_column("Change %", justify="right", style="yellow")

    # Show first 20 changes (to avoid overwhelming output)
    display_rows = result.changed_rows.head(20)

    for row in display_rows.iter_rows(named=True):
        row_data = []

        # Add dimension values
        for dim_col in result.dimension_columns:
            row_data.append(str(row[dim_col]))

        # Add baseline/comparison values
        baseline_val = row["baseline_value"]
        comparison_val = row["comparison_value"]

        # Check if change columns exist (only for numeric values)
        change_val = row.get("change")
        change_pct = row.get("change_percent")

        row_data.append(
            _format_number(baseline_val)
            if isinstance(baseline_val, (int, float))
            else str(baseline_val)
        )
        row_data.append(
            _format_number(comparison_val)
            if isinstance(comparison_val, (int, float))
            else str(comparison_val)
        )

        # Display change values - check if they exist and are valid numbers
        if change_val is not None and isinstance(change_val, (int, float)):
            row_data.append(_format_number(change_val))
        else:
            row_data.append("-")

        if change_pct is not None and isinstance(change_pct, (int, float)):
            row_data.append(f"{change_pct:.1f}%")
        else:
            row_data.append("-")

        table.add_row(*row_data)

    console.print(table)

    if len(result.changed_rows) > 20:
        remaining = len(result.changed_rows) - 20
        console.print(f"\n[dim]... and {remaining} more changed rows[/dim]")


def _display_additions_direct(console: Console, result: ComparisonResult) -> None:
    """Display added rows directly to console (I/O operation)."""
    console.print(f"\n➕ [bold blue]Added Rows ({len(result.added_rows)})[/bold blue]")
    console.print("-" * 40)

    _display_simple_table_direct(
        console, result.added_rows, result.dimension_columns, max_rows=10
    )


def _display_removals_direct(console: Console, result: ComparisonResult) -> None:
    """Display removed rows directly to console (I/O operation)."""
    console.print(
        f"\n➖ [bold red]Removed Rows ({len(result.removed_rows)})[/bold red]"
    )
    console.print("-" * 40)

    _display_simple_table_direct(
        console, result.removed_rows, result.dimension_columns, max_rows=10
    )


def _display_overall_status_direct(console: Console, result: ComparisonResult) -> None:
    """Display overall status message directly to console (I/O operation)."""
    changed_count = len(result.changed_rows)
    added_count = len(result.added_rows)
    removed_count = len(result.removed_rows)

    if changed_count + added_count + removed_count == 0:
        console.print("\n✅ [green]No differences found - files are identical[/green]")
    else:
        total_changes = changed_count + added_count + removed_count
        console.print(f"\n⚠️  [yellow]{total_changes} differences found[/yellow]")


def _display_simple_table_direct(
    console: Console, df, dimension_columns: list[str], max_rows: int = 10
) -> None:
    """Display a simple table of rows directly to console (I/O operation)."""
    if len(df) == 0:
        return

    table = Table(box=None, show_edge=False)

    # Add all columns
    for col in df.columns:
        table.add_column(col, style="dim" if col in dimension_columns else "bold")

    # Show limited number of rows
    display_rows = df.head(max_rows)

    for row in display_rows.iter_rows(named=True):
        row_data = []
        for col in df.columns:
            value = row[col]
            if isinstance(value, int | float):
                row_data.append(_format_number(value))
            else:
                row_data.append(str(value))
        table.add_row(*row_data)

    console.print(table)

    if len(df) > max_rows:
        remaining = len(df) - max_rows
        console.print(f"\n[dim]... and {remaining} more rows[/dim]")


def export_to_csv(result: ComparisonResult, output_path: str) -> Result[None, str]:
    """
    Export comparison results to a CSV file.

    Creates a single CSV file with all changes, additions, and removals,
    each tagged with a change_type column.
    """
    try:
        # Build list of dataframes with change type tags
        dfs_to_export = []

        # Changed rows
        if len(result.changed_rows) > 0:
            changed_df = result.changed_rows.with_columns(
                pl.lit("CHANGED").alias("change_type")
            )
            dfs_to_export.append(changed_df)

        # Added rows
        if len(result.added_rows) > 0:
            # For added rows, we need to match the schema of changed rows
            # Add placeholder columns for baseline values and changes
            added_df = result.added_rows.with_columns(
                pl.lit("ADDED").alias("change_type")
            )

            # If changed_rows has baseline/comparison/change columns, add placeholders
            if (
                len(result.changed_rows) > 0
                and "baseline_value" in result.changed_rows.columns
            ):
                # Get the measure column name (the original column before _value suffix)
                measure_col = (
                    result.measure_columns[0] if result.measure_columns else None
                )
                if measure_col and measure_col in added_df.columns:
                    added_df = added_df.rename({measure_col: "comparison_value"})
                    added_df = added_df.with_columns(
                        [
                            pl.lit(None).alias("baseline_value"),
                            pl.lit(None).alias("change"),
                            pl.lit(None).alias("change_percent"),
                        ]
                    )

            dfs_to_export.append(added_df)

        # Removed rows
        if len(result.removed_rows) > 0:
            removed_df = result.removed_rows.with_columns(
                pl.lit("REMOVED").alias("change_type")
            )

            # Match schema with changed rows if needed
            if (
                len(result.changed_rows) > 0
                and "baseline_value" in result.changed_rows.columns
            ):
                measure_col = (
                    result.measure_columns[0] if result.measure_columns else None
                )
                if measure_col and measure_col in removed_df.columns:
                    removed_df = removed_df.rename({measure_col: "baseline_value"})
                    removed_df = removed_df.with_columns(
                        [
                            pl.lit(None).alias("comparison_value"),
                            pl.lit(None).alias("change"),
                            pl.lit(None).alias("change_percent"),
                        ]
                    )

            dfs_to_export.append(removed_df)

        # Check if there's anything to export
        if not dfs_to_export:
            return Failure("No changes to export")

        # Combine all dataframes
        # If schemas don't match exactly, align them
        if len(dfs_to_export) > 1:
            # Get all unique columns
            all_columns = set()
            for df in dfs_to_export:
                all_columns.update(df.columns)

            # Align schemas by adding missing columns as nulls
            aligned_dfs = []
            for df in dfs_to_export:
                for col in all_columns:
                    if col not in df.columns:
                        df = df.with_columns(pl.lit(None).alias(col))
                # Reorder columns to match (dimension cols, then others, then change_type)
                col_order = [c for c in df.columns if c != "change_type"] + [
                    "change_type"
                ]
                df = df.select([c for c in col_order if c in df.columns])
                aligned_dfs.append(df)

            combined_df = pl.concat(aligned_dfs, how="diagonal")
        else:
            combined_df = dfs_to_export[0]

        # Write to CSV
        combined_df.write_csv(output_path)

        return Success(None)

    except Exception as e:
        return Failure(f"Failed to write CSV: {e}")
