from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal


@dataclass
class Message:
    role: Literal["system", "user", "assistant", "function"]
    content: str


@dataclass
class Record(ABC):
    """
    Base class for storing model response information
    """

    @property
    @abstractmethod
    def json_fields(self):
        """Return the DuckDB JSON fields for the record"""
        pass

    @property
    @abstractmethod
    def duckdb_schema(self):
        """Return the DuckDB schema for the record"""
        pass

    @property
    @abstractmethod
    def table_name(self):
        """Return the DuckDB table name for the record"""
        pass
