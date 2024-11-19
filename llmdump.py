"""
LLM Dump - A utility for tracking and storing OpenAI API Endpoint calls
"""

from dataclasses import dataclass, asdict, field
from typing import Optional, Any, Dict, List, Literal
import datetime
import duckdb
import json
import uuid
import os
from openai import OpenAI

DEFAULT_DB_NAME = "store.db"
JSON_FIELDS = ['tool_calls', 'function_call', 'tags', 'properties', 'raw_response']

OPENAI_RECORDS_SCHEMA = """
    CREATE TABLE IF NOT EXISTS openai_records (
        id VARCHAR PRIMARY KEY,
        model VARCHAR,
        timestamp TIMESTAMP,
        messages STRUCT(role VARCHAR, content VARCHAR)[],
        assistant_message TEXT,
        completion_tokens INTEGER,
        prompt_tokens INTEGER,
        total_tokens INTEGER,
        finish_reason VARCHAR,
        tool_calls JSON,
        function_call JSON,
        tags VARCHAR[],
        properties JSON,
        error VARCHAR,
        raw_response JSON,
        synced_at TIMESTAMP
    )
"""

@dataclass
class Message:
    role: Literal["system", "user", "assistant", "function"]
    content: str

@dataclass
class OpenAIResponseRecord:
    """
    Data class for storing OpenAI API response information
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    model: str = None
    timestamp: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    messages: List[Message] = None
    assistant_message: Optional[str] = None
    completion_tokens: Optional[int] = None
    prompt_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    finish_reason: str = None
    tool_calls: Optional[Any] = None
    function_call: Optional[Any] = None
    tags: List[str] = None
    properties: Dict[str, Any] = None
    error: Optional[str] = None
    raw_response: Optional[Dict] = None

    @classmethod
    def create(cls, response=None, error=None, **kwargs):
        """Create a response record from an API response or error"""
        if not response:
            return cls(finish_reason="error", error=str(error), **kwargs)

        dump = response.model_dump()
        choices = dump.get("choices", [{}])[0].get("message", {})
        usage = dump.get("usage", {})

        return cls(
            id=response.id if response.id else str(uuid.uuid4()),
            completion_tokens=usage.get("completion_tokens"),
            prompt_tokens=usage.get("prompt_tokens"),
            total_tokens=usage.get("total_tokens"),
            assistant_message=choices.get("content"),
            finish_reason=dump.get("choices", [{}])[0].get("finish_reason"),
            tool_calls=choices.get("tool_calls"),
            function_call=choices.get("function_call"),
            raw_response=dump,
            **kwargs,
        )

@dataclass
class Store:
    """
    Database store for OpenAI API calls
    """
    path: str = field(default_factory=lambda: os.path.join(os.getcwd(), DEFAULT_DB_NAME))
    _conn: Optional[duckdb.DuckDBPyConnection] = None

    def __post_init__(self):
        """Initialize database connection and table"""
        if self._conn is None:
            self._conn = duckdb.connect(self.path)
            self._init_table()

    @classmethod
    def connect(cls, path: Optional[str] = None) -> 'Store':
        """Create a new store instance with optional custom path"""
        if not path:
            path = os.path.join(os.getcwd(), DEFAULT_DB_NAME)
        return cls(path=path)

    def _init_table(self):
        self._conn.execute(OPENAI_RECORDS_SCHEMA)

    def add(self, record: 'OpenAIResponseRecord'):
        """Add a new record to the database"""
        record_dict = asdict(record)
        record_dict['synced_at'] = None
        
        for field in JSON_FIELDS:
            if record_dict[field]:
                record_dict[field] = json.dumps(record_dict[field])
        
        placeholders = ', '.join(['$' + str(i+1) for i in range(len(record_dict))])
        self._conn.execute(
            f"INSERT INTO openai_records VALUES ({placeholders})",
            [record_dict[k] for k in record_dict.keys()]
        )

    def get_unsynced(self) -> List[tuple]:
        """Retrieve unsynced records"""
        return self._conn.execute(
            "SELECT * FROM openai_records WHERE synced_at IS NULL"
        ).fetchall()

    def mark_as_synced(self, record_ids: List[str]) -> None:
        """Mark specified records as synced"""
        self._conn.execute(
            "UPDATE openai_records SET synced_at = CURRENT_TIMESTAMP WHERE id = ANY($1)",
            [record_ids]
        )

    def close(self) -> None:
        """Close the database connection"""
        if self._conn:
            self._conn.close()
            self._conn = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

def wrap_openai(
    client: OpenAI,
    store: Optional[Store] = None,
    tags: Optional[List[str]] = None,
    properties: Optional[Dict[str, Any]] = None
) -> OpenAI:
    """
    Wrap OpenAI client to track API calls in a Store.
    
    Args:
        client: OpenAI client instance
        store: Store instance for persistence. Creates new if None
        tags: Optional list of tags to associate with records
        properties: Optional dictionary of properties to associate with records
    """
    if store is None:
        store = Store.connect()
        
    original_create = client.chat.completions.create
    
    def tracked_create(*args, **kwargs):
        try:
            response = original_create(*args, **kwargs)
            
            entry = OpenAIResponseRecord.create(
                response=response,
                messages=kwargs.get("messages"),
                model=kwargs.get("model"),
                tags=tags or [],
                properties=properties,
            )
            store.add(entry)
            return response
            
        except Exception as e:
            entry = OpenAIResponseRecord.create(
                error=e,
                messages=kwargs.get("messages"),
                model=kwargs.get("model"),
                tags=tags or [],
                properties=properties,
            )
            store.add(entry)
            raise

    client.chat.completions.create = tracked_create
    return client