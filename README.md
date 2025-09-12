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
Region,Product,Sales,Quantity
North,Widget A,1000,10
South,Widget B,2000,20
East,Widget C,1500,15
West,Widget D,3000,30
```

**examples/comparison.csv**
```csv
Region,Product,Sales,Quantity
North,Widget A,1200,10
South,Widget B,2000,25
West,Widget D,3000,30
Central,Widget E,2500,25
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
Detected dimensions: Region, Product, Sales

📊 Comparison Summary
========================================
  Total Baseline:      4  
  Total Comparison:    4  
  Unchanged:           1  
  Changed:             1  
  Added:               2  
  Removed:             2  

🔄 Changed Rows (1)
----------------------------------------
 Region  Product   Sales  Baseline  Comparison  Change  Change % 
 South   Widget B  2000      20.00       25.00    5.00     25.0% 

➕ Added Rows (2)
----------------------------------------
 Region   Product   Sales    Quantity 
 North    Widget A  1,200.0  10.00    
 Central  Widget E  2,500.0  25.00    

➖ Removed Rows (2)
----------------------------------------
 Region  Product   Sales    Quantity 
 North   Widget A  1,000.0  10.00    
 East    Widget C  1,500.0  15.00    

⚠️  5 differences found
```

The tool automatically detects that `Region` and `Product` are dimension columns (used for matching rows), while `Sales` and `Quantity` are measure columns (compared for changes).

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
