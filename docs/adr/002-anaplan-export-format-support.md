# ADR-002: Anaplan Export Format Support

## Status
Accepted

## Context

Anaplan offers multiple CSV export formats, each with different data organization and structure. The pyanaplan-diff tool needs to support these formats to effectively compare Anaplan data exports and identify changes between versions.

Anaplan provides three export formats:

### 1. Grid Format (Not Supported)
- **Structure**: Native Anaplan grid view export
- **Characteristics**:
  - Preserves original module layout with merged cells and formatting
  - Complex hierarchical structure with nested dimensions
  - Difficult to parse programmatically due to variable structure

### 2. Tabular Single Column Format (Supported)
- **Structure**: Line Item | Dimension 1 | Dimension 2 | ... | Dimension N | Value
- **Characteristics**:
  - First column always contains the line item name
  - Followed by dimension columns (e.g., Time, Product, Region, etc.)
  - Final column contains the numeric value
  - Each row represents a single data point
  - Most commonly used for structured analysis

### 3. Tabular Multiple Column Format (Future Support)
- **Structure**: Line Item | Dimension 1 | ... | Dimension N | Value Col 1 | Value Col 2 | ... | Value Col M
- **Characteristics**:
  - Values spread across multiple columns (e.g., monthly columns)
  - More complex dimension handling required
  - Requires pivot/unpivot operations for comparison

## Decision

**We will initially support only the Tabular Single Column format** for the following reasons:

1. **Most Common Usage**: This format is the standard export for analytical comparisons
2. **Clear Structure**: Predictable column organization enables reliable dimension detection
3. **Implementation Simplicity**: Single value column simplifies comparison logic
4. **Business Value**: Covers the primary use case of comparing development changes

## Technical Implementation

### Format Detection
The `FileAnalyzer` class will detect Tabular Single Column format by:
- Identifying that the last column contains numeric values
- Verifying that preceding columns contain categorical/dimensional data
- Confirming single-value-per-row structure

### Dimension Detection Strategy
The `DimensionDetector` will identify dimensions using these heuristics:
- **All columns except the last** are treated as potential dimensions
- **Line Item Column**: First column is always a dimension (line item names)
- **Dimension Columns**: Columns 2 through N-1 with categorical data
- **Value Column**: Final column with numeric data

### Data Structure
```python
# Expected CSV structure:
# Line Item, Time, Product, Region, Value
# Revenue, 2024-01, Widget A, North, 150000
# Revenue, 2024-01, Widget A, South, 120000
# Costs, 2024-01, Widget A, North, 45000
```

### Comparison Key
Rows will be compared using a composite key of:
- Line Item + all dimension values (excluding the final Value column)
- This ensures proper matching between baseline/comparison exports

## Consequences

### Positive
- **Focused Implementation**: Single format support enables robust, well-tested functionality
- **Clear Requirements**: Predictable structure reduces edge cases
- **Business Alignment**: Covers primary analytical workflow
- **Foundation**: Establishes patterns for future format support

### Negative
- **Limited Scope**: Other export formats will require separate implementation
- **Format Dependency**: Tool effectiveness depends on users exporting in supported format

### Risks
- **Format Evolution**: Anaplan changes to export structure could break detection
- **Edge Cases**: Unusual dimension arrangements might cause detection failures

## Future Considerations

1. **Tabular Multiple Column Support**: Extend to handle multiple value columns with pivot/unpivot operations
2. **Grid Format Support**: Add support for complex hierarchical structures (low priority due to parsing complexity)
3. **Auto-Format Detection**: Implement intelligent format identification across all three formats
4. **Configuration Options**: Allow users to specify format when auto-detection fails

## Implementation Notes

- The `CSVInfo` class should include a `format_type` field to track detected format
- Error messages should guide users to export in supported format when detection fails
- Consider adding format validation before attempting comparison

---

**Decision Date**: 2024-09-07  
**Participants**: Christopher Jelly
**Related Components**: `detector.py`, `comparator.py`, `cli.py`
