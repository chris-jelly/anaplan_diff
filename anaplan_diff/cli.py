"""
CLI interface for the Anaplan CSV diff tool.
"""

from pathlib import Path

import typer

from .formatter import TerminalFormatter

app = typer.Typer(help="Compare two CSV exports from Anaplan and show changes")


@app.command()
def diff(
    before: Path = typer.Argument(..., help="Path to the 'before' CSV file"),
    after: Path = typer.Argument(..., help="Path to the 'after' CSV file"),
) -> None:
    """Compare two CSV files and display the differences."""
    formatter = TerminalFormatter()

    # TODO: Implement the full pipeline
    # 1. Validate file paths exist
    # 2. Analyze both CSV files
    # 3. Load DataFrames
    # 4. Detect dimension columns
    # 5. Compare the data
    # 6. Format and display results

    try:
        # Placeholder implementation
        formatter.print_success("Analysis complete - implementation needed")
    except Exception as e:
        formatter.print_error(str(e))


def main() -> None:
    """Entry point for the CLI application."""
    app()


if __name__ == "__main__":
    main()
