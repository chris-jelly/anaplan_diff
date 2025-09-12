"""CLI interface for the Anaplan CSV diff tool."""

from pathlib import Path
from typing import Annotated

import typer
from returns.result import Failure, Success

from .formatter import TerminalFormatter
from .pipeline import run_csv_diff_pipeline

app = typer.Typer(help="Compare two CSV exports from Anaplan and show changes")


@app.command()
def diff(
    baseline: Annotated[Path, typer.Argument(help="Path to the 'baseline' CSV file")],
    comparison: Annotated[Path, typer.Argument(help="Path to the 'comparison' CSV file")],
) -> None:
    """Compare two CSV files and display the differences."""
    formatter = TerminalFormatter()

    # Progress indicators (side effects)
    formatter.console.print("🔍 Analyzing CSV files...")
    formatter.console.print("📊 Loading data...")
    formatter.console.print("🔎 Detecting dimensions...")
    formatter.console.print("⚖️  Comparing data...")

    # Execute pipeline
    result = run_csv_diff_pipeline(str(baseline), str(comparison))

    # Handle result (I/O operation)
    match result:
        case Success(comparison_result):
            formatter.console.print(
                f"Detected dimensions: {', '.join(comparison_result.dimension_columns)}"
            )
            formatter.format_results(comparison_result)
        case Failure(error_message):
            formatter.print_error(error_message)
            raise typer.Exit(1)


def main() -> None:
    """Entry point for the CLI application."""
    app()


if __name__ == "__main__":
    main()
