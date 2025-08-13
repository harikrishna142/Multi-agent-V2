"""
Requirement Analysis Agent for the Multi-Agentic Coding Framework.
Refines natural language requirements into structured software specifications.
"""

import autogen
import re
from datetime import datetime
from typing import Dict, Any, List
from core.config import get_agent_config, config
from core.utils import save_json, setup_logging
from core.validation import validate_requirement_analysis, sanitize_llm_output

logger = setup_logging()

class RequirementAnalysisAgent:
    """Agent responsible for analyzing and refining requirements."""
    
    def __init__(self):
        self.agent_config = get_agent_config("requirement_agent")
        self.llm_config = config.get_llm_config()
        
        # Create the agent
        self.agent = autogen.AssistantAgent(
            name=self.agent_config["name"],
            system_message=self.agent_config["system_message"],
            llm_config=self.llm_config
        )
        
        # Create user proxy for interaction
        self.user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=10,
            is_termination_msg=lambda x: "TERMINATE" in x.get("content", ""),
            code_execution_config={"work_dir": "workspace", "use_docker": False},
            llm_config=self.llm_config
        )
    
    def analyze_requirement(self, natural_language_requirement: str) -> Dict[str, Any]:
        """
        Analyze natural language requirement and convert to structured format.
        
        Args:
            natural_language_requirement: The original requirement in natural language
            
        Returns:
            Dict containing structured requirements
        """
        logger.info("Starting requirement analysis")
        
        # Create the analysis prompt
        analysis_prompt = f"""
Please analyze the following software requirement and provide a structured breakdown:

REQUIREMENT: {natural_language_requirement}

Based on this requirement, please provide a comprehensive analysis in the following JSON format:

{{
    "project_name": "",
    "description": "",
    "functional_requirements": [
        {{
            "id": "FR001",
            "title": "",
            "description": "",
            "priority": "",
            "acceptance_criteria": []
        }}
    ],
    "non_functional_requirements": [
        {{
            "id": "NFR001",
            "title": "",
            "description": "",
            "category": ""
        }}
    ],
    "technical_constraints": [],
    "assumptions": [],
    "dependencies": [],
    "estimated_complexity": "",
    "suggested_architecture": "",
    "key_components": []
}}

ANALYSIS GUIDELINES:
1. Project Name: Create a clear, descriptive name that reflects the main purpose
2. Description: Explain what the application will do and its main features   
3. Functional Requirements: List specific features and capabilities the system must have
4. Non-Functional Requirements: Consider performance, security, usability, reliability
5. Technical Constraints: Any limitations or requirements for technology/platform
6. Assumptions: What you assume about users, environment, or other factors   
7. Dependencies: External systems, libraries, or services needed
8. Complexity: Assess the overall complexity based on features and requirements
9. Architecture: Suggest an appropriate technical architecture
10. Key Components: Main modules or components the system will need

CRITICAL INSTRUCTIONS:
- You MUST fill in ALL empty fields with your actual analysis
- Do NOT leave any fields empty or with placeholder text
- Do NOT copy the template structure - replace it with real content
- Generate a complete, functional project specification
- Be specific and detailed in your analysis

IMPORTANT: End your response with the word "TERMINATE" to indicate completion.
"""
        
        try:
            # Start the conversation
            chat_result = self.user_proxy.initiate_chat(
                self.agent,
                message=analysis_prompt
            )
            
            # Extract the last message from the agent
            last_message = None
            logger.info(f"Chat history length: {len(chat_result.chat_history)}")
            
            # Log all messages for debugging
            for i, message in enumerate(chat_result.chat_history):
                role = message.get("role", "unknown")
                content_preview = message.get("content", "")[:100]
                logger.info(f"Message {i}: role={role}, content_preview={content_preview}...")
            
            # Find the LLM response - it's in the user message (AutoGen structure)
            for message in reversed(chat_result.chat_history):
                if message.get("role") == "user":
                    last_message = message.get("content", "")
                    logger.info(f"Found user message (LLM response) with length: {len(last_message)}")
                    break
            
            # If no user message found, fall back to assistant message
            if not last_message:
                for message in reversed(chat_result.chat_history):
                    if message.get("role") == "assistant":
                        last_message = message.get("content", "")
                        logger.info(f"Found assistant message with length: {len(last_message)}")
                        break
            
            if not last_message:
                raise ValueError("No response received from requirement analysis agent")
            
            # Debug: Log the actual response content
            logger.info(f"Full response length: {len(last_message)}")
            logger.info(f"Response preview: {last_message[:500]}...")
            logger.info(f"Response ends with: {last_message[-100:]}")
            
            # Save the full response for debugging
            with open('debug_last_message.txt', 'w', encoding='utf-8') as f:
                f.write(last_message)
            logger.info("Full response saved to debug_last_message.txt")
            
            # Use Pydantic validation to extract and validate the requirement analysis
            try:
                # Clean up the LLM output
                cleaned_output = sanitize_llm_output(last_message)
                
                # Validate and extract the requirement analysis
                validated_requirements = validate_requirement_analysis(cleaned_output)
                
                # Convert Pydantic model to dictionary
                structured_requirements = validated_requirements.dict()
                
                logger.info("✅ Successfully validated requirement analysis using Pydantic")
                logger.info(f"Project name: {structured_requirements.get('project_name', 'N/A')}")
                
            except Exception as e:
                logger.error(f"Validation failed: {e}")
                logger.info("Falling back to basic structure")
                
                # Fall back to basic structure
                structured_requirements = {
                    "project_name": "Generated Project",
                    "description": natural_language_requirement,
                    "functional_requirements": [
                        {
                            "id": "FR001",
                            "title": "Main Functionality",
                            "description": natural_language_requirement,
                            "priority": "high",
                            "acceptance_criteria": ["Functionality works as described"]
                        }
                    ],
                    "non_functional_requirements": [],
                    "technical_constraints": [],
                    "assumptions": [],
                    "dependencies": [],
                    "estimated_complexity": "medium",
                    "suggested_architecture": "Modular Python application",
                    "key_components": ["Main application module"]
                }
            
            # Add metadata
            structured_requirements["original_requirement"] = natural_language_requirement
            structured_requirements["analysis_timestamp"] = str(datetime.now())
            
            logger.info("Requirement analysis completed successfully")
            return structured_requirements
            
        except Exception as e:
            logger.error(f"Error in requirement analysis: {e}")
            # Return a basic structure in case of error
            return {
                "project_name": "Generated Project",
                "description": natural_language_requirement,
                "functional_requirements": [
                    {
                        "id": "FR001",
                        "title": "Main Functionality",
                        "description": natural_language_requirement,
                        "priority": "high",
                        "acceptance_criteria": ["Functionality works as described"]
                    }
                ],
                "non_functional_requirements": [],
                "technical_constraints": [],
                "assumptions": [],
                "dependencies": [],
                "estimated_complexity": "medium",
                "suggested_architecture": "Modular Python application",
                "key_components": ["Main application module"],
                "original_requirement": natural_language_requirement,
                "analysis_timestamp": str(datetime.now()),
                "error": str(e)
            }
    
    def save_requirements(self, requirements: Dict[str, Any], project_id: str) -> str:
        """Save structured requirements to a JSON file."""
        filename = f"{project_id}_requirements.json"
        return save_json(requirements, filename, config.output_dir)
    
    def get_requirements_summary(self, requirements: Dict[str, Any]) -> str:
        """Generate a human-readable summary of the requirements."""
        summary = f"""
# Project Requirements Summary

## Project: {requirements.get('project_name', 'N/A')}

### Description
{requirements.get('description', 'N/A')}

### Functional Requirements ({len(requirements.get('functional_requirements', []))})
"""
        
        for req in requirements.get('functional_requirements', []):
            summary += f"""
- **{req.get('id', 'N/A')}: {req.get('title', 'N/A')}**
  - Priority: {req.get('priority', 'N/A')}
  - Description: {req.get('description', 'N/A')}
  - Acceptance Criteria: {', '.join(req.get('acceptance_criteria', []))}
"""
        
        summary += f"""
### Non-Functional Requirements ({len(requirements.get('non_functional_requirements', []))})
"""
        
        for req in requirements.get('non_functional_requirements', []):
            summary += f"""
- **{req.get('id', 'N/A')}: {req.get('title', 'N/A')}**
  - Category: {req.get('category', 'N/A')}
  - Description: {req.get('description', 'N/A')}
"""
        
        summary += f"""
### Technical Constraints
{chr(10).join(f'- {constraint}' for constraint in requirements.get('technical_constraints', []))}

### Assumptions
{chr(10).join(f'- {assumption}' for assumption in requirements.get('assumptions', []))}

### Dependencies
{chr(10).join(f'- {dependency}' for dependency in requirements.get('dependencies', []))}

### Architecture Suggestion
{requirements.get('suggested_architecture', 'N/A')}

### Key Components
{chr(10).join(f'- {component}' for component in requirements.get('key_components', []))}

### Estimated Complexity
{requirements.get('estimated_complexity', 'N/A')}
"""
        
        return summary 