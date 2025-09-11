"""
Terminal output formatting using Rich library.
"""

from typing import Optional
import attrs
from rich.console import Console
from rich.table import Table

from .comparator import ComparisonResult


@attrs.frozen
class FormattedOutput:
    """Immutable structured output for terminal display."""

    summary: str
    changes_table: Optional[str] = None
    additions_table: Optional[str] = None
    removals_table: Optional[str] = None
    overall_status: str = ""


# Pure functional formatting functions


def format_results(result: ComparisonResult) -> FormattedOutput:
    """Format comparison results into structured output (pure function)."""
    summary = _format_summary(result)

    changes_table = None
    if len(result.changed_rows) > 0:
        changes_table = _format_changes(result)

    additions_table = None
    if len(result.added_rows) > 0:
        additions_table = _format_additions(result)

    removals_table = None
    if len(result.removed_rows) > 0:
        removals_table = _format_removals(result)

    overall_status = _format_overall_status(result)

    return FormattedOutput(
        summary=summary,
        changes_table=changes_table,
        additions_table=additions_table,
        removals_table=removals_table,
        overall_status=overall_status,
    )


def display_formatted_output(formatted: FormattedOutput, console: Console) -> None:
    """Display formatted output to console (I/O operation)."""
    console.print(formatted.summary, markup=False)

    if formatted.changes_table:
        console.print(formatted.changes_table, markup=False)

    if formatted.additions_table:
        console.print(formatted.additions_table, markup=False)

    if formatted.removals_table:
        console.print(formatted.removals_table, markup=False)

    if formatted.overall_status:
        console.print(formatted.overall_status, markup=False)


def _format_summary(result: ComparisonResult) -> str:
    """Format summary statistics as string (pure function)."""
    unchanged_count = len(result.unchanged_rows)
    changed_count = len(result.changed_rows)
    added_count = len(result.added_rows)
    removed_count = len(result.removed_rows)

    # Create summary table
    console = Console(file=None, width=80)  # For string capture
    summary_table = Table(show_header=False, box=None, padding=(0, 2))
    summary_table.add_column("Category", style="bold")
    summary_table.add_column("Count", justify="right")

    summary_table.add_row("Total Baseline:", str(result.total_baseline))
    summary_table.add_row("Total Comparison:", str(result.total_comparison))
    summary_table.add_row("Unchanged:", f"[green]{unchanged_count}[/green]")
    summary_table.add_row("Changed:", f"[yellow]{changed_count}[/yellow]")
    summary_table.add_row("Added:", f"[blue]{added_count}[/blue]")
    summary_table.add_row("Removed:", f"[red]{removed_count}[/red]")

    # Capture table as string
    with console.capture() as capture:
        console.print()
        console.print("📊 [bold]Comparison Summary[/bold]", style="blue")
        console.print("=" * 40)
        console.print(summary_table)

    return capture.get()


def _format_overall_status(result: ComparisonResult) -> str:
    """Format overall status message (pure function)."""
    changed_count = len(result.changed_rows)
    added_count = len(result.added_rows)
    removed_count = len(result.removed_rows)

    if changed_count + added_count + removed_count == 0:
        return "\n✅ [green]No differences found - files are identical[/green]"
    else:
        total_changes = changed_count + added_count + removed_count
        return f"\n⚠️  [yellow]{total_changes} differences found[/yellow]"


def _format_changes(result: ComparisonResult) -> str:
    """Format rows with changed values as string (pure function)."""
    console = Console(file=None, width=120)

    with console.capture() as capture:
        console.print(
            f"\n🔄 [bold yellow]Changed Rows ({len(result.changed_rows)})[/bold yellow]"
        )
        console.print("-" * 40)

        if len(result.changed_rows) == 0:
            return ""

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

    return capture.get()


def _format_additions(result: ComparisonResult) -> str:
    """Format newly added rows as string (pure function)."""
    console = Console(file=None, width=120)

    with console.capture() as capture:
        console.print(
            f"\n➕ [bold blue]Added Rows ({len(result.added_rows)})[/bold blue]"
        )
        console.print("-" * 40)

        _display_simple_table_to_console(
            result.added_rows, result.dimension_columns, console, max_rows=10
        )

    return capture.get()


def _format_removals(result: ComparisonResult) -> str:
    """Format removed rows as string (pure function)."""
    console = Console(file=None, width=120)

    with console.capture() as capture:
        console.print(
            f"\n➖ [bold red]Removed Rows ({len(result.removed_rows)})[/bold red]"
        )
        console.print("-" * 40)

        _display_simple_table_to_console(
            result.removed_rows, result.dimension_columns, console, max_rows=10
        )

    return capture.get()


def _display_simple_table_to_console(
    df, dimension_columns: list[str], console: Console, max_rows: int = 10
) -> None:
    """Display a simple table of rows to console (helper for string capture)."""
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
            if isinstance(value, (int, float)):
                row_data.append(_format_number(value))
            else:
                row_data.append(str(value))
        table.add_row(*row_data)

    console.print(table)

    if len(df) > max_rows:
        remaining = len(df) - max_rows
        console.print(f"\n[dim]... and {remaining} more rows[/dim]")


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


# Legacy wrapper for backward compatibility
class TerminalFormatter:
    """Legacy wrapper for backward compatibility."""

    def __init__(self):
        self.console = Console()

    def format_results(self, result: ComparisonResult) -> None:
        """Display formatted comparison results in terminal (legacy method)."""
        formatted = format_results(result)
        display_formatted_output(formatted, self.console)

    def print_error(self, message: str) -> None:
        """Print formatted error message."""
        self.console.print(f"❌ Error: {message}", style="red")

    def print_success(self, message: str) -> None:
        """Print formatted success message."""
        self.console.print(f"✅ {message}", style="green")
