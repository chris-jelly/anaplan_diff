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
Line Item,Region,Product,Value
Revenue,North,Widget A,1000
Revenue,South,Widget B,2000
Revenue,East,Widget C,1500
Revenue,West,Widget D,3000
Costs,North,Widget A,300
Costs,South,Widget B,600
Costs,East,Widget C,450
Costs,West,Widget D,900
Project Status,North,Widget A,Complete
Project Status,South,Widget B,In Progress
Feature Active,North,Widget A,True
Feature Active,South,Widget B,False
```

**examples/comparison.csv**
```csv
Line Item,Region,Product,Value
Revenue,North,Widget A,1200
Revenue,South,Widget B,2000
Revenue,West,Widget D,3000
Revenue,Central,Widget E,2500
Costs,North,Widget A,350
Costs,South,Widget B,600
Costs,West,Widget D,900
Costs,Central,Widget E,750
Project Status,North,Widget A,In Progress
Project Status,Central,Widget E,Complete
Feature Active,North,Widget A,False
Feature Active,Central,Widget E,True
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
Detected dimensions: Line Item, Region, Product

📊 Comparison Summary
========================================
  Total Baseline:      12  
  Total Comparison:    12  
  Unchanged:           4  
  Changed:             4  
  Added:               4  
  Removed:             4  

🔄 Changed Rows (4)
----------------------------------------
 Line Item       Region  Product   Baseline   Comparison  Change  Change % 
 Revenue         North   Widget A      1000         1200  200.00     20.0% 
 Costs           North   Widget A       300          350   50.00     16.7% 
 Project Status  North   Widget A  Complete  In Progress       -         - 
 Feature Active  North   Widget A      True        False       -         - 

➕ Added Rows (4)
----------------------------------------
 Line Item       Region   Product   Value    
 Revenue         Central  Widget E  2500     
 Costs           Central  Widget E  750      
 Project Status  Central  Widget E  Complete 
 Feature Active  Central  Widget E  True     

➖ Removed Rows (4)
----------------------------------------
 Line Item       Region  Product   Value       
 Revenue         East    Widget C  1500        
 Costs           East    Widget C  450         
 Project Status  South   Widget B  In Progress 
 Feature Active  South   Widget B  False       

⚠️  12 differences found
```

The tool automatically detects that `Line Item`, `Region` and `Product` are dimension columns (used for matching rows), while `Value` is the measure column (compared for changes).

## Data Type Support

The tool supports **all data types** in any column:

- **Numeric measures**: Shows change amounts and percentages (e.g., `1000 → 1200, +200, +20%`)
- **String measures**: Shows before/after values (e.g., `"Complete" → "In Progress"`)
- **Boolean measures**: Shows true/false changes (e.g., `True → False`)
- **Mixed data types**: Dimensions can be any combination of text, numbers, booleans, dates

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
