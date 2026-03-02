"""
Agent interaction schemas
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class AgentType(str, Enum):
    """Agent type"""
    QUERY = "query"
    DESIGN = "design"
    SUPPORT = "support"
    OPS = "ops"


class AgentStatus(str, Enum):
    """Agent status"""
    IDLE = "idle"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


class LLMProvider(str, Enum):
    """LLM provider"""
    CLAUDE = "claude"
    GPT4 = "gpt4"
    GLM5 = "glm5"


class AgentRequest(BaseModel):
    """Agent request"""
    agent_type: AgentType
    prompt: str = Field(..., min_length=1, max_length=10000)
    context: Optional[Dict[str, Any]] = None
    data_source_id: Optional[str] = None
    provider: Optional[LLMProvider] = None
    model: Optional[str] = None
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(2000, gt=0, le=16000)

    @validator('prompt')
    def prompt_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Prompt cannot be empty')
        return v


class AgentResponse(BaseModel):
    """Agent response"""
    id: str
    user_id: str
    agent_type: str
    prompt: str
    response: Optional[str] = None
    status: str
    provider: Optional[str] = None
    model: Optional[str] = None
    tokens_used: Optional[int] = 0
    processing_time_ms: Optional[float] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class QueryAgentRequest(BaseModel):
    """Query agent specific request"""
    data_source_id: str = Field(..., min_length=1)
    natural_language: str = Field(..., min_length=1, max_length=10000)
    provider: Optional[LLMProvider] = None
    temperature: float = Field(0.3, ge=0.0, le=2.0)  # Lower temperature for SQL


class QueryAgentResponse(BaseModel):
    """Query agent response"""
    id: str
    natural_language: str
    generated_sql: str
    explanation: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    suggested_improvements: Optional[List[str]] = None
    execution_plan: Optional[Dict[str, Any]] = None


class DesignAgentRequest(BaseModel):
    """Design agent specific request"""
    requirements: str = Field(..., min_length=1, max_length=10000)
    data_volume_gb: Optional[int] = Field(None, ge=1)
    query_patterns: Optional[List[str]] = None
    performance_requirements: Optional[Dict[str, Any]] = None


class DesignAgentResponse(BaseModel):
    """Design agent response"""
    id: str
    requirements: str
    schema_design: Dict[str, Any]
    infrastructure_recommendations: List[str]
    optimization_suggestions: List[str]
    estimated_costs: Optional[Dict[str, float]] = None


class SupportAgentRequest(BaseModel):
    """Support agent specific request"""
    question: str = Field(..., min_length=1, max_length=10000)
    context: Optional[Dict[str, Any]] = None
    category: Optional[str] = None


class SupportAgentResponse(BaseModel):
    """Support agent response"""
    id: str
    question: str
    answer: str
    category: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    related_articles: Optional[List[str]] = None
    escalation_needed: bool = False


class AgentHealthResponse(BaseModel):
    """Agent health status"""
    agent_type: str
    status: str
    provider: str
    model: str
    last_used: Optional[datetime] = None
    total_requests: int
    success_rate: float
    average_response_time_ms: float


class AgentAnalytics(BaseModel):
    """Agent usage analytics"""
    total_requests: int
    requests_by_agent: Dict[str, int]
    requests_by_provider: Dict[str, int]
    success_rate: float
    average_response_time_ms: float
    total_tokens_used: int
    estimated_cost_usd: float


class AgentConfigUpdate(BaseModel):
    """Update agent configuration"""
    default_provider: Optional[LLMProvider] = None
    default_model: Optional[str] = None
    default_temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    default_max_tokens: Optional[int] = Field(None, gt=0, le=16000)
    rate_limit_per_minute: Optional[int] = Field(None, gt=0)
