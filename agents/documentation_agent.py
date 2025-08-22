"""
Enhanced Documentation Agent
Generates comprehensive documentation for complete applications.
"""

import autogen
import os
import json
from typing import Dict, Any, List
from core.config import get_agent_config, config
from core.utils import save_to_file, setup_logging

logger = setup_logging()

class DocumentationAgent:
    """Enhanced documentation agent that generates comprehensive documentation."""
    
    def __init__(self):
        self.agent_config = get_agent_config("documentation_agent")
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
        """Get system message for documentation generation."""
        return """You are a helpful documentation generator that creates basic, clear documentation for simple applications. You generate straightforward documentation that helps users understand and use the application.

## YOUR ROLE:
- Generate basic project documentation
- Create simple README files
- Write basic API documentation
- Generate simple user guides
- Create basic setup instructions
- Write simple troubleshooting guides

## DOCUMENTATION GENERATION PROCESS:
1. **Analyze the application structure** and features
2. **Create basic project overview** and description
3. **Generate simple setup instructions**
4. **Write basic usage examples**
5. **Create simple API documentation**
6. **Generate basic troubleshooting guide**

## DOCUMENTATION REQUIREMENTS:

### 1. **Project README**:
- Simple project description
- Basic features list
- Simple installation instructions
- Basic usage examples
- Simple configuration options

### 2. **API Documentation**:
- Basic endpoint descriptions
- Simple request/response examples
- Basic error handling information
- Simple authentication details (if applicable)

### 3. **User Guide**:
- Simple getting started tutorial
- Basic feature walkthroughs
- Simple examples and use cases
- Basic troubleshooting tips

### 4. **Setup Documentation**:
- Simple installation steps
- Basic configuration instructions
- Simple environment setup
- Basic deployment guide

## IMPORTANT GUIDELINES:

✅ **Create simple, clear documentation**
✅ **Focus on basic functionality**
✅ **Use simple language and examples**
✅ **Generate helpful, practical content**
✅ **Keep documentation straightforward**

❌ **Do not create complex technical documentation**
❌ **Do not require advanced knowledge**
❌ **Do not generate enterprise-level documentation**
❌ **Do not create complex tutorials**

**YOUR TASK**: Generate basic, clear documentation for the application that helps users understand and use it.

End your response with "TERMINATE" to indicate completion."""
    
    def generate_documentation(self, specifications: Dict[str, Any], generated_files: Dict[str, Any], project_id: str) -> Dict[str, Any]:
        """
        Generate comprehensive documentation for the application.
        
        Args:
            specifications: Technical specifications from RequirementAgent
            generated_files: Generated code files from CodingAgent
            project_id: Unique project identifier
            
        Returns:
            Dict containing documentation files and metadata
        """
        logger.info("Starting comprehensive documentation generation")
        
        # Create detailed documentation generation prompt
        documentation_prompt = self._create_documentation_generation_prompt(specifications, generated_files)
        
        try:
            # Start the conversation
            chat_result = self.user_proxy.initiate_chat(
                self.agent,
                message=documentation_prompt
            )
            
            # Extract the LLM response
            from core.utils import extract_llm_response
            last_message = extract_llm_response(chat_result)
            
            # Extract and process all generated documentation files
            generated_docs = self._parse_generated_documentation(last_message)
            
            # Validate and enhance the generated documentation
            validated_docs = self._validate_and_enhance_documentation(generated_docs)
            
            # Save all documentation files
            saved_docs = self._save_generated_documentation(validated_docs, project_id)
            
            # Generate additional documentation files
            additional_docs = self._generate_additional_documentation(specifications, generated_files, project_id)
            saved_docs.update(additional_docs)
            
            result = {
                "project_id": project_id,
                "documentation_files": saved_docs,
                "documentation_type": self._determine_documentation_type(specifications),
                "total_documentation_files": len(saved_docs),
                "readme_files": len([f for f in saved_docs.keys() if "README" in f]),
                "api_docs": len([f for f in saved_docs.keys() if "api" in f.lower()]),
                "user_guides": len([f for f in saved_docs.keys() if "user" in f.lower() or "guide" in f.lower()]),
                "developer_docs": len([f for f in saved_docs.keys() if "developer" in f.lower() or "dev" in f.lower()]),
                "deployment_docs": len([f for f in saved_docs.keys() if "deployment" in f.lower() or "deploy" in f.lower()]),
                "documentation_ready": True
            }
            
            logger.info(f"Comprehensive documentation generation finished. Generated {len(saved_docs)} documentation files.")
            return result
            
        except Exception as e:
            logger.error(f"Error in documentation generation: {e}")
            return self._generate_fallback_documentation(specifications, generated_files, project_id, str(e))
    
    def _create_documentation_generation_prompt(self, specifications: Dict[str, Any], generated_files: Dict[str, Any]) -> str:
        """Create detailed documentation generation prompt."""
        
        # Extract key information from specifications
        project_overview = specifications.get("project_overview", {})
        functional_reqs = specifications.get("functional_requirements", [])
        architecture = specifications.get("architecture", {})
        
        tech_stack = project_overview.get("technology_stack", {})
        backend_stack = tech_stack.get("backend", {})
        frontend_stack = tech_stack.get("frontend", {})
        
        prompt = f"""
Generate comprehensive documentation for the following application:

## PROJECT OVERVIEW:
- Name: {project_overview.get('name', 'Generated Application')}
- Description: {project_overview.get('description', 'N/A')}
- Backend: {backend_stack.get('framework', 'FastAPI')}
- Frontend: {frontend_stack.get('framework', 'React')}
- Database: {backend_stack.get('database', 'PostgreSQL')}

## FUNCTIONAL REQUIREMENTS:
"""
        
        for req in functional_reqs:
            prompt += f"""
- {req.get('id', 'N/A')}: {req.get('title', 'N/A')}
  Description: {req.get('description', 'N/A')}
  Acceptance Criteria: {', '.join(req.get('acceptance_criteria', []))}
"""
        
        prompt += f"""
## ARCHITECTURE:
{json.dumps(architecture, indent=2)}

## GENERATED CODE FILES:
The following code has been generated for this project. Please create documentation based on the actual implementation:

"""
        
        # Add generated files to the prompt
        for filename, content in generated_files.items():
            prompt += f"""
### {filename}:
```{self._get_file_extension(filename)}
{content}
```
"""
        
        prompt += """
## DOCUMENTATION REQUIREMENTS:

Please generate the following documentation files:

1. **README.md** - Project overview, setup, and usage
2. **API_DOCUMENTATION.md** - API endpoints and usage
3. **USER_GUIDE.md** - User instructions and examples
4. **DEVELOPER_GUIDE.md** - Development setup and contribution
5. **DEPLOYMENT_GUIDE.md** - Deployment instructions

For each file, provide complete documentation with:
- Clear explanations
- Code examples
- Setup instructions
- Usage examples
- Troubleshooting tips

IMPORTANT: Generate documentation that matches the actual code implementation.

Please generate the complete documentation with all files and full content.

IMPORTANT: End your response with "TERMINATE" to indicate completion.
"""
        
        return prompt
    
    def _parse_generated_documentation(self, response: str) -> Dict[str, str]:
        """Parse generated documentation files from the response."""
        import re
        
        docs = {}
        
        # Extract markdown blocks with filenames
        markdown_blocks = re.findall(r'```markdown\s*# filename: ([^\n]+)\s*(.*?)```', response, re.DOTALL)
        
        for filename, content in markdown_blocks:
            docs[filename] = content.strip()
        
        # Also look for markdown blocks without explicit filenames
        if not docs:
            markdown_blocks = re.findall(r'```markdown\s*(.*?)```', response, re.DOTALL)
            for i, content in enumerate(markdown_blocks):
                # Try to infer filename from content
                filename = self._infer_documentation_filename(content, i)
                docs[filename] = content.strip()
        
        return docs
    
    def _infer_documentation_filename(self, content: str, index: int) -> str:
        """Infer documentation filename from content."""
        if "# API Documentation" in content or "## Endpoints" in content:
            return f"docs/api/overview.md"
        elif "# User Guide" in content or "## Getting Started" in content:
            return f"docs/user-guide/getting-started.md"
        elif "# Developer Guide" in content or "## Architecture" in content:
            return f"docs/developer/architecture.md"
        elif "# README" in content or "## Project Overview" in content:
            return f"README.md"
        elif "# Deployment" in content or "## Installation" in content:
            return f"docs/deployment/guide.md"
        else:
            return f"docs/documentation_{index}.md"
    
    def _get_file_extension(self, filename: str) -> str:
        """Get appropriate file extension for a filename."""
        if filename.endswith('.py'):
            return 'python'
        elif filename.endswith('.js'):
            return 'javascript'
        elif filename.endswith('.html'):
            return 'html'
        elif filename.endswith('.css'):
            return 'css'
        elif filename.endswith('.json'):
            return 'json'
        elif filename.endswith('.yml') or filename.endswith('.yaml'):
            return 'yaml'
        elif filename.endswith('.sql'):
            return 'sql'
        elif filename.endswith('.md'):
            return 'markdown'
        else:
            return 'text'
    
    def _validate_and_enhance_documentation(self, docs: Dict[str, str]) -> Dict[str, str]:
        """Validate and enhance the generated documentation."""
        enhanced_docs = {}
        
        for filename, content in docs.items():
            # Basic validation for markdown content
            if not content.strip():
                logger.warning(f"Empty documentation content for {filename}")
                continue
            
            # Enhance documentation with better formatting
            enhanced_content = self._enhance_markdown_content(content)
            enhanced_docs[filename] = enhanced_content
        
        return enhanced_docs
    
    def _enhance_markdown_content(self, content: str) -> str:
        """Enhance markdown content with better formatting."""
        # Add table of contents if not present
        if "# " in content and "## " in content and "## Table of Contents" not in content:
            lines = content.split('\n')
            toc_lines = []
            toc_lines.append("## 📋 Table of Contents\n")
            
            for line in lines:
                if line.startswith('## '):
                    title = line[3:].strip()
                    anchor = title.lower().replace(' ', '-').replace(':', '').replace('(', '').replace(')', '')
                    toc_lines.append(f"- [{title}](#{anchor})")
            
            if len(toc_lines) > 1:
                # Insert TOC after first heading
                for i, line in enumerate(lines):
                    if line.startswith('# ') and not line.startswith('## '):
                        lines.insert(i + 1, '')
                        lines.insert(i + 2, '\n'.join(toc_lines))
                        lines.insert(i + 3, '')
                        break
                
                content = '\n'.join(lines)
        
        return content
    
    def _save_generated_documentation(self, docs: Dict[str, str], project_id: str) -> Dict[str, str]:
        """Save generated documentation files and return content."""
        try:
            saved_docs = {}
            project_dir = f"output/documentation/{project_id}"
            os.makedirs(project_dir, exist_ok=True)
            
            for filename, content in docs.items():
                # Use save_to_file with correct parameters: (content, filename, output_dir)
                file_path = save_to_file(content, filename, project_dir)
                saved_docs[filename] = file_path
                logger.info(f"Saved documentation file: {file_path}")
            
            return saved_docs
            
        except Exception as e:
            logger.error(f"Error saving documentation files: {e}")
            return {}
    
    def _generate_additional_documentation(self, specifications: Dict[str, Any], generated_files: Dict[str, Any], project_id: str) -> Dict[str, str]:
        """Generate additional documentation files."""
        additional_docs = {}
        
        # Generate CHANGELOG
        changelog = self._generate_changelog(specifications)
        additional_docs["CHANGELOG.md"] = changelog
        
        # Generate CONTRIBUTING guide
        contributing = self._generate_contributing_guide(specifications)
        additional_docs["CONTRIBUTING.md"] = contributing
        
        # Generate LICENSE
        license_file = self._generate_license_file(specifications)
        additional_docs["LICENSE"] = license_file
        
        return additional_docs
    
    def _generate_changelog(self, specifications: Dict[str, Any]) -> str:
        """Generate changelog."""
        project_name = specifications.get("project_overview", {}).get("name", "Generated Application")
        
        return f"""# Changelog

All notable changes to {project_name} will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project setup
- Basic functionality implementation
- Documentation generation

### Changed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- N/A

## [1.0.0] - 2024-01-01

### Added
- Initial release
- Core application features
- API endpoints
- User interface
- Database integration
- Authentication system
- Documentation

### Security
- JWT-based authentication
- Password hashing
- Input validation
- Rate limiting
"""
    
    def _generate_contributing_guide(self, specifications: Dict[str, Any]) -> str:
        """Generate contributing guide."""
        return """# Contributing

We love your input! We want to make contributing to this project as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## We Develop with Github
We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

## We Use [Github Flow](https://guides.github.com/introduction/flow/)
Pull requests are the best way to propose changes to the codebase. We actively welcome your pull requests:

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!

## We Use [Conventional Commits](https://www.conventionalcommits.org/)
We use conventional commits to keep our commit history clean and meaningful. Please follow the conventional commits specification when making commits.

### Commit Types
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools and libraries such as documentation generation

### Examples
```
feat: add user authentication system
fix: resolve database connection issue
docs: update API documentation
style: format code according to style guide
refactor: restructure user service
perf: optimize database queries
test: add unit tests for auth service
chore: update dependencies
```

## Any contributions you make will be under the MIT Software License
In short, when you submit code changes, your submissions are understood to be under the same [MIT License](http://choosealicense.com/licenses/mit/) that covers the project. Feel free to contact the maintainers if that's a concern.

## Report bugs using Github's [issue tracker](https://github.com/username/project/issues)
We use GitHub issues to track public bugs. Report a bug by [opening a new issue](https://github.com/username/project/issues/new); it's that easy!

## Write bug reports with detail, background, and sample code

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can.
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

## License
By contributing, you agree that your contributions will be licensed under its MIT License.

## References
This document was adapted from the open-source contribution guidelines for [Facebook's Draft](https://github.com/facebook/draft-js/blob/a9316a723f9e918afde44dea68b5f9f39b7d9b00/CONTRIBUTING.md).
"""
    
    def _generate_license_file(self, specifications: Dict[str, Any]) -> str:
        """Generate MIT license file."""
        current_year = "2024"
        project_name = specifications.get("project_overview", {}).get("name", "Generated Application")
        
        return f"""MIT License

Copyright (c) {current_year} {project_name}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
    
    def _determine_documentation_type(self, specifications: Dict[str, Any]) -> str:
        """Determine the type of documentation generated."""
        tech_stack = specifications.get("project_overview", {}).get("technology_stack", {})
        
        if tech_stack.get("frontend") and tech_stack.get("backend"):
            return "Full-Stack Application Documentation"
        elif tech_stack.get("backend"):
            return "Backend API Documentation"
        elif tech_stack.get("frontend"):
            return "Frontend Application Documentation"
        else:
            return "General Application Documentation"
    
    def _generate_fallback_documentation(self, specifications: Dict[str, Any], 
                                        generated_files: Dict[str, Any], project_id: str, error: str) -> Dict[str, Any]:
        """Generate fallback documentation when generation fails."""
        fallback_docs = {
            "README.md": self._generate_basic_readme(specifications),
            "CHANGELOG.md": self._generate_changelog(specifications),
            "LICENSE": self._generate_license_file(specifications),
            "docs/basic-guide.md": "# Basic Guide\n\nBasic documentation generated as fallback."
        }
        
        saved_docs = self._save_generated_documentation(fallback_docs, project_id)
        
        return {
            "project_id": project_id,
            "documentation_files": saved_docs,
            "documentation_type": "Basic Documentation",
            "total_documentation_files": len(saved_docs),
            "readme_files": 1,
            "api_docs": 0,
            "user_guides": 1,
            "developer_docs": 0,
            "deployment_docs": 0,
            "documentation_ready": False,
            "error": error,
            "fallback_mode": True
        }
    
    def _generate_basic_readme(self, specifications: Dict[str, Any]) -> str:
        """Generate basic README."""
        project_name = specifications.get("project_overview", {}).get("name", "Generated Application")
        description = specifications.get("project_overview", {}).get("description", "A generated application")
        
        return f"""# {project_name}

{description}

## Quick Start

1. Clone the repository
2. Install dependencies
3. Run the application

## Features

- Basic functionality
- API endpoints
- User interface

## License

MIT License
""" 