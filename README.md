# 🤖 Multi-Agentic Coding Framework

A comprehensive AI-powered software development framework that uses multiple specialized agents to collaboratively generate complete software projects from natural language requirements.

## 🚀 Features

- **7 Specialized AI Agents**: Each agent has a specific role in the software development pipeline
- **End-to-End Project Generation**: From requirements analysis to deployment configuration
- **Interactive Web Interface**: Streamlit-based UI for easy project creation and management
- **Complete Project Structure**: Generates source code, documentation, tests, deployment configs, and UI
- **Download Functionality**: Export complete projects as ZIP files with proper directory structure
- **Real-time Progress Tracking**: Monitor agent progress and view results in real-time

## 🏗️ Architecture

### Agent Pipeline

1. **📋 Requirement Analysis Agent**: Transforms natural language into structured requirements
2. **💻 Coding Agent**: Generates functional Python code from structured requirements
3. **🔍 Code Review Agent**: Reviews code for quality, security, and best practices
4. **📚 Documentation Agent**: Creates comprehensive documentation
5. **🧪 Test Generation Agent**: Generates unit and integration tests
6. **🚀 Deployment Agent**: Creates deployment configurations (Docker, scripts)
7. **🎨 UI Agent**: Generates Streamlit user interfaces

### Technology Stack

- **Backend**: Python 3.8+
- **AI Framework**: AutoGen (Microsoft)
- **Web Interface**: Streamlit
- **LLM Integration**: OpenAI GPT-4 (configurable)
- **Code Quality**: Black, Flake8, Pytest
- **Documentation**: Markdown, Jinja2 templates
- **Deployment**: Docker, Docker Compose

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Git

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/multi-agentic-coding-framework.git
   cd multi-agentic-coding-framework
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:8501`

### Manual Installation

If you prefer manual setup:

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install core dependencies
pip install pyautogen openai streamlit pytest pytest-cov python-dotenv markdown jinja2 requests typing-extensions black flake8

# Set up environment
export OPENAI_API_KEY="your-api-key-here"
```

## 🎯 Usage

### Creating a New Project

1. **Navigate to "New Project"** in the sidebar
2. **Enter your requirements** in natural language (e.g., "Create a calculator app that can perform basic arithmetic operations")
3. **Click "Generate Project"** to start the multi-agent pipeline
4. **Monitor progress** as each agent completes its task
5. **Review results** for each agent in the tabs
6. **Download the complete project** as a ZIP file

### Example Requirements

```
Create a task management application with the following features:
- Add, edit, and delete tasks
- Mark tasks as complete
- Set task priorities (high, medium, low)
- Filter tasks by status and priority
- Store tasks in a JSON file
- Provide a simple command-line interface
```

### Project Structure

Generated projects include:

```
project_name/
├── src/                    # Source code files
│   ├── main.py
│   └── modules/
├── tests/                  # Test files
│   └── test_*.py
├── docs/                   # Documentation
│   ├── README.md
│   ├── API_DOCUMENTATION.md
│   └── USER_GUIDE.md
├── deployment/             # Deployment configs
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── deploy.sh
├── ui/                     # Streamlit UI
│   ├── app.py
│   └── style.css
├── requirements.txt        # Python dependencies
├── setup.py               # Package configuration
├── .gitignore             # Git ignore file
└── README.md              # Project documentation
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
OPENAI_API_KEY=your-openai-api-key
OPENAI_API_BASE=https://api.openai.com/v1
MAX_ITERATIONS=10
TEMPERATURE=0.7
MODEL_NAME=gpt-4
OUTPUT_DIR=./output
LOG_LEVEL=INFO
```

### Agent Configuration

Each agent can be configured in `core/config.py`:

- System messages
- Temperature settings
- Model preferences
- Output formatting

## 🧪 Testing

### Run Basic Tests

```bash
python test_basic.py
```

### Test Individual Agents

```bash
# Test requirement analysis agent
python test_requirement_agent.py

# Test coding agent
python test_coding_agent.py

# Test all agents
python test_all_agents.py
```

### Run Framework Tests

```bash
pytest tests/
```

## 📚 Documentation

- **[Interview Guide](INTERVIEW_GUIDE.md)**: Comprehensive technical documentation
- **[Setup Guide](SETUP_GUIDE.md)**: Detailed setup instructions
- **[Project Summary](PROJECT_SUMMARY.md)**: Technical architecture overview

## 🔧 Development

### Project Structure

```
multi-agentic-coding-framework/
├── agents/                 # Agent implementations
│   ├── requirement_agent.py
│   ├── coding_agent.py
│   ├── review_agent.py
│   ├── documentation_agent.py
│   ├── test_agent.py
│   ├── deployment_agent.py
│   └── ui_agent.py
├── core/                   # Core framework
│   ├── config.py          # Configuration management
│   ├── coordinator.py     # Agent orchestration
│   ├── utils.py           # Utility functions
│   └── validation.py      # Data validation
├── templates/              # Documentation templates
├── examples/               # Example projects
├── tests/                  # Test files
├── app.py                  # Streamlit web interface
├── requirements.txt        # Dependencies
└── README.md              # This file
```

### Adding New Agents

1. Create a new agent file in `agents/`
2. Implement the required interface
3. Add configuration in `core/config.py`
4. Update the coordinator in `core/coordinator.py`
5. Add tests in `tests/`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add tests for new features
- Update documentation
- Use meaningful commit messages

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Microsoft AutoGen**: Multi-agent conversation framework
- **OpenAI**: Large language model API
- **Streamlit**: Web application framework
- **Python Community**: Open-source libraries and tools

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/multi-agentic-coding-framework/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/multi-agentic-coding-framework/discussions)
- **Documentation**: [Wiki](https://github.com/yourusername/multi-agentic-coding-framework/wiki)

## 🚀 Roadmap

- [ ] Support for multiple LLM providers
- [ ] Custom agent templates
- [ ] CI/CD integration
- [ ] Cloud deployment options
- [ ] Multi-language support
- [ ] Advanced code analysis
- [ ] Performance optimization
- [ ] Enterprise features

---

**Made with ❤️ by the Multi-Agentic Coding Framework Team** 