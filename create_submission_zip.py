#!/usr/bin/env python3
"""
Script to create a comprehensive ZIP file for assignment submission.
Includes all necessary files while excluding temporary and generated files.
"""

import os
import zipfile
import shutil
from datetime import datetime

def create_submission_zip():
    """Create a comprehensive ZIP file for assignment submission."""
    
    # Define the submission filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    submission_filename = f"Multi_Agentic_Coding_Framework_Submission_{timestamp}.zip"
    
    # Files and directories to include
    include_patterns = [
        # Core application files
        "app.py",
        "requirements.txt",
        "README.md",
        "LICENSE",
        ".env.example",
        ".gitignore",
        
        # Core framework
        "core/",
        
        # Agents
        "agents/",
        
        # Templates and examples
        "templates/",
        "examples/",
        
        # Documentation
        "INTERVIEW_GUIDE.md",
        "PROJECT_SUMMARY.md",
        "SETUP_GUIDE.md",
        
        # Deployment scripts
        "deploy.sh",
        "run_tests.sh",
        
        # Test files (excluding temporary ones)
        "test_basic.py",
        "tests/",
    ]
    
    # Files and directories to exclude
    exclude_patterns = [
        "__pycache__/",
        ".venv/",
        ".git/",
        "output/",
        "workspace/",
        "*.log",
        "test_*.py",  # Exclude temporary test files
        "debug_*.py",
        "*_test_result.json",
        "test_*.zip",
        "multi_agent_framework.log",
        "debug_last_message.txt",
        "coding_test_result.json",
        "requirement_test_result.json",
        "test_download.py",
        "create_submission_zip.py",  # Exclude this script itself
    ]
    
    print(f"Creating submission ZIP: {submission_filename}")
    
    with zipfile.ZipFile(submission_filename, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Walk through all files and directories
        for root, dirs, files in os.walk('.'):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if not any(pattern in os.path.join(root, d) for pattern in exclude_patterns)]
            
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, '.')
                
                # Skip excluded files
                if any(pattern in relative_path for pattern in exclude_patterns):
                    continue
                
                # Check if file should be included
                should_include = False
                for pattern in include_patterns:
                    if pattern.endswith('/'):
                        # Directory pattern
                        if relative_path.startswith(pattern):
                            should_include = True
                            break
                    else:
                        # File pattern
                        if relative_path == pattern or relative_path.endswith(pattern):
                            should_include = True
                            break
                
                if should_include:
                    try:
                        zip_file.write(file_path, relative_path)
                        print(f"✅ Added: {relative_path}")
                    except Exception as e:
                        print(f"❌ Error adding {relative_path}: {e}")
    
    # Get file size
    file_size = os.path.getsize(submission_filename)
    file_size_mb = file_size / (1024 * 1024)
    
    print(f"\n🎉 Submission ZIP created successfully!")
    print(f"📁 Filename: {submission_filename}")
    print(f"📊 Size: {file_size_mb:.2f} MB ({file_size:,} bytes)")
    
    # List contents for verification
    print(f"\n📋 Contents:")
    with zipfile.ZipFile(submission_filename, 'r') as zip_file:
        file_list = zip_file.namelist()
        for file_path in sorted(file_list):
            print(f"  - {file_path}")
    
    print(f"\n📦 Total files: {len(file_list)}")
    print(f"✅ Ready for submission!")
    
    return submission_filename

def create_readme_for_submission():
    """Create a submission README with instructions."""
    
    readme_content = """# Multi-Agentic Coding Framework - Assignment Submission

## Project Overview

This submission contains a complete implementation of a Multi-Agentic Coding Framework that uses AI agents to collaboratively generate software projects from natural language requirements.

## Key Features Implemented

✅ **7 Specialized AI Agents**
- Requirement Analysis Agent
- Coding Agent  
- Code Review Agent
- Documentation Agent
- Test Generation Agent
- Deployment Configuration Agent
- Streamlit UI Agent

✅ **Complete Pipeline**
- Natural language to structured requirements
- Code generation with validation
- Comprehensive documentation
- Unit and integration tests
- Deployment configurations
- User interface generation

✅ **Interactive Web Interface**
- Streamlit-based UI
- Real-time progress tracking
- Download functionality for complete projects
- Project history management

✅ **Quality Assurance**
- Code validation and formatting
- Error handling and fallback mechanisms
- Comprehensive testing framework
- Pydantic data validation

## File Structure

```
Multi_Agentic_Coding_Framework/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation
├── LICENSE                         # MIT License
├── .env.example                    # Environment variables template
├── .gitignore                      # Git ignore rules
├── core/                           # Core framework
│   ├── config.py                   # Configuration management
│   ├── coordinator.py              # Agent orchestration
│   ├── utils.py                    # Utility functions
│   └── validation.py               # Data validation
├── agents/                         # Agent implementations
│   ├── requirement_agent.py        # Requirement analysis
│   ├── coding_agent.py             # Code generation
│   ├── review_agent.py             # Code review
│   ├── documentation_agent.py      # Documentation generation
│   ├── test_agent.py               # Test generation
│   ├── deployment_agent.py         # Deployment configuration
│   └── ui_agent.py                 # UI generation
├── templates/                      # Documentation templates
├── examples/                       # Example projects
├── tests/                          # Test files
├── deploy.sh                       # Deployment script
├── run_tests.sh                    # Test runner script
├── INTERVIEW_GUIDE.md              # Technical documentation
├── PROJECT_SUMMARY.md              # Architecture overview
└── SETUP_GUIDE.md                  # Setup instructions
```

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

3. **Run the application:**
   ```bash
   streamlit run app.py
   ```

4. **Open browser:**
   Navigate to `http://localhost:8501`

## Testing

Run the test suite:
```bash
python test_basic.py
```

## Technical Highlights

- **AutoGen Integration**: Uses Microsoft's AutoGen for multi-agent conversations
- **Pydantic Validation**: Robust data validation between agents
- **Streamlit UI**: Modern, responsive web interface
- **Complete Project Generation**: End-to-end software development pipeline
- **Download Functionality**: Export complete projects as ZIP files
- **Error Handling**: Comprehensive error handling and fallback mechanisms

## Assignment Requirements Met

✅ **Multi-Agentic Framework**: 7 specialized agents working collaboratively
✅ **AutoGen Implementation**: Full integration with Microsoft AutoGen
✅ **Python Codebase**: Complete implementation in Python
✅ **Documentation**: Comprehensive documentation and guides
✅ **Test Cases**: Unit and integration tests with execution results
✅ **Streamlit UI**: Interactive web interface for project creation
✅ **README**: Complete project documentation
✅ **Download Functionality**: Export complete projects with proper structure

## Submission Details

- **Framework**: Multi-Agentic Coding Framework
- **Technology**: Python, AutoGen, Streamlit, OpenAI GPT-4
- **Architecture**: 7-agent collaborative pipeline
- **Features**: End-to-end software project generation
- **Documentation**: Complete technical and user documentation

---
**Submitted by**: [Your Name]
**Date**: {date}
**Course**: [Course Name]
**Assignment**: Multi-Agentic Framework Implementation
""".format(date=datetime.now().strftime("%Y-%m-%d"))
    
    with open("SUBMISSION_README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("📝 Created SUBMISSION_README.md")

if __name__ == "__main__":
    # Create submission README
    create_readme_for_submission()
    
    # Create submission ZIP
    submission_file = create_submission_zip()
    
    print(f"\n🎯 Assignment submission ready!")
    print(f"📤 Submit the file: {submission_file}")
    print(f"📖 Review: SUBMISSION_README.md") 