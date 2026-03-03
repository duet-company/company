# Platform Designer Agent

Autonomous AI agent for designing and managing scalable data platforms using Kubernetes and ClickHouse.

## Overview

The Platform Designer Agent is an intelligent infrastructure architect that takes natural language requirements and produces production-ready platform designs. It leverages LLM capabilities to generate architecture overviews, Kubernetes manifests, resource estimates, and cost analyses.

## Capabilities

The agent supports three core capabilities:

### 1. DESIGN
Create comprehensive infrastructure designs from high-level requirements. Generates complete architecture documents with component specifications and deployment manifests.

### 2. ANALYSIS
Analyze requirements and recommend optimal solutions. Evaluates trade-offs between different technologies, deployment patterns, and cost structures.

### 3. GENERATION
Generate production-ready Kubernetes manifests and configuration. Produces YAML files for deployments, services, ingress, HPA, and more.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Platform Designer Agent                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Input: Natural Language Requirements                        │
│  "I need a data platform with ClickHouse for analytics,      │
│   FastAPI backend, and React frontend"                       │
│                           ↓                                   │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              LLM Provider Integration                  │  │
│  │  - Claude, GPT-4, GLM-5                               │  │
│  │  - Configurable temperature & max tokens             │  │
│  └───────────────────────────────────────────────────────┘  │
│                           ↓                                   │
│  ┌───────────────────────────────────────────────────────┐  │
│  │               Design Generation Engine                │  │
│  │  - Architecture analysis                              │  │
│  │  - Component selection                                │  │
│  │  - Resource estimation                                │  │
│  │  - Cost calculation                                    │  │
│  └───────────────────────────────────────────────────────┘  │
│                           ↓                                   │
│  Output: Structured Design Document                         │
│  - Architecture overview                                   │
│  - Component specifications                                │
│  - Kubernetes manifests (YAML)                             │
│  - Resource estimates (CPU, memory, storage)               │
│  - Cost estimate (monthly breakdown)                       │
│  - Deployment steps                                         │
│  - Recommendations                                         │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### Basic Usage

```python
import asyncio
from agents.platform_designer import PlatformDesignerAgent, get_platform_config

async def main():
    # Get default configuration
    config = get_platform_config()

    # Create agent
    agent = PlatformDesignerAgent(config)

    # Initialize agent
    await agent.initialize()

    # Process design request
    requirements = """
    I need a complete data platform with:
    - ClickHouse for analytics and OLAP workloads
    - FastAPI backend for data ingestion
    - React dashboard for visualization
    - Redis caching layer
    - Prometheus monitoring

    Constraints:
    - Budget < $100/month
    - Single node deployment for MVP
    - Support 100 concurrent users
    """

    result = await agent.process(requirements)

    # Access results
    print("Architecture Overview:")
    print(result["design"])

    print("\nResource Estimates:")
    print(result.get("resource_estimates", {}))

    print("\nCost Estimate:")
    print(result.get("cost_estimate", {}))

    # Cleanup
    await agent.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
```

### Using Structured Input

```python
input_data = {
    "requirements": "Data platform for analytics with ClickHouse",
    "constraints": "Budget < $50/month, single node",
    "format": "json",  # or "markdown"
}

result = await agent.process(input_data)

# For JSON format:
print(result["architecture_overview"])
print(result["components"])
print(result["cost_estimate"]["monthly_total"])

# For Markdown format:
print(result["design"])
print(result["sections"])  # Dictionary of sections
```

### Accessing Specific Sections (Markdown Output)

```python
result = await agent.process(requirements, output_format="markdown")

# Access specific sections
architecture = result["sections"]["Architecture Overview"]
components = result["sections"]["Component Specifications"]
cost = result["sections"]["Cost Estimate"]

print(architecture)
print(f"Total Cost: {cost}")
```

## Configuration

### Default Configuration

```python
from agents.platform_designer import get_platform_config

config = get_platform_config()
# Uses:
# - LLM Provider: Claude (default)
# - Model: claude-3-5-sonnet-20241022
# - Temperature: 0.7
# - Max Tokens: 8192
# - Task Timeout: 600 seconds (10 minutes)
# - Max Concurrent Tasks: 3
```

### Custom Configuration

```python
from agents.platform_designer import PlatformDesignerAgent
from agents.config import AgentConfig, LLMProviderConfig

config = AgentConfig(
    agent_id="my-platform-designer",
    name="My Platform Designer",
    version="2.0.0",
    agent_type=AgentType.DESIGN,

    # LLM Provider Configuration
    llm_provider=LLMProviderConfig(
        provider="gpt-4",  # or "claude", "glm-5"
        model="gpt-4-turbo",
        api_key="your-api-key",
        api_url="https://api.example.com/v1",  # Optional custom endpoint
        temperature=0.5,  # Lower for more deterministic designs
        max_tokens=16384,  # Higher for more detailed designs
        timeout=120,  # LLM request timeout in seconds
    ),

    # Task Configuration
    max_concurrent_tasks=5,
    task_timeout=900,  # 15 minutes for complex designs
    max_retries=3,

    # Resource Limits
    memory_limit_mb=2048,
    log_level="DEBUG",
)

agent = PlatformDesignerAgent(config)
```

### Environment Variables

Override defaults using environment variables:

```bash
# LLM Provider
export PLATFORM_DESIGNER_LLM_PROVIDER="gpt-4"
export PLATFORM_DESIGNER_LLM_MODEL="gpt-4-turbo"

# API Keys
export ANTHROPIC_API_KEY="your-anthropic-key"
export OPENAI_API_KEY="your-openai-key"
export ZAI_API_KEY="your-zai-key"
```

## Input Formats

### 1. String (Natural Language)

```python
result = await agent.process("""
Design a real-time analytics platform with:
- ClickHouse for time-series data
- Kafka for stream ingestion
- FastAPI backend
- Grafana dashboards
""")
```

### 2. Dictionary with Constraints

```python
result = await agent.process({
    "requirements": "Analytics platform with ClickHouse",
    "constraints": "Budget < $100/month, single region deployment",
})
```

### 3. Dictionary with Output Format

```python
result = await agent.process({
    "requirements": "Analytics platform",
    "format": "json",  # or "markdown"
})
```

### 4. Full Input Specification

```python
result = await agent.process({
    "requirements": "Complete data platform",
    "constraints": """
    Budget: < $150/month
    Deployment: Single node (MVP)
    Region: us-east-1
    Availability: 99.9% SLA
    """,
    "format": "markdown",
})
```

## Output Formats

### JSON Format

```json
{
  "architecture_overview": "Complete data platform for analytics...",
  "components": [
    {
      "name": "clickhouse",
      "type": "database",
      "description": "OLAP database for analytics",
      "specs": {
        "cpu": "2 cores",
        "memory": "8GB",
        "storage": "100GB SSD"
      },
      "kubernetes_yaml": "..."
    }
  ],
  "resource_estimates": {
    "total_cpu": "4 cores",
    "total_memory": "16GB",
    "total_storage": "200GB"
  },
  "cost_estimate": {
    "monthly_total": "$120",
    "breakdown": {
      "vps": "$100",
      "managed_services": "$20",
      "bandwidth": "$0"
    }
  },
  "deployment_steps": [
    "Deploy Kubernetes cluster",
    "Install ClickHouse operator",
    "Create ClickHouse cluster",
    "Deploy backend services",
    "Deploy frontend dashboard"
  ],
  "recommendations": [
    "Use persistent volumes for data",
    "Configure automated backups",
    "Set up monitoring alerts",
    "Implement rate limiting"
  ]
}
```

### Markdown Format

```markdown
# Architecture Overview

Complete data platform for analytics with ClickHouse...

# Component Specifications

## ClickHouse Database
### Kubernetes Manifests
```yaml
apiVersion: clickhouse.altinity.com/v1
kind: ClickHouseInstallation
...
```

## FastAPI Backend
...

# Resource Estimates

- Total CPU: 4 cores
- Total Memory: 16GB
- Total Storage: 200GB

# Cost Estimate

- VPS: $100/month
- Managed Services: $20/month
- **Total: $120/month**

# Deployment Steps

1. Deploy Kubernetes cluster
2. Install ClickHouse operator
3. Create ClickHouse cluster
4. Deploy backend services
5. Deploy frontend dashboard

# Recommendations

- Use persistent volumes for data
- Configure automated backups
- Set up monitoring alerts
- Implement rate limiting
```

