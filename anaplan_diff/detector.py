"""
CSV file analysis and dimension detection.

Implements position-based dimension detection for Tabular Single Column format:
- First column: ALWAYS line item name from module (dimension)
- Last column: ALWAYS value for that line item (measure)
- Middle columns: ALWAYS dimensions of the module
"""

from pathlib import Path

import attrs
import chardet
import polars as pl
from returns.result import Failure, Result, Success


@attrs.frozen
class CSVInfo:
    """Immutable CSV format information."""

    encoding: str
    delimiter: str
    has_header: bool
    skip_rows: int = 0
    format_type: str = "tabular_single_column"

    def __post_init__(self) -> None:
        """Validate CSVInfo invariants."""
        if self.skip_rows < 0:
            raise ValueError("skip_rows must be non-negative")
        if not self.encoding:
            raise ValueError("encoding must be non-empty")
        if not self.delimiter:
            raise ValueError("delimiter must be non-empty")


def analyze_file(file_path: str) -> Result[CSVInfo, str]:
    """Analyze a CSV file and return format information (I/O operation)."""
    path = Path(file_path)

    if not path.exists():
        return Failure(f"Could not find '{file_path}'")

    return (
        _detect_encoding(path)
        .bind(lambda encoding: _read_sample_lines(path, encoding))
        .bind(lambda data: _analyze_csv_structure(path, data[0], data[1]))
    )


def load_dataframe(file_path: str, csv_info: CSVInfo) -> Result[pl.DataFrame, str]:
    """Load CSV file as a polars DataFrame (I/O operation)."""
    try:
        df = pl.read_csv(
            file_path,
            encoding=csv_info.encoding,
            separator=csv_info.delimiter,
            skip_rows=csv_info.skip_rows,
            has_header=csv_info.has_header,
            ignore_errors=True,
        )
        return Success(df)
    except Exception as e:
        return Failure(f"Could not load CSV file: {e}")


def detect_dimensions(df: pl.DataFrame) -> Result[list[str], str]:
    """
    Detect dimension columns in DataFrame using Tabular Single Column format structure.

    For Tabular Single Column format:
    - First column: ALWAYS line item name from module (dimension)
    - Last column: ALWAYS value for that line item (measure)
    - All middle columns: ALWAYS dimensions of the module
    """
    if df.shape[1] < 2:
        return Failure("DataFrame must have at least 2 columns")

    columns = df.columns

    # First column is always line item (dimension)
    # All columns except last are dimensions
    dimension_columns = columns[:-1]

    return Success(list(dimension_columns))


# Private helper functions


def _detect_encoding(path: Path) -> Result[str, str]:
    """Detect file encoding using chardet (I/O operation)."""
    try:
        with path.open("rb") as f:
            raw_data = f.read(10000)

        detected = chardet.detect(raw_data)
        encoding = detected.get("encoding", "utf-8")

        if encoding.lower() in ["utf-8-sig", "utf-8"]:
            return Success("utf-8-sig")

        return Success(encoding)
    except Exception as e:
        return Failure(f"Could not detect encoding: {e}")


def _read_sample_lines(path: Path, encoding: str) -> Result[tuple[str, list[str]], str]:
    """Read sample lines for analysis (I/O operation)."""
    try:
        with path.open("r", encoding=encoding) as f:
            lines = [f.readline().strip() for _ in range(10) if f.readable()]
        return Success((encoding, lines))
    except Exception as e:
        return Failure(f"Could not read file: {e}")


def _analyze_csv_structure(
    path: Path, encoding: str, lines: list[str]
) -> Result[CSVInfo, str]:
    """Analyze CSV structure from sample lines."""
    skip_rows = _count_page_selector_lines(lines)
    data_lines = lines[skip_rows:]

    if not data_lines:
        return Failure("No data lines found after page selectors")

    delimiter = _detect_delimiter(data_lines)
    has_header = _has_header(data_lines, delimiter)

    return _detect_format_type(path, encoding, delimiter, skip_rows).bind(
        lambda format_type: Success(
            CSVInfo(
                encoding=encoding,
                delimiter=delimiter,
                has_header=has_header,
                skip_rows=skip_rows,
                format_type=format_type,
            )
        )
    )


def _count_page_selector_lines(lines: list[str]) -> int:
    """Count Anaplan page selector lines to skip."""
    skip_count = 0
    for line in lines:
        if not line or "Page Selectors:" in line or line.startswith("Total:"):
            skip_count += 1
        else:
            break
    return skip_count


def _detect_delimiter(lines: list[str]) -> str:
    """Detect CSV delimiter from sample lines."""
    if not lines:
        return ","

    delimiters = [",", "\t", ";", "|"]

    for delimiter in delimiters:
        counts = [line.count(delimiter) for line in lines if line.strip()]
        if counts and all(count > 0 for count in counts):
            if len(set(counts)) <= 2:
                return delimiter

    return ","


def _has_header(lines: list[str], delimiter: str) -> bool:
    """Determine if first data line is a header."""
    if len(lines) < 2:
        return True

    first_row = lines[0].split(delimiter)
    second_row = lines[1].split(delimiter) if len(lines) > 1 else []

    if not first_row or not second_row:
        return True

    try:
        float(first_row[-1].strip())
        return False
    except (ValueError, IndexError):
        try:
            if second_row:
                float(second_row[-1].strip())
                return True
        except (ValueError, IndexError):
            pass

    return True


def _detect_format_type(
    path: Path, encoding: str, delimiter: str, skip_rows: int
) -> Result[str, str]:
    """
    Detect if file matches Tabular Single Column format.

    Validates that the last column contains numeric values (measures),
    which is required for the guaranteed structure.
    """
    try:
        df = pl.read_csv(
            path,
            encoding=encoding,
            separator=delimiter,
            skip_rows=skip_rows,
            n_rows=100,
            ignore_errors=True,
        )

        if df.shape[1] < 2:
            return Failure("File must have at least 2 columns")

        # Try to convert last column to numeric
        last_col = df.columns[-1]
        last_col_data = df.select(pl.col(last_col)).to_series()

        try:
            last_col_data.cast(pl.Float64)
            return Success("tabular_single_column")
        except Exception:
            return Failure("Last column must contain numeric values")

    except Exception as e:
        return Failure(f"Could not read CSV file: {e}")
