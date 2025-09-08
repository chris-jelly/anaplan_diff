# ADR-001: Comparison Tolerance for Numeric Data

**Status:** Accepted  
**Date:** 2025-09-07  
**Deciders:** Development Team  

## Context

When comparing numeric data from Anaplan CSV exports, we encountered the fundamental challenge of floating-point precision in computer systems. Direct equality comparisons of floating-point numbers often fail due to:

1. **Binary representation limitations**: Decimal numbers like 0.1 cannot be exactly represented in binary floating-point format
2. **Calculation accumulation errors**: Mathematical operations can introduce tiny precision differences
3. **Export format variations**: Different Anaplan export settings or calculation engines may produce slight rounding differences
4. **Cross-system consistency**: The same logical value might have microscopic differences when processed by different systems

## Problem

Without tolerance handling, the comparison engine would incorrectly identify functionally identical values as "changed":

```python
# Real scenario from Anaplan exports
baseline_value = 1000.3333333333333
comparison_value  = 1000.3333333333334  # Differs by 1e-13

# Without tolerance: FALSE POSITIVE change detected
# With tolerance: Correctly identified as unchanged
```

This leads to:
- **False positives**: Reporting changes where none occurred
- **Noise in reports**: Overwhelming users with insignificant differences  
- **Lost trust**: Users questioning the tool's accuracy
- **Ineffective analysis**: Real changes buried in floating-point artifacts

## Decision

We implement a configurable `comparison_tolerance` parameter in the `DataComparator` class with the following design:

### Core Design
- **Default tolerance**: `1e-10` (very conservative, catches only floating-point artifacts)
- **Configurable**: Constructor parameter allows customization per use case
- **Applied consistently**: Same tolerance used for both "unchanged" and "changed" detection
- **Numeric-only**: Tolerance only applies to numeric columns; text comparisons remain exact

### Implementation
```python
class DataComparator:
    def __init__(self, comparison_tolerance: float = 1e-10):
        if comparison_tolerance <= 0:
            raise ValueError("Comparison tolerance must be positive")
        self.comparison_tolerance = comparison_tolerance
```

### Comparison Logic
- **Unchanged**: `abs(baseline - comparison) < tolerance`
- **Changed**: `abs(baseline - comparison) >= tolerance`  
- **Text data**: Exact equality comparison (no tolerance)

## Alternatives Considered

### 1. No Tolerance (Exact Equality)
**Rejected**: Would produce too many false positives due to floating-point precision issues.

### 2. Fixed Rounding
```python
round(value, 10) == round(other_value, 10)
```
**Rejected**: Loses precision and doesn't handle different magnitude scales well.

### 3. Relative Tolerance
```python
abs(baseline - comparison) / max(abs(baseline), abs(comparison)) < relative_tolerance
```
**Rejected**: More complex to understand and configure; absolute tolerance is sufficient for Anaplan use cases.

### 4. Automatic Tolerance Detection
**Rejected**: Too complex and unpredictable; explicit configuration provides better user control.

## Consequences

### Positive
- **Accurate comparisons**: Eliminates floating-point precision false positives
- **Flexibility**: Different use cases can specify appropriate tolerance levels
- **Business alignment**: Financial users can set penny-level precision (0.01)
- **Scientific support**: High-precision scenarios can use very small tolerances (1e-15)
- **Predictable behavior**: Clear, documented comparison logic

### Negative
- **Configuration complexity**: Users must understand appropriate tolerance values
- **Potential false negatives**: Very small real changes might be missed if tolerance is too large
- **Additional parameter**: Increases API surface area

### Neutral
- **Performance**: Negligible impact on comparison performance
- **Memory**: No significant memory overhead

## Guidance

### Recommended Tolerance Values

| Use Case | Tolerance | Rationale |
|----------|-----------|-----------|
| Financial (Currency) | `0.01` | Penny-level precision |
| Financial (Percentages) | `0.001` | 0.1% precision |
| Scientific/Engineering | `1e-15` | High precision requirements |
| General Business Metrics | `1e-6` | Balances precision with practicality |
| Integer-like Data | `0.1` | Allows for minor rounding |
| Default (Conservative) | `1e-10` | Only catches floating-point artifacts |

### Usage Examples
```python
# Financial data comparison
financial_comparator = DataComparator(comparison_tolerance=0.01)

# High-precision scientific data  
scientific_comparator = DataComparator(comparison_tolerance=1e-15)

# Conservative default (recommended starting point)
default_comparator = DataComparator()  # Uses 1e-10
```

## Implementation Notes

- **Type checking**: Only numeric columns use tolerance; text columns use exact equality
- **Validation**: Constructor validates that tolerance is positive
- **Consistency**: Same tolerance applied throughout all comparison operations
- **Documentation**: Clear examples and guidance provided for different use cases

## Future Considerations

- **Column-specific tolerances**: Different tolerance per measure column
- **Automatic tolerance recommendation**: Analyze data to suggest appropriate tolerance
- **Relative tolerance option**: For data with widely varying magnitudes
- **Tolerance reporting**: Show which comparisons were affected by tolerance