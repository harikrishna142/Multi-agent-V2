"""
Documentation Agent for the Multi-Agentic Coding Framework.
Generates comprehensive documentation for the developed code.
"""

import autogen
import re
from typing import Dict, Any, List
from core.config import get_agent_config, config
from core.utils import save_to_file, setup_logging, load_from_file

logger = setup_logging()

class DocumentationAgent:
    """Agent responsible for generating comprehensive documentation."""
    
    def __init__(self):
        self.agent_config = get_agent_config("documentation_agent")
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
    
    def generate_documentation(self, generated_code: Dict[str, Any], requirements: Dict[str, Any], project_id: str) -> Dict[str, Any]:
        """
        Generate comprehensive documentation for the developed code.
        
        Args:
            generated_code: Output from CodingAgent containing generated files
            requirements: Original requirements for context
            project_id: Unique project identifier
            
        Returns:
            Dict containing generated documentation files
        """
        logger.info("Starting documentation generation")
        
        # Load the actual code content
        code_files = {}
        for filename, filepath in generated_code.get("generated_files", {}).items():
            try:
                code_files[filename] = load_from_file(filepath)
            except Exception as e:
                logger.warning(f"Could not load file {filename}: {e}")
                code_files[filename] = f"# Error loading file: {e}"
        
        # Create the documentation prompt
        doc_prompt = f"""
Please generate comprehensive documentation for the following Python project:

PROJECT REQUIREMENTS:
{self._format_requirements_for_documentation(requirements)}

GENERATED CODE FILES:
{self._format_code_for_documentation(code_files)}

Please generate the following documentation:

1. **README.md**: Main project documentation with:
   - Project overview and description
   - Installation instructions
   - Usage examples
   - API documentation
   - Contributing guidelines

2. **API_DOCUMENTATION.md**: Detailed API documentation with:
   - Function and class documentation
   - Parameter descriptions
   - Return value descriptions
   - Usage examples
   - Error handling

3. **DEVELOPER_GUIDE.md**: Developer-focused documentation with:
   - Architecture overview
   - Code structure explanation
   - Development setup
   - Testing guidelines
   - Deployment instructions

4. **USER_GUIDE.md**: End-user documentation with:
   - Getting started guide
   - Feature descriptions
   - Troubleshooting
   - FAQ

5. **CHANGELOG.md**: Version history and changes

For each file, provide complete, well-structured documentation that is:
- Clear and easy to understand
- Comprehensive and detailed
- Well-organized with proper headings
- Includes practical examples
- Follows documentation best practices

Please provide each documentation file in the following format:

```markdown
# filename: README.md
[complete documentation here]
```

```markdown
# filename: API_DOCUMENTATION.md
[complete documentation here]
```

And so on for each file.

IMPORTANT: End your response with the word "TERMINATE" to indicate completion.
"""
        
        try:
            # Start the conversation
            chat_result = self.user_proxy.initiate_chat(
                self.agent,
                message=doc_prompt
            )
            
            # Extract the LLM response using utility function
            from core.utils import extract_llm_response
            last_message = extract_llm_response(chat_result)
            
            # Parse and organize the generated documentation
            generated_docs = self._parse_generated_documentation(last_message)
            
            # Save the generated documentation
            saved_docs = self._save_generated_documentation(generated_docs, project_id)
            
            result = {
                "project_id": project_id,
                "generated_documentation": saved_docs,
                "total_docs": len(saved_docs),
                "documentation_summary": self._generate_documentation_summary(saved_docs)
            }
            
            logger.info(f"Documentation generation completed. Generated {len(saved_docs)} documentation files.")
            return result
            
        except Exception as e:
            logger.error(f"Error in documentation generation: {e}")
            # Generate fallback documentation
            fallback_docs = self._generate_fallback_documentation(requirements, code_files, project_id)
            return {
                "project_id": project_id,
                "generated_documentation": fallback_docs,
                "total_docs": len(fallback_docs),
                "documentation_summary": "Fallback documentation generated due to error",
                "error": str(e)
            }
    
    def _format_requirements_for_documentation(self, requirements: Dict[str, Any]) -> str:
        """Format requirements for documentation context."""
        formatted = f"""
Project: {requirements.get('project_name', 'N/A')}
Description: {requirements.get('description', 'N/A')}

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
        
        return formatted
    
    def _format_code_for_documentation(self, code_files: Dict[str, str]) -> str:
        """Format code files for documentation generation."""
        formatted = ""
        
        for filename, content in code_files.items():
            formatted += f"""
=== FILE: {filename} ===
{content}
=== END FILE: {filename} ===

"""
        
        return formatted
    
    def _parse_generated_documentation(self, response: str) -> Dict[str, str]:
        """Parse the generated documentation response and extract individual files."""
        import re
        
        files = {}
        
        # Look for filename patterns in the response
        filename_pattern = r'# filename: ([^\n]+)'
        filename_matches = re.findall(filename_pattern, response)
        
        # Split the response by filename markers
        sections = re.split(r'# filename:', response)
        
        if len(sections) > 1:
            for i, section in enumerate(sections[1:], 1):
                if i <= len(filename_matches):
                    filename = filename_matches[i-1].strip()
                    # Extract content after the filename
                    content = section.strip()
                    if content:
                        files[filename] = content
        else:
            # Fallback: create basic documentation files
            files = self._create_basic_documentation_structure(response)
        
        return files
    
    def _create_basic_documentation_structure(self, response: str) -> Dict[str, str]:
        """Create basic documentation structure when parsing fails."""
        return {
            "README.md": f"""# Project Documentation

{response}

## Overview
This is the main documentation for the generated project.

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```bash
python main.py
```

## Documentation
This documentation was generated automatically. Please refer to the code comments for detailed information.
""",
            "API_DOCUMENTATION.md": f"""# API Documentation

{response}

## Functions and Classes
This section contains detailed API documentation for all functions and classes in the project.

## Usage Examples
Examples of how to use the various functions and classes.
""",
            "DEVELOPER_GUIDE.md": f"""# Developer Guide

{response}

## Architecture
Overview of the project architecture and design decisions.

## Development Setup
Instructions for setting up the development environment.

## Testing
Guidelines for testing the application.
""",
            "USER_GUIDE.md": f"""# User Guide

{response}

## Getting Started
Step-by-step guide for new users.

## Features
Detailed description of all available features.

## Troubleshooting
Common issues and their solutions.
"""
        }
    
    def _save_generated_documentation(self, docs: Dict[str, str], project_id: str) -> Dict[str, str]:
        """Save generated documentation to files and return content."""
        saved_docs = {}
        
        for filename, content in docs.items():
            # Create project-specific documentation directory
            project_dir = f"{config.output_dir}/{project_id}/docs"
            filepath = save_to_file(content, filename, project_dir)
            # Return the content, not the filepath, for frontend display
            saved_docs[filename] = content
        
        return saved_docs
    
    def _generate_documentation_summary(self, saved_docs: Dict[str, str]) -> str:
        """Generate a summary of the created documentation."""
        summary = f"""
# Documentation Summary

Generated {len(saved_docs)} documentation files:

"""
        
        for filename, filepath in saved_docs.items():
            summary += f"- **{filename}**: {filepath}\n"
        
        summary += f"""
## Documentation Coverage
- ✅ README.md: Main project documentation
- ✅ API_DOCUMENTATION.md: Detailed API reference
- ✅ DEVELOPER_GUIDE.md: Developer-focused guide
- ✅ USER_GUIDE.md: End-user documentation

## Next Steps
1. Review the generated documentation
2. Customize content as needed
3. Add project-specific examples
4. Update installation instructions
5. Add screenshots or diagrams if applicable
"""
        
        return summary
    
    def _generate_fallback_documentation(self, requirements: Dict[str, Any], code_files: Dict[str, str], project_id: str) -> Dict[str, str]:
        """Generate basic fallback documentation when the main generation fails."""
        project_name = requirements.get('project_name', 'GeneratedProject')
        
        readme_content = f"""# {project_name}

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

## Project Structure
This project was generated automatically based on the following requirements:

### Functional Requirements
"""
        
        for req in requirements.get('functional_requirements', []):
            readme_content += f"""
- **{req.get('id', 'N/A')}: {req.get('title', 'N/A')}**
  - Description: {req.get('description', 'N/A')}
  - Priority: {req.get('priority', 'N/A')}
"""
        
        readme_content += f"""
### Non-Functional Requirements
"""
        
        for req in requirements.get('non_functional_requirements', []):
            readme_content += f"""
- **{req.get('id', 'N/A')}: {req.get('title', 'N/A')}**
  - Category: {req.get('category', 'N/A')}
  - Description: {req.get('description', 'N/A')}