## Metadata

Each response includes metadata:

```python
result = await agent.process(requirements)

metadata = result["metadata"]
# {
#   "agent_id": "platform-designer-001",
#   "agent_name": "Platform Designer",
#   "timestamp": "2026-03-03T18:00:00Z",
#   "requirements": "...",
#   "constraints": "...",
#   "output_format": "markdown",
#   "model": "claude-3-5-sonnet-20241022"
# }
```

## Health Checks

Monitor agent health and LLM provider status:

```python
health = await agent.health_check()

# Returns:
# {
#   "agent_id": "platform-designer-001",
#   "name": "Platform Designer",
#   "version": "1.0.0",
#   "status": "ready",  # ready, processing, error, etc.
#   "llm_provider": "claude",
#   "model": "claude-3-5-sonnet-20241022",
#   "uptime_seconds": 3600,
#   "tasks_processed": 10,
#   "last_error": null
# }
```

## Design Principles

The agent follows these design principles when generating platforms:

### 1. Scalability
- Design for horizontal scaling
- Use auto-scaling (HPA) where appropriate
- Consider load balancing strategies

### 2. Security
- Zero-trust architecture
- Least privilege access
- Secret management
- Network policies

### 3. Reliability
- High availability where needed
- Automated backups
- Disaster recovery plans
- Health checks and readiness probes

### 4. Cost-Effective
- Optimize resource usage
- Right-size components
- Use spot instances when appropriate
- Consider managed vs. self-hosted trade-offs

### 5. Maintainable
- Clear documentation
- Version control
- Infrastructure as code
- Monitoring and observability

## Components Considered

The agent can design platforms with:

**Databases:**
- PostgreSQL, MySQL (OLTP)
- ClickHouse, TimescaleDB (OLAP)
- Redis (cache)
- MongoDB (document)

**API Services:**
- FastAPI, Django REST (Python)
- Express.js, NestJS (Node.js)
- Go, Rust (performance)

**Frontend:**
- React, Next.js (SPA)
- Vue.js, Nuxt.js
- Static sites (Hugo, Jekyll)

**Messaging:**
- RabbitMQ, Apache Kafka
- Redis Streams
- AWS SQS, Pub/Sub

**Caching:**
- Redis, Memcached
- CDN caching (Cloudflare, AWS CloudFront)

**Monitoring:**
- Prometheus + Grafana
- Datadog, New Relic
- ELK Stack (Elasticsearch, Logstash, Kibana)

**Ingress:**
- NGINX Ingress Controller
- Traefik
- AWS ALB, GCP Ingress

## Error Handling

The agent provides specific error types:

```python
from agents.errors import (
    AgentInitializationError,
    AgentExecutionError,
    AgentConfigError,
)

try:
    result = await agent.process(requirements)
except AgentInitializationError as e:
    print(f"Failed to initialize agent: {e}")
except AgentExecutionError as e:
    print(f"Design generation failed: {e}")
except AgentConfigError as e:
    print(f"Configuration error: {e}")
```

## Testing

Run unit tests:

```bash
cd apps/backend
python -m pytest src/agents/test_platform_designer.py -v
```

Run specific test:

```bash
python -m pytest src/agents/test_platform_designer.py::TestPlatformDesignerAgent::test_process_string_input -v
```

Run with coverage:

```bash
python -m pytest src/agents/test_platform_designer.py --cov=src/agents/platform_designer --cov-report=html
```

## Performance Considerations

### LLM Request Time

- Simple design: ~10-30 seconds
- Complex platform: ~60-120 seconds
- Very large platforms: ~2-5 minutes

### Recommendations

1. **Cache designs** for similar requirements
2. **Use lower temperature** for more consistent results
3. **Be specific** in requirements to reduce iteration
4. **Use JSON format** for programmatic processing
5. **Implement timeout handling** for long-running designs

## Use Cases

### 1. Rapid Prototyping

