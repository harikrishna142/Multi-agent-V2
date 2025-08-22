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
       
        
        # Check if this is an iteration with improvement instructions
        is_iteration = "improvement_instructions" in requirements
        current_iteration = requirements.get("current_iteration", 1)
        max_iterations = requirements.get("max_iterations", 3)
        
        if is_iteration:
            # This is an iteration - use project context and improvement instructions
            project_context = requirements.get("project_context", "")
            improvement_instructions = requirements.get("improvement_instructions", [])
            existing_code = requirements.get("existing_code", {})
            
            coding_prompt = f"""
## ITERATION {current_iteration}/{max_iterations} - CODE IMPROVEMENT

You are improving existing code based on review feedback and specific instructions.

## PROJECT CONTEXT:
{project_context}

## EXISTING CODE BASE:
"""
            
            # Add existing code to prompt
            for filename, content in existing_code.items():
                coding_prompt += f"""
### {filename}:
```{self._get_file_extension(filename)}
{content}
```
"""
            
            coding_prompt += f"""
## IMPROVEMENT INSTRUCTIONS:
"""
            
            for i, instruction in enumerate(improvement_instructions, 1):
                coding_prompt += f"{i}. {instruction}\n"
            
            coding_prompt += f"""
## TASK:
Based on the improvement instructions above, update the existing code to:
1. Complete any TODO items or placeholder implementations
2. Implement missing functionality
3. Fix any incomplete functions
4. Ensure all code is runnable and complete

IMPORTANT REQUIREMENTS:
- DO NOT create new files unless specifically requested
- UPDATE existing files with complete implementations
- Replace any TODO, #implement, or placeholder code with actual implementation
- Follow the existing code patterns and style
- Ensure all functions are fully implemented
- Make sure the code is runnable

Please provide the updated code files with complete implementations.

IMPORTANT: End your response with "TERMINATE" to indicate completion.
"""
        else:
            # Initial code generation
            coding_prompt = f"""
Based on the following structured requirements, generate functional Python code:

REQUIREMENTS:
{requirements}

Please generate the following:

1. code and files needed for running simple basic version of the application, choose the techstack based on the requirements
2. **Core Modules**: separate files for components based on techstack
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
- **IMPORTANT**: If you need to mark something as incomplete, use TODO comments that can be detected by the review system

Please provide each file with complete code:

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
            logger.info(f"Last message: {last_message}")
            # Extract code blocks from the response
            from core.utils import extract_code_blocks
            code_blocks = extract_code_blocks(last_message)
            logger.info(f"Code blocks: {code_blocks}")
            
            # Extract and save code blocks with their filenames
            generated_files = self._extract_and_save_code_blocks(last_message, project_id)
            print(f"Generated files: {list(generated_files.keys())}")
        
            # Validate and format the code
            validated_files = self._validate_and_format_code(generated_files)
            
            # Save the generated files
            saved_files = self._save_generated_files(validated_files, project_id)
            
            result = {
                "project_id": project_id,
                "generated_files": generated_files,  # Use the extracted files directly
                "code_validation": self._validate_all_code(validated_files),
                "total_files": len(generated_files),
                "main_file": "app.py" if "app.py" in generated_files else "main.py" if "main.py" in generated_files else list(generated_files.keys())[0] if generated_files else None,
                "project_directory": f"output/projects/{project_id}",
                "last_message": last_message  # Include for debugging
            }
            
            logger.info(f"Code generation completed. Generated {len(generated_files)} files.")
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
                "project_directory": f"output/projects/{project_id}",
                "last_message": f"Error in code generation: {str(e)}",
                "error": str(e)
            }
    
    
    
    def _parse_generated_code(self, response: str) -> Dict[str, str]:
        
        
        """Parse generated files from the response."""
        import re
        
        files = {}
        
        # Extract code blocks with filenames
        code_blocks = re.findall(r'```(\w+)\s*# filename: ([^\n]+)\s*(.*?)```', response, re.DOTALL)
        
        for language, filename, content in code_blocks:
            files[filename] = content.strip()
        
        # Also look for code blocks without explicit filenames
        if not files:
            code_blocks = re.findall(r'```(\w+)\s*(.*?)```', response, re.DOTALL)
            for i, (language, content) in enumerate(code_blocks):
                if language in ['python', 'javascript', 'json', 'yaml', 'yml']:
                    # Try to infer filename from content
                    filename = self._infer_filename(content, language, i)
                    files[filename] = content.strip()
        
        return files
        
    
    def _validate_and_format_code(self, files: Dict[str, str]) -> Dict[str, str]:
        """Validate and enhance the generated code."""
        enhanced_files = {}
        
        for filename, content in files.items():
            # Validate Python code
            if filename.endswith('.py'):
                validation = validate_python_code(content)
                if validation["valid"]:
                    try:
                        formatted_content = format_code_with_black(content)
                        enhanced_files[filename] = formatted_content
                    except Exception as e:
                        logger.warning(f"Code formatting failed for {filename}: {e}")
                        enhanced_files[filename] = content
                else:
                    logger.warning(f"Code validation failed for {filename}: {validation['errors']}")
                    enhanced_files[filename] = content
            else:
                enhanced_files[filename] = content
        
        return enhanced_files
    
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
    
    def _extract_and_save_code_blocks(self, last_message: str, project_id: str) -> Dict[str, str]:
        """
        Extract code blocks from LLM output and save them to files with their filenames.
        
        Args:
            last_message: The complete LLM response containing code blocks
            project_id: The project ID for organizing files
            
        Returns:
            Dict mapping filenames to file content for review agent
        """
        import re
        import os
        from datetime import datetime
        
        # Create project directory
        project_dir = f"output/projects/{project_id}"
        os.makedirs(project_dir, exist_ok=True)
        
        generated_files = {}
        
        # Pattern to match code blocks with filenames
        # Matches: ```python filename.py\ncode content\n```
        filename_pattern = r'```(\w+)\s*#?\s*([^\n]+\.\w+)\s*\n(.*?)```'
        filename_matches = re.findall(filename_pattern, last_message, re.DOTALL)
        
        # Pattern to match code blocks without explicit filenames
        # Matches: ```python\ncode content\n```
        no_filename_pattern = r'```(\w+)\s*\n(.*?)```'
        no_filename_matches = re.findall(no_filename_pattern, last_message, re.DOTALL)
        
        # Process code blocks with explicit filenames
        for language, filename, content in filename_matches:
            # Clean filename (remove any extra whitespace or comments)
            filename = filename.strip()
            if filename.startswith('#'):
                filename = filename[1:].strip()
            
            # Ensure filename has proper extension
            if not '.' in filename:
                filename = f"{filename}.{self._get_file_extension(language)}"
            
            # Save the file
            file_path = os.path.join(project_dir, filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content.strip())
            
            generated_files[filename] = content.strip()
            logger.info(f"Saved file: {filename}")
            print(f"Saved file: {filename}")
        
        # Process code blocks without explicit filenames
        for i, (language, content) in enumerate(no_filename_matches):
            # Skip if this content was already processed with a filename
            content_stripped = content.strip()
            if any(content_stripped in file_content for file_content in generated_files.values()):
                continue
            
            # Infer filename based on content and language
            filename = self._infer_filename_from_content(content_stripped, language, i)
            
            # Save the file
            file_path = os.path.join(project_dir, filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content_stripped)
            
            generated_files[filename] = content_stripped
            logger.info(f"Saved inferred file: {filename}")
            print(f"Saved inferred file: {filename}")
        
        # Save the complete last message for debugging
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        debug_file = os.path.join(project_dir, f"llm_output_{timestamp}.txt")
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write(last_message)
        
        logger.info(f"Generated {len(generated_files)} files in {project_dir}")
        print(f"Generated {len(generated_files)} files in {project_dir}")
        
        return generated_files
    
    def _infer_filename_from_content(self, content: str, language: str, index: int) -> str:
        """Infer filename from code content."""
        content_lower = content.lower()
        
        # Common patterns for different file types
        if language == 'python':
            if 'fastapi' in content_lower or 'app = fastapi()' in content_lower:
                return 'app/main.py'
            elif 'flask' in content_lower or 'app = flask(__name__)' in content_lower:
                return 'app.py'
            elif 'django' in content_lower:
                return 'manage.py'
            elif 'class' in content_lower and 'model' in content_lower:
                return f'models/model_{index}.py'
            elif 'def test_' in content_lower:
                return f'tests/test_{index}.py'
            elif 'requirements' in content_lower or 'flask' in content_lower or 'fastapi' in content_lower:
                return 'requirements.txt'
            else:
                return f'src/{index}.py'
        
        elif language == 'javascript':
            if 'react' in content_lower or 'import react' in content_lower:
                return f'src/components/Component{index}.js'
            elif 'package.json' in content_lower or 'dependencies' in content_lower:
                return 'package.json'
            else:
                return f'src/{index}.js'
        
        elif language == 'html':
            if 'index' in content_lower or '<!doctype' in content_lower:
                return 'index.html'
            else:
                return f'templates/{index}.html'
        
        elif language == 'css':
            return f'static/css/style{index}.css'
        
        elif language == 'json':
            if 'dependencies' in content_lower:
                return 'package.json'
            else:
                return f'config{index}.json'
        
        elif language in ['yaml', 'yml']:
            if 'docker' in content_lower:
                return 'docker-compose.yml'
            else:
                return f'config{index}.yml'
        
        elif language == 'sql':
            return f'database/schema{index}.sql'
        
        elif language == 'markdown':
            if 'readme' in content_lower:
                return 'README.md'
            else:
                return f'docs/{index}.md'
        
        else:
            return f'files/{index}.{self._get_file_extension(language)}'
    
    def _save_coding_context(self, last_message: str, code_blocks: List[Dict[str, Any]], project_id: str) -> Dict[str, Any]:
        """
        Save the last message and code blocks to files for debugging and review context.
        
        Args:
            last_message: The complete last message from the coding agent
            code_blocks: List of extracted code blocks
            project_id: The project ID for file organization
            
        Returns:
            Dict containing file paths and metadata
        """
        try:
            import json
            import os
            from datetime import datetime
            
            # Create output directory for coding context
            output_dir = f"output/coding_context/{project_id}"
            os.makedirs(output_dir, exist_ok=True)
            
            # Save the complete last message
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            last_message_file = f"last_message_{timestamp}.txt"
            last_message_path = os.path.join(output_dir, last_message_file)
            
            with open(last_message_path, 'w', encoding='utf-8') as f:
                f.write(last_message)
            
            # Save code blocks as separate files
            code_blocks_dir = os.path.join(output_dir, "code_blocks")
            os.makedirs(code_blocks_dir, exist_ok=True)
            
            code_blocks_files = {}
            for i, block in enumerate(code_blocks):
                language = block.get('language', 'text')
                content = block.get('content', '')
                
                # Create filename for code block
                block_filename = f"code_block_{i+1}_{language}_{timestamp}.{self._get_file_extension(language)}"
                block_path = os.path.join(code_blocks_dir, block_filename)
                
                with open(block_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                code_blocks_files[f"block_{i+1}"] = {
                    "filename": block_filename,
                    "path": block_path,
                    "language": language,
                    "content": content
                }
            
            # Save metadata about the coding session
            metadata = {
                "project_id": project_id,
                "timestamp": timestamp,
                "last_message_file": last_message_file,
                "last_message_path": last_message_path,
                "code_blocks_count": len(code_blocks),
                "code_blocks_files": code_blocks_files,
                "total_files_generated": len(code_blocks)
            }
            
            metadata_file = f"coding_session_metadata_{timestamp}.json"
            metadata_path = os.path.join(output_dir, metadata_file)
            
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Coding context saved to: {output_dir}")
            print(f"Coding context saved to: {output_dir}")
            
            return {
                "output_directory": output_dir,
                "last_message_file": last_message_path,
                "code_blocks_directory": code_blocks_dir,
                "metadata_file": metadata_path,
                "code_blocks_files": code_blocks_files,
                "timestamp": timestamp
            }
            
        except Exception as e:
            logger.error(f"Failed to save coding context: {e}")
            print(f"Failed to save coding context: {e}")
            return {
                "error": str(e),
                "output_directory": None,
                "last_message_file": None,
                "code_blocks_directory": None
            }
    
    def _get_file_extension(self, language: str) -> str:
        """Get appropriate file extension for a programming language."""
        extensions = {
            'python': 'py',
            'javascript': 'js',
            'typescript': 'ts',
            'html': 'html',
            'css': 'css',
            'json': 'json',
            'yaml': 'yml',
            'yml': 'yml',
            'markdown': 'md',
            'md': 'md',
            'sql': 'sql',
            'bash': 'sh',
            'shell': 'sh',
            'dockerfile': 'Dockerfile',
            'docker': 'Dockerfile'
        }
        return extensions.get(language.lower(), 'txt')
    
    def _infer_filename(self, content: str, language: str, index: int) -> str:
        """Infer filename from content."""
        if language == 'python':
            if 'FastAPI' in content or 'app = FastAPI()' in content:
                return f"backend/app/main.py"
            elif 'class' in content and 'BaseModel' in content:
                return f"backend/app/models/model_{index}.py"
            else:
                return f"backend/app/{index}.py"
        elif language == 'javascript':
            if 'React' in content or 'import React' in content:
                return f"frontend/src/components/Component{index}.js"
            else:
                return f"frontend/src/{index}.js"
        elif language == 'json':
            if 'dependencies' in content:
                return f"frontend/package.json"
            else:
                return f"config{index}.json"
        elif language in ['yaml', 'yml']:
            return f"docker-compose.yml"
        else:
            return f"file_{index}.{language}"
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
{requirements}

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
{requirements}

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
2. **Implements Requirements**: Ensure all basic functional requirements are properly implemented for running basic version
3. **Follows Best Practices**: Use proper error handling, documentation, and code structure
4. **Improves Quality**: Apply the recommendations from the review

Please generate the following:

1. code and files needed for running simple basic version of the application, choose the techstack based on the requirements
2. **Core Modules**: separate files for components based on techstack
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