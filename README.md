# Anaplan CSV Diff Tool

A Python CLI tool that compares two CSV exports from Anaplan and shows what changed between them.

## Why This Exists

When I am making development changes in Anaplan, I usually then need a business analyst to review what I did to see if it lines up with expectations. What was the impact?

This tool automatically detects dimensions in your CSV files and presents differences in a clean, readable format - no configuration required.



## Installation

```bash
# Clone the repository
git clone <repository-url>
cd pyanaplan-diff

# Install with UV (recommended)
uv sync

# Or install with pip
pip install -e .
```

## Usage

```bash
# Basic usage - compare two CSV files
anaplan-diff before.csv after.csv

# The tool will automatically:
# - Detect CSV format and encoding
# - Identify dimension columns
# - Show added, removed, and changed rows
# - Display summary statistics
```

## Development

```bash
# Format code
uv run ruff format

# Run tests
uv run pytest

# Build package
uv build
```

Zero configuration needed - just point it at your CSV files and go.