Generate complete platform designs in minutes instead of days:

```python
prototype = await agent.process("""
I need a quick prototype for real-time analytics:
- Stream ingestion
- Time-series database
- Simple dashboard
- Cost < $50/month
""")
```

### 2. Cost Optimization

Analyze current infrastructure and suggest cost-saving alternatives:

```python
current_setup = """
Currently running:
- PostgreSQL on dedicated instance
- Custom ETL pipeline
- Static HTML dashboard
- Cost: $200/month

Goal: Reduce cost while maintaining functionality
"""

optimized = await agent.process(current_setup)
```

### 3. Migration Planning

Plan migration to Kubernetes and cloud-native technologies:

```python
migration = await agent.process("""
Migrate existing platform to Kubernetes:
- Current: 3 EC2 instances with Docker Compose
- Target: EKS cluster with ClickHouse
- Maintain zero downtime
- Improve scalability
""")
```

### 4. Multi-Cloud Design

Design platforms spanning multiple cloud providers:

```python
multi_cloud = await agent.process("""
Multi-cloud data platform:
- ClickHouse on GCP (best pricing)
- API services on AWS (existing infrastructure)
- Frontend on Cloudflare (CDN)
- Disaster recovery to Azure
""")
```

## Best Practices

1. **Be Specific**: Provide clear, detailed requirements for better designs
2. **Set Constraints**: Define budget, region, and availability requirements
3. **Iterate**: Use feedback to refine designs in multiple passes
4. **Review**: Always review generated designs before deployment
5. **Test**: Validate manifests in a dev environment first
6. **Document**: Keep track of design decisions and trade-offs
7. **Monitor**: Set up comprehensive monitoring after deployment
8. **Backup**: Configure automated backups for all data stores

## Limitations

- Designs are AI-generated and should be reviewed by human architects
- May not account for all edge cases or specific requirements
- Cost estimates are approximate and depend on actual usage
- Security configurations may need customization for compliance requirements
- Performance characteristics should be validated with load testing

## Troubleshooting

### Agent Fails to Initialize

**Symptom**: `AgentInitializationError`

**Solutions**:
- Check LLM provider API key is set
- Verify network connectivity to LLM API
- Ensure API quota/credits are sufficient
- Check logs for detailed error messages

### Design Generation Times Out

**Symptom**: `AgentTimeoutError`

**Solutions**:
- Increase `task_timeout` in configuration
- Simplify requirements for faster generation
- Use lower `max_tokens` limit
- Check LLM API response times

### Invalid JSON Output

**Symptom**: JSON parse error in result

**Solutions**:
- Agent automatically falls back to markdown format
- Check `result["error"]` for details
- Try with "markdown" format instead
- Simplify requirements to reduce complexity

### Poor Design Quality

**Symptom**: Generated design doesn't meet needs

**Solutions**:
- Provide more specific requirements
- Add detailed constraints
- Lower `temperature` for more deterministic results
- Iterate: refine design with follow-up prompts

## API Reference

### PlatformDesignerAgent

**Constructor**: `PlatformDesignerAgent(config: AgentConfig)`

**Methods**:
- `async initialize()` → None
- `async process(input_data: Any, metadata: Optional[Dict] = None)` → Dict[str, Any]
- `async shutdown()` → None
- `async health_check()` → Dict[str, Any]

### get_platform_config()

**Returns**: `AgentConfig` - Default configuration for Platform Designer Agent

## Contributing

To extend the Platform Designer Agent:

1. Add new capabilities in `_build_system_prompt()`
2. Extend output parsing in `_parse_response()`
3. Add new validation logic in `process()`
4. Write comprehensive tests
5. Update documentation

## License

MIT License - See LICENSE file

## Related Documentation

- [AI Agent Framework](./README.md) - Base framework documentation
- [Query Agent](../query/) - NL to SQL conversion agent
- [Support Agent](../support/) - Customer assistance agent

## Changelog

### Version 1.0.0 (2026-03-03)
- Initial release
- DESIGN, ANALYSIS, GENERATION capabilities
- Support for Claude, GPT-4, GLM-5
- JSON and Markdown output formats
- Comprehensive documentation and tests
