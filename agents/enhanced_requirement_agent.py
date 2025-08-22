"""
Enhanced Requirement Analysis Agent
Generates detailed, technical specifications for complete application development.
"""

import autogen, time
from typing import Dict, Any, List
from core.config import get_agent_config, config
from core.utils import setup_logging

logger = setup_logging()

class EnhancedRequirementAgent:
    """Enhanced requirement analysis agent that generates complete technical specifications."""
    
    def __init__(self):
        self.agent_config = get_agent_config("requirement_agent")
        self.llm_config = config.get_llm_config()
        
        # Create the agent with enhanced system message
        enhanced_system_message = self._create_enhanced_system_message()
        
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
    
    def _create_enhanced_system_message(self) -> str:
        """Create enhanced system message for detailed requirement analysis."""
        
        return """
You are an expert software architect and business analyst specializing in creating detailed, technical specifications for complete software applications. Your task is to transform high-level requirements into comprehensive, implementation-ready specifications.

## REQUIREMENT ANALYSIS REQUIREMENTS:

### 1. Project Architecture Specification:
- **Technology Stack Selection**: Choose the best frameworks and tools
- **System Architecture**: Design the complete system architecture
- **Database Design**: Specify database schema and relationships
- **API Design**: Define RESTful API endpoints and data models
- **Security Architecture**: Specify authentication, authorization, and security measures
- **Deployment Architecture**: Define deployment strategy and infrastructure

### 2. Detailed Functional Specifications:
For each functional requirement, provide:
- **Detailed Use Cases**: Step-by-step user interactions
- **Data Models**: Complete data structures and relationships
- **API Endpoints**: RESTful API specifications with request/response formats
- **Business Logic**: Detailed algorithms and workflows
- **Error Handling**: Comprehensive error scenarios and responses
- **Validation Rules**: Input validation and business rule specifications

### 3. Technical Implementation Details:
- **Database Schema**: Complete table definitions with relationships
- **API Documentation**: OpenAPI/Swagger specifications
- **Authentication System**: JWT, OAuth, or session-based authentication
- **File Structure**: Complete project file organization
- **Dependencies**: Specific versions of all required packages
- **Configuration**: Environment variables and configuration files

### 4. User Interface Specifications:
- **Frontend Framework**: React, Vue, Angular, or other modern framework
- **UI/UX Design**: Component specifications and user flows
- **Responsive Design**: Mobile and desktop compatibility
- **Accessibility**: WCAG compliance specifications
- **State Management**: Redux, Vuex, or other state management

### 5. Non-Functional Requirements:
- **Performance**: Response time, throughput, and scalability requirements
- **Security**: Data protection, encryption, and compliance requirements
- **Reliability**: Availability, fault tolerance, and disaster recovery
- **Maintainability**: Code organization, documentation, and testing requirements

## OUTPUT FORMAT:

Generate a comprehensive JSON specification with the following structure:

```json
{
  "project_overview": {
    "name": "Project Name",
    "description": "Detailed project description",
    "version": "1.0.0",
    "technology_stack": {
      "backend": {
        "framework": "FastAPI/Django/Flask",
        "database": "PostgreSQL/MySQL/MongoDB",
        "authentication": "JWT/OAuth/Session",
        "caching": "Redis/Memcached",
        "message_queue": "Celery/RabbitMQ"
      },
      "frontend": {
        "framework": "React/Vue/Angular",
        "state_management": "Redux/Vuex/NgRx",
        "ui_library": "Material-UI/Ant Design/Tailwind",
        "build_tool": "Webpack/Vite"
      },
      "deployment": {
        "containerization": "Docker",
        "orchestration": "Kubernetes/Docker Compose",
        "cloud_provider": "AWS/Azure/GCP",
        "ci_cd": "GitHub Actions/Jenkins"
      }
    }
  },
  "architecture": {
    "system_design": "Detailed system architecture description",
    "database_schema": {
      "tables": [
        {
          "name": "users",
          "columns": [
            {"name": "id", "type": "UUID", "primary_key": true},
            {"name": "username", "type": "VARCHAR(50)", "unique": true},
            {"name": "email", "type": "VARCHAR(100)", "unique": true},
            {"name": "password_hash", "type": "VARCHAR(255)"},
            {"name": "created_at", "type": "TIMESTAMP", "default": "CURRENT_TIMESTAMP"}
          ],
          "relationships": [
            {"type": "one_to_many", "target": "events", "foreign_key": "organizer_id"}
          ]
        }
      ]
    },
    "api_specification": {
      "base_url": "/api/v1",
      "endpoints": [
        {
          "path": "/users",
          "method": "POST",
          "description": "Create new user",
          "request_body": {
            "username": "string",
            "email": "string",
            "password": "string"
          },
          "response": {
            "201": {
              "id": "UUID",
              "username": "string",
              "email": "string",
              "created_at": "timestamp"
            },
            "400": {
              "error": "string",
              "details": "object"
            }
          }
        }
      ]
    }
  },
  "functional_requirements": [
    {
      "id": "FR001",
      "title": "User Registration and Authentication",
      "description": "Complete user management system",
      "priority": "High",
      "acceptance_criteria": [
        "Users can register with email verification",
        "Users can login with JWT authentication",
        "Users can reset passwords",
        "Users can update profiles"
      ],
      "use_cases": [
        {
          "title": "User Registration",
          "steps": [
            "User fills registration form",
            "System validates input data",
            "System creates user account",
            "System sends verification email",
            "User verifies email",
            "System activates account"
          ],
          "data_models": {
            "User": {
              "id": "UUID",
              "username": "string",
              "email": "string",
              "password_hash": "string",
              "is_verified": "boolean",
              "created_at": "timestamp"
            }
          },
          "api_endpoints": [
            {
              "path": "/auth/register",
              "method": "POST",
              "request": "UserRegistrationRequest",
              "response": "UserRegistrationResponse"
            }
          ]
        }
      ],
      "business_logic": {
        "validation_rules": [
          "Username must be 3-50 characters",
          "Email must be valid format",
          "Password must be 8+ characters with complexity",
          "Username and email must be unique"
        ],
        "security_measures": [
          "Password hashing with bcrypt",
          "JWT token generation",
          "Email verification required",
          "Rate limiting on registration"
        ]
      }
    }
  ],
  "non_functional_requirements": [
    {
      "id": "NFR001",
      "category": "Performance",
      "description": "Application performance requirements",
      "specifications": {
        "response_time": "API responses under 200ms",
        "throughput": "1000 requests per second",
        "availability": "99.9% uptime",
        "scalability": "Horizontal scaling support"
      }
    }
  ],
  "implementation_plan": {
    "phases": [
      {
        "phase": "Phase 1",
        "duration": "2 weeks",
        "deliverables": [
          "Database schema implementation",
          "User authentication system",
          "Basic API endpoints"
        ]
      }
    ],
    "file_structure": {
      "backend": {
        "app/": {
          "models/": "Database models",
          "api/": "API endpoints",
          "services/": "Business logic",
          "utils/": "Utility functions"
        },
        "tests/": "Test files",
        "migrations/": "Database migrations"
      },
      "frontend": {
        "src/": {
          "components/": "React components",
          "pages/": "Page components",
          "services/": "API services",
          "utils/": "Utility functions"
        },
        "public/": "Static assets"
      }
    }
  }
}
```

## ANALYSIS PROCESS:

1. **Requirement Analysis**: Break down high-level requirements into detailed specifications
2. **Technology Selection**: Choose the best tools and frameworks for the project
3. **Architecture Design**: Design complete system architecture
4. **Data Modeling**: Create comprehensive database schema
5. **API Design**: Define complete API specifications
6. **Security Planning**: Specify security measures and authentication
7. **Implementation Planning**: Create detailed implementation roadmap

## QUALITY STANDARDS:

- **Completeness**: Every requirement must have detailed implementation specifications
- **Specificity**: Use exact technology names, versions, and configurations
- **Real-world**: Specifications must be implementable in production
- **Scalability**: Design for growth and future requirements
- **Security**: Include comprehensive security measures
- **Maintainability**: Design for long-term maintenance and updates

IMPORTANT: Generate complete, production-ready specifications that can be directly implemented. Do not create placeholder or skeleton specifications. Every detail should be specific and actionable.

End your response with "TERMINATE" to indicate completion.
"""
    
    def analyze_requirements(self, natural_language_input: str) -> Dict[str, Any]:
        """
        Analyze natural language input and generate comprehensive technical specifications.
        
        Args:
            natural_language_input: Natural language description of the project
            
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
            
            result = {
                "project_id": f"project_{int(time.time())}_{hash(natural_language_input) % 10000:04x}",
                "natural_language_input": natural_language_input,
                "specifications": enhanced_specifications,
                "analysis_timestamp": time.time(),
                "total_requirements": len(enhanced_specifications.get("functional_requirements", [])),
                "technology_stack": enhanced_specifications.get("project_overview", {}).get("technology_stack", {})
            }
            
            # Save specifications to file
            self._save_specifications_to_file(result, result["project_id"])
            
            logger.info(f"Enhanced requirement analysis completed. Generated {result['total_requirements']} detailed requirements.")
            return result
            
        except Exception as e:
            logger.error(f"Error in enhanced requirement analysis: {e}")
            return self._generate_fallback_specifications(natural_language_input, str(e))
    
    def _create_analysis_prompt(self, natural_language_input: str) -> str:
        """Create detailed analysis prompt."""
        
        return f"""
Please analyze the following project requirement and generate comprehensive, production-ready technical specifications:

## PROJECT REQUIREMENT:
{natural_language_input}

## ANALYSIS REQUIREMENTS:

1. **Technology Stack Selection**: Choose the most appropriate and modern technology stack for this project
2. **System Architecture**: Design a complete, scalable system architecture
3. **Database Design**: Create a comprehensive database schema with all necessary tables and relationships
4. **API Design**: Define complete RESTful API specifications with all endpoints
5. **Frontend Design**: Specify the frontend framework and component architecture
6. **Security Implementation**: Define authentication, authorization, and security measures
7. **Deployment Strategy**: Specify deployment architecture and infrastructure

## EXPECTED OUTPUT:

Generate a complete JSON specification that includes:

1. **Project Overview**: Complete project details and technology stack
2. **Architecture**: System design, database schema, and API specifications
3. **Functional Requirements**: Detailed use cases, data models, and business logic
4. **Non-Functional Requirements**: Performance, security, and reliability specifications
5. **Implementation Plan**: Phases, deliverables, and file structure

## IMPORTANT GUIDELINES:

- **Be Specific**: Use exact technology names, versions, and configurations
- **Be Complete**: Every requirement must have detailed implementation specifications
- **Be Production-Ready**: Specifications must be implementable in real-world scenarios
- **Be Scalable**: Design for growth and future requirements
- **Be Secure**: Include comprehensive security measures
- **Be Modern**: Use current best practices and modern frameworks

Please provide the complete JSON specification that can be directly used for implementation.

IMPORTANT: End your response with "TERMINATE" to indicate completion.
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
        
        # Enhance technology stack with specific versions
        tech_stack = specifications.get("project_overview", {}).get("technology_stack", {})
        if "backend" in tech_stack:
            backend = tech_stack["backend"]
            if "framework" in backend and backend["framework"] == "FastAPI":
                backend["version"] = "0.104.0"
                backend["dependencies"] = [
                    "fastapi==0.104.0",
                    "uvicorn==0.24.0",
                    "sqlalchemy==2.0.23",
                    "alembic==1.12.1",
                    "pydantic==2.5.0"
                ]
        
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
            filename = f"enhanced_specifications_{project_id}_{timestamp}.json"
            filepath = os.path.join(output_dir, filename)
            
            # Save the complete result
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Enhanced specifications saved to: {filepath}")
            print(f"Enhanced specifications saved to: {filepath}")
            
            # Also save a simplified version with just the specifications
            spec_filename = f"enhanced_specifications_only_{project_id}_{timestamp}.json"
            spec_filepath = os.path.join(output_dir, spec_filename)
            
            with open(spec_filepath, 'w', encoding='utf-8') as f:
                json.dump(result.get("specifications", {}), f, indent=2, ensure_ascii=False)
            
            logger.info(f"Enhanced specifications only saved to: {spec_filepath}")
            print(f"Enhanced specifications only saved to: {spec_filepath}")
            
        except Exception as e:
            logger.error(f"Failed to save enhanced specifications to file: {e}")
            print(f"Failed to save enhanced specifications to file: {e}")
