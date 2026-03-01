"""
Query schemas
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class QueryStatus(str, Enum):
    """Query status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class QueryLanguage(str, Enum):
    """Query language"""
    SQL = "sql"
    NATURAL_LANGUAGE = "natural_language"


class QueryCreate(BaseModel):
    """Create a new query"""
    data_source_id: str = Field(..., min_length=1)
    query: str = Field(..., min_length=1)
    language: QueryLanguage = QueryLanguage.SQL
    query_name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    parameters: Optional[Dict[str, Any]] = None

    @validator('query')
    def query_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Query cannot be empty')
        return v


class QueryExecuteRequest(BaseModel):
    """Execute a query"""
    data_source_id: str = Field(..., min_length=1)
    query: str = Field(..., min_length=1)
    language: QueryLanguage = QueryLanguage.SQL
    parameters: Optional[Dict[str, Any]] = None
    limit: Optional[int] = Field(1000, gt=0, le=100000)
    timeout: Optional[int] = Field(300, gt=0, le=3600)  # 5 minutes default, max 1 hour


class QueryResponse(BaseModel):
    """Query response"""
    id: str
    user_id: str
    data_source_id: str
    query: str
    language: str
    status: str
    rows_affected: Optional[int] = 0
    execution_time_ms: Optional[float] = None
    result: Optional[List[Dict[str, Any]]] = None
    columns: Optional[List[str]] = None
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class QueryListResponse(BaseModel):
    """Paginated query list response"""
    queries: list[QueryResponse]
    total: int
    page: int
    page_size: int


class QueryAnalytics(BaseModel):
    """Query analytics"""
    total_queries: int
    successful_queries: int
    failed_queries: int
    average_execution_time_ms: float
    total_rows_processed: int
    queries_by_status: Dict[str, int]
    queries_by_language: Dict[str, int]


class QueryTemplateCreate(BaseModel):
    """Create a query template"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    query: str = Field(..., min_length=1)
    parameters: Optional[List[Dict[str, Any]]] = None
    category: Optional[str] = Field(None, max_length=100)


class QueryTemplateUpdate(BaseModel):
    """Update a query template"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    query: Optional[str] = Field(None, min_length=1)
    parameters: Optional[List[Dict[str, Any]]] = None
    category: Optional[str] = Field(None, max_length=100)


class QueryTemplateResponse(BaseModel):
    """Query template response"""
    id: str
    user_id: str
    name: str
    description: Optional[str] = None
    query: str
    parameters: Optional[List[Dict[str, Any]]] = None
    category: Optional[str] = None
    usage_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
