"""
Schema management schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ColumnInfo(BaseModel):
    """Column information"""
    name: str
    type: str
    nullable: bool
    default: Optional[str] = None
    comment: Optional[str] = None


class TableInfo(BaseModel):
    """Table information"""
    name: str
    schema: str
    type: str  # TABLE, VIEW, etc.
    rows: Optional[int] = None
    size_bytes: Optional[int] = None
    columns: List[ColumnInfo]
    comment: Optional[str] = None


class SchemaInfo(BaseModel):
    """Database schema information"""
    database: str
    tables: List[TableInfo]
    total_tables: int
    total_columns: int


class SchemaListResponse(BaseModel):
    """Schema list response"""
    data_source_id: str
    schemas: List[str]
    total: int


class TableListResponse(BaseModel):
    """Table list response"""
    data_source_id: str
    schema_name: str
    tables: List[TableInfo]
    total: int


class SchemaDetailResponse(BaseModel):
    """Detailed schema response"""
    data_source_id: str
    database: str
    schema_info: SchemaInfo
    last_refreshed: datetime


class SchemaRefreshRequest(BaseModel):
    """Refresh schema request"""
    data_source_id: str
    force: bool = False


class SchemaRefreshResponse(BaseModel):
    """Schema refresh response"""
    success: bool
    message: str
    tables_refreshed: int
    columns_refreshed: int
    duration_ms: float


class SchemaSearchRequest(BaseModel):
    """Search schema request"""
    data_source_id: str
    query: str = Field(..., min_length=1)
    search_type: str = "column"  # column, table, both
    limit: int = Field(50, gt=0, le=1000)


class SchemaSearchResponse(BaseModel):
    """Schema search response"""
    data_source_id: str
    query: str
    tables: List[TableInfo]
    columns: List[ColumnInfo]
    total_results: int


class SchemaDiffRequest(BaseModel):
    """Schema diff request"""
    data_source_id: str
    compare_with: str  # Another data source or timestamp


class SchemaDiffResponse(BaseModel):
    """Schema diff response"""
    data_source_id: str
    compare_with: str
    added_tables: List[str]
    removed_tables: List[str]
    modified_tables: List[Dict[str, Any]]
    added_columns: List[Dict[str, str]]
    removed_columns: List[Dict[str, str]]
    modified_columns: List[Dict[str, Any]]
