"""
Enhanced Deployment Agent
Generates complete deployment configurations for production-ready applications.
"""

import autogen
import os
import json
import yaml
from typing import Dict, Any, List
from core.config import get_agent_config, config
from core.utils import save_to_file, setup_logging

logger = setup_logging()

class DeploymentAgent:
    """Enhanced deployment agent that generates complete deployment configurations."""
    
    def __init__(self):
        self.agent_config = get_agent_config("deployment_agent")
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
        """Get system message for deployment configuration generation."""
        return """You are a helpful deployment configuration generator that creates basic deployment files for simple applications. You generate straightforward deployment configurations that can be used to run applications.

## YOUR ROLE:
- Generate basic deployment configurations
- Create simple Docker files
- Write basic docker-compose files
- Generate simple Kubernetes manifests
- Create basic CI/CD configurations
- Generate simple deployment scripts

## DEPLOYMENT GENERATION PROCESS:
1. **Analyze the application structure** and technology stack
2. **Create basic Docker configurations** for simple deployment
3. **Generate simple docker-compose files** for local development
4. **Write basic Kubernetes manifests** (if needed)
5. **Create simple CI/CD configurations**
6. **Generate basic deployment scripts**

## DEPLOYMENT REQUIREMENTS:

### 1. **Containerization**:
- Simple Dockerfile for the application
- Basic multi-stage builds (if needed)
- Simple environment configurations
- Basic health checks

### 2. **Orchestration**:
- Simple docker-compose files
- Basic service configurations
- Simple networking setup
- Basic volume management

### 3. **CI/CD Pipeline**:
- Simple GitHub Actions workflows
- Basic build and test steps
- Simple deployment steps
- Basic error handling

### 4. **Configuration Files**:
- Simple environment files
- Basic configuration templates
- Simple deployment scripts
- Basic documentation

## IMPORTANT GUIDELINES:

✅ **Create simple, basic deployment files**
✅ **Focus on local development and simple deployment**
✅ **Use basic, well-known tools**
✅ **Generate runnable configurations**
✅ **Keep deployment simple**

❌ **Do not create complex production deployments**
❌ **Do not require advanced infrastructure**
❌ **Do not generate enterprise-level configurations**
❌ **Do not create complex orchestration**

**YOUR TASK**: Generate basic deployment configurations for the application that can be used to run and deploy it.

End your response with "TERMINATE" to indicate completion."""
    
    def generate_deployment(self, specifications: Dict[str, Any], generated_files: Dict[str, Any], project_id: str) -> Dict[str, Any]:
        """
        Generate complete deployment configurations for the application.
        
        Args:
            specifications: Technical specifications from RequirementAgent
            generated_files: Generated code files from CodingAgent
            project_id: Unique project identifier
            
        Returns:
            Dict containing deployment configurations and metadata
        """
        logger.info("Starting complete deployment generation")
        
        # Create detailed deployment generation prompt
        deployment_prompt = self._create_deployment_generation_prompt(specifications, generated_files)
        
        try:
            # Start the conversation
            chat_result = self.user_proxy.initiate_chat(
                self.agent,
                message=deployment_prompt
            )
            
            # Extract the LLM response
            from core.utils import extract_llm_response
            last_message = extract_llm_response(chat_result)
            
            # Extract and process all generated deployment files
            generated_deployments = self._parse_generated_deployments(last_message)
            
            # Validate and enhance the generated deployments
            validated_deployments = self._validate_and_enhance_deployments(generated_deployments)
            
            # Save all deployment files
            saved_deployments = self._save_generated_deployments(validated_deployments, project_id)
            
            # Generate additional deployment configuration files
            config_files = self._generate_deployment_configuration(specifications, project_id)
            saved_deployments.update(config_files)
            
            result = {
                "project_id": project_id,
                "deployment_files": saved_deployments,
                "deployment_type": self._determine_deployment_type(specifications),
                "technology_stack": specifications.get("project_overview", {}).get("technology_stack", {}),
                "total_deployment_files": len(saved_deployments),
                "docker_files": len([f for f in saved_deployments.keys() if "docker" in f.lower()]),
                "kubernetes_files": len([f for f in saved_deployments.keys() if "k8s" in f or "kubernetes" in f]),
                "ci_cd_files": len([f for f in saved_deployments.keys() if "workflow" in f or "pipeline" in f]),
                "monitoring_files": len([f for f in saved_deployments.keys() if "prometheus" in f or "grafana" in f]),
                "deployment_ready": True
            }
            
            logger.info(f"Complete deployment generation finished. Generated {len(saved_deployments)} deployment files.")
            return result
            
        except Exception as e:
            logger.error(f"Error in deployment generation: {e}")
            return self._generate_fallback_deployment(specifications, project_id, str(e))
    
    def _create_deployment_generation_prompt(self, specifications: Dict[str, Any], generated_files: Dict[str, Any]) -> str:
        """Create detailed deployment generation prompt."""
        
        # Extract key information from specifications
        project_overview = specifications.get("project_overview", {})
        functional_reqs = specifications.get("functional_requirements", [])
        architecture = specifications.get("architecture", {})
        
        tech_stack = project_overview.get("technology_stack", {})
        backend_stack = tech_stack.get("backend", {})
        frontend_stack = tech_stack.get("frontend", {})
        deployment_stack = tech_stack.get("deployment", {})
        
        prompt = f"""
Generate complete deployment configurations for the following application:

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
  Priority: {req.get('priority', 'N/A')}
"""
        
        prompt += f"""
## ARCHITECTURE:
{json.dumps(architecture, indent=2)}

## GENERATED CODE FILES:
The following code has been generated for this project. Please create deployment configurations based on the actual implementation:

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
## DEPLOYMENT GENERATION REQUIREMENTS:

Please generate the following deployment files:

1. **Dockerfile** - Container configuration for the application
2. **docker-compose.yml** - Multi-service orchestration
3. **Kubernetes manifests** - K8s deployment configurations
4. **CI/CD pipelines** - GitHub Actions or GitLab CI
5. **Environment configurations** - Environment variables and configs

For each file, provide:
- Complete configuration with all necessary settings
- Environment-specific configurations
- Health checks and monitoring
- Security best practices
- Production-ready settings

IMPORTANT: Generate deployment configurations that match the actual code implementation.

Please generate the complete deployment configuration with all required files and full implementation.

IMPORTANT: End your response with "TERMINATE" to indicate completion.
"""
        
        return prompt
    
    def _parse_generated_deployments(self, response: str) -> Dict[str, str]:
        """Parse generated deployment files from the response."""
        import re
        
        deployments = {}
        
        # Extract code blocks with filenames
        code_blocks = re.findall(r'```(\w+)\s*# filename: ([^\n]+)\s*(.*?)```', response, re.DOTALL)
        
        for language, filename, content in code_blocks:
            deployments[filename] = content.strip()
        
        # Also look for code blocks without explicit filenames
        if not deployments:
            code_blocks = re.findall(r'```(\w+)\s*(.*?)```', response, re.DOTALL)
            for i, (language, content) in enumerate(code_blocks):
                if language in ['yaml', 'yml', 'dockerfile', 'nginx', 'json']:
                    # Try to infer filename from content
                    filename = self._infer_deployment_filename(content, language, i)
                    deployments[filename] = content.strip()
        
        return deployments
    
    def _infer_deployment_filename(self, content: str, language: str, index: int) -> str:
        """Infer deployment filename from content."""
        if language == 'yaml' or language == 'yml':
            if 'version:' in content and 'services:' in content:
                return f"docker-compose.prod.yml"
            elif 'apiVersion:' in content and 'kind:' in content:
                return f"k8s/deployment-{index}.yaml"
            elif 'name:' in content and 'on:' in content:
                return f".github/workflows/deploy.yml"
            else:
                return f"deployment-{index}.yml"
        elif language == 'dockerfile':
            return f"Dockerfile.{index}"
        elif language == 'nginx':
            return f"nginx/nginx.conf"
        elif language == 'json':
            return f"config-{index}.json"
        else:
            return f"deployment-{index}.{language}"
    
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
    
    def _validate_and_enhance_deployments(self, deployments: Dict[str, str]) -> Dict[str, str]:
        """Validate and enhance the generated deployments."""
        enhanced_deployments = {}
        
        for filename, content in deployments.items():
            # Basic validation for YAML files
            if filename.endswith(('.yml', '.yaml')):
                try:
                    import yaml
                    yaml.safe_load(content)
                    enhanced_deployments[filename] = content
                except Exception as e:
                    logger.warning(f"YAML validation failed for {filename}: {e}")
                    enhanced_deployments[filename] = content
            else:
                enhanced_deployments[filename] = content
        
        return enhanced_deployments
    
    def _save_generated_deployments(self, deployments: Dict[str, str], project_id: str) -> Dict[str, str]:
        """Save generated deployment files and return content."""
        try:
            saved_deployments = {}
            project_dir = f"output/deployment/{project_id}"
            os.makedirs(project_dir, exist_ok=True)
            
            for filename, content in deployments.items():
                # Use save_to_file with correct parameters: (content, filename, output_dir)
                file_path = save_to_file(content, filename, project_dir)
                saved_deployments[filename] = file_path
                logger.info(f"Saved deployment file: {file_path}")
            
            return saved_deployments
            
        except Exception as e:
            logger.error(f"Error saving deployment files: {e}")
            return {}
    
    def _generate_deployment_configuration(self, specifications: Dict[str, Any],project_id: str) -> Dict[str, str]:
        """Generate additional deployment configuration files."""
        config_files = {}
        
        # Generate environment file
        env_file = self._generate_env_file(specifications)
        config_files[".env.production"] = env_file
        
        # Generate deployment script
        deploy_script = self._generate_deploy_script(specifications)
        config_files["deploy.sh"] = deploy_script
        
        # Generate monitoring configuration
        monitoring_config = self._generate_monitoring_config(specifications)
        config_files["monitoring/prometheus.yml"] = monitoring_config
        
        return config_files
    
    def _generate_env_file(self, specifications: Dict[str, Any]) -> str:
        """Generate production environment file."""
        return """# Production Environment Variables
# Database Configuration
DATABASE_URL=postgresql://postgres:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
POSTGRES_DB=app_production
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-secure-password-here

# Redis Configuration
REDIS_URL=redis://redis:6379
REDIS_PASSWORD=your-redis-password-here

# Application Configuration
SECRET_KEY=your-super-secret-key-change-in-production
DEBUG=False
LOG_LEVEL=INFO
ENVIRONMENT=production

# Frontend Configuration
REACT_APP_API_URL=https://api.myapp.com
REACT_APP_ENVIRONMENT=production

# Monitoring Configuration
GRAFANA_PASSWORD=your-grafana-password-here
PROMETHEUS_RETENTION_DAYS=30

# External Services
PAYMENT_API_KEY=your-payment-api-key
EMAIL_SERVICE_API_KEY=your-email-api-key
SMS_SERVICE_API_KEY=your-sms-api-key

# Security Configuration
SSL_CERT_PATH=/etc/nginx/ssl/cert.pem
SSL_KEY_PATH=/etc/nginx/ssl/key.pem
"""
    
    def _generate_deploy_script(self, specifications: Dict[str, Any]) -> str:
        """Generate deployment script."""
        return """#!/bin/bash

# Production Deployment Script
set -e

echo "🚀 Starting production deployment..."

# Load environment variables
if [ -f .env.production ]; then
    export $(cat .env.production | grep -v '^#' | xargs)
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Build and push images
echo "📦 Building and pushing Docker images..."

# Build backend image
docker build -t myapp/backend:latest ./backend
docker push myapp/backend:latest

# Build frontend image
docker build -t myapp/frontend:latest ./frontend
docker push myapp/frontend:latest

# Deploy with Docker Compose
echo "🚀 Deploying application..."

# Stop existing containers
docker-compose -f docker-compose.prod.yml down

# Pull latest images
docker-compose -f docker-compose.prod.yml pull

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 30

# Check service health
echo "🔍 Checking service health..."

# Check backend health
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend health check failed"
    exit 1
fi

# Check frontend health
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is healthy"
else
    echo "❌ Frontend health check failed"
    exit 1
fi

# Check database health
if docker-compose -f docker-compose.prod.yml exec -T db pg_isready -U postgres > /dev/null 2>&1; then
    echo "✅ Database is healthy"
else
    echo "❌ Database health check failed"
    exit 1
fi

echo "🎉 Deployment completed successfully!"
echo "📊 Application is available at:"
echo "   - Frontend: http://localhost:3000"
echo "   - Backend API: http://localhost:8000"
echo "   - API Documentation: http://localhost:8000/docs"
echo "   - Grafana: http://localhost:3001"
echo "   - Prometheus: http://localhost:9090"

# Show running containers
echo "📋 Running containers:"
docker-compose -f docker-compose.prod.yml ps
"""
    
    def _generate_monitoring_config(self, specifications: Dict[str, Any]) -> str:
        """Generate Prometheus monitoring configuration."""
        return """global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  # Prometheus itself
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # Backend application
  - job_name: 'backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    scrape_interval: 10s

  # Frontend application (if it exposes metrics)
  - job_name: 'frontend'
    static_configs:
      - targets: ['frontend:3000']
    metrics_path: '/metrics'
    scrape_interval: 10s

  # Database (if using postgres_exporter)
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']
    scrape_interval: 30s

  # Redis (if using redis_exporter)
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
    scrape_interval: 30s

  # Nginx (if using nginx_exporter)
  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx-exporter:9113']
    scrape_interval: 30s

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          # - alertmanager:9093
"""
    
    def _determine_deployment_type(self, specifications: Dict[str, Any]) -> str:
        """Determine the type of deployment generated."""
        tech_stack = specifications.get("project_overview", {}).get("technology_stack", {})
        deployment_stack = tech_stack.get("deployment", {})
        
        if deployment_stack.get("orchestration") == "Kubernetes":
            return "Kubernetes Deployment"
        elif deployment_stack.get("orchestration") == "Docker Compose":
            return "Docker Compose Deployment"
        else:
            return "Multi-Platform Deployment"
    
    def _generate_fallback_deployment(self, specifications: Dict[str, Any], 
                                     project_id: str, error: str) -> Dict[str, Any]:
        """Generate fallback deployment when generation fails."""
        fallback_deployments = {
            "docker-compose.yml": self._generate_basic_docker_compose(),
            "Dockerfile": self._generate_basic_dockerfile(),
            ".env.example": self._generate_basic_env_file(),
            "README.md": "# Deployment\n\nBasic deployment configuration generated as fallback."
        }
        
        saved_deployments = self._save_generated_deployments(fallback_deployments, project_id)
        
        return {
            "project_id": project_id,
            "deployment_files": saved_deployments,
            "deployment_type": "Basic Deployment",
            "technology_stack": {},
            "total_deployment_files": len(saved_deployments),
            "docker_files": 2,
            "kubernetes_files": 0,
            "ci_cd_files": 0,
            "monitoring_files": 0,
            "deployment_ready": False,
            "error": error,
            "fallback_mode": True
        }
    
    def _generate_basic_docker_compose(self) -> str:
        """Generate basic Docker Compose configuration."""
        return """version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/app_db
    depends_on:
      - db

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=app_db
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
"""
    
    def _generate_basic_dockerfile(self) -> str:
        """Generate basic Dockerfile."""
        return """FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
    
    def _generate_basic_env_file(self) -> str:
        """Generate basic environment file."""
        return """# Basic Environment Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/app_db
SECRET_KEY=your-secret-key-here
DEBUG=True
LOG_LEVEL=INFO
""" 