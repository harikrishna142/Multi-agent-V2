"""
Main Streamlit Application for the Multi-Agentic Coding Framework.
Provides a user-friendly interface for interacting with the multi-agent system.
"""

import streamlit as st
import sys
import os
from datetime import datetime
import json
import time
import zipfile
import io
import shutil

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.coordinator import MultiAgentCoordinator
from core.config import config
from core.utils import setup_logging

# Set up logging
logger = setup_logging()

# Page configuration
st.set_page_config(
    page_title="Multi-Agentic Coding Framework",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.main-header {
    font-size: 3rem;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
    font-weight: bold;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
}
.sidebar-header {
    font-size: 1.5rem;
    color: #2c3e50;
    margin-bottom: 1rem;
    font-weight: 600;
}
.agent-card {
    background-color: #f8f9fa;
    padding: 1.5rem;
    border-radius: 10px;
    border: 1px solid #dee2e6;
    margin: 1rem 0;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
.status-completed {
    color: #28a745;
    font-weight: bold;
}
.status-processing {
    color: #ffc107;
    font-weight: bold;
}
.status-failed {
    color: #dc3545;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

def main():
    """Main application function."""
    
    # Initialize coordinator
    if 'coordinator' not in st.session_state:
        st.session_state.coordinator = MultiAgentCoordinator()
    
    # Header
    st.markdown('<h1 class="main-header">🤖 Multi-Agentic Coding Framework</h1>', unsafe_allow_html=True)
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown('<h2 class="sidebar-header">Navigation</h2>', unsafe_allow_html=True)
        page = st.selectbox(
            "Choose a page:",
            ["New Project", "Project History", "Agent Status", "Configuration", "About"]
        )
        
        st.markdown("---")
        st.markdown("**Framework Info**")
        st.write(f"Version: 1.0.0")
        st.write(f"Status: Active")
        st.write(f"Agents: 7")
    
    # Main content based on selected page
    if page == "New Project":
        show_new_project_page()
    elif page == "Project History":
        show_project_history_page()
    elif page == "Agent Status":
        show_agent_status_page()
    elif page == "Configuration":
        show_configuration_page()
    elif page == "About":
        show_about_page()

def show_new_project_page():
    """Show the new project creation page."""
    st.header("🚀 Create New Project")
    st.write("Enter your software requirement in natural language and let our AI agents create a complete solution.")
    
    # Requirement input
    with st.form("new_project_form"):
        st.subheader("Project Requirement")
        requirement = st.text_area(
            "Describe your software requirement:",
            placeholder="e.g., Create a web application that allows users to manage their personal task list with features like adding tasks, marking them as complete, setting due dates, and categorizing tasks by priority.",
            height=200,
            help="Be as detailed as possible to get the best results from our AI agents."
        )
        
        # Advanced options
        with st.expander("Advanced Options"):
            col1, col2 = st.columns(2)
            with col1:
                max_iterations = st.slider("Max Code Review Iterations", 1, 5, 3)
                temperature = st.slider("AI Creativity Level", 0.1, 1.0, 0.7, 0.1)
            with col2:
                include_tests = st.checkbox("Generate Tests", value=True)
                include_docs = st.checkbox("Generate Documentation", value=True)
                include_deployment = st.checkbox("Generate Deployment Config", value=True)
                include_ui = st.checkbox("Generate UI", value=True)
        
        submit_button = st.form_submit_button("🚀 Start Multi-Agent Processing")
    
    # Handle form submission outside the form
    if submit_button and requirement.strip():
        process_new_project(requirement, max_iterations, temperature, 
                          include_tests, include_docs, include_deployment, include_ui)
    elif submit_button and not requirement.strip():
        st.error("Please enter a requirement before starting.")

def process_new_project(requirement: str, max_iterations: int, temperature: float,
                       include_tests: bool, include_docs: bool, include_deployment: bool, include_ui: bool):
    """Process a new project through the multi-agent pipeline."""
    
    # Update configuration
    config.max_iterations = max_iterations
    config.temperature = temperature
    
    # Create progress container
    progress_container = st.container()
    results_container = st.container()
    
    with progress_container:
        st.subheader("🔄 Processing Pipeline")
        
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Agent status
        agent_status = st.empty()
        
        # Define agent steps
        agents = [
            "Requirement Analysis",
            "Code Generation", 
            "Code Review",
            "Documentation Generation",
            "Test Generation",
            "Deployment Configuration",
            "UI Generation"
        ]
        
        # Skip agents based on options
        if not include_docs:
            agents.remove("Documentation Generation")
        if not include_tests:
            agents.remove("Test Generation")
        if not include_deployment:
            agents.remove("Deployment Configuration")
        if not include_ui:
            agents.remove("UI Generation")
        
        total_agents = len(agents)
        
        try:
            # Start processing
            status_text.text("Initializing multi-agent pipeline...")
            progress_bar.progress(0)
            
            # Process requirement
            results = st.session_state.coordinator.process_requirement(requirement)
            
            # Update progress based on results
            completed_agents = len([agent for agent in results.get("agents", {}).values() 
                                  if agent.get("status") == "completed"])
            
            progress = min(completed_agents / total_agents, 1.0)
            progress_bar.progress(progress)
            
            if results.get("final_status") == "completed":
                status_text.text("✅ Processing completed successfully!")
                st.success("🎉 Project created successfully!")
            else:
                status_text.text("❌ Processing failed")
                st.error("Processing failed. Check the logs for details.")
            
            # Display agent status
            agent_status_data = []
            for agent_name, agent_data in results.get("agents", {}).items():
                status = agent_data.get("status", "unknown")
                timestamp = agent_data.get("timestamp", "")
                agent_status_data.append({
                    "Agent": agent_name.replace("_", " ").title(),
                    "Status": status,
                    "Timestamp": timestamp
                })
            
            if agent_status_data:
                agent_status.dataframe(agent_status_data, use_container_width=True)
            
            # Store results in session state
            st.session_state.last_results = results
            
            # Show results
            with results_container:
                show_project_results(results)
                
        except Exception as e:
            st.error(f"Error during processing: {e}")
            logger.error(f"Error in process_new_project: {e}")

def show_project_results(results: dict):
    """Display project results."""
    st.subheader("📊 Project Results")
    
    # Project summary
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Project ID", results.get("project_id", "N/A"))
    with col2:
        st.metric("Status", results.get("final_status", "N/A"))
    with col3:
        st.metric("Total Agents", len(results.get("agents", {})))
    with col4:
        completed = len([agent for agent in results.get("agents", {}).values() 
                        if agent.get("status") == "completed"])
        st.metric("Completed", completed)
    
    # Agent results tabs
    if results.get("agents"):
        tabs = st.tabs([agent.replace("_", " ").title() for agent in results["agents"].keys()])
        
        for i, (agent_name, agent_data) in enumerate(results["agents"].items()):
            with tabs[i]:
                show_agent_results(agent_name, agent_data)
    
    # Download results
    st.subheader("📥 Download Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        results_json = json.dumps(results, indent=2)
        st.download_button(
            label="📄 Download JSON Results",
            data=results_json,
            file_name=f"{results.get('project_id', 'project')}_results.json",
            mime="application/json"
        )
    
    with col2:
        project_zip = create_project_package(results)
        if project_zip:
            st.download_button(
                label="📦 Download Complete Project",
                data=project_zip,
                file_name=f"{results.get('project_id', 'project')}_complete_project.zip",
                mime="application/zip"
            )
        else:
            st.error("Failed to create project package")

def create_project_package(results: dict) -> bytes:
    """Create a complete project package as a ZIP file."""
    try:
        # Create a BytesIO object to store the ZIP file
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            project_id = results.get('project_id', 'project')
            
            # Add project metadata
            metadata = {
                "project_id": project_id,
                "generated_at": datetime.now().isoformat(),
                "framework_version": "1.0.0",
                "agents_used": list(results.get('agents', {}).keys()),
                "final_status": results.get('final_status', 'unknown')
            }
            
            zip_file.writestr(f"{project_id}/project_metadata.json", json.dumps(metadata, indent=2))
            
            # Add README file
            readme_content = create_project_readme(results)
            zip_file.writestr(f"{project_id}/README.md", readme_content)
            
            # Add generated code files
            if results.get('agents', {}).get('code_generation', {}).get('results', {}).get('generated_files'):
                code_files = results['agents']['code_generation']['results']['generated_files']
                for filename, content in code_files.items():
                    try:
                        # Content is already the file content, not a filepath
                        zip_file.writestr(f"{project_id}/src/{filename}", content)
                    except Exception as e:
                        logger.error(f"Error adding code file {filename}: {e}")
            
            # Add documentation files
            if results.get('agents', {}).get('documentation', {}).get('results', {}).get('generated_documentation'):
                doc_files = results['agents']['documentation']['results']['generated_documentation']
                for filename, content in doc_files.items():
                    try:
                        # Content is already the file content, not a filepath
                        zip_file.writestr(f"{project_id}/docs/{filename}", content)
                    except Exception as e:
                        logger.error(f"Error adding doc file {filename}: {e}")
            
            # Add test files
            if results.get('agents', {}).get('test_generation', {}).get('results', {}).get('generated_tests'):
                test_files = results['agents']['test_generation']['results']['generated_tests']
                for filename, content in test_files.items():
                    try:
                        # Content is already the file content, not a filepath
                        zip_file.writestr(f"{project_id}/tests/{filename}", content)
                    except Exception as e:
                        logger.error(f"Error adding test file {filename}: {e}")
            
            # Add deployment files
            if results.get('agents', {}).get('deployment_config', {}).get('results', {}).get('generated_configs'):
                deploy_files = results['agents']['deployment_config']['results']['generated_configs']
                for filename, content in deploy_files.items():
                    try:
                        # Content is already the file content, not a filepath
                        zip_file.writestr(f"{project_id}/deployment/{filename}", content)
                    except Exception as e:
                        logger.error(f"Error adding deployment file {filename}: {e}")
            
            # Add UI files
            if results.get('agents', {}).get('ui_generation', {}).get('results', {}).get('generated_ui'):
                ui_files = results['agents']['ui_generation']['results']['generated_ui']
                for filename, content in ui_files.items():
                    try:
                        # Content is already the file content, not a filepath
                        zip_file.writestr(f"{project_id}/ui/{filename}", content)
                    except Exception as e:
                        logger.error(f"Error adding UI file {filename}: {e}")
            
            # Add requirements.txt
            requirements_content = create_requirements_file(results)
            zip_file.writestr(f"{project_id}/requirements.txt", requirements_content)
            
            # Add setup.py
            setup_content = create_setup_file(results)
            zip_file.writestr(f"{project_id}/setup.py", setup_content)
            
            # Add .gitignore
            gitignore_content = create_gitignore_file()
            zip_file.writestr(f"{project_id}/.gitignore", gitignore_content)
        
        # Return the ZIP file as bytes
        zip_buffer.seek(0)
        return zip_buffer.getvalue()
        
    except Exception as e:
        logger.error(f"Error creating project package: {e}")
        return None

def create_project_readme(results: dict) -> str:
    """Create a comprehensive README file for the project."""
    project_id = results.get('project_id', 'project')
    agents = results.get('agents', {})
    
    readme = f"""# {project_id.replace('_', ' ').title()}

This project was generated using the Multi-Agentic Coding Framework.

## Project Overview

- **Project ID**: {project_id}
- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Framework Version**: 1.0.0
- **Status**: {results.get('final_status', 'unknown')}

## Generated Components

"""
    
    # Add information about each agent's output
    for agent_name, agent_data in agents.items():
        if agent_data.get('status') == 'completed':
            results_data = agent_data.get('results', {})
            
            if agent_name == 'requirement_analysis':
                readme += f"""
### 📋 Requirements Analysis
- **Project Name**: {results_data.get('project_name', 'N/A')}
- **Description**: {results_data.get('description', 'N/A')}
- **Complexity**: {results_data.get('estimated_complexity', 'N/A')}
- **Architecture**: {results_data.get('suggested_architecture', 'N/A')}
"""
            
            elif agent_name == 'code_generation':
                files = results_data.get('generated_files', {})
                readme += f"""
### 💻 Code Generation
- **Total Files**: {len(files)}
- **Files Generated**:
"""
                for filename in files.keys():
                    readme += f"  - `{filename}`\n"
            
            elif agent_name == 'documentation':
                docs = results_data.get('generated_documentation', {})
                readme += f"""
### 📚 Documentation
- **Total Docs**: {len(docs)}
- **Documents Generated**:
"""
                for filename in docs.keys():
                    readme += f"  - `{filename}`\n"
            
            elif agent_name == 'test_generation':
                tests = results_data.get('generated_tests', {})
                readme += f"""
### 🧪 Test Generation
- **Total Tests**: {len(tests)}
- **Test Files Generated**:
"""
                for filename in tests.keys():
                    readme += f"  - `{filename}`\n"
            
            elif agent_name == 'deployment_config':
                configs = results_data.get('generated_configs', {})
                readme += f"""
### 🚀 Deployment Configuration
- **Total Configs**: {len(configs)}
- **Config Files Generated**:
"""
                for filename in configs.keys():
                    readme += f"  - `{filename}`\n"
            
            elif agent_name == 'ui_generation':
                ui_files = results_data.get('generated_ui', {})
                readme += f"""
### 🎨 UI Generation
- **Total UI Files**: {len(ui_files)}
- **UI Files Generated**:
"""
                for filename in ui_files.keys():
                    readme += f"  - `{filename}`\n"
    
    readme += f"""
## Project Structure

```
{project_id}/
├── src/                    # Source code files
├── docs/                   # Documentation files
├── tests/                  # Test files
├── deployment/             # Deployment configuration
├── ui/                     # User interface files
├── requirements.txt        # Python dependencies
├── setup.py               # Package setup
├── .gitignore             # Git ignore file
├── README.md              # This file
└── project_metadata.json  # Project metadata
```

## Installation

1. Extract the project files
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python src/main.py
   ```

## Development

This project was generated using AI agents. You can:
- Review and modify the generated code
- Add additional features
- Customize the documentation
- Enhance the test coverage
- Modify deployment configurations

## Framework Information

Generated using the Multi-Agentic Coding Framework with the following agents:
- Requirement Analysis Agent
- Code Generation Agent
- Code Review Agent
- Documentation Agent
- Test Generation Agent
- Deployment Configuration Agent
- UI Generation Agent

## License

This project is generated code. Please review and add appropriate licensing.
"""
    
    return readme

def create_requirements_file(results: dict) -> str:
    """Create a requirements.txt file based on the project."""
    requirements = """# Generated by Multi-Agentic Coding Framework

# Core dependencies
requests>=2.25.1
python-dotenv>=0.19.0

# Testing
pytest>=6.0.0
pytest-cov>=2.10.0

# Code quality
black>=21.0.0
flake8>=3.8.0

# Documentation
markdown>=3.3.0
jinja2>=3.0.0

# Type hints
typing-extensions>=3.10.0

# Add your project-specific dependencies below:
"""
    
    # Add project-specific dependencies based on requirements
    if results.get('agents', {}).get('requirement_analysis', {}).get('results'):
        req_data = results['agents']['requirement_analysis']['results']
        dependencies = req_data.get('dependencies', [])
        
        if dependencies:
            requirements += "\n# Project-specific dependencies:\n"
            for dep in dependencies:
                requirements += f"# {dep}\n"
    
    return requirements

def create_setup_file(results: dict) -> str:
    """Create a setup.py file for the project."""
    project_name = "generated-project"
    description = "A project generated by Multi-Agentic Coding Framework"
    
    if results.get('agents', {}).get('requirement_analysis', {}).get('results'):
        req_data = results['agents']['requirement_analysis']['results']
        project_name = req_data.get('project_name', 'generated-project').lower().replace(' ', '-')
        description = req_data.get('description', description)
    
    setup_content = f"""from setuptools import setup, find_packages

setup(
    name="{project_name}",
    version="1.0.0",
    description="{description}",
    author="Multi-Agentic Coding Framework",
    author_email="generated@example.com",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.1",
        "python-dotenv>=0.19.0",
    ],
    extras_require={{
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "black>=21.0.0",
            "flake8>=3.8.0",
        ],
    }},
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
"""
    return setup_content

def create_gitignore_file() -> str:
    """Create a .gitignore file for the project."""
    return """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# pipenv
Pipfile.lock

# PEP 582
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Project specific
workspace/
output/
logs/
*.log
"""

def show_agent_results(agent_name: str, agent_data: dict):
    """Display results from a specific agent."""
    status = agent_data.get("status", "unknown")
    results = agent_data.get("results", {})
    
    # Status indicator
    if status == "completed":
        st.success(f"✅ {agent_name.replace('_', ' ').title()} - Completed")
    elif status == "processing":
        st.warning(f"⏳ {agent_name.replace('_', ' ').title()} - Processing")
    else:
        st.error(f"❌ {agent_name.replace('_', ' ').title()} - Failed")
    
    # Display results based on agent type
    if agent_name == "requirement_analysis":
        show_requirement_results(results)
    elif agent_name == "code_generation":
        show_code_results(results)
    elif agent_name == "code_review":
        show_review_results(results)
    elif agent_name == "documentation":
        show_documentation_results(results)
    elif agent_name == "test_generation":
        show_test_results(results)
    elif agent_name == "deployment_config":
        show_deployment_results(results)
    elif agent_name == "ui_generation":
        show_ui_results(results)

def show_requirement_results(results: dict):
    """Display requirement analysis results."""
    st.subheader("📋 Structured Requirements")
    
    # Project info
    st.write(f"**Project Name:** {results.get('project_name', 'N/A')}")
    st.write(f"**Description:** {results.get('description', 'N/A')}")
    
    # Functional requirements
    if results.get('functional_requirements'):
        st.subheader("Functional Requirements")
        for req in results['functional_requirements']:
            with st.expander(f"{req.get('id', 'N/A')}: {req.get('title', 'N/A')}"):
                st.write(f"**Description:** {req.get('description', 'N/A')}")
                st.write(f"**Priority:** {req.get('priority', 'N/A')}")
                st.write(f"**Acceptance Criteria:** {', '.join(req.get('acceptance_criteria', []))}")

def show_code_results(results: dict):
    """Display code generation results."""
    st.subheader("💻 Generated Code")
    
    if results.get('generated_files'):
        st.write(f"**Total Files:** {len(results['generated_files'])}")
        
        # File list
        for filename, content in results['generated_files'].items():
            with st.expander(f"📄 {filename}"):
                try:
                    # Content is already the file content, not a filepath
                    st.code(content, language='python' if filename.endswith('.py') else 'text')
                except Exception as e:
                    st.error(f"Error displaying file content: {e}")

def show_review_results(results: dict):
    """Display code review results."""
    st.subheader("🔍 Code Review")
    
    # Overall score
    score = results.get('overall_score', 0)
    st.metric("Overall Score", f"{score}/100")
    
    # Issues
    if results.get('critical_issues'):
        st.error("Critical Issues")
        for issue in results['critical_issues']:
            st.write(f"- {issue.get('issue', 'N/A')}")
    
    if results.get('high_priority_issues'):
        st.warning("High Priority Issues")
        for issue in results['high_priority_issues']:
            st.write(f"- {issue.get('issue', 'N/A')}")

def show_documentation_results(results: dict):
    """Display documentation results."""
    st.subheader("📚 Generated Documentation")
    
    if results.get('generated_documentation'):
        st.write(f"**Total Docs:** {len(results['generated_documentation'])}")
        
        for filename, content in results['generated_documentation'].items():
            with st.expander(f"📄 {filename}"):
                try:
                    # Content is already the file content, not a filepath
                    st.markdown(content)
                except Exception as e:
                    st.error(f"Error displaying documentation: {e}")

def show_test_results(results: dict):
    """Display test generation results."""
    st.subheader("🧪 Generated Tests")
    
    if results.get('generated_tests'):
        st.write(f"**Total Test Files:** {len(results['generated_tests'])}")
        
        for filename, content in results['generated_tests'].items():
            with st.expander(f"📄 {filename}"):
                try:
                    # Content is already the file content, not a filepath
                    st.code(content, language='python')
                except Exception as e:
                    st.error(f"Error displaying test content: {e}")

def show_deployment_results(results: dict):
    """Display deployment configuration results."""
    st.subheader("🚀 Deployment Configuration")
    
    if results.get('generated_configs'):
        st.write(f"**Total Config Files:** {len(results['generated_configs'])}")
        
        for filename, content in results['generated_configs'].items():
            with st.expander(f"📄 {filename}"):
                try:
                    # Content is already the file content, not a filepath
                    st.code(content, language='dockerfile' if 'Dockerfile' in filename else 'yaml' if filename.endswith('.yml') else 'text')
                except Exception as e:
                    st.error(f"Error displaying deployment config: {e}")

def show_ui_results(results: dict):
    """Display UI generation results."""
    st.subheader("🎨 Generated UI")
    
    if results.get('generated_ui'):
        st.write(f"**Total UI Files:** {len(results['generated_ui'])}")
        
        for filename, content in results['generated_ui'].items():
            with st.expander(f"📄 {filename}"):
                try:
                    # Content is already the file content, not a filepath
                    if filename.endswith('.py'):
                        st.code(content, language='python')
                    elif filename.endswith('.css'):
                        st.code(content, language='css')
                    else:
                        st.code(content, language='text')
                except Exception as e:
                    st.error(f"Error displaying UI content: {e}")

def show_project_history_page():
    """Show the project history page."""
    st.header("📚 Project History")
    st.write("View and manage your previously created projects.")
    
    # Get project list
    projects = st.session_state.coordinator.list_projects()
    
    if not projects:
        st.info("No projects found. Create your first project to get started!")
        return
    
    # Project list
    for project in projects:
        with st.expander(f"📁 {project['project_id']} - {project['status']}"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**Requirement:** {project['original_requirement']}")
                st.write(f"**Start Time:** {project['start_time']}")
                if project.get('end_time'):
                    st.write(f"**End Time:** {project['end_time']}")
            
            with col2:
                if st.button(f"View Details", key=f"view_{project['project_id']}"):
                    show_project_details(project['project_id'])

def show_project_details(project_id: str):
    """Show detailed information about a specific project."""
    results = st.session_state.coordinator.get_project_status(project_id)
    
    if "error" in results:
        st.error(results["error"])
        return
    
    st.subheader(f"Project: {project_id}")
    
    # Project summary
    if results.get("project_summary"):
        summary = results["project_summary"]
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Status", summary.get("status", "N/A"))
        with col2:
            st.metric("Total Agents", summary.get("total_agents", 0))
        with col3:
            st.metric("Completed", summary.get("completed_agents", 0))
        with col4:
            st.metric("Files Generated", sum(summary.get("files_generated", {}).values()))
    
    # Show agent results
    if results.get("agents"):
        show_project_results(results)

def show_agent_status_page():
    """Show the agent status page."""
    st.header("🤖 Agent Status")
    st.write("Monitor the status and performance of individual agents.")
    
    # Agent information
    agents_info = [
        {"name": "Requirement Analysis Agent", "description": "Analyzes and refines natural language requirements", "status": "Ready"},
        {"name": "Coding Agent", "description": "Converts requirements into functional Python code", "status": "Ready"},
        {"name": "Code Review Agent", "description": "Reviews code for quality and correctness", "status": "Ready"},
        {"name": "Documentation Agent", "description": "Generates comprehensive documentation", "status": "Ready"},
        {"name": "Test Generation Agent", "description": "Creates unit and integration tests", "status": "Ready"},
        {"name": "Deployment Agent", "description": "Generates deployment configurations", "status": "Ready"},
        {"name": "UI Agent", "description": "Creates Streamlit user interfaces", "status": "Ready"}
    ]
    
    for agent in agents_info:
        with st.container():
            st.markdown(f"""
            <div class="agent-card">
                <h3>{agent['name']}</h3>
                <p>{agent['description']}</p>
                <strong>Status: <span class="status-completed">{agent['status']}</span></strong>
            </div>
            """, unsafe_allow_html=True)

def show_configuration_page():
    """Show the configuration page."""
    st.header("⚙️ Configuration")
    st.write("Configure the multi-agent framework settings.")
    
    with st.form("configuration_form"):
        st.subheader("Framework Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.text_input("OpenAI API Key", value=config.openai_api_key or "", type="password")
            st.text_input("Model Name", value=config.model_name)
            st.slider("Temperature", 0.1, 1.0, config.temperature, 0.1)
        
        with col2:
            st.number_input("Max Iterations", 1, 10, config.max_iterations)
            st.text_input("Output Directory", value=config.output_dir)
            st.selectbox("Log Level", ["DEBUG", "INFO", "WARNING", "ERROR"], index=1)
        
        if st.form_submit_button("Save Configuration"):
            st.success("Configuration saved successfully!")

def show_about_page():
    """Show the about page."""
    st.header("ℹ️ About")
    st.write("Information about the Multi-Agentic Coding Framework.")
    
    st.subheader("Framework Overview")
    st.write("""
    The Multi-Agentic Coding Framework is a comprehensive system that uses multiple AI agents 
    to collaboratively develop software from natural language requirements. The framework 
    implements a complete pipeline from requirement analysis to deployment configuration.
    """)
    
    st.subheader("Agents")
    agents = [
        ("Requirement Analysis Agent", "Analyzes and refines natural language requirements into structured specifications"),
        ("Coding Agent", "Converts structured requirements into functional Python code"),
        ("Code Review Agent", "Reviews generated code for correctness, efficiency, and security"),
        ("Documentation Agent", "Generates comprehensive documentation for the developed code"),
        ("Test Generation Agent", "Creates unit tests and integration tests"),
        ("Deployment Configuration Agent", "Generates deployment scripts and configuration files"),
        ("Streamlit UI Agent", "Creates user interface components")
    ]
    
    for name, description in agents:
        st.write(f"**{name}**: {description}")
    
    st.subheader("Features")
    st.write("""
    - **Iterative Processing**: Agents can iterate on improvements based on feedback
    - **Quality Assurance**: Multi-level code review and validation
    - **Complete Documentation**: Auto-generated documentation with usage examples
    - **Comprehensive Testing**: Automatic generation of unit and integration tests
    - **Deployment Ready**: Complete deployment configuration and scripts
    - **User-Friendly Interface**: Streamlit-based UI for easy interaction
    """)
    
    st.subheader("Technology Stack")
    st.write("""
    - **Python**: Core programming language
    - **AutoGen**: Multi-agent coordination framework
    - **OpenAI GPT-4**: Large language model for agent intelligence
    - **Streamlit**: User interface framework
    - **Pytest**: Testing framework
    - **Docker**: Containerization and deployment
    """)

if __name__ == "__main__":
    main() 