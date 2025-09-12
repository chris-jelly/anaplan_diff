"""
Terminal output formatting using Rich library.
"""

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
        change_val = row["change"]
        change_pct = row["change_percent"]

        row_data.append(_format_number(baseline_val))
        row_data.append(_format_number(comparison_val))
        row_data.append(_format_number(change_val))
        row_data.append(f"{change_pct:.1f}%" if change_pct is not None else "N/A")

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
