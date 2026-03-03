"""
Platform Designer Agent for AI Data Labs.

This agent takes natural language infrastructure requirements and produces:
- Architecture design documents
- Kubernetes manifests
- Resource estimates
- Cost analysis
- Deployment recommendations
"""

import json
import os
from typing import Any, Dict, Optional

from .base import BaseAgent, AgentCapability, AgentStatus
from .config import AgentConfig, AgentType, LLMProviderConfig
from .errors import AgentConfigError, AgentInitializationError, AgentExecutionError
from llm_providers import create_llm_provider


class PlatformDesignerAgent(BaseAgent):
    """
    AI agent that designs infrastructure platforms from natural language requirements.

    Capabilities:
    - DESIGN: Create infrastructure designs
    - ANALYSIS: Analyze requirements and recommend solutions
    - GENERATION: Generate Kubernetes manifests and configuration

    Example usage:
        agent = PlatformDesignerAgent(config)
        await agent.initialize()
        result = await agent.process({
            "requirements": "I need a data platform with ClickHouse for analytics, FastAPI backend, and React frontend...",
            "constraints": "Cost < $100/month, single node deployment"
        })
    """

    def __init__(self, config: AgentConfig):
        """
        Initialize the Platform Designer agent.

        Args:
            config: Agent configuration
        """
        super().__init__(config)
        self.llm_provider = None

    async def initialize(self) -> None:
        """
        Initialize the agent.

        Sets up the LLM provider and validates configuration.

        Raises:
            AgentInitializationError: If initialization fails
        """
        try:
            self.set_status(AgentStatus.INITIALIZING)
            self.logger.info("Initializing Platform Designer Agent...")

            # Create LLM provider from config
            if not self.config.llm_provider:
                raise AgentConfigError("LLM provider configuration required")

            self.llm_provider = create_llm_provider(
                provider=self.config.llm_provider.provider,
                model=self.config.llm_provider.model,
                api_key=self.config.llm_provider.api_key,
                api_url=self.config.llm_provider.api_url,
                temperature=self.config.llm_provider.temperature,
                max_tokens=self.config.llm_provider.max_tokens,
            )

            # Validate LLM connection
            self.logger.info("Testing LLM provider connection...")
            test_response = await self.llm_provider.generate([
                {"role": "user", "content": "Test connection"}
            ])
            self.logger.info(f"LLM connection successful: {len(test_response)} chars")

            self.set_status(AgentStatus.READY)
            self.logger.info("Platform Designer Agent initialized successfully")

        except Exception as e:
            self.set_status(AgentStatus.ERROR)
            self.logger.error(f"Failed to initialize Platform Designer Agent: {e}")
            raise AgentInitializationError(f"Initialization failed: {e}")

    async def process(
        self,
        input_data: Any,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Process infrastructure requirements and produce a design.

        Args:
            input_data: Can be:
                - String (natural language requirements)
                - Dict with keys:
                  - 'requirements': Natural language description
                  - 'constraints': Optional constraints (budget, single-node, etc.)
                  - 'format': Optional output format (json, yaml, markdown)
            metadata: Optional request metadata

        Returns:
            Dictionary with:
                - 'design': Architecture description
                - 'components': List of components with specs
                - 'kubernetes_manifests': Dict of K8s manifests
                - 'resource_estimates': CPU/memory estimates
                - 'cost_estimate': Monthly cost estimate
                - 'recommendations': Additional recommendations

        Raises:
            AgentExecutionError: If processing fails
        """
        try:
            self.set_status(AgentStatus.PROCESSING)
            self.logger.info("Processing platform design request...")

            # Parse input
            if isinstance(input_data, str):
                requirements = input_data
                constraints = ""
                output_format = "markdown"
            elif isinstance(input_data, dict):
                requirements = input_data.get("requirements", "")
                constraints = input_data.get("constraints", "")
                output_format = input_data.get("format", "markdown")
            else:
                raise ValueError("input_data must be string or dict")

            if not requirements:
                raise ValueError("No requirements provided")

            # Build prompt
            system_prompt = self._build_system_prompt(constraints, output_format)
            user_prompt = f"""## Infrastructure Requirements

{requirements}

## Additional Constraints

{constraints if constraints else "None specified"}

Please provide a comprehensive platform design.
"""

            # Generate response from LLM
            self.logger.info("Generating design using LLM...")
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]

            response = await self.llm_provider.generate(messages)
            self.logger.info(f"Received response: {len(response)} characters")

            # Parse response based on format
            result = self._parse_response(response, output_format)

            # Add metadata
            result["metadata"] = {
                "agent_id": self.config.agent_id,
                "agent_name": self.config.name,
                "timestamp": self._get_timestamp(),
                "requirements": requirements,
                "constraints": constraints,
                "output_format": output_format,
                "model": self.config.llm_provider.model,
            }

            self.set_status(AgentStatus.READY)
            self.logger.info("Platform design generation completed successfully")
            return result

        except Exception as e:
            self.set_status(AgentStatus.ERROR)
            self.logger.error(f"Failed to process platform design: {e}")
            raise AgentExecutionError(f"Processing failed: {e}")

    def _build_system_prompt(self, constraints: str, output_format: str) -> str:
        """
        Build the system prompt for the Platform Designer.

        Args:
            constraints: User constraints
            output_format: Desired output format (json/markdown)

        Returns:
            System prompt string
        """
        base_prompt = """You are an expert cloud infrastructure architect and DevOps engineer. Your expertise includes Kubernetes, microservices architecture, cost optimization, and platform design.

Your task: design a complete, production-ready data platform based on the provided requirements.

## Design Principles

1. **Scalability**: Design for growth
2. **Security**: Implement zero-trust, least privilege
3. **Reliability**: HA, backups, monitoring
4. **Cost-Effective**: Optimize for the budget
5. **Maintainable**: Clear documentation, version control

## Components to Consider

- Databases (PostgreSQL, ClickHouse, Redis, etc.)
- API services (FastAPI, Node.js, etc.)
- Frontend (React, Next.js, static sites)
- Message queues (RabbitMQ, Kafka)
- Caching (Redis)
- Monitoring (Prometheus, Grafana)
- Ingress controllers (NGINX, Traefik)
- Storage (Persistent volumes, object storage)

## Output Structure

Provide:
1. **Architecture Overview**: High-level diagram and description
2. **Component Specifications**: CPU, memory, storage for each
3. **Kubernetes Manifests**: YAML for deployments, services, ingress, etc.
4. **Resource Estimates**: Total CPU, memory, storage needs
5. **Cost Estimate**: Monthly cost breakdown (VPS, managed services)
6. **Deployment Steps**: How to deploy the platform
7. **Recommendations**: Best practices, security, monitoring

## Constraints Consideration

Always respect the user's constraints. If constraints conflict with best practices, explain the trade-offs.

Now, generate the design based on the requirements.
"""

        if constraints:
            base_prompt += f"\n\n## Additional Constraints\n{constraints}\n\nPlease ensure the design respects these constraints."

        if output_format == "json":
            base_prompt += """

## Output Format

Return your response as valid JSON with this structure:
{
  "architecture_overview": "...",
  "components": [
    {
      "name": "...",
      "type": "...",
      "description": "...",
      "specs": {
        "cpu": "...",
        "memory": "...",
        "storage": "..."
      },
      "kubernetes_yaml": "..."
    }
  ],
  "resource_estimates": {
    "total_cpu": "...",
    "total_memory": "...",
    "total_storage": "..."
  },
  "cost_estimate": {
    "monthly_total": "...",
    "breakdown": {
      "vps": "...",
      "managed_services": "...",
      "bandwidth": "..."
    }
  },
  "deployment_steps": ["..."],
  "recommendations": ["..."]
}
"""
        else:
            base_prompt += """

## Output Format

Return in Markdown format with sections:
# Architecture Overview
# Component Specifications
## [Component Name]
### Kubernetes Manifests
```yaml
...
```
# Resource Estimates
# Cost Estimate
# Deployment Steps
# Recommendations
"""

        return base_prompt

    def _parse_response(
        self, response: str, output_format: str
    ) -> Dict[str, Any]:
        """
        Parse the LLM response into structured data.

        Args:
            response: Raw LLM response
            output_format: Expected format (json or markdown)

        Returns:
            Parsed dictionary
        """
        if output_format == "json":
            try:
                return json.loads(response)
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse JSON response: {e}")
                # Fallback: return as raw text in markdown format
                return {
                    "design": response,
                    "format": "raw",
                    "error": "JSON parse failed, returning raw response",
                }
        else:
            # For markdown, return as structured dict with sections
            return {
                "design": response,
                "format": "markdown",
                "sections": self._extract_markdown_sections(response),
            }

    def _extract_markdown_sections(self, markdown: str) -> Dict[str, str]:
        """
        Extract sections from markdown.

        Args:
            markdown: Markdown text

        Returns:
            Dictionary mapping section titles to content
        """
        sections = {}
        current_section = None
        current_content = []

        for line in markdown.split("\n"):
            if line.startswith("# "):
                if current_section:
                    sections[current_section] = "\n".join(current_content).strip()
                current_section = line[2:].strip()
                current_content = []
            elif current_section:
                current_content.append(line)

        if current_section:
            sections[current_section] = "\n".join(current_content).strip()

        return sections

    def _get_timestamp(self) -> str:
        """Get current UTC timestamp in ISO format."""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"

    async def health_check(self) -> Dict[str, Any, bool]:
        """Extended health check with LLM provider status."""
        base_health = await super().health_check()
        base_health["llm_provider"] = self.config.llm_provider.provider if self.config.llm_provider else None
        base_health["model"] = self.config.llm_provider.model if self.config.llm_provider else None
        return base_health


def get_platform_config() -> AgentConfig:
    """
    Get default configuration for Platform Designer Agent.

    Returns:
        AgentConfig instance
    """
    return AgentConfig(
        agent_id="platform-designer-001",
        name="Platform Designer",
        version="1.0.0",
        agent_type=AgentType.DESIGN,
        capabilities=[
            AgentCapability.DESIGN,
            AgentCapability.ANALYSIS,
            AgentCapability.GENERATION,
        ],
        llm_provider=LLMProviderConfig(
            provider=os.getenv("PLATFORM_DESIGNER_LLM_PROVIDER", "claude"),
            model=os.getenv("PLATFORM_DESIGNER_LLM_MODEL", "claude-3-5-sonnet-20241022"),
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            temperature=0.7,
            max_tokens=8192,
            timeout=60,
        ),
        max_concurrent_tasks=3,
        task_timeout=600,  # 10 minutes for design generation
        memory_limit_mb=1024,
        log_level="INFO",
    )
