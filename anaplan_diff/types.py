"""Shared type definitions for the anaplan-diff package."""

from enum import Enum


class AnaplanFormat(Enum):
    """Anaplan CSV export format types."""

    TABULAR_SINGLE_COLUMN = "tabular_single_column"
    TABULAR_MULTI_COLUMN = "tabular_multi_column"
