# Parameter Naming Consistency Todo

## Issue
Found inconsistent parameter naming across test files. Some function calls use named parameters while others use positional parameters, making the code less readable and maintainable.

## Function Signatures and Problems

### 1. `compare_dataframes` Function
```python
def compare_dataframes(
    baseline_df: pl.DataFrame,                       # Required - positional OK
    comparison_df: pl.DataFrame,                     # Required - positional OK  
    dimension_columns: list[str],                    # Required - should be named for clarity
    format_type: AnaplanFormat | None = None,       # Optional - should be named
    comparison_tolerance: float = 1e-10,             # Optional - should be named
) -> Result[ComparisonResult, str]:
```

**Problems Found in `tests/test_basic.py`:**
- Line 18: `compare_dataframes(df, df, ["A"], comparison_tolerance=-1)`
  - Missing `dimension_columns=` and has unnamed optional parameter
- Line 93: `compare_dataframes(empty_df, data_df, ["A"])`
  - Missing `dimension_columns=`
- Line 96: `compare_dataframes(data_df, empty_df, ["A"])`
  - Missing `dimension_columns=`  
- Line 104: `compare_dataframes(before_df, after_df, ["A"])`
  - Missing `dimension_columns=`
- Line 111: `compare_dataframes(df, df, ["X"])`
  - Missing `dimension_columns=`
- Line 118: `compare_dataframes(df, df, ["A", "B"])`
  - Missing `dimension_columns=`

### 2. `create_test_csv_pair` Function
```python
def create_test_csv_pair(
    scenario_name: str,           # Required - positional OK
    temp_dir: Path,               # Required - positional OK
    file_prefix: str = "test"     # Optional - should be named
) -> tuple[Path, Path]:
```

**Problems Found:**
- `tests/conftest.py:33`: `create_test_csv_pair("identical_files", temp_dir, "basic")`
  - Missing `file_prefix=`
- `tests/conftest.py:77`: `create_test_csv_pair(scenario_name, self.temp_dir, prefix)`
  - Missing `file_prefix=`

### 3. `save_csv_file` Function
```python
def save_csv_file(
    file_path: str | Path,        # Required - positional OK
    content: str,                 # Required - positional OK
    encoding: str = "utf-8"       # Optional - should be named
) -> None:
```

**No problems found** - All calls use default encoding or don't specify it.

## Standards to Apply

1. **Always name required parameters that are not obvious** (like `dimension_columns`)
2. **Always name optional parameters** when they are specified
3. **Positional parameters OK for first 1-2 parameters** when they are obvious from context

## Files to Fix

### `tests/test_basic.py` (6 issues)
- Line 18: Add `dimension_columns=` 
- Line 93: Add `dimension_columns=`
- Line 96: Add `dimension_columns=`
- Line 104: Add `dimension_columns=`
- Line 111: Add `dimension_columns=`
- Line 118: Add `dimension_columns=`

### `tests/conftest.py` (2 issues)  
- Line 33: Add `file_prefix=`
- Line 77: Add `file_prefix=`

## ✅ COMPLETED - Total Issues Fixed: 8
- **compare_dataframes**: 6 issues ✅
- **create_test_csv_pair**: 2 issues ✅

### Changes Applied:

**tests/test_basic.py (6 fixes):**
- Line 18: Fixed `compare_dataframes(df, df, dimension_columns=["A"], comparison_tolerance=-1)`
- Line 93: Fixed `compare_dataframes(empty_df, data_df, dimension_columns=["A"])`
- Line 96: Fixed `compare_dataframes(data_df, empty_df, dimension_columns=["A"])`
- Line 104: Fixed `compare_dataframes(before_df, after_df, dimension_columns=["A"])`
- Line 111: Fixed `compare_dataframes(df, df, dimension_columns=["X"])`
- Line 118: Fixed `compare_dataframes(df, df, dimension_columns=["A", "B"])`

**tests/conftest.py (2 fixes):**
- Line 33: Fixed `create_test_csv_pair("identical_files", temp_dir, file_prefix="basic")`
- Line 77: Fixed `create_test_csv_pair(scenario_name, self.temp_dir, file_prefix=prefix)`

All parameter naming is now consistent across the test suite, improving code readability and maintainability.