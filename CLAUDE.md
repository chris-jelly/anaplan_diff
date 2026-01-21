# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Anaplan CSV Diff Tool** - A Python CLI tool that compares two CSV exports from Anaplan and shows what changed between them. The tool automatically detects dimensions and displays differences in a clean terminal format.

**Core Interface**: `anaplan-diff baseline.csv comparison.csv` (zero configuration needed)

**CSV Export**: `anaplan-diff baseline.csv comparison.csv --output results.csv` (optional CSV export)

**Current Status**: ✅ **Fully implemented and production-ready.** All core functionality is complete with 64 passing tests. The tool successfully handles CSV comparison, automatic dimension detection, rich terminal output, and CSV export.

## Development Commands

```bash
# Setup development environment (creates venv and installs all dependencies)
uv sync

# Add new dependencies
uv add polars typer rich  # runtime dependencies
uv add --dev pytest ruff  # development dependencies

# Format code (run after any Python file changes)
uv run ruff format

# Lint code
uv run ruff check

# Run tests
uv run pytest

# Run specific test
uv run pytest tests/test_basic.py::test_function_name

# Build package
uv build

# Install in development mode (alternative to uv sync)
uv pip install -e .
```

## Architecture & Core Components

The tool follows a pipeline architecture with these key components:

### 1. File Analysis (`anaplan_diff/detector.py`)
- **CSVInfo dataclass**: Stores detected encoding, delimiter, header info ✅ Implemented
- **File analysis functions**: Auto-detects CSV format parameters ✅ Implemented
- Handles Anaplan-specific formats (page selector lines, BOM, various encodings) ✅ Implemented
- **Data Type Support**: Accepts any data type in all columns (strings, booleans, numbers) ✅ Implemented

### 2. Dimension Detection (`anaplan_diff/detector.py`)
- **Position-based detection**: Uses Tabular Single Column format structure ✅ Implemented
- Logic: All columns except last are dimensions (data type independent) ✅ Implemented
- Supports all data types in dimension columns (text, numbers, booleans) ✅ Implemented
- Critical for proper comparison grouping ✅ Implemented

### 3. Comparison Engine (`anaplan_diff/comparator.py`)
- **ComparisonResult dataclass**: Structured diff results ✅ Implemented
- **Functional comparison**: Core comparison logic using polars merge operations ✅ Implemented
- Identifies unchanged, changed, added, and removed rows based on dimension keys ✅ Implemented
- **Smart data type handling**: Numeric measures get change/percentage, non-numeric get before/after ✅ Implemented
- Handles string-encoded numbers by casting to Float64 for change calculations ✅ Implemented

### 4. Terminal Output & Export (`anaplan_diff/formatter.py`)
- **Direct console output functions**: Progress, error, and success messages ✅ Implemented
- Uses Rich library for formatted console output with tables and colors ✅ Implemented
- Displays summary statistics and detailed change listings ✅ Implemented
- Shows percentage changes for numeric values ✅ Implemented
- Limits output to prevent overwhelming (first 20 changes, first 10 additions/removals) ✅ Implemented
- **CSV export function**: Exports all changes to a single CSV file with change_type tags ✅ Implemented

### 5. CLI Interface (`anaplan_diff/cli.py`)
- Typer-based command interface ✅ Implemented
- Orchestrates the full pipeline: analyze → detect → compare → format → export ✅ Implemented
- Uses Railway-Oriented Programming with Result types for error handling ✅ Implemented
- Optional `--output/-o` flag for CSV export ✅ Implemented

### 6. Pipeline (`anaplan_diff/pipeline.py`)
- Functional pipeline composition using returns library ✅ Implemented
- Validates file paths, analyzes CSVs, loads dataframes, detects dimensions, executes comparison ✅ Implemented
- Clean separation of I/O operations from pure functions ✅ Implemented

## Current Implementation Status

**Completed** ✅:
- Project structure and package configuration
- Dataclass definitions (CSVInfo, ComparisonResult)
- CLI command structure with typer
- File format detection and encoding handling
- CSV parsing with Anaplan-specific handling
- Position-based dimension detection
- DataFrame comparison logic with merge operations
- Rich terminal output formatting with tables and colors
- Full pipeline integration with Railway-Oriented Programming
- Comprehensive test suite (64 tests covering all functionality)
- Error/success/progress message printing
- Numeric change calculations (absolute and percentage)
- Support for non-numeric measures (strings, booleans)
- CSV export functionality with --output option

**Known Limitations**:
- In-memory processing (suitable for files up to ~100MB)
- Single measure column optimized (multi-measure supported but simplified output)

## Key Technical Decisions

**Build System**: Hatchling (modern Python packaging) + UV (package management)
**Dependencies**: polars (data handling), typer (CLI), rich (output), chardet (encoding detection)
**Package Management**: UV with lock file for reproducible builds (uv.lock)
**Package Structure**: Standard Python package with console script entry point
**Testing**: pytest with basic class instantiation tests

**Performance**: In-memory processing suitable for files up to ~100MB (typical Anaplan exports)

**Comparison Strategy**: Merge DataFrames on detected dimension columns, then identify row-level changes

**Auto-detection Heuristics**:
- Dimensions: Position-based - all columns except last (data type independent)
- CSV format: chardet for encoding, polars inference for delimiters  
- Headers: Skip Anaplan page selector lines if present

## Error Handling Patterns

The tool uses specific error message formats:
- File issues: `❌ Error: Could not find 'filename.csv'`
- Format issues: `❌ Error: Could not read CSV file. Try saving as UTF-8.`
- Structure issues: `❌ Error: Files have different column structures:`

## Project Structure

```
anaplan-diff/
├── anaplan_diff/           # Main package
│   ├── __init__.py
│   ├── cli.py             # CLI entry point and orchestration
│   ├── detector.py        # File analysis and dimension detection
│   ├── comparator.py      # Core comparison logic
│   └── formatter.py       # Terminal output formatting
├── tests/
│   └── test_basic.py      # Basic functionality tests
├── pyproject.toml         # Project configuration and dependencies
└── README.md              # User documentation
```

## Development Notes

- Always run `uv run ruff format` after modifying Python files
- Uses UV for fast dependency management with lock file for reproducible builds
- Uses hatchling build system with UV package management
- The tool prioritizes simplicity over configuration - most functionality should work automatically
- Focus on clear error messages since users won't have detailed CSV knowledge
- Test with various Anaplan export formats (UTF-8-BOM, different delimiters, page selectors)

## Additional Files

- `main.py`: Simple standalone script (currently just prints hello message)
- `mise.toml`: Development environment configuration (includes uv)
- `.python-version`: Python version specification  
- `uv.lock`: UV lock file for reproducible dependency installations
- `.venv/`: Virtual environment created by UV