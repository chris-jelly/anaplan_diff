"""
Terminal output formatting using Rich library.
"""

from rich.console import Console
from rich.table import Table

from .comparator import ComparisonResult


class TerminalFormatter:
    """Formats comparison results for terminal display."""

    def __init__(self):
        self.console = Console()

    def format_results(self, result: ComparisonResult) -> None:
        """Display formatted comparison results in terminal."""
        # Display summary first
        self._display_summary(result)

        # Show detailed changes if any exist
        if len(result.changed_rows) > 0:
            self._display_changes(result)

        if len(result.added_rows) > 0:
            self._display_additions(result)

        if len(result.removed_rows) > 0:
            self._display_removals(result)

    def _display_summary(self, result: ComparisonResult) -> None:
        """Display summary statistics."""
        unchanged_count = len(result.unchanged_rows)
        changed_count = len(result.changed_rows)
        added_count = len(result.added_rows)
        removed_count = len(result.removed_rows)

        self.console.print()
        self.console.print("📊 [bold]Comparison Summary[/bold]", style="blue")
        self.console.print("=" * 40)

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

        self.console.print(summary_table)

        # Show overall status
        if changed_count + added_count + removed_count == 0:
            self.console.print(
                "\n✅ [green]No differences found - files are identical[/green]"
            )
        else:
            total_changes = changed_count + added_count + removed_count
            self.console.print(
                f"\n⚠️  [yellow]{total_changes} differences found[/yellow]"
            )

    def _display_changes(self, result: ComparisonResult) -> None:
        """Display rows with changed values."""
        self.console.print(
            f"\n🔄 [bold yellow]Changed Rows ({len(result.changed_rows)})[/bold yellow]"
        )
        self.console.print("-" * 40)

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

            row_data.append(self._format_number(baseline_val))
            row_data.append(self._format_number(comparison_val))
            row_data.append(self._format_number(change_val))
            row_data.append(f"{change_pct:.1f}%" if change_pct is not None else "N/A")

            table.add_row(*row_data)

        self.console.print(table)

        if len(result.changed_rows) > 20:
            remaining = len(result.changed_rows) - 20
            self.console.print(f"\n[dim]... and {remaining} more changed rows[/dim]")

    def _display_additions(self, result: ComparisonResult) -> None:
        """Display newly added rows."""
        self.console.print(
            f"\n➕ [bold blue]Added Rows ({len(result.added_rows)})[/bold blue]"
        )
        self.console.print("-" * 40)

        self._display_simple_table(
            result.added_rows, result.dimension_columns, max_rows=10
        )

    def _display_removals(self, result: ComparisonResult) -> None:
        """Display removed rows."""
        self.console.print(
            f"\n➖ [bold red]Removed Rows ({len(result.removed_rows)})[/bold red]"
        )
        self.console.print("-" * 40)

        self._display_simple_table(
            result.removed_rows, result.dimension_columns, max_rows=10
        )

    def _display_simple_table(
        self, df, dimension_columns: list[str], max_rows: int = 10
    ) -> None:
        """Display a simple table of rows."""
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
                    row_data.append(self._format_number(value))
                else:
                    row_data.append(str(value))
            table.add_row(*row_data)

        self.console.print(table)

        if len(df) > max_rows:
            remaining = len(df) - max_rows
            self.console.print(f"\n[dim]... and {remaining} more rows[/dim]")

    def _format_number(self, value) -> str:
        """Format numeric values for display."""
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

    def print_error(self, message: str) -> None:
        """Print formatted error message."""
        self.console.print(f"❌ Error: {message}", style="red")

    def print_success(self, message: str) -> None:
        """Print formatted success message."""
        self.console.print(f"✅ {message}", style="green")
