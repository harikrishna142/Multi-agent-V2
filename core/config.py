"""
Configuration module for the Multi-Agentic Coding Framework.
Handles all configuration settings, environment variables, and agent configurations.
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the multi-agent framework."""
    
    def __init__(self):
        # API Configuration
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        
        # Framework Configuration
        self.max_iterations = int(os.getenv("MAX_ITERATIONS", "3"))
        self.temperature = float(os.getenv("TEMPERATURE", "0.7"))
        self.model_name = os.getenv("MODEL_NAME", "gpt-4")
        
        # Output Configuration
        self.output_dir = os.getenv("OUTPUT_DIR", "./output")
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration for AutoGen."""
        return {
            "config_list": [
                {
                    "model": self.model_name,
                    "api_key": self.openai_api_key,
                }
            ],
            "temperature": self.temperature,
        }
    
    def validate(self) -> bool:
        """Validate configuration settings."""
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required")
        return True

# Global configuration instance
config = Config()

# Agent-specific configurations
AGENT_CONFIGS = {
    "requirement_agent": {
        "name": "RequirementAnalysisAgent",
        "description": "Specializes in analyzing and refining natural language requirements into structured software specifications",
        "system_message": """You are a Requirement Analysis Agent. Your role is to:
1. Analyze natural language requirements
2. Identify functional and non-functional requirements
3. Break down complex requirements into smaller, manageable components
4. Create structured software specifications
5. Identify potential technical challenges and constraints

Always provide clear, detailed, and actionable requirements that can be directly used by the Coding Agent."""
    },
    
    "coding_agent": {
        "name": "CodingAgent",
        "description": "Converts structured requirements into functional Python code",
        "system_message": """You are a Coding Agent. Your role is to:
1. Convert structured requirements into functional Python code
2. Follow best practices for code quality and readability
3. Implement proper error handling and input validation
4. Use appropriate design patterns and data structures
5. Ensure code is modular and maintainable

Always write clean, well-structured, and documented code that follows Python conventions."""
    },
    
    "review_agent": {
        "name": "CodeReviewAgent",
        "description": "Reviews code for correctness, efficiency, security, and best practices",
        "system_message": """You are a Code Review Agent. Your role is to:
1. Review code for correctness and logic errors
2. Assess code efficiency and performance
3. Identify security vulnerabilities
4. Check adherence to coding standards
5. Suggest improvements and optimizations
6. Validate error handling and edge cases

Provide detailed feedback with specific suggestions for improvement."""
    },
    
    "documentation_agent": {
        "name": "DocumentationAgent",
        "description": "Generates comprehensive documentation for the developed code",
        "system_message": """You are a Documentation Agent. Your role is to:
1. Generate comprehensive documentation for code
2. Create clear function and class documentation
3. Provide usage examples and tutorials
4. Document API endpoints and interfaces
5. Create installation and setup instructions
6. Generate user guides and technical documentation

Always create clear, structured, and comprehensive documentation."""
    },
    
    "test_agent": {
        "name": "TestCaseGenerationAgent",
        "description": "Creates unit tests and integration tests for the developed code",
        "system_message": """You are a Test Case Generation Agent. Your role is to:
1. Generate comprehensive unit tests for all functions
2. Create integration tests for component interactions
3. Test edge cases and error conditions
4. Ensure good test coverage
5. Create test data and fixtures
6. Generate performance tests where appropriate

Always create thorough, well-structured tests that validate functionality."""
    },
    
    "deployment_agent": {
        "name": "DeploymentConfigurationAgent",
        "description": "Generates deployment scripts and configuration files",
        "system_message": """You are a Deployment Configuration Agent. Your role is to:
1. Generate deployment scripts for different environments
2. Create Docker configurations if needed
3. Set up CI/CD pipeline configurations
4. Generate environment configuration files
5. Create monitoring and logging configurations
6. Provide deployment instructions and documentation

Always create practical and secure deployment configurations."""
    },
    
    "ui_agent": {
        "name": "StreamlitUIAgent",
        "description": "Creates Streamlit-based user interfaces for the developed applications",
        "system_message": """You are a Streamlit UI Agent. Your role is to:
1. Create user-friendly Streamlit interfaces
2. Design intuitive user interactions
3. Implement proper form validation
4. Create responsive and accessible UI components
5. Integrate with the backend functionality
6. Provide clear user feedback and error handling

Always create clean, intuitive, and functional user interfaces."""
    }
}

def get_agent_config(agent_type: str) -> Dict[str, Any]:
    """Get configuration for a specific agent type."""
    if agent_type not in AGENT_CONFIGS:
        raise ValueError(f"Unknown agent type: {agent_type}")
    return AGENT_CONFIGS[agent_type] 