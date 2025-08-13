"""
Utility functions for the Multi-Agentic Coding Framework.
Provides helper functions for file operations, logging, and common tasks.
"""

import os
import json
import logging
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Set up logging configuration."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('multi_agent_framework.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def save_to_file(content: str, filename: str, output_dir: str = "./output") -> str:
    """Save content to a file in the output directory."""
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return filepath

def load_from_file(filepath: str) -> str:
    """Load content from a file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def save_json(data: Dict[str, Any], filename: str, output_dir: str = "./output") -> str:
    """Save data as JSON file."""
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return filepath

def load_json(filepath: str) -> Dict[str, Any]:
    """Load data from JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_project_id(requirement: str) -> str:
    """Generate a unique project ID based on the requirement."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    requirement_hash = hashlib.md5(requirement.encode()).hexdigest()[:8]
    return f"project_{timestamp}_{requirement_hash}"

def create_project_structure(project_id: str, output_dir: str = "./output") -> Dict[str, str]:
    """Create directory structure for a project."""
    project_dir = os.path.join(output_dir, project_id)
    
    directories = {
        "root": project_dir,
        "src": os.path.join(project_dir, "src"),
        "tests": os.path.join(project_dir, "tests"),
        "docs": os.path.join(project_dir, "docs"),
        "deployment": os.path.join(project_dir, "deployment"),
        "ui": os.path.join(project_dir, "ui")
    }
    
    for dir_path in directories.values():
        os.makedirs(dir_path, exist_ok=True)
    
    return directories

def extract_code_blocks(text: str) -> List[str]:
    """Extract code blocks from markdown or text content."""
    import re
    
    # Pattern to match code blocks
    code_block_pattern = r'```(?:python)?\n(.*?)\n```'
    matches = re.findall(code_block_pattern, text, re.DOTALL)
    
    # If no matches found, try alternative patterns
    if not matches:
        # Look for code blocks without language specification
        alt_pattern = r'```\n(.*?)\n```'
        matches = re.findall(alt_pattern, text, re.DOTALL)
    
    # If still no matches, try to extract any code-like content
    if not matches:
        # Look for content between triple backticks
        fallback_pattern = r'```(.*?)```'
        matches = re.findall(fallback_pattern, text, re.DOTALL)
    
    return [match.strip() for match in matches]

def extract_file_paths(text: str) -> List[str]:
    """Extract file paths mentioned in text."""
    import re
    
    # Pattern to match file paths
    file_pattern = r'`([^`]+\.(py|md|txt|json|yaml|yml))`'
    matches = re.findall(file_pattern, text)
    
    return [match[0] for match in matches]

def validate_python_code(code: str) -> Dict[str, Any]:
    """Validate Python code syntax and basic structure."""
    import ast
    
    result = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "functions": [],
        "classes": [],
        "imports": []
    }
    
    try:
        tree = ast.parse(code)
        
        # Extract functions, classes, and imports
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                result["functions"].append(node.name)
            elif isinstance(node, ast.ClassDef):
                result["classes"].append(node.name)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    result["imports"].append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    result["imports"].append(f"{module}.{alias.name}")
        
        # Basic checks
        if not result["functions"] and not result["classes"]:
            result["warnings"].append("No functions or classes found in code")
        
    except SyntaxError as e:
        result["valid"] = False
        result["errors"].append(f"Syntax error: {e}")
    except Exception as e:
        result["valid"] = False
        result["errors"].append(f"Error parsing code: {e}")
    
    return result

def format_code_with_black(code: str) -> str:
    """Format Python code using black (if available)."""
    try:
        import black
        mode = black.FileMode()
        formatted_code = black.format_str(code, mode=mode)
        return formatted_code
    except ImportError:
        # Black not available, return original code
        return code
    except Exception:
        # Black failed, return original code
        return code

def create_requirements_file(dependencies: List[str], output_path: str) -> str:
    """Create a requirements.txt file with specified dependencies."""
    content = "\n".join(dependencies)
    return save_to_file(content, "requirements.txt", output_path)

def create_setup_py(project_name: str, version: str = "1.0.0", 
                   description: str = "", author: str = "", 
                   dependencies: List[str] = None, output_path: str = "./output") -> str:
    """Create a setup.py file for the project."""
    if dependencies is None:
        dependencies = []
    
    setup_content = f'''from setuptools import setup, find_packages

setup(
    name="{project_name}",
    version="{version}",
    description="{description}",
    author="{author}",
    packages=find_packages(),
    install_requires={dependencies},
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
'''
    
    return save_to_file(setup_content, "setup.py", output_path)

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file system operations."""
    import re
    
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    sanitized = re.sub(r'\s+', '_', sanitized)
    sanitized = sanitized.strip('._')
    
    return sanitized

def get_file_extension(content: str, filename: str = "") -> str:
    """Determine the appropriate file extension based on content or filename."""
    if filename and '.' in filename:
        return filename.split('.')[-1]
    
    # Try to determine from content
    if content.strip().startswith('import ') or 'def ' in content or 'class ' in content:
        return 'py'
    elif content.strip().startswith('#') or '##' in content:
        return 'md'
    elif content.strip().startswith('{') or content.strip().startswith('['):
        return 'json'
    elif 'yaml' in content.lower() or '---' in content:
        return 'yaml'
    else:
        return 'txt' 

def extract_llm_response(chat_result) -> str:
    """
    Extract the LLM response from AutoGen chat history.
    
    Args:
        chat_result: The result from AutoGen chat
        
    Returns:
        The LLM response content
        
    Raises:
        ValueError: If no response is found
    """
    logger = setup_logging()
    logger.info(f"Chat history length: {len(chat_result.chat_history)}")
    
    # Log all messages for debugging
    for i, message in enumerate(chat_result.chat_history):
        role = message.get("role", "unknown")
        content_preview = message.get("content", "")[:100]
        logger.info(f"Message {i}: role={role}, content_preview={content_preview}...")
    
    # Find the LLM response - it's in the user message (AutoGen structure)
    last_message = None
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
        raise ValueError("No response received from agent")
    
    return last_message 