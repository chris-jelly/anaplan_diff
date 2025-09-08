# ADR-003: Functional Programming Approach

**Status:** Accepted  
**Date:** 2025-09-07  
**Deciders:** Development Team  

## Context

This codebase adopts functional programming principles throughout its architecture. As a data processing pipeline that compares CSV files, the tool benefits from functional patterns for error handling, composability, and testability.

## Decision

We adopt functional programming patterns with the following principles:

### Core Patterns
- **Pure functions** where possible (no side effects, predictable outputs)
- **Result types** for error handling using `returns.result`
- **Immutable data structures** using `attrs.frozen` classes
- **Function composition** for pipeline operations
- **Explicit I/O separation** from pure computation

### Implementation Strategy
- Use `Result[T, str]` for operations that can fail
- Chain operations using `.bind()` for error propagation
- Separate I/O operations from pure computations
- Prefer function composition over class methods for business logic

## Benefits

**Reliability**: Pure functions are easier to test and debug  
**Composability**: Pipeline stages can be easily combined and reordered  
**Error Handling**: Result types provide explicit error propagation without exceptions  
**Testability**: Pure functions require no mocking or complex setup  
**Maintainability**: Clear separation of concerns and predictable behavior  

## Do's and Don'ts

### ✅ DO's

```python
# Use Result types for fallible operations
def analyze_file(file_path: str) -> Result[CSVInfo, str]:
    if not Path(file_path).exists():
        return Failure(f"Could not find '{file_path}'")
    return Success(csv_info)

# Chain operations with .bind() for error propagation  
def pipeline(path: str) -> Result[ComparisonResult, str]:
    return (
        analyze_file(path)
        .bind(load_dataframe)
        .bind(detect_dimensions)
    )

# Use immutable data structures
@attrs.frozen
class CSVInfo:
    encoding: str
    delimiter: str
    has_header: bool

# Separate I/O from pure computation
def detect_dimensions(df: pl.DataFrame) -> Result[List[str], str]:
    """Pure function - no I/O, predictable output"""
    return Success(df.columns[:-1])

def load_dataframe(file_path: str) -> Result[pl.DataFrame, str]:
    """I/O operation - clearly marked"""
    try:
        return Success(pl.read_csv(file_path))
    except Exception as e:
        return Failure(str(e))
```

### ❌ DON'Ts

```python
# Don't mix I/O with computation
def bad_analyze(file_path: str) -> CSVInfo:
    df = pl.read_csv(file_path)  # I/O mixed with analysis
    dimensions = df.columns[:-1]  # computation mixed with I/O
    return CSVInfo(...)

# Don't use exceptions for control flow
def bad_validate(df: pl.DataFrame) -> List[str]:
    if df.shape[0] == 0:
        raise ValueError("Empty DataFrame")  # Use Result instead
    return df.columns

# Don't create mutable state
class BadAnalyzer:
    def __init__(self):
        self.results = []  # Mutable state
        
    def analyze(self, path: str):
        self.results.append(...)  # Side effects

# Don't hide error conditions
def bad_parse(text: str) -> float:
    try:
        return float(text)
    except ValueError:
        return 0.0  # Silently converts errors - use Result instead
```

## Trade-offs

**Benefits**: Increased reliability, testability, and maintainability  
**Costs**: Learning curve for functional patterns, additional typing overhead  
**Mitigation**: Provide compatibility wrappers for tests, clear documentation  

## Implementation Notes

- Compatibility wrappers (e.g., `FileAnalyzer`, `DataComparator`) are provided for tests
- I/O operations are clearly documented as "(I/O operation)"  
- Pure functions are the default - side effects are explicitly noted
- Result types replace exception-based error handling throughout the pipeline