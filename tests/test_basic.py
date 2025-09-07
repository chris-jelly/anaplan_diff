"""
Basic functionality tests for the anaplan-diff tool.
"""

from anaplan_diff.comparator import DataComparator
from anaplan_diff.detector import CSVInfo, DimensionDetector, FileAnalyzer
from anaplan_diff.formatter import TerminalFormatter


class TestCSVInfo:
    """Test the CSVInfo dataclass."""

    def test_csv_info_creation(self):
        """Test creating a CSVInfo instance."""
        csv_info = CSVInfo(
            encoding="utf-8", delimiter=",", has_header=True, skip_rows=0
        )
        assert csv_info.encoding == "utf-8"
        assert csv_info.delimiter == ","
        assert csv_info.has_header is True
        assert csv_info.skip_rows == 0


class TestFileAnalyzer:
    """Test the FileAnalyzer class."""

    def test_file_analyzer_creation(self):
        """Test creating a FileAnalyzer instance."""
        analyzer = FileAnalyzer()
        assert analyzer is not None


class TestDimensionDetector:
    """Test the DimensionDetector class."""

    def test_dimension_detector_creation(self):
        """Test creating a DimensionDetector instance."""
        detector = DimensionDetector()
        assert detector is not None


class TestDataComparator:
    """Test the DataComparator class."""

    def test_data_comparator_creation(self):
        """Test creating a DataComparator instance."""
        comparator = DataComparator()
        assert comparator is not None


class TestTerminalFormatter:
    """Test the TerminalFormatter class."""

    def test_terminal_formatter_creation(self):
        """Test creating a TerminalFormatter instance."""
        formatter = TerminalFormatter()
        assert formatter is not None
        assert formatter.console is not None
