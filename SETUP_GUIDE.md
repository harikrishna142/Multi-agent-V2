# 🚀 Enhanced Multi-Agentic Framework v2.0 - Setup Guide

Complete setup guide for the enhanced multi-agentic coding framework with production-ready application generation.

## 📋 Prerequisites

### System Requirements
- **Python**: 3.11 or higher
- **Node.js**: 18.0 or higher (for generated frontend applications)
- **Docker**: 24.0 or higher (for deployment)
- **Git**: Latest version
- **Memory**: 8GB RAM minimum (16GB recommended)
- **Storage**: 10GB free space

### Required Accounts
- **OpenAI API Key**: [Get your API key here](https://platform.openai.com/api-keys)
- **GitHub Account**: For CI/CD and version control
- **Cloud Provider Account**: AWS, Azure, or GCP (optional, for deployment)

## 🛠️ Installation Steps

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone <repository-url>
cd multi-agentic-framework

# Verify the structure
ls -la
```

Expected structure:
```
multi-agentic-framework/
├── agents/           # Enhanced AI agents
├── core/            # Core framework components
├── examples/        # Example demonstrations
├── output/          # Generated projects
├── tests/           # Framework tests
├── app.py           # Streamlit web interface
├── main.py          # Command line interface
├── requirements.txt # Python dependencies
└── README.md        # Project documentation
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Verify activation
which python  # Should point to venv/bin/python
```

### Step 3: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt

# Verify installation
python -c "import streamlit, autogen, openai; print('Dependencies installed successfully!')"
```

### Step 4: Configure Environment

```bash
# Copy environment template
cp env_example.txt .env

# Edit .env file with your configuration
nano .env  # or use your preferred editor
```

Required `.env` configuration:
```env
# OpenAI Configuration (Required)
OPENAI_API_KEY=your_openai_api_key_here

# Framework Configuration
OUTPUT_DIR=./output
LOG_LEVEL=INFO
MAX_ITERATIONS=3
TEMPERATURE=0.7
MODEL=gpt-4

# Optional: Database Configuration (for generated apps)
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
REDIS_URL=redis://localhost:6379

# Optional: Security Configuration
SECRET_KEY=your-secret-key-here
```

### Step 5: Verify Installation

```bash
# Test the framework
python -m pytest tests/ -v

# Test individual components
python test_agents.py
python test_basic.py

# Check framework capabilities
python -c "
from core.orchestrator import EnhancedOrchestrator
orchestrator = EnhancedOrchestrator()
capabilities = orchestrator.get_framework_capabilities()
print(f'Framework: {capabilities[\"framework_name\"]} v{capabilities[\"version\"]}')
print(f'Description: {capabilities[\"description\"]}')
"
```

## 🚀 Running the Framework

### Option A: Streamlit Web Interface (Recommended)

```bash
# Start the Streamlit interface
streamlit run app.py

# Access the interface
open http://localhost:8501
```

**Features of the Web Interface:**
- 🎯 **New Project**: Create complete applications from natural language
- 📚 **Project History**: View and download previous projects
- 🤖 **Agent Status**: Monitor agent capabilities and status
- 🚀 **Framework Capabilities**: View enhanced features and supported technologies
- ⚙️ **Configuration**: Manage framework settings
- ℹ️ **About**: Learn about the enhanced framework

### Option B: Command Line Interface

```bash
# Run the command line interface
python main.py

# Follow the prompts to create a project
```

### Option C: Direct API Usage

```python
from core.orchestrator import EnhancedOrchestrator

# Initialize the orchestrator
orchestrator = EnhancedOrchestrator()

# Generate a complete application
requirement = """
Create a complete e-commerce platform with user authentication, 
product catalog, shopping cart, payment processing, and order management. 
Include admin panel for product and order management.
"""

result = orchestrator.generate_complete_application(requirement)
print(f"Generated {result['total_files']} files")
print(f"Project ID: {result['project_id']}")
```

## 🧪 Testing the Framework

### Run All Tests

```bash
# Run complete test suite
python -m pytest tests/ -v --tb=short

# Run with coverage
python -m pytest tests/ --cov=core --cov=agents --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Test Individual Components

```bash
# Test requirement analysis
python test_requirement_agent.py

# Test code generation
python test_coding_agent.py

# Test all agents
python test_all_agents.py

# Test validation
python test_validation.py
```

### Test Generated Applications

```bash
# Navigate to a generated project
cd output/project_id/

# Test backend
cd backend
pytest

# Test frontend
cd ../frontend
npm install
npm test

# Test deployment
docker-compose up --build
```

## 📊 Framework Capabilities

### Enhanced Agents

1. **Enhanced Requirement Agent**
   - Detailed technical specifications
   - Exact technology versions
   - Complete database schema
   - API specifications

2. **Enhanced Coding Agent**
   - Complete application generation
   - No skeleton code
   - Full business logic
   - Production-ready code

3. **Enhanced Test Agent**
   - 90%+ test coverage
   - Unit, integration, e2e tests
   - Performance and security tests

4. **Enhanced Deployment Agent**
   - Docker and Kubernetes configs
   - CI/CD pipelines
   - Monitoring setup

5. **Enhanced Documentation Agent**
   - Professional documentation
   - API docs and user guides
   - Deployment guides

6. **Enhanced Review Agent**
   - Security analysis
   - Quality assessment
   - Performance optimization

### Supported Technologies

**Backend:**
- FastAPI, Django, Flask, Express.js, Spring Boot

**Frontend:**
- React, Vue.js, Angular, Next.js, Nuxt.js

**Database:**
- PostgreSQL, MySQL, MongoDB, Redis

**Deployment:**
- Docker, Kubernetes, AWS, Azure, GCP

**Testing:**
- pytest, Jest, Cypress, Playwright

## 🎯 Example Usage

### 1. E-commerce Platform

```python
requirement = """
Create a complete e-commerce platform with:
- User authentication and registration
- Product catalog with categories
- Shopping cart functionality
- Payment processing integration
- Order management system
- Admin panel for products and orders
- Email notifications
- Search and filtering
"""

result = orchestrator.generate_complete_application(requirement)
```

**Expected Output:**
- 50+ generated files
- Complete FastAPI backend
- React frontend with Redux
- PostgreSQL database with migrations
- JWT authentication
- Payment integration
- Admin dashboard
- Comprehensive testing
- Docker deployment

### 2. Project Management Application

```python
requirement = """
Build a comprehensive project management application with:
- User registration and team management
- Task creation and assignment
- File sharing and collaboration
- Real-time notifications
- Progress tracking and reporting
- Calendar integration
- Mobile responsive design
"""

result = orchestrator.generate_complete_application(requirement)
```

## 🔧 Configuration Options

### Advanced Configuration

```python
# In core/config.py
config = {
    "max_iterations": 3,        # Code review iterations
    "temperature": 0.7,         # AI creativity level
    "model": "gpt-4",          # OpenAI model
    "output_dir": "./output",   # Output directory
    "log_level": "INFO",       # Logging level
    "timeout": 300,            # Request timeout
    "max_tokens": 4000,        # Max tokens per request
}
```

### Environment Variables

```env
# Framework Configuration
OUTPUT_DIR=./output
LOG_LEVEL=INFO
MAX_ITERATIONS=3
TEMPERATURE=0.7
MODEL=gpt-4
TIMEOUT=300
MAX_TOKENS=4000

# OpenAI Configuration
OPENAI_API_KEY=your_api_key_here
OPENAI_ORG_ID=your_org_id_here

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
REDIS_URL=redis://localhost:6379

# Security Configuration
SECRET_KEY=your-secret-key-here
DEBUG=False
```

## 🚀 Deployment

### Local Development

```bash
# Start development server
streamlit run app.py --server.port 8501 --server.address 0.0.0.0

# Access from other devices
open http://your-ip:8501
```

### Production Deployment

```bash
# Build Docker image
docker build -t multi-agentic-framework .

# Run with Docker
docker run -d -p 8501:8501 \
  -e OPENAI_API_KEY=your_api_key \
  -v $(pwd)/output:/app/output \
  multi-agentic-framework

# Or use Docker Compose
docker-compose up -d
```

### Cloud Deployment

```bash
# Deploy to AWS
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin your-account.dkr.ecr.us-east-1.amazonaws.com
docker tag multi-agentic-framework:latest your-account.dkr.ecr.us-east-1.amazonaws.com/multi-agentic-framework:latest
docker push your-account.dkr.ecr.us-east-1.amazonaws.com/multi-agentic-framework:latest

# Deploy to Google Cloud
gcloud auth configure-docker
docker tag multi-agentic-framework:latest gcr.io/your-project/multi-agentic-framework:latest
docker push gcr.io/your-project/multi-agentic-framework:latest
```

## 🔍 Troubleshooting

### Common Issues

**1. OpenAI API Key Error**
```bash
# Check API key configuration
echo $OPENAI_API_KEY

# Test API connection
python -c "
import openai
openai.api_key = 'your_api_key'
try:
    response = openai.ChatCompletion.create(
        model='gpt-4',
        messages=[{'role': 'user', 'content': 'Hello'}]
    )
    print('API connection successful!')
except Exception as e:
    print(f'API error: {e}')
"
```

**2. Dependencies Installation Error**
```bash
# Upgrade pip and setuptools
pip install --upgrade pip setuptools wheel

# Install dependencies with verbose output
pip install -r requirements.txt -v

# Check for conflicts
pip check
```

**3. Streamlit Connection Error**
```bash
# Check if port is available
lsof -i :8501

# Kill existing process
kill -9 $(lsof -t -i:8501)

# Start with different port
streamlit run app.py --server.port 8502
```

**4. Memory Issues**
```bash
# Check available memory
free -h

# Increase swap space
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Performance Optimization

**1. Reduce Memory Usage**
```python
# In core/config.py
config = {
    "max_tokens": 2000,        # Reduce token limit
    "batch_size": 1,           # Process one at a time
    "cache_results": False,    # Disable caching
}
```

**2. Improve Speed**
```python
# Use faster model
config["model"] = "gpt-3.5-turbo"

# Reduce iterations
config["max_iterations"] = 1
```

**3. Parallel Processing**
```python
# Enable parallel processing
import multiprocessing
config["max_workers"] = multiprocessing.cpu_count()
```

## 📈 Monitoring and Logging

### Enable Detailed Logging

```python
# In core/config.py
config["log_level"] = "DEBUG"
config["log_file"] = "framework.log"
```

### Monitor Performance

```bash
# Check resource usage
htop

# Monitor logs
tail -f multi_agent_framework.log

# Check disk usage
du -sh output/
```

### Health Checks

```bash
# Test framework health
python -c "
from core.orchestrator import EnhancedOrchestrator
orchestrator = EnhancedOrchestrator()
status = orchestrator.get_agent_status()
for agent, info in status.items():
    print(f'{agent}: {info[\"status\"]}')
"
```

## 🎉 Success Indicators

### Framework Ready
- ✅ All tests pass
- ✅ Streamlit interface accessible
- ✅ OpenAI API connection successful
- ✅ Output directory created
- ✅ Logs generated without errors

### First Project Generated
- ✅ 50+ files generated
- ✅ Backend and frontend code complete
- ✅ Database schema and migrations
- ✅ Authentication system implemented
- ✅ Tests with 90%+ coverage
- ✅ Documentation generated
- ✅ Deployment configuration ready

## 📞 Support

- **Documentation**: [Full Documentation](docs/)
- **Issues**: [GitHub Issues](https://github.com/username/multi-agentic-framework/issues)
- **Discussions**: [GitHub Discussions](https://github.com/username/multi-agentic-framework/discussions)
- **Email**: support@multi-agentic-framework.com

---

**🎯 You're now ready to generate complete, production-ready applications from natural language!** 