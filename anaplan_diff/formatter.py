"""
Terminal output formatting using Rich library.
"""

from rich.console import Console

from .comparator import ComparisonResult


class TerminalFormatter:
    """Formats comparison results for terminal display."""

    def __init__(self):
        self.console = Console()

    def format_results(self, result: ComparisonResult) -> None:
        """Display formatted comparison results in terminal."""
        # TODO: Implement terminal output formatting
        # - Display summary statistics
        # - Show detailed change listings
        # - Format percentage changes for numeric values
        # - Use Rich library for colored output
        pass

    def print_error(self, message: str) -> None:
        """Print formatted error message."""
        self.console.print(f"❌ Error: {message}", style="red")

    def print_success(self, message: str) -> None:
        """Print formatted success message."""
        self.console.print(f"✅ {message}", style="green")
