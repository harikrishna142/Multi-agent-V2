"""
Streamlit UI Agent for the Multi-Agentic Coding Framework.
Creates Streamlit-based user interfaces for the developed applications.
"""

import autogen
import re
from typing import Dict, Any, List
from core.config import get_agent_config, config
from core.utils import save_to_file, setup_logging, load_from_file

logger = setup_logging()

class StreamlitUIAgent:
    """Agent responsible for creating Streamlit user interfaces."""
    
    def __init__(self):
        self.agent_config = get_agent_config("ui_agent")
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
    
    def generate_ui(self, generated_code: Dict[str, Any], requirements: Dict[str, Any], project_id: str) -> Dict[str, Any]:
        """
        Generate Streamlit UI for the developed code.
        
        Args:
            generated_code: Output from CodingAgent containing generated files
            requirements: Original requirements for context
            project_id: Unique project identifier
            
        Returns:
            Dict containing generated UI files
        """
        logger.info("Starting Streamlit UI generation")
        
        # Load the actual code content
        code_files = {}
        for filename, filepath in generated_code.get("generated_files", {}).items():
            try:
                code_files[filename] = load_from_file(filepath)
            except Exception as e:
                logger.warning(f"Could not load file {filename}: {e}")
                code_files[filename] = f"# Error loading file: {e}"
        
        # Create the UI generation prompt
        ui_prompt = f"""
Please generate a comprehensive Streamlit user interface for the following Python project:

PROJECT REQUIREMENTS:
{self._format_requirements_for_ui(requirements)}

GENERATED CODE FILES:
{self._format_code_for_ui(code_files)}

Please generate the following UI components:

1. **Main Streamlit App** (`app.py`):
   - Main application interface
   - Navigation and layout
   - Integration with backend functionality
   - User input forms and validation

2. **UI Components** (`components/`):
   - Reusable UI components
   - Custom widgets and forms
   - Data visualization components
   - Interactive elements

3. **Pages** (`pages/`):
   - Multiple page navigation
   - Feature-specific pages
   - Settings and configuration pages
   - Help and documentation pages

4. **Styling** (`style.css`, `theme.toml`):
   - Custom CSS styling
   - Streamlit theme configuration
   - Responsive design
   - Branding and colors

5. **Configuration** (`config.toml`):
   - Streamlit configuration
   - Page settings
   - Server configuration

For each file, provide:
- Clean and intuitive user interface
- Proper form validation and error handling
- Responsive design for different screen sizes
- Accessibility features
- Clear user feedback and messaging
- Integration with the backend functionality

UI Requirements:
- Modern and professional design
- Intuitive navigation
- Clear visual hierarchy
- Consistent styling
- Mobile-friendly layout
- Fast loading and responsive

Please provide each file in the following format:

```python
# filename: app.py
[complete Streamlit app code here]
```

```css
# filename: style.css
[complete CSS styling here]
```

And so on for each file.

IMPORTANT: End your response with the word "TERMINATE" to indicate completion.
"""
        
        try:
            # Start the conversation
            chat_result = self.user_proxy.initiate_chat(
                self.agent,
                message=ui_prompt
            )
            
            # Extract the LLM response using utility function
            from core.utils import extract_llm_response
            last_message = extract_llm_response(chat_result)
            
            # Parse and organize the generated UI components
            generated_ui = self._parse_generated_ui(last_message)
            
            # Validate and enhance the UI components
            validated_ui = self._validate_and_enhance_ui(generated_ui, requirements)
            
            # Save the generated UI components
            saved_ui = self._save_generated_ui(validated_ui, project_id)
            
            result = {
                "project_id": project_id,
                "generated_ui": saved_ui,
                "total_ui_files": len(saved_ui),
                "ui_summary": self._generate_ui_summary(saved_ui)
            }
            
            logger.info(f"Streamlit UI generation completed. Generated {len(saved_ui)} UI files.")
            return result
            
        except Exception as e:
            logger.error(f"Error in Streamlit UI generation: {e}")
            # Generate fallback UI
            fallback_ui = self._generate_fallback_ui(requirements, code_files, project_id)
            return {
                "project_id": project_id,
                "generated_ui": fallback_ui,
                "total_ui_files": len(fallback_ui),
                "ui_summary": "Fallback UI generated due to error",
                "error": str(e)
            }
    
    def _format_requirements_for_ui(self, requirements: Dict[str, Any]) -> str:
        """Format requirements for UI generation context."""
        formatted = f"""
Project: {requirements.get('project_name', 'N/A')}
Description: {requirements.get('description', 'N/A')}

UI Requirements:
"""
        
        for req in requirements.get('functional_requirements', []):
            formatted += f"""
- {req.get('id', 'N/A')}: {req.get('title', 'N/A')}
  Description: {req.get('description', 'N/A')}
  UI Component: Create interface for {req.get('description', 'N/A')}
"""
        
        formatted += f"""
Non-Functional Requirements:
"""
        
        for req in requirements.get('non_functional_requirements', []):
            formatted += f"""
- {req.get('id', 'N/A')}: {req.get('title', 'N/A')}
  Category: {req.get('category', 'N/A')}
  Description: {req.get('description', 'N/A')}
  UI Consideration: Ensure {req.get('category', 'N/A')} requirements are met in the interface
"""
        
        return formatted
    
    def _format_code_for_ui(self, code_files: Dict[str, str]) -> str:
        """Format code files for UI generation."""
        formatted = ""
        
        for filename, content in code_files.items():
            formatted += f"""
=== FILE: {filename} ===
{content}
=== END FILE: {filename} ===

"""
        
        return formatted
    
    def _parse_generated_ui(self, response: str) -> Dict[str, str]:
        """Parse the generated UI response and extract individual files."""
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
            # Fallback: create basic UI structure
            files = self._create_basic_ui_structure(response)
        
        return files
    
    def _create_basic_ui_structure(self, response: str) -> Dict[str, str]:
        """Create basic UI structure when parsing fails."""
        return {
            "app.py": '''import streamlit as st
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Page configuration
st.set_page_config(
    page_title="Generated Application",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.main-header {{
    font-size: 2.5rem;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
}}
.sidebar-header {{
    font-size: 1.5rem;
    color: #2c3e50;
    margin-bottom: 1rem;
}}
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">🚀 Generated Application</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown('<h2 class="sidebar-header">Navigation</h2>', unsafe_allow_html=True)
        page = st.selectbox(
            "Choose a page:",
            ["Home", "Features", "Settings", "About"]
        )
    
    # Main content
    if page == "Home":
        show_home_page()
    elif page == "Features":
        show_features_page()
    elif page == "Settings":
        show_settings_page()
    elif page == "About":
        show_about_page()

def show_home_page():
    st.header("🏠 Welcome")
    st.write("This is a generated application based on your requirements.")
    
    # Main functionality
    st.subheader("Main Functionality")
    
    # Example form
    with st.form("main_form"):
        user_input = st.text_input("Enter your input:")
        submit_button = st.form_submit_button("Submit")
        
        if submit_button:
            if user_input:
                st.success(f"Processed: {user_input}")
            else:
                st.error("Please enter some input.")

def show_features_page():
    st.header("✨ Features")
    st.write("This page showcases the main features of the application.")
    
    # Feature cards
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("Feature 1")
        st.write("Description of feature 1")
    
    with col2:
        st.info("Feature 2")
        st.write("Description of feature 2")

def show_settings_page():
    st.header("⚙️ Settings")
    st.write("Configure your application settings.")
    
    # Settings form
    with st.form("settings_form"):
        st.subheader("Application Settings")
        
        debug_mode = st.checkbox("Enable Debug Mode")
        log_level = st.selectbox("Log Level", ["INFO", "DEBUG", "WARNING", "ERROR"])
        
        if st.form_submit_button("Save Settings"):
            st.success("Settings saved successfully!")

def show_about_page():
    st.header("ℹ️ About")
    st.write("Information about the application and its development.")
    
    st.subheader("Project Information")
    st.write("- Generated using Multi-Agentic Coding Framework")
    st.write("- Built with Streamlit")
    st.write("- Python-based application")

if __name__ == "__main__":
    main()
''',
            "style.css": """/* Custom CSS for Streamlit App */

/* Main header styling */
.main-header {
    font-size: 2.5rem;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
    font-weight: bold;
}

/* Sidebar header styling */
.sidebar-header {
    font-size: 1.5rem;
    color: #2c3e50;
    margin-bottom: 1rem;
    font-weight: 600;
}

/* Button styling */
.stButton > button {
    border-radius: 20px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* Form styling */
.stForm {
    background-color: #f8f9fa;
    padding: 2rem;
    border-radius: 10px;
    border: 1px solid #dee2e6;
}

/* Success message styling */
.stSuccess {
    background-color: #d4edda;
    border: 1px solid #c3e6cb;
    color: #155724;
    padding: 1rem;
    border-radius: 5px;
    margin: 1rem 0;
}

/* Error message styling */
.stError {
    background-color: #f8d7da;
    border: 1px solid #f5c6cb;
    color: #721c24;
    padding: 1rem;
    border-radius: 5px;
    margin: 1rem 0;
}

/* Info message styling */
.stInfo {
    background-color: #d1ecf1;
    border: 1px solid #bee5eb;
    color: #0c5460;
    padding: 1rem;
    border-radius: 5px;
    margin: 1rem 0;
}
""",
            "config.toml": """[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[server]
headless = true
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false

[client]
showErrorDetails = true
"""
        }
    
    def _validate_and_enhance_ui(self, ui_components: Dict[str, str], requirements: Dict[str, Any]) -> Dict[str, str]:
        """Validate and enhance the generated UI components."""
        enhanced_ui = {}
        
        for filename, content in ui_components.items():
            # Enhance the UI based on requirements
            enhanced_content = self._enhance_ui_component(content, filename, requirements)
            enhanced_ui[filename] = enhanced_content
        
        return enhanced_ui
    
    def _enhance_ui_component(self, content: str, filename: str, requirements: Dict[str, Any]) -> str:
        """Enhance UI component with additional features."""
        enhanced = content
        
        # Add responsive design if it's a CSS file
        if filename.endswith('.css'):
            enhanced += """

/* Responsive design */
@media (max-width: 768px) {
    .main-header {
        font-size: 2rem;
    }
    
    .sidebar-header {
        font-size: 1.2rem;
    }
    
    .stCard {
        margin: 0.5rem 0;
    }
}

/* Accessibility improvements */
.stButton > button:focus {
    outline: 2px solid #1f77b4;
    outline-offset: 2px;
}

.stTextInput > div > div > input:focus {
    border-color: #1f77b4;
    box-shadow: 0 0 0 2px rgba(31, 119, 180, 0.2);
}
"""
        
        # Add error handling if it's a Python file
        if filename.endswith('.py'):
            enhanced += """

# Error handling
def handle_error(error):
    st.error(f"An error occurred: {error}")
    st.info("Please try again or contact support if the problem persists.")

# Input validation
def validate_input(input_value, field_name):
    if not input_value or input_value.strip() == "":
        st.error(f"{field_name} cannot be empty")
        return False
    return True
"""
        
        return enhanced
    
    def _save_generated_ui(self, ui_components: Dict[str, str], project_id: str) -> Dict[str, str]:
        """Save generated UI components to files and return content."""
        saved_ui = {}
        
        for filename, content in ui_components.items():
            # Create project-specific UI directory
            project_dir = f"{config.output_dir}/{project_id}/ui"
            filepath = save_to_file(content, filename, project_dir)
            # Return the content, not the filepath, for frontend display
            saved_ui[filename] = content
        
        return saved_ui
    
    def _generate_ui_summary(self, saved_ui: Dict[str, str]) -> str:
        """Generate a summary of the created UI components."""
        summary = f"""
# Streamlit UI Summary

Generated {len(saved_ui)} UI files:

"""
        
        for filename, filepath in saved_ui.items():
            summary += f"- **{filename}**: {filepath}\n"
        
        summary += f"""
## UI Components Available

### Main Application
- `app.py`: Main Streamlit application with navigation and core functionality

### Styling and Configuration
- `style.css`: Custom CSS styling for the application
- `config.toml`: Streamlit configuration and theme settings

## Features Included

### Navigation
- Multi-page navigation with sidebar
- Responsive design for different screen sizes
- Clean and intuitive user interface

### Forms and Input
- User input forms with validation
- Error handling and user feedback
- Success and error message display

### Styling
- Modern and professional design
- Consistent color scheme and typography
- Mobile-friendly responsive layout

## How to Run

1. Navigate to the UI directory:
   ```bash
   cd {config.output_dir}/[project_id]/ui
   ```

2. Install Streamlit:
   ```bash
   pip install streamlit
   ```

3. Run the application:
   ```bash
   streamlit run app.py
   ```

4. Open your browser and navigate to `http://localhost:8501`

## Customization

- Update `style.css` for custom styling
- Modify `config.toml` for theme changes
- Add new pages and features to `app.py`
- Integrate with backend functionality as needed

## Next Steps

1. Review and customize the UI components
2. Add project-specific functionality
3. Integrate with the backend code
4. Test on different devices and screen sizes
5. Add more interactive features as needed
"""
        
        return summary
    
    def _generate_fallback_ui(self, requirements: Dict[str, Any], code_files: Dict[str, str], project_id: str) -> Dict[str, str]:
        """Generate basic fallback UI when the main generation fails."""
        project_name = requirements.get('project_name', 'GeneratedProject').replace(' ', '_')
        
        app_py = """import streamlit as st
import sys
import os
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Page configuration
st.set_page_config(
    page_title="Generated Application",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown(\"\"\"
<style>
.main-header {
    font-size: 2.5rem;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
    font-weight: bold;
}
.sidebar-header {
    font-size: 1.5rem;
    color: #2c3e50;
    margin-bottom: 1rem;
    font-weight: 600;
}
.feature-card {
    background-color: #f8f9fa;
    padding: 1.5rem;
    border-radius: 10px;
    border: 1px solid #dee2e6;
    margin: 1rem 0;
}
</style>
\"\"\", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">🚀 Generated Application</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown('<h2 class="sidebar-header">Navigation</h2>', unsafe_allow_html=True)
        page = st.selectbox(
            "Choose a page:",
            ["Dashboard", "Features", "Configuration", "Documentation", "About"]
        )
        
        st.markdown("---")
        st.markdown("**Project Info**")
        st.write("Project: Generated Application")
        st.write("Generated: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    # Main content
    if page == "Dashboard":
        show_dashboard()
    elif page == "Features":
        show_features()
    elif page == "Configuration":
        show_configuration()
    elif page == "Documentation":
        show_documentation()
    elif page == "About":
        show_about()

def show_dashboard():
    st.header("📊 Dashboard")
    st.write("Welcome to the main dashboard of your generated application.")
    
    # Main functionality section
    st.subheader("Main Functionality")
    
    # Example form
    with st.form("main_functionality"):
        st.write("**Input Form**")
        user_input = st.text_input("Enter your input:", placeholder="Type something here...")
        option = st.selectbox("Select an option:", ["Option 1", "Option 2", "Option 3"])
        number_input = st.number_input("Enter a number:", min_value=0, max_value=100, value=50)
        
        col1, col2 = st.columns(2)
        with col1:
            checkbox = st.checkbox("Enable feature")
        with col2:
            radio = st.radio("Choose:", ["A", "B", "C"])
        
        submit_button = st.form_submit_button("Process Input")
        
        if submit_button:
            if user_input:
                st.success("✅ Processed successfully!")
                st.info("Input: " + user_input + " | Option: " + option + " | Number: " + str(number_input))
            else:
                st.error("❌ Please enter some input.")
    
    # Statistics
    st.subheader("Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Users", "1,234", "+12%")
    with col2:
        st.metric("Active Sessions", "567", "+5%")
    with col3:
        st.metric("Success Rate", "98.5%", "+2.1%")
    with col4:
        st.metric("Response Time", "0.2s", "-0.1s")

def show_features():
    st.header("✨ Features")
    st.write("Explore the features of your generated application.")
    
    # Feature cards
    features = [
        {
            "title": "Feature 1",
            "description": "Description of the first feature",
            "icon": "🔧",
            "status": "Active"
        },
        {
            "title": "Feature 2", 
            "description": "Description of the second feature",
            "icon": "⚡",
            "status": "Active"
        },
        {
            "title": "Feature 3",
            "description": "Description of the third feature", 
            "icon": "🎯",
            "status": "Coming Soon"
        }
    ]
    
    for feature in features:
        with st.container():
            st.markdown(\"\"\"
            <div class="feature-card">
                <h3>\"\"\" + feature["icon"] + \" \" + feature["title"] + \"</h3>
                <p>\"\"\" + feature["description"] + \"</p>
                <strong>Status: \"\"\" + feature["status"] + \"</strong>
            </div>
            \"\"\", unsafe_allow_html=True)

def show_configuration():
    st.header("⚙️ Configuration")
    st.write("Configure your application settings.")
    
    # Settings form
    with st.form("settings"):
        st.subheader("Application Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            debug_mode = st.checkbox("Enable Debug Mode")
            log_level = st.selectbox("Log Level", ["INFO", "DEBUG", "WARNING", "ERROR"])
            max_connections = st.number_input("Max Connections", min_value=1, max_value=1000, value=100)
        
        with col2:
            auto_save = st.checkbox("Auto Save", value=True)
            notifications = st.checkbox("Enable Notifications", value=True)
            theme = st.selectbox("Theme", ["Light", "Dark", "Auto"])
        
        st.subheader("Advanced Settings")
        api_key = st.text_input("API Key", type="password")
        timeout = st.slider("Timeout (seconds)", min_value=1, max_value=60, value=30)
        
        if st.form_submit_button("Save Configuration"):
            st.success("✅ Configuration saved successfully!")

def show_documentation():
    st.header("📚 Documentation")
    st.write("Documentation and help for your application.")
    
    # Documentation sections
    with st.expander("Getting Started", expanded=True):
        st.write(\"\"\"
        ## Quick Start Guide
        
        1. **Installation**: Ensure all dependencies are installed
        2. **Configuration**: Set up your configuration in the Settings page
        3. **Usage**: Use the Dashboard to interact with the application
        4. **Support**: Check the About page for more information
        \"\"\")
    
    with st.expander("API Reference"):
        st.write(\"\"\"
        ## API Endpoints
        
        - `GET /health` - Health check endpoint
        - `POST /process` - Process input data
        - `GET /status` - Get application status
        \"\"\")
    
    with st.expander("Troubleshooting"):
        st.write(\"\"\"
        ## Common Issues
        
        - **Connection errors**: Check your network connection
        - **Configuration issues**: Verify settings in the Configuration page
        - **Performance problems**: Check system resources
        \"\"\")

def show_about():
    st.header("ℹ️ About")
    st.write("Information about the application and its development.")
    
    # Project information
    st.subheader("Project Information")
    st.write(\"\"\"
    - **Project Name**: Generated Application
    - **Description**: A generated application
    - **Generated**: \"\"\" + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + \"\"\"
    - **Framework**: Multi-Agentic Coding Framework
    - **UI Framework**: Streamlit
    - **Language**: Python
    \"\"\")
    
    # Technical details
    st.subheader("Technical Details")
    st.write(\"\"\"
    This application was generated automatically using the Multi-Agentic Coding Framework.
    The framework uses multiple AI agents to analyze requirements, generate code, review quality,
    create documentation, generate tests, and create user interfaces.
    \"\"\")
    
    # Contact information
    st.subheader("Support")
    st.write(\"\"\"
    For support and questions:
    - Check the Documentation page
    - Review the generated code
    - Contact the development team
    \"\"\")

if __name__ == "__main__":
    main()
"""
        
        style_css = """/* Custom CSS for Generated Application */

/* Main header styling */
.main-header {
    font-size: 2.5rem;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
    font-weight: bold;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
}

/* Sidebar header styling */
.sidebar-header {
    font-size: 1.5rem;
    color: #2c3e50;
    margin-bottom: 1rem;
    font-weight: 600;
}

/* Feature card styling */
.feature-card {
    background-color: #f8f9fa;
    padding: 1.5rem;
    border-radius: 10px;
    border: 1px solid #dee2e6;
    margin: 1rem 0;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s ease-in-out;
}

.feature-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

/* Button styling */
.stButton > button {
    border-radius: 20px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

/* Form styling */
.stForm {
    background-color: #f8f9fa;
    padding: 2rem;
    border-radius: 10px;
    border: 1px solid #dee2e6;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* Success message styling */
.stSuccess {
    background-color: #d4edda;
    border: 1px solid #c3e6cb;
    color: #155724;
    padding: 1rem;
    border-radius: 5px;
    margin: 1rem 0;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* Error message styling */
.stError {
    background-color: #f8d7da;
    border: 1px solid #f5c6cb;
    color: #721c24;
    padding: 1rem;
    border-radius: 5px;
    margin: 1rem 0;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* Info message styling */
.stInfo {
    background-color: #d1ecf1;
    border: 1px solid #bee5eb;
    color: #0c5460;
    padding: 1rem;
    border-radius: 5px;
    margin: 1rem 0;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* Responsive design */
@media (max-width: 768px) {
    .main-header {
        font-size: 2rem;
    }
    
    .sidebar-header {
        font-size: 1.2rem;
    }
    
    .feature-card {
        margin: 0.5rem 0;
        padding: 1rem;
    }
}

/* Accessibility improvements */
.stButton > button:focus {
    outline: 2px solid #1f77b4;
    outline-offset: 2px;
}

.stTextInput > div > div > input:focus {
    border-color: #1f77b4;
    box-shadow: 0 0 0 2px rgba(31, 119, 180, 0.2);
}

/* Animation for loading states */
@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
}

.loading {
    animation: pulse 2s infinite;
}
"""
        
        config_toml = """[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[server]
headless = true
enableCORS = false
enableXsrfProtection = true
maxUploadSize = 200

[browser]
gatherUsageStats = false

[client]
showErrorDetails = true
"""
        
        return {
            "app.py": app_py,
            "style.css": style_css,
            "config.toml": config_toml
        } 