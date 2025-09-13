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
anaplan-diff baseline.csv comparison.csv

# The tool will automatically:
# - Detect CSV format and encoding
# - Identify dimension columns
# - Show added, removed, and changed rows
# - Display summary statistics
```

## Example

Here's what you can expect when running the tool on typical Anaplan CSV exports:

### Input Files

**examples/baseline.csv**
```csv
Line_Item,Region,Product,Value
Revenue,North,Widget A,1000
Revenue,South,Widget B,2000
Revenue,East,Widget C,1500
Revenue,West,Widget D,3000
Costs,North,Widget A,300
Costs,South,Widget B,600
Costs,East,Widget C,450
Costs,West,Widget D,900
```

**examples/comparison.csv**
```csv
Line_Item,Region,Product,Value
Revenue,North,Widget A,1200
Revenue,South,Widget B,2000
Revenue,West,Widget D,3000
Revenue,Central,Widget E,2500
Costs,North,Widget A,350
Costs,South,Widget B,600
Costs,West,Widget D,900
Costs,Central,Widget E,750
```

### Command
```bash
anaplan-diff examples/baseline.csv examples/comparison.csv
```

### Output
```
🔍 Analyzing CSV files...
📊 Loading data...
🔎 Detecting dimensions...
⚖️  Comparing data...
Detected dimensions: Line_Item, Region, Product

📊 Comparison Summary
========================================
  Total Baseline:      8  
  Total Comparison:    8  
  Unchanged:           6  
  Changed:             2  
  Added:               2  
  Removed:             2  

🔄 Changed Rows (2)
----------------------------------------
 Line_Item  Region  Product   Baseline  Comparison  Change  Change %
 Revenue    North   Widget A  1000.00   1200.00     200.00  20.0%
 Costs      North   Widget A   300.00    350.00      50.00  16.7%

➕ Added Rows (2)
----------------------------------------
 Line_Item  Region   Product   Value
 Revenue    Central  Widget E  2500.0
 Costs      Central  Widget E   750.0

➖ Removed Rows (2)
----------------------------------------
 Line_Item  Region  Product   Value  
 Revenue    East    Widget C  1500.0
 Costs      East    Widget C   450.0

⚠️  4 differences found
```

The tool automatically detects that `Line_Item`, `Region` and `Product` are dimension columns (used for matching rows), while `Value` is the measure column (compared for changes).

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
