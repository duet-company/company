"""
Data source schemas
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Literal, Dict, Any
from datetime import datetime
from enum import Enum


class DataSourceType(str, Enum):
    """Data source type"""
    CLICKHOUSE = "clickhouse"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    BIGQUERY = "bigquery"
    SNOWFLAKE = "snowflake"
    REDSHIFT = "redshift"


class DataSourceStatus(str, Enum):
    """Data source status"""
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"


class DataSourceCreate(BaseModel):
    """Create a new data source"""
    name: str = Field(..., min_length=1, max_length=255)
    type: DataSourceType
    host: str = Field(..., min_length=1)
    port: int = Field(..., gt=0, le=65535)
    database: str = Field(..., min_length=1)
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)
    description: Optional[str] = Field(None, max_length=1000)
    config: Optional[Dict[str, Any]] = None

    @validator('name')
    def name_must_not_contain_spaces(cls, v):
        if ' ' in v:
            raise ValueError('Name must not contain spaces')
        return v


class DataSourceUpdate(BaseModel):
    """Update a data source"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class DataSourceResponse(BaseModel):
    """Data source response"""
    id: str
    user_id: str
    name: str
    type: str
    host: str
    port: int
    database: str
    username: str
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    status: str
    is_active: bool
    tables_count: Optional[int] = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DataSourceTestConnection(BaseModel):
    """Test data source connection"""
    id: str


class DataSourceTestResponse(BaseModel):
    """Data source connection test response"""
    success: bool
    message: str
    latency_ms: Optional[float] = None
    version: Optional[str] = None


class DataSourceListResponse(BaseModel):
    """Paginated data source list response"""
    data_sources: list[DataSourceResponse]
    total: int
    page: int
    page_size: int