"""
        
        readme_content += f"""
## Generated Files
"""
        
        for filename in code_files.keys():
            readme_content += f"- `{filename}`\n"
        
        readme_content += f"""
## Technical Details
- **Architecture**: {requirements.get('suggested_architecture', 'N/A')}
- **Complexity**: {requirements.get('estimated_complexity', 'N/A')}
- **Dependencies**: {', '.join(requirements.get('dependencies', []))}

## Contributing
This is an automatically generated project. Please refer to the code comments for implementation details.

## License
This project is generated automatically and may require customization for production use.
"""
        
        api_doc_content = f"""# API Documentation - {project_name}

## Overview
This document provides detailed API documentation for the {project_name} project.

## Generated Code Files
"""
        
        for filename, content in code_files.items():
            api_doc_content += f"""
### {filename}
```python
{content[:500]}...
```

**Purpose**: This file was generated based on the project requirements.
"""
        
        api_doc_content += f"""
## Functions and Classes
The following functions and classes are available in the generated code:

### Main Application
- `main()`: Entry point of the application

### Configuration
- `Config`: Application configuration class

## Usage Examples
```python
# Run the main application
python main.py

# Import and use configuration
from config import Config
config = Config()
```

## Error Handling
The generated code includes basic error handling. Please refer to the individual files for specific error handling patterns.

## Dependencies
See `requirements.txt` for the complete list of dependencies.
"""
        
        dev_guide_content = f"""# Developer Guide - {project_name}

## Architecture Overview
This project follows a modular architecture with the following components:

### Core Components
"""
        
        for component in requirements.get('key_components', []):
            dev_guide_content += f"- {component}\n"
        
        dev_guide_content += f"""
## Development Setup
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python main.py`

## Code Structure
The project consists of the following files:

"""
        
        for filename in code_files.keys():
            dev_guide_content += f"- `{filename}`: {self._get_file_purpose(filename)}\n"
        
        dev_guide_content += f"""
## Testing
To test the application:
```bash
python -m pytest tests/
```

## Deployment
1. Ensure all dependencies are installed
2. Configure environment variables if needed
3. Run the application: `python main.py`

## Technical Constraints
{chr(10).join(f'- {constraint}' for constraint in requirements.get('technical_constraints', []))}

## Assumptions
{chr(10).join(f'- {assumption}' for assumption in requirements.get('assumptions', []))}
"""
        
        user_guide_content = f"""# User Guide - {project_name}

## Getting Started
Welcome to {project_name}! This guide will help you get started with the application.

## What is {project_name}?
{requirements.get('description', 'N/A')}

## Installation
1. Ensure you have Python 3.8 or higher installed
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application
To start the application:
```bash
python main.py
```

## Features
The following features are available:

"""
        
        for req in requirements.get('functional_requirements', []):
            user_guide_content += f"""
### {req.get('title', 'N/A')}
{req.get('description', 'N/A')}

**How to use**: [Instructions will be provided based on implementation]
"""
        
        user_guide_content += f"""
## Troubleshooting

### Common Issues
1. **Import errors**: Make sure all dependencies are installed
2. **Configuration errors**: Check that all required environment variables are set
3. **Runtime errors**: Check the console output for error messages

### Getting Help
If you encounter issues:
1. Check the console output for error messages
2. Review the API documentation
3. Check the developer guide for technical details

## FAQ
**Q: What is this application for?**
A: {requirements.get('description', 'N/A')}

**Q: How do I customize the application?**
A: Refer to the developer guide for customization instructions.

**Q: Is this application production-ready?**
A: This is an automatically generated application and may require additional testing and customization for production use.
"""
        
        return {
            "README.md": readme_content,
            "API_DOCUMENTATION.md": api_doc_content,
            "DEVELOPER_GUIDE.md": dev_guide_content,
            "USER_GUIDE.md": user_guide_content
        }
    
    def _get_file_purpose(self, filename: str) -> str:
        """Get a description of the file's purpose based on its name."""
        purposes = {
            "main.py": "Main application entry point",
            "config.py": "Application configuration and settings",
            "requirements.txt": "Python package dependencies",
            "README.md": "Project documentation and overview",
            "test_": "Test files for the application",
            "utils": "Utility functions and helpers",
            "models": "Data models and classes",
            "api": "API endpoints and handlers"
        }
        
        for key, purpose in purposes.items():
            if key in filename.lower():
                return purpose
        
        return "Generated code file" 