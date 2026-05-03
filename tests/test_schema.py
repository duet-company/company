"""
Schema validation tests for Duet Company backend.
"""

import pytest
from pydantic import ValidationError
from apps.backend.src.schemas import QueryRequest, DesignRequest, UserCreate


class TestQueryRequest:
    """Test cases for QueryRequest schema."""
    
    def test_valid_query_request(self):
        """Test valid query request."""
        data = {
            "query": "What is artificial intelligence?",
            "type": "general",
            "context": {}
        }
        
        request = QueryRequest(**data)
        assert request.query == data["query"]
        assert request.type == data["type"]
        assert request.context == data["context"]
    
    def test_query_request_minimal(self):
        """Test query request with minimal data."""
        data = {
            "query": "Hello"
        }
        
        request = QueryRequest(**data)
        assert request.query == data["query"]
        assert request.type == "general"  # default value
        assert request.context == {}  # default value
    
    def test_invalid_query_request(self):
        """Test invalid query request."""
        with pytest.raises(ValidationError):
            QueryRequest()
    
    def test_query_request_type_validation(self):
        """Test query request type validation."""
        valid_types = ["general", "technical", "creative", "analysis"]
        
        for query_type in valid_types:
            data = {
                "query": "Test query",
                "type": query_type
            }
            request = QueryRequest(**data)
            assert request.type == query_type


class TestDesignRequest:
    """Test cases for DesignRequest schema."""
    
    def test_valid_design_request(self):
        """Test valid design request."""
        data = {
            "requirements": "Build an e-commerce platform",
            "scope": "full",
            "technologies": ["React", "Node.js"],
            "constraints": ["budget: $10,000", "timeline: 3 months"]
        }
        
        request = DesignRequest(**data)
        assert request.requirements == data["requirements"]
        assert request.scope == data["scope"]
        assert request.technologies == data["technologies"]
        assert request.constraints == data["constraints"]
    
    def test_design_request_minimal(self):
        """Test design request with minimal data."""
        data = {
            "requirements": "Build a simple website"
        }
        
        request = DesignRequest(**data)
        assert request.requirements == data["requirements"]
        assert request.scope == "basic"  # default value
        assert request.technologies == []  # default value
        assert request.constraints == []  # default value
    
    def test_design_request_scope_validation(self):
        """Test design request scope validation."""
        valid_scopes = ["basic", "standard", "full", "enterprise"]
        
        for scope in valid_scopes:
            data = {
                "requirements": "Test requirements",
                "scope": scope
            }
            request = DesignRequest(**data)
            assert request.scope == scope


class TestUserCreate:
    """Test cases for UserCreate schema."""
    
    def test_valid_user_create(self):
        """Test valid user creation."""
        data = {
            "email": "test@example.com",
            "name": "Test User",
            "password": "SecurePassword123!"
        }
        
        user = UserCreate(**data)
        assert user.email == data["email"]
        assert user.name == data["name"]
    
    def test_invalid_email(self):
        """Test invalid email format."""
        with pytest.raises(ValidationError):
            UserCreate(
                email="invalid-email",
                name="Test User",
                password="SecurePassword123!"
            )
    
    def test_weak_password(self):
        """Test weak password validation."""
        weak_passwords = [
            "short",
            "onlyletters",
            "12345678",
            "NOUPPERCASE123!",
            "nouppercase123!",
            "NoNumbers!"
        ]
        
        for password in weak_passwords:
            with pytest.raises(ValidationError):
                UserCreate(
                    email="test@example.com",
                    name="Test User",
                    password=password
                )