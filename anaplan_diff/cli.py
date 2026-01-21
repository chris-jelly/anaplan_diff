"""CLI interface for the Anaplan CSV diff tool."""

from pathlib import Path
from typing import Annotated

import typer
from returns.result import Failure, Success

from rich.console import Console

from .formatter import (
    display_comparison_results,
    export_to_csv,
    print_error_message,
    print_progress_message,
    print_success_message,
)
from .pipeline import run_csv_diff_pipeline

app = typer.Typer(help="Compare two CSV exports from Anaplan and show changes")


@app.command()
def diff(
    baseline: Annotated[Path, typer.Argument(help="Path to the 'baseline' CSV file")],
    comparison: Annotated[
        Path, typer.Argument(help="Path to the 'comparison' CSV file")
    ],
    output: Annotated[
        Path | None,
        typer.Option(
            "--output",
            "-o",
            help="Path to export results as CSV (optional)",
        ),
    ] = None,
) -> None:
    """Compare two CSV files and display the differences."""
    console = Console()

    # Progress indicators (side effects)
    print_progress_message(console, "🔍 Analyzing CSV files...")
    print_progress_message(console, "📊 Loading data...")
    print_progress_message(console, "🔎 Detecting dimensions...")
    print_progress_message(console, "⚖️  Comparing data...")

    # Execute pipeline
    result = run_csv_diff_pipeline(str(baseline), str(comparison))

    # Handle result (I/O operation)
    match result:
        case Success(comparison_result):
            print_progress_message(
                console,
                f"Detected dimensions: {', '.join(comparison_result.dimension_columns)}",
            )
            display_comparison_results(console, comparison_result)

            # Export to CSV if output path is specified
            if output:
                export_result = export_to_csv(comparison_result, str(output))
                match export_result:
                    case Success(_):
                        print_success_message(console, f"Results exported to {output}")
                    case Failure(error_message):
                        print_error_message(console, f"Export failed: {error_message}")
                        raise typer.Exit(1)
        case Failure(error_message):
            print_error_message(console, error_message)
            raise typer.Exit(1)


def main() -> None:
    """Entry point for the CLI application."""
    app()


if __name__ == "__main__":
    main()
