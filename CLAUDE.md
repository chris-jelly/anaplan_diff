# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Anaplan CSV Diff Tool** - A Python CLI tool that compares two CSV exports from Anaplan and shows what changed between them. The tool automatically detects dimensions and displays differences in a clean terminal format.

**Core Interface**: `anaplan-diff baseline.csv comparison.csv` (zero configuration needed)

**Current Status**: Project skeleton is established with package structure and dependencies configured. Core functionality is not yet implemented - all main classes have placeholder methods with TODO comments.

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

## Architecture & Core Components (Planned)

The tool follows a pipeline architecture with these key components:

### 1. File Analysis (`anaplan_diff/detector.py`)
- **CSVInfo dataclass**: Stores detected encoding, delimiter, header info ✅ Defined
- **FileAnalyzer class**: Auto-detects CSV format parameters ✅ Implemented
- Handles Anaplan-specific formats (page selector lines, BOM, various encodings) ✅ Implemented
- **Data Type Support**: Accepts any data type in all columns (strings, booleans, numbers) ✅ Implemented

### 2. Dimension Detection (`anaplan_diff/detector.py`)
- **Position-based detection**: Uses Tabular Single Column format structure ✅ Implemented
- Logic: All columns except last are dimensions (data type independent) ✅ Implemented
- Supports all data types in dimension columns (text, numbers, booleans) ✅ Implemented
- Critical for proper comparison grouping ✅ Implemented

### 3. Comparison Engine (`anaplan_diff/comparator.py`)
- **ComparisonResult dataclass**: Structured diff results ✅ Defined
- **Functional comparison**: Core comparison logic using polars merge operations ✅ Implemented
- Identifies unchanged, changed, added, and removed rows based on dimension keys ✅ Implemented
- **Smart data type handling**: Numeric measures get change/percentage, non-numeric get before/after ✅ Implemented

### 4. Terminal Output (`anaplan_diff/formatter.py`)
- **TerminalFormatter class**: Basic error/success printing ✅ Partial
- Uses Rich library for formatted console output ⚠️ TODO
- Displays summary statistics and detailed change listings ⚠️ TODO
- Shows percentage changes for numeric values ⚠️ TODO

### 5. CLI Interface (`anaplan_diff/cli.py`)
- Typer-based command interface ✅ Basic structure
- Orchestrates the full pipeline: analyze → detect → compare → format ⚠️ TODO

## Current Implementation Status

**Completed**:
- Project structure and package configuration
- Basic dataclass definitions (CSVInfo, ComparisonResult)  
- CLI command structure with typer
- Error/success message printing in formatter
- Basic test structure

**TODO** (Core functionality to implement):
- File format detection and encoding handling
- CSV parsing with Anaplan-specific handling
- Dimension detection heuristics
- DataFrame comparison logic
- Rich terminal output formatting
- Full pipeline integration in CLI

## Key Technical Decisions

**Build System**: Hatchling (modern Python packaging) + UV (package management)
**Dependencies**: polars (data handling), typer (CLI), rich (output), chardet (encoding detection)
**Package Management**: UV with lock file for reproducible builds (uv.lock)
**Package Structure**: Standard Python package with console script entry point
**Testing**: pytest with basic class instantiation tests

**Performance**: In-memory processing suitable for files up to ~100MB (typical Anaplan exports)

**Planned Comparison Strategy**: Merge DataFrames on detected dimension columns, then identify row-level changes

**Planned Auto-detection Heuristics**:
- Dimensions: `dtype == 'object'` OR low cardinality OR Anaplan keywords
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