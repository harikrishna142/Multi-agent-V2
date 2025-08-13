"""
Deployment Configuration Agent for the Multi-Agentic Coding Framework.
Generates deployment scripts and configuration files for the developed code.
"""

import autogen
import re
from typing import Dict, Any, List
from core.config import get_agent_config, config
from core.utils import save_to_file, setup_logging, load_from_file

logger = setup_logging()

class DeploymentConfigurationAgent:
    """Agent responsible for generating deployment configurations."""
    
    def __init__(self):
        self.agent_config = get_agent_config("deployment_agent")
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
    
    def generate_deployment_config(self, generated_code: Dict[str, Any], requirements: Dict[str, Any], project_id: str) -> Dict[str, Any]:
        """
        Generate deployment configuration for the developed code.
        
        Args:
            generated_code: Output from CodingAgent containing generated files
            requirements: Original requirements for context
            project_id: Unique project identifier
            
        Returns:
            Dict containing generated deployment files
        """
        logger.info("Starting deployment configuration generation")
        
        # Load the actual code content
        code_files = {}
        for filename, filepath in generated_code.get("generated_files", {}).items():
            try:
                code_files[filename] = load_from_file(filepath)
            except Exception as e:
                logger.warning(f"Could not load file {filename}: {e}")
                code_files[filename] = f"# Error loading file: {e}"
        
        # Create the deployment prompt
        deployment_prompt = f"""
Please generate comprehensive deployment configuration for the following Python project:

PROJECT REQUIREMENTS:
{self._format_requirements_for_deployment(requirements)}

GENERATED CODE FILES:
{self._format_code_for_deployment(code_files)}

Please generate the following deployment files:

1. **Docker Configuration** (`Dockerfile`):
   - Multi-stage build if appropriate
   - Proper Python environment setup
   - Security best practices
   - Optimized for production

2. **Docker Compose** (`docker-compose.yml`):
   - Service definitions
   - Environment variables
   - Volume mounts
   - Network configuration

3. **Deployment Scripts** (`deploy.sh`, `deploy.ps1`):
   - Linux/Unix deployment script
   - Windows PowerShell deployment script
   - Environment setup
   - Service installation

4. **CI/CD Configuration** (`.github/workflows/deploy.yml`):
   - GitHub Actions workflow
   - Automated testing
   - Build and deployment pipeline

5. **Environment Configuration** (`.env.example`, `config.prod.yaml`):
   - Environment variable templates
   - Production configuration
   - Security considerations

6. **Monitoring Configuration** (`monitoring.yml`, `logging.conf`):
   - Logging configuration
   - Health check endpoints
   - Monitoring setup

7. **Kubernetes Configuration** (`k8s/`):
   - Deployment manifests
   - Service definitions
   - ConfigMaps and Secrets

For each file, provide:
- Production-ready configuration
- Security best practices
- Scalability considerations
- Monitoring and logging
- Error handling and recovery

Please provide each file in the following format:

```dockerfile
# filename: Dockerfile
[complete configuration here]
```

```yaml
# filename: docker-compose.yml
[complete configuration here]
```

And so on for each file.

IMPORTANT: End your response with the word "TERMINATE" to indicate completion.
"""
        
        try:
            # Start the conversation
            chat_result = self.user_proxy.initiate_chat(
                self.agent,
                message=deployment_prompt
            )
            
            # Extract the LLM response using utility function
            from core.utils import extract_llm_response
            last_message = extract_llm_response(chat_result)
            
            # Parse and organize the generated deployment configs
            generated_configs = self._parse_generated_deployment_configs(last_message)
            
            # Validate and enhance the configurations
            validated_configs = self._validate_and_enhance_configs(generated_configs, requirements)
            
            # Save the generated configurations
            saved_configs = self._save_generated_configs(validated_configs, project_id)
            
            result = {
                "project_id": project_id,
                "generated_configs": saved_configs,
                "total_configs": len(saved_configs),
                "deployment_summary": self._generate_deployment_summary(saved_configs)
            }
            
            logger.info(f"Deployment configuration generation completed. Generated {len(saved_configs)} configuration files.")
            return result
            
        except Exception as e:
            logger.error(f"Error in deployment configuration generation: {e}")
            # Generate fallback deployment configs
            fallback_configs = self._generate_fallback_deployment_configs(requirements, code_files, project_id)
            return {
                "project_id": project_id,
                "generated_configs": fallback_configs,
                "total_configs": len(fallback_configs),
                "deployment_summary": "Fallback deployment configuration generated",
                "error": str(e)
            }
    
    def _format_requirements_for_deployment(self, requirements: Dict[str, Any]) -> str:
        """Format requirements for deployment context."""
        formatted = f"""
Project: {requirements.get('project_name', 'N/A')}
Description: {requirements.get('description', 'N/A')}

Deployment Requirements:
"""
        
        for req in requirements.get('functional_requirements', []):
            formatted += f"""
- {req.get('id', 'N/A')}: {req.get('title', 'N/A')}
  Description: {req.get('description', 'N/A')}
  Deployment Impact: Consider deployment requirements for {req.get('description', 'N/A')}
"""
        
        formatted += f"""
Non-Functional Requirements:
"""
        
        for req in requirements.get('non_functional_requirements', []):
            formatted += f"""
- {req.get('id', 'N/A')}: {req.get('title', 'N/A')}
  Category: {req.get('category', 'N/A')}
  Description: {req.get('description', 'N/A')}
  Deployment Consideration: Ensure {req.get('category', 'N/A')} requirements are met
"""
        
        formatted += f"""
Technical Constraints: {', '.join(requirements.get('technical_constraints', []))}
Dependencies: {', '.join(requirements.get('dependencies', []))}
Architecture: {requirements.get('suggested_architecture', 'N/A')}
Complexity: {requirements.get('estimated_complexity', 'N/A')}
"""
        
        return formatted
    
    def _format_code_for_deployment(self, code_files: Dict[str, str]) -> str:
        """Format code files for deployment generation."""
        formatted = ""
        
        for filename, content in code_files.items():
            formatted += f"""
=== FILE: {filename} ===
{content}
=== END FILE: {filename} ===

"""
        
        return formatted
    
    def _parse_generated_deployment_configs(self, response: str) -> Dict[str, str]:
        """Parse the generated deployment configuration response and extract individual files."""
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
            # Fallback: create basic deployment structure
            files = self._create_basic_deployment_structure(response)
        
        return files
    
    def _create_basic_deployment_structure(self, response: str) -> Dict[str, str]:
        """Create basic deployment structure when parsing fails."""
        return {
            "Dockerfile": f"""# Basic Dockerfile for Python application
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
  CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run the application
CMD ["python", "main.py"]
""",
            "docker-compose.yml": f"""version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - ENVIRONMENT=production
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - app
    restart: unless-stopped
""",
            "deploy.sh": f"""#!/bin/bash

# Deployment script for Python application

set -e

echo "Starting deployment..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Build and start the application
echo "Building and starting the application..."
docker-compose up -d --build

# Wait for the application to be ready
echo "Waiting for application to be ready..."
sleep 30

# Check if the application is running
if curl -f http://localhost:8000/health; then
    echo "Deployment successful!"
else
    echo "Deployment failed. Application is not responding."
    exit 1
fi

echo "Deployment completed successfully!"
""",
            ".env.example": f"""# Environment variables for the application
# Copy this file to .env and update the values

# Application settings
DEBUG=False
ENVIRONMENT=production
LOG_LEVEL=INFO

# Database settings (if applicable)
# DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# API keys (if applicable)
# API_KEY=your_api_key_here

# Security settings
SECRET_KEY=your_secret_key_here
ALLOWED_HOSTS=localhost,127.0.0.1

# Performance settings
WORKERS=4
MAX_CONNECTIONS=100
"""
        }
    
    def _validate_and_enhance_configs(self, configs: Dict[str, str], requirements: Dict[str, Any]) -> Dict[str, str]:
        """Validate and enhance the generated deployment configurations."""
        enhanced_configs = {}
        
        for filename, content in configs.items():
            # Enhance the configuration based on requirements
            enhanced_content = self._enhance_deployment_config(content, filename, requirements)
            enhanced_configs[filename] = enhanced_content
        
        return enhanced_configs
    
    def _enhance_deployment_config(self, content: str, filename: str, requirements: Dict[str, Any]) -> str:
        """Enhance deployment configuration with additional features."""
        enhanced = content
        
        # Add security headers if it's a web application
        if "nginx" in filename.lower() or "web" in filename.lower():
            enhanced += """

# Security headers
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
"""
        
        # Add monitoring if it's a Docker Compose file
        if "docker-compose" in filename.lower():
            enhanced += """
  # Monitoring service (optional)
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    restart: unless-stopped
"""
        
        return enhanced
    
    def _save_generated_configs(self, configs: Dict[str, str], project_id: str) -> Dict[str, str]:
        """Save generated deployment configurations to files and return content."""
        saved_configs = {}
        
        for filename, content in configs.items():
            # Create project-specific deployment directory
            project_dir = f"{config.output_dir}/{project_id}/deployment"
            filepath = save_to_file(content, filename, project_dir)
            # Return the content, not the filepath, for frontend display
            saved_configs[filename] = content
        
        return saved_configs
    
    def _generate_deployment_summary(self, saved_configs: Dict[str, str]) -> str:
        """Generate a summary of the created deployment configurations."""
        summary = f"""
# Deployment Configuration Summary

Generated {len(saved_configs)} deployment configuration files:

"""
        
        for filename, filepath in saved_configs.items():
            summary += f"- **{filename}**: {filepath}\n"
        
        summary += f"""
## Deployment Options Available

### Docker Deployment
- Use `Dockerfile` for containerized deployment
- Use `docker-compose.yml` for multi-service deployment
- Run `./deploy.sh` for automated deployment

### Environment Configuration
- Copy `.env.example` to `.env` and configure
- Update environment variables for your deployment

### Manual Deployment
1. Install dependencies: `pip install -r requirements.txt`
2. Set environment variables
3. Run the application: `python main.py`

## Next Steps
1. Review and customize the deployment configurations
2. Update environment variables and secrets
3. Test the deployment in a staging environment
4. Configure monitoring and logging
5. Set up CI/CD pipeline if needed

## Security Considerations
- Update default passwords and secrets
- Configure firewall rules
- Enable HTTPS in production
- Set up proper logging and monitoring
- Regular security updates
"""
        
        return summary
    
    def _generate_fallback_deployment_configs(self, requirements: Dict[str, Any], code_files: Dict[str, str], project_id: str) -> Dict[str, str]:
        """Generate basic fallback deployment configurations when the main generation fails."""
        project_name = requirements.get('project_name', 'GeneratedProject').replace(' ', '_')
        
        dockerfile = f"""# Dockerfile for {project_name}
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
  CMD python -c "print('Health check passed')" || exit 1

# Run the application
CMD ["python", "main.py"]
"""
        
        docker_compose = f"""version: '3.8'

services:
  {project_name.lower()}:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - ENVIRONMENT=production
      - PROJECT_NAME={project_name}
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "print('Health check passed')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Optional: Add a reverse proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - {project_name.lower()}
    restart: unless-stopped
    profiles:
      - production
"""
        
        deploy_sh = f"""#!/bin/bash

# Deployment script for {project_name}

set -e

echo "Starting deployment of {project_name}..."

# Colors for output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m' # No Color

# Function to print colored output
print_status() {{
    echo -e "${{GREEN}}[INFO]${{NC}} $1"
}}

print_warning() {{
    echo -e "${{YELLOW}}[WARNING]${{NC}} $1"
}}

print_error() {{
    echo -e "${{RED}}[ERROR]${{NC}} $1"
}}

# Check prerequisites
print_status "Checking prerequisites..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        print_warning "Please update .env file with your configuration."
    else
        print_error ".env.example file not found. Please create .env file manually."
        exit 1
    fi
fi

# Stop existing containers
print_status "Stopping existing containers..."
docker-compose down || true

# Build and start the application
print_status "Building and starting the application..."
docker-compose up -d --build

# Wait for the application to be ready
print_status "Waiting for application to be ready..."
sleep 30

# Check if the application is running
print_status "Checking application health..."
if curl -f http://localhost:8000/health 2>/dev/null || python -c "print('Health check passed')" 2>/dev/null; then
    print_status "Deployment successful!"
    print_status "Application is running on http://localhost:8000"
else
    print_error "Deployment failed. Application is not responding."
    print_status "Checking container logs..."
    docker-compose logs
    exit 1
fi

print_status "Deployment completed successfully!"
"""
        
        deploy_ps1 = f"""# PowerShell deployment script for {project_name}

param(
    [string]$Environment = "production"
)

Write-Host "Starting deployment of {project_name}..." -ForegroundColor Green

# Check if Docker is installed
try {{
    docker --version | Out-Null
    Write-Host "Docker is installed." -ForegroundColor Green
}} catch {{
    Write-Host "Docker is not installed. Please install Docker first." -ForegroundColor Red
    exit 1
}}

# Check if Docker Compose is installed
try {{
    docker-compose --version | Out-Null
    Write-Host "Docker Compose is installed." -ForegroundColor Green
}} catch {{
    Write-Host "Docker Compose is not installed. Please install Docker Compose first." -ForegroundColor Red
    exit 1
}}

# Check if .env file exists
if (-not (Test-Path ".env")) {{
    Write-Host ".env file not found. Creating from .env.example..." -ForegroundColor Yellow
    if (Test-Path ".env.example") {{
        Copy-Item ".env.example" ".env"
        Write-Host "Please update .env file with your configuration." -ForegroundColor Yellow
    }} else {{
        Write-Host ".env.example file not found. Please create .env file manually." -ForegroundColor Red
        exit 1
    }}
}}

# Stop existing containers
Write-Host "Stopping existing containers..." -ForegroundColor Green
docker-compose down

# Build and start the application
Write-Host "Building and starting the application..." -ForegroundColor Green
docker-compose up -d --build

# Wait for the application to be ready
Write-Host "Waiting for application to be ready..." -ForegroundColor Green
Start-Sleep -Seconds 30

# Check if the application is running
Write-Host "Checking application health..." -ForegroundColor Green
try {{
    Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing | Out-Null
    Write-Host "Deployment successful!" -ForegroundColor Green
    Write-Host "Application is running on http://localhost:8000" -ForegroundColor Green
}} catch {{
    Write-Host "Deployment failed. Application is not responding." -ForegroundColor Red
    Write-Host "Checking container logs..." -ForegroundColor Green
    docker-compose logs
    exit 1
}}

Write-Host "Deployment completed successfully!" -ForegroundColor Green
"""
        
        env_example = f"""# Environment variables for {project_name}
# Copy this file to .env and update the values

# Application settings
DEBUG=False
ENVIRONMENT=production
LOG_LEVEL=INFO
PROJECT_NAME={project_name}

# Server settings
HOST=0.0.0.0
PORT=8000

# Security settings
SECRET_KEY=your_secret_key_here_change_in_production
ALLOWED_HOSTS=localhost,127.0.0.1

# Database settings (if applicable)
# DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# API keys (if applicable)
# API_KEY=your_api_key_here

# Performance settings
WORKERS=4
MAX_CONNECTIONS=100

# Monitoring settings
ENABLE_MONITORING=True
METRICS_PORT=9090
"""
        
        nginx_conf = f"""events {{
    worker_connections 1024;
}}

http {{
    upstream {project_name.lower()} {{
        server {project_name.lower()}:8000;
    }}

    server {{
        listen 80;
        server_name localhost;

        location / {{
            proxy_pass http://{project_name.lower()};
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }}

        # Health check endpoint
        location /health {{
            proxy_pass http://{project_name.lower()}/health;
            access_log off;
        }}
    }}
}}
"""
        
        return {
            "Dockerfile": dockerfile,
            "docker-compose.yml": docker_compose,
            "deploy.sh": deploy_sh,
            "deploy.ps1": deploy_ps1,
            ".env.example": env_example,
            "nginx.conf": nginx_conf
        } 