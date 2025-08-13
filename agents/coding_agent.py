"""
Coding Agent for the Multi-Agentic Coding Framework.
Converts structured requirements into functional Python code.
"""

import autogen
import re
from typing import Dict, Any, List
from core.config import get_agent_config, config
from core.utils import save_to_file, setup_logging, validate_python_code, format_code_with_black

logger = setup_logging()

class CodingAgent:
    """Agent responsible for converting requirements into functional code."""
    
    def __init__(self):
        self.agent_config = get_agent_config("coding_agent")
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
    
    def generate_code(self, requirements: Dict[str, Any], project_id: str) -> Dict[str, Any]:
        """
        Generate Python code based on structured requirements.
        
        Args:
            requirements: Structured requirements from RequirementAnalysisAgent
            project_id: Unique project identifier
            
        Returns:
            Dict containing generated code files and metadata
        """
        logger.info("Starting code generation")
        logger.info(f"Requirements type: {type(requirements)}")
        logger.info(f"Requirements keys: {list(requirements.keys()) if isinstance(requirements, dict) else 'Not a dict'}")
        logger.info(f"Project ID: {project_id}")
        
        # Create the coding prompt
        coding_prompt = f"""
Based on the following structured requirements, generate functional Python code:

REQUIREMENTS:
{self._format_requirements_for_coding(requirements)}

Please generate the following:

1. **Main Application File** (`main.py`): Entry point of the application
2. **Core Modules**: Separate Python files for different components
3. **Configuration File** (`config.py`): Application configuration
4. **Requirements File** (`requirements.txt`): Dependencies
5. **README.md**: Basic documentation

For each file, provide the complete code with proper imports, error handling, and documentation.

Code Requirements:
- Follow PEP 8 style guidelines
- Include proper docstrings and comments
- Implement error handling and input validation
- Use appropriate design patterns
- Make code modular and maintainable
- Include type hints where appropriate

Please provide each file with complete code:


And so on for each file.

IMPORTANT: End your response with the word "TERMINATE" to indicate completion.
"""
        
        try:
            # Start the conversation
            chat_result = self.user_proxy.initiate_chat(
                self.agent,
                message=coding_prompt
            )
            
            # Extract the LLM response using utility function
            from core.utils import extract_llm_response
            last_message = extract_llm_response(chat_result)
            
            # Extract code blocks from the response
            from core.utils import extract_code_blocks
            code_blocks = extract_code_blocks(last_message)
            
            # Parse and organize the generated code
            generated_files = self._parse_generated_code(last_message, code_blocks)
            
            # Validate and format the code
            validated_files = self._validate_and_format_code(generated_files)
            
            # Save the generated files
            saved_files = self._save_generated_files(validated_files, project_id)
            
            result = {
                "project_id": project_id,
                "generated_files": saved_files,
                "code_validation": self._validate_all_code(validated_files),
                "total_files": len(saved_files),
                "main_file": "main.py" if "main.py" in saved_files else list(saved_files.keys())[0] if saved_files else None
            }
            
            logger.info(f"Code generation completed. Generated {len(saved_files)} files.")
            return result
            
        except Exception as e:
            logger.error(f"Error in code generation: {e}")
            # Generate a basic fallback code structure
            fallback_code = self._generate_fallback_code(requirements, project_id)
            return {
                "project_id": project_id,
                "generated_files": fallback_code,
                "code_validation": {"valid": False, "errors": [str(e)]},
                "total_files": len(fallback_code),
                "main_file": "main.py",
                "error": str(e)
            }
    
    def _format_requirements_for_coding(self, requirements: Dict[str, Any]) -> str:
        """Format requirements in a way that's useful for code generation."""
        # Debug logging
        logger.info(f"Formatting requirements: {type(requirements)}")
        logger.info(f"Requirements keys: {list(requirements.keys()) if isinstance(requirements, dict) else 'Not a dict'}")
        
        # Debug the actual values
        project_name = requirements.get('project_name', 'N/A')
        description = requirements.get('description', 'N/A')
        logger.info(f"Actual project_name: {project_name}")
        logger.info(f"Actual description: {description}")
        
        formatted = f"""
Project: {project_name}
Description: {description}

Functional Requirements:
"""
        
        for req in requirements.get('functional_requirements', []):
            formatted += f"""
- {req.get('id', 'N/A')}: {req.get('title', 'N/A')}
  Description: {req.get('description', 'N/A')}
  Priority: {req.get('priority', 'N/A')}
  Acceptance Criteria: {', '.join(req.get('acceptance_criteria', []))}
"""
        
        formatted += f"""
Non-Functional Requirements:
"""
        
        for req in requirements.get('non_functional_requirements', []):
            formatted += f"""
- {req.get('id', 'N/A')}: {req.get('title', 'N/A')}
  Category: {req.get('category', 'N/A')}
  Description: {req.get('description', 'N/A')}
"""
        
        formatted += f"""
Technical Constraints: {', '.join(requirements.get('technical_constraints', []))}
Dependencies: {', '.join(requirements.get('dependencies', []))}
Architecture: {requirements.get('suggested_architecture', 'N/A')}
Key Components: {', '.join(requirements.get('key_components', []))}
"""
        
        return formatted
    
    def _parse_generated_code(self, response: str, code_blocks: List[str]) -> Dict[str, str]:
        """Parse the generated code response and extract individual files."""
        import re
        
        # Debug logging
        logger.info(f"Parsing generated code. Response length: {len(response)}")
        logger.info(f"Code blocks found: {len(code_blocks)}")
        
        files = {}
        
        # Look for filename patterns in the response
        filename_pattern = r'# filename: ([^\n]+)'
        filename_matches = re.findall(filename_pattern, response)
        
        # Also look for alternative patterns
        alt_filename_pattern = r'```(?:python)?\n# filename: ([^\n]+)'
        alt_filename_matches = re.findall(alt_filename_pattern, response)
        
        # Look for filename patterns within code blocks
        code_block_filename_pattern = r'```(?:python)?\n# filename: ([^\n]+)\n(.*?)\n```'
        code_block_matches = re.findall(code_block_filename_pattern, response, re.DOTALL)
        
        # Combine all patterns
        all_filename_matches = filename_matches + alt_filename_matches
        
        # If we found code block matches, use those
        if code_block_matches:
            for filename, code in code_block_matches:
                files[filename.strip()] = code.strip()
                logger.info(f"Added file from code block: {filename.strip()}")
            return files
        
        logger.info(f"Filename matches found: {all_filename_matches}")
        
        if all_filename_matches and len(all_filename_matches) == len(code_blocks):
            # Match filenames with code blocks
            for filename, code in zip(all_filename_matches, code_blocks):
                files[filename.strip()] = code.strip()
                logger.info(f"Added file: {filename.strip()}")
        else:
            # Fallback: create files based on content
            if code_blocks:
                files["main.py"] = code_blocks[0]
                logger.info("Added main.py as fallback")
                
                # Try to identify other files based on content
                for i, code in enumerate(code_blocks[1:], 1):
                    if "import" in code and "def " in code:
                        files[f"module_{i}.py"] = code
                        logger.info(f"Added module_{i}.py")
                    elif "class " in code:
                        files[f"models_{i}.py"] = code
                        logger.info(f"Added models_{i}.py")
                    else:
                        files[f"utils_{i}.py"] = code
                        logger.info(f"Added utils_{i}.py")
        
        logger.info(f"Total files parsed: {len(files)}")
        return files
    
    def _validate_and_format_code(self, files: Dict[str, str]) -> Dict[str, str]:
        """Validate and format the generated code."""
        validated_files = {}
        
        for filename, code in files.items():
            # Validate the code
            validation = validate_python_code(code)
            
            if validation["valid"]:
                # Format the code
                formatted_code = format_code_with_black(code)
                validated_files[filename] = formatted_code
            else:
                # Try to fix common issues
                fixed_code = self._fix_common_code_issues(code)
                validated_files[filename] = fixed_code
        
        return validated_files
    
    def _fix_common_code_issues(self, code: str) -> str:
        """Fix common code issues."""
        # Add basic imports if missing
        if "import" not in code and "from" not in code:
            code = "import os\nimport sys\nfrom typing import Dict, Any, List\n\n" + code
        
        # Add basic error handling if missing
        if "try:" not in code and "except" not in code and "def " in code:
            # Add basic error handling to functions
            import re
            def_pattern = r'def ([^(]+)\([^)]*\):'
            matches = re.findall(def_pattern, code)
            
            for func_name in matches:
                # Add basic error handling
                code = code.replace(
                    f"def {func_name}(",
                    f"def {func_name}(\n    try:\n        # Function implementation\n        pass\n    except Exception as e:\n        print(f'Error in {func_name}: {{e}}')\n        raise\n\n"
                )
        
        return code
    
    def _save_generated_files(self, files: Dict[str, str], project_id: str) -> Dict[str, str]:
        """Save generated files to the output directory and return file content."""
        saved_files = {}
        
        for filename, content in files.items():
            # Create project-specific directory
            project_dir = f"{config.output_dir}/{project_id}"
            filepath = save_to_file(content, filename, project_dir)
            # Return the content, not the filepath, for frontend display
            saved_files[filename] = content
        
        return saved_files
    
    def _validate_all_code(self, files: Dict[str, str]) -> Dict[str, Any]:
        """Validate all generated code files."""
        overall_validation = {
            "valid": True,
            "total_files": len(files),
            "valid_files": 0,
            "errors": [],
            "warnings": []
        }
        
        for filename, code in files.items():
            validation = validate_python_code(code)
            
            if validation["valid"]:
                overall_validation["valid_files"] += 1
            else:
                overall_validation["valid"] = False
                overall_validation["errors"].extend([f"{filename}: {error}" for error in validation["errors"]])
            
            overall_validation["warnings"].extend([f"{filename}: {warning}" for warning in validation["warnings"]])
        
        return overall_validation
    
    def _generate_fallback_code(self, requirements: Dict[str, Any], project_id: str) -> Dict[str, str]:
        """Generate basic fallback code when the main generation fails."""
        project_name = requirements.get('project_name', 'GeneratedProject').replace(' ', '_')
        
        main_code = f'''"""
{project_name} - Generated Application

This is a basic implementation based on the requirements:
{requirements.get('description', 'N/A')}
"""

import os
import sys
from typing import Dict, Any, List

def main():
    """Main application entry point."""
    print(f"Welcome to {{project_name}}!")
    print("This is a generated application based on your requirements.")
    
    # TODO: Implement the main functionality based on requirements
    for req in {requirements.get('functional_requirements', [])}:
        print(f"- {{req.get('title', 'N/A')}}: {{req.get('description', 'N/A')}}")
    
    print("\\nApplication completed successfully!")

if __name__ == "__main__":
    main()
'''
        
        config_code = f'''"""
Configuration for {project_name}
"""

import os
from typing import Dict, Any

class Config:
    """Application configuration."""
    
    def __init__(self):
        self.app_name = "{project_name}"
        self.version = "1.0.0"
        self.debug = os.getenv("DEBUG", "False").lower() == "true"
        
        # Add configuration based on requirements
        self.requirements = {requirements}
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a configuration setting."""
        return getattr(self, key, default)

# Global configuration instance
config = Config()
'''
        
        requirements_txt = f'''# Requirements for {project_name}
# Generated based on project requirements

# Core dependencies
typing-extensions>=4.0.0

# Add specific dependencies based on requirements
# TODO: Add required packages based on functional requirements
'''
        
        readme_code = f'''# {project_name}

## Description
{requirements.get('description', 'N/A')}

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```bash
python main.py
```

## Requirements
{self._format_requirements_for_coding(requirements)}

## Generated Files
- `main.py`: Main application entry point
- `config.py`: Application configuration
- `requirements.txt`: Python dependencies

## Next Steps
This is a basic generated implementation. You may need to:
1. Implement specific functionality based on requirements
2. Add proper error handling
3. Implement tests
4. Add more detailed documentation
'''
        
        return {
            "main.py": main_code,
            "config.py": config_code,
            "requirements.txt": requirements_txt,
            "README.md": readme_code
        }
    
    def generate_code_with_feedback(self, requirements: Dict[str, Any], project_id: str, 
                                   review_feedback: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate improved code based on review feedback.
        
        Args:
            requirements: Structured requirements from RequirementAnalysisAgent
            project_id: Unique project identifier
            review_feedback: Feedback from CodeReviewAgent
            
        Returns:
            Dict containing improved code files and metadata
        """
        logger.info("Starting code generation with feedback")
        
        # Create the improved coding prompt
        feedback_prompt = f"""
Based on the following structured requirements and review feedback, generate improved Python code:

REQUIREMENTS:
{self._format_requirements_for_coding(requirements)}

REVIEW FEEDBACK:
Overall Score: {review_feedback.get('overall_score', 0)}/100
Passes Review: {review_feedback.get('passes_review', False)}

Critical Issues:
{chr(10).join([f"- {issue.get('issue', 'N/A')}" for issue in review_feedback.get('critical_issues', []) if isinstance(issue, dict)])}

High Priority Issues:
{chr(10).join([f"- {issue.get('issue', 'N/A')}" for issue in review_feedback.get('high_priority_issues', []) if isinstance(issue, dict)])}

Medium Priority Issues:
{chr(10).join([f"- {issue.get('issue', 'N/A')}" for issue in review_feedback.get('medium_priority_issues', []) if isinstance(issue, dict)])}

Recommendations:
{chr(10).join([f"- {rec}" for rec in review_feedback.get('recommendations', []) if isinstance(rec, str)])}

Revision Notes: {review_feedback.get('revision_notes', 'N/A')}

Please address all the issues mentioned in the review feedback and generate improved code that:

1. **Fixes Critical Issues**: Address all critical and high-priority issues
2. **Implements Requirements**: Ensure all functional requirements are properly implemented
3. **Follows Best Practices**: Use proper error handling, documentation, and code structure
4. **Improves Quality**: Apply the recommendations from the review

Please generate the following:

1. **Main Application File** (`main.py`): Entry point with proper implementation
2. **Core Modules**: Separate Python files for different components
3. **Configuration File** (`config.py`): Application configuration
4. **Requirements File** (`requirements.txt`): Dependencies
5. **README.md**: Basic documentation

For each file, provide the complete code with proper imports, error handling, and documentation.

Code Requirements:
- Follow PEP 8 style guidelines
- Include proper docstrings and comments
- Implement error handling and input validation
- Use appropriate design patterns
- Make code modular and maintainable
- Include type hints where appropriate
- Address all review feedback issues

Please provide each file in the following format:

```python
# filename: main.py
[complete code here]
```

```python
# filename: config.py
[complete code here]
```

And so on for each file.

IMPORTANT: End your response with the word "TERMINATE" to indicate completion.
"""
        
        try:
            # Start the conversation
            chat_result = self.user_proxy.initiate_chat(
                self.agent,
                message=feedback_prompt
            )
            
            # Extract the LLM response using utility function
            from core.utils import extract_llm_response
            last_message = extract_llm_response(chat_result)
            
            # Extract code blocks from the response
            from core.utils import extract_code_blocks
            code_blocks = extract_code_blocks(last_message)
            
            # Parse and organize the generated code
            generated_files = self._parse_generated_code(last_message, code_blocks)
            
            # Validate and format the code
            validated_files = self._validate_and_format_code(generated_files)
            
            # Save the generated files
            saved_files = self._save_generated_files(validated_files, project_id)
            
            result = {
                "project_id": project_id,
                "generated_files": saved_files,
                "total_files": len(saved_files),
                "feedback_addressed": True,
                "improvements_made": [
                    "Addressed critical issues from review",
                    "Improved code quality based on feedback",
                    "Enhanced error handling and documentation"
                ]
            }
            
            logger.info(f"Code generation with feedback completed. Generated {len(saved_files)} files.")
            return result
            
        except Exception as e:
            logger.error(f"Error in code generation with feedback: {e}")
            # Generate fallback code
            fallback_files = self._generate_fallback_code(requirements, project_id)
            return {
                "project_id": project_id,
                "generated_files": fallback_files,
                "total_files": len(fallback_files),
                "feedback_addressed": False,
                "improvements_made": [],
                "error": str(e)
            } 