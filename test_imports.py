#!/usr/bin/env python3
"""Simple test to verify the agent framework imports work."""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/company/apps/backend/src')

try:
    # Test basic imports
    from agents.enums import AgentStatus, AgentCapability, AgentType
    print("✓ Successfully imported enums: AgentStatus, AgentCapability, AgentType")
    
    from agents.base import BaseAgent, AgentMessage
    print("✓ Successfully imported base: BaseAgent, AgentMessage")
    
    from agents.config import AgentConfig
    print("✓ Successfully imported config: AgentConfig")
    
    from agents.errors import AgentError
    print("✓ Successfully imported errors: AgentError")
    
    from agents.registry import AgentRegistry
    print("✓ Successfully imported registry: AgentRegistry")
    
    from agents.communication import CommunicationChannel
    print("✓ Successfully imported communication: CommunicationChannel")
    
    from agents.task_queue import TaskQueue, TaskStatus, TaskPriority
    print("✓ Successfully imported task_queue: TaskQueue, TaskStatus, TaskPriority")
    
    from agents.framework_config import AgentFrameworkManager, FrameworkConfig, AgentFramework
    print("✓ Successfully imported framework_config: AgentFrameworkManager, FrameworkConfig")
    
    print("\n" + "="*80)
    print("All imports successful! Framework structure is valid.")
    print("="*80)
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    print(f"  File: {e.__traceback__.tb_frame.f_code.co_filename}")
    print(f"  Line: {e.__traceback__.tb_lineno}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
