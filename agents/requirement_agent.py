"""
Enhanced Requirement Analysis Agent
Generates detailed, technical specifications for complete application development.
"""

import autogen, time
from typing import Dict, Any, List
from core.config import get_agent_config, config
from core.utils import setup_logging

logger = setup_logging()

class RequirementAgent:
    """Enhanced requirement analysis agent that generates complete technical specifications."""
    
    def __init__(self):
        self.agent_config = get_agent_config("requirement_agent")
        self.llm_config = config.get_llm_config()
        
        # Create the agent with enhanced system message
        enhanced_system_message = self._get_system_message()
        
        self.agent = autogen.AssistantAgent(
            name=self.agent_config["name"],
            system_message=enhanced_system_message,
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
    
    def _get_system_message(self) -> str:
        """Get system message for requirement analysis."""
        return """You are a helpful requirement analyst that creates simple, clear specifications for basic applications. You analyze user requirements and create straightforward technical specifications.

## YOUR ROLE:
- Analyze natural language requirements
- Create simple, achievable specifications for basic version of the application that cane ruunable
- Define basic functional requirements
- Suggest simple technology stacks
- Generate basic architecture descriptions

## ANALYSIS PROCESS:
1. **Understand the basic requirement** from user input
2. **Identify simple features** that can be implemented
3. **Choose basic technology stack** (Flask, React, SQLite, etc.)
4. **Create simple architecture** description
5. **Define basic functional requirements**
6. **Generate simple API specifications**

## SPECIFICATION REQUIREMENTS:

### 1. **Project Overview**:
- Simple project name and description
- Basic technology stack (backend, frontend, database)
- Simple version information

### 2. **Functional Requirements**:
- List basic features that can be implemented
- Simple descriptions of each feature
- Basic priority levels (High, Medium, Low)
- Simple acceptance criteria

### 3. **Architecture**:
- Simple system design description
- Basic database schema (if needed)
- Simple API endpoints
- Basic file structure

### 4. **Technology Stack**:
- Choose simple, popular frameworks
- Use basic databases (SQLite, simple file storage)
- Include basic dependencies
- Keep it simple and achievable

## IMPORTANT GUIDELINES:

✅ **Keep specifications simple and achievable**
✅ **Use basic, well-known technologies**
✅ **Focus on core functionality**
✅ **Create specifications for basic applications**
✅ **Make requirements clear and simple**

❌ **Do not create complex enterprise specifications**
❌ **Do not demand advanced features**
❌ **Do not require complex architectures**
❌ **Do not specify production-level requirements**

**YOUR TASK**: Create simple, clear specifications for a basic application based on the user's requirements.

End your response with "TERMINATE" to indicate completion."""
    
    def analyze_requirements(self, natural_language_input: str, project_id: str = None) -> Dict[str, Any]:
        """
        Analyze natural language input and generate comprehensive technical specifications.
        
        Args:
            natural_language_input: Natural language description of the project
            project_id: Optional project ID to use (if not provided, will generate one)
            
        Returns:
            Dict containing detailed technical specifications
        """
        logger.info("Starting enhanced requirement analysis")
        
        # Create detailed analysis prompt
        analysis_prompt = self._create_analysis_prompt(natural_language_input)
        
        try:
            # Start the conversation
            chat_result = self.user_proxy.initiate_chat(
                self.agent,
                message=analysis_prompt
            )
            
            # Extract the LLM response
            from core.utils import extract_llm_response
            last_message = extract_llm_response(chat_result)
            
            # Parse the JSON response
            import json
            import re
            
            # Extract JSON from the response
            json_match = re.search(r'```json\s*(.*?)\s*```', last_message, re.DOTALL)
            if json_match:
                specifications = json.loads(json_match.group(1))
            else:
                # Try to find JSON without markdown
                json_match = re.search(r'\{.*\}', last_message, re.DOTALL)
                if json_match:
                    specifications = json.loads(json_match.group(0))
                else:
                    raise ValueError("No valid JSON found in response")
            
            # Validate and enhance specifications
            enhanced_specifications = self._enhance_specifications(specifications)
            
            # Use provided project_id or generate one
            if project_id is None:
                project_id = f"project_{int(time.time())}_{hash(natural_language_input) % 10000:04x}"
            
            result = {
                "project_id": project_id,
                "natural_language_input": natural_language_input,
                "specifications": enhanced_specifications,
                "analysis_timestamp": time.time(),
                "total_requirements": len(enhanced_specifications.get("functional_requirements", [])),
                
            }
            
            # Save specifications to file
            self._save_specifications_to_file(result, project_id)
            
            print(f"Parsed Specifications: {json.dumps(enhanced_specifications, indent=2)}")
            print(f"Final Result: {json.dumps(result, indent=2)}")
            logger.info(f"Enhanced requirement analysis completed. Generated {result['total_requirements']} detailed requirements.")
            return result
            
        except Exception as e:
            logger.error(f"Error in enhanced requirement analysis: {e}")
            return self._generate_fallback_specifications(natural_language_input, str(e))
    
    def _create_analysis_prompt(self, natural_language_input: str) -> str:
        """Create detailed analysis prompt."""
        
        return f"""
Please analyze the following project requirement and generate technical specifications for basic version of the application that can run:

## PROJECT REQUIREMENT:
{natural_language_input}

## ANALYSIS REQUIREMENTS:

1. **Technology Stack Selection**: Choose the most appropriate and modern technology stack for this project     
2. **System Architecture**: simple system architecture for basic version of the application that can demonstrate requirement
3. **Database Design**: if database needed create simple schema
4. **API Design**: if needed implement few endpoints that needed to demonstrate simple demo
5. **Frontend Design**: Specify the frontend framework and component architecture
6. **Security Implementation**: Define basic authentication and security measures
7. **Deployment Strategy**: Specify simple deployment approach

## EXPECTED OUTPUT:

Generate JSON specification that includes:

1. **Project Overview**: project details and technology stack
2. **Architecture**: System design, database schema, and API specifications
3. **Functional Requirements**: Detailed use cases, data models, and business logic
4. **Non-Functional Requirements**: Performance, security, and reliability specifications
5. **Implementation Plan**: Phases, deliverables, and file structure

## IMPORTANT GUIDELINES:

- **Be Specific**: Use exact technology names, versions, and configurations
- **Be Clear**: Every requirement must have detailed implementation specifications for basic version of the application that can run
- **Be Scalable**: Design for growth and future requirements
- **Be Secure**: Include basic security measures
- **Be Modern**: Use current best practices and modern frameworks

## OUTPUT FORMAT:

You MUST respond with ONLY a valid JSON object in this exact format:

```json
{{
  "project_overview": {{
    "name": "Project Name",
    "description": "Project description",
    "version": "1.0.0",
    "technology_stack": {{
      "backend_framework": "flask",
      "frontend_framework": "react",
      "database": "sqlite",
      "api_type": "rest"
    }}
  }},
  "architecture": {{
    "system_design": "Simple description",
    "database_schema": {{
      "tables": [
        {{
          "name": "users",
          "columns": [
            {{"name": "id", "type": "integer", "primary_key": true}},
            {{"name": "username", "type": "string", "nullable": false}}
          ]
        }}
      ]
    }},
    "api_specifications": {{
      "endpoints": [
        {{
          "path": "/api/users",
          "method": "GET",
          "description": "Get all users"
        }}
      ]
    }}
  }},
  "functional_requirements": [
    {{
      "id": "FR001",
      "name": "User Registration",
      "description": "Users can register for an account",
      "priority": "High",
      "acceptance_criteria": ["User can create account", "Email validation"]
    }}
  ],
  "non_functional_requirements": {{
    "performance": "Basic performance requirements",
    "security": "Basic security measures",
    "reliability": "Basic reliability requirements"
  }},
  "implementation_plan": {{
    "phases": [
      {{
        "phase": 1,
        "name": "Setup",
        "deliverables": ["Project structure", "Basic configuration"]
      }}
    ],
    "file_structure": [
      "app.py",
      "requirements.txt",
      "README.md"
    ]
  }}
}}
```

IMPORTANT: Respond with ONLY the JSON object, no additional text or explanations.

TERMINATE
"""
    
    def _enhance_specifications(self, specifications: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance specifications with additional details and validation."""
        
        # Add missing sections if not present
        if "project_overview" not in specifications:
            specifications["project_overview"] = {}
        
        if "architecture" not in specifications:
            specifications["architecture"] = {}
        
        if "functional_requirements" not in specifications:
            specifications["functional_requirements"] = []
        
        if "non_functional_requirements" not in specifications:
            specifications["non_functional_requirements"] = []
        
       
        
        # Add implementation details
        specifications["implementation_details"] = {
            "development_environment": {
                "python_version": "3.11",
                "node_version": "18.0.0",
                "database": "PostgreSQL 15",
                "cache": "Redis 7.0"
            },
            "deployment_environment": {
                "containerization": "Docker",
                "orchestration": "Docker Compose",
                "cloud_provider": "AWS",
                "monitoring": "Prometheus + Grafana"
            }
        }
        
        return specifications
    
    def _generate_fallback_specifications(self, natural_language_input: str, error: str) -> Dict[str, Any]:
        """Generate fallback specifications when analysis fails."""
        
        return {
            "project_id": f"project_{int(time.time())}_{hash(natural_language_input) % 10000:04x}",
            "natural_language_input": natural_language_input,
            "specifications": {
                "project_overview": {
                    "name": "Generated Project",
                    "description": natural_language_input,
                    "version": "1.0.0",
                    "technology_stack": {
                        "backend": {
                            "framework": "FastAPI",
                            "database": "PostgreSQL",
                            "authentication": "JWT"
                        },
                        "frontend": {
                            "framework": "React",
                            "state_management": "Redux Toolkit"
                        }
                    }
                },
                "functional_requirements": [
                    {
                        "id": "FR001",
                        "title": "Basic Functionality",
                        "description": "Implement basic application functionality",
                        "priority": "High"
                    }
                ]
            },
            "error": error,
            "fallback_mode": True
        }
    
    def _save_specifications_to_file(self, result: Dict[str, Any], project_id: str) -> None:
        """
        Save specifications to a JSON file for debugging and reference.
        
        Args:
            result: The complete result from requirement analysis
            project_id: The project ID to use in filename
        """
        try:
            import json
            import os
            from datetime import datetime
            
            # Create output directory if it doesn't exist
            output_dir = "output/requirement_specifications"
            os.makedirs(output_dir, exist_ok=True)
            
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"specifications_{project_id}_{timestamp}.json"
            filepath = os.path.join(output_dir, filename)
            
            # Save the complete result
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Specifications saved to: {filepath}")
            print(f"Specifications saved to: {filepath}")
            
            # Also save a simplified version with just the specifications
            spec_filename = f"specifications_only_{project_id}_{timestamp}.json"
            spec_filepath = os.path.join(output_dir, spec_filename)
            
            with open(spec_filepath, 'w', encoding='utf-8') as f:
                json.dump(result.get("specifications", {}), f, indent=2, ensure_ascii=False)
            
            logger.info(f"Specifications only saved to: {spec_filepath}")
            print(f"Specifications only saved to: {spec_filepath}")
            
        except Exception as e:
            logger.error(f"Failed to save specifications to file: {e}")
            print(f"Failed to save specifications to file: {e}")
