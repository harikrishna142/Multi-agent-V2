"""
Enhanced Coding Agent V2
Generates complete, production-ready applications with full implementation.
"""

import autogen
import os
import json
from typing import Dict, Any, List
from core.config import get_agent_config, config
from core.utils import save_to_file, setup_logging, validate_python_code, format_code_with_black

logger = setup_logging()

class EnhancedCodingAgentV2:
    """Enhanced coding agent that generates complete, production-ready applications."""
    
    def __init__(self):
        self.agent_config = get_agent_config("coding_agent")
        self.llm_config = config.get_llm_config()
        
        # Create the agent with enhanced system message
        enhanced_system_message = self._create_enhanced_system_message()
        
        self.agent = autogen.AssistantAgent(
            name=self.agent_config["name"],
            system_message=enhanced_system_message,
            llm_config=self.llm_config
        )
        
        # Create user proxy for interaction
        self.user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=15,
            is_termination_msg=lambda x: "TERMINATE" in x.get("content", ""),
            code_execution_config={"work_dir": "workspace", "use_docker": False},
            llm_config=self.llm_config
        )
    
    def _create_enhanced_system_message(self) -> str:
        """Create enhanced system message for complete application generation."""
        
        return """
You are an expert full-stack software engineer specializing in creating complete, production-ready applications. Your task is to generate fully functional, deployable applications based on detailed technical specifications.

## APPLICATION GENERATION REQUIREMENTS:

### 1. Complete Implementation:
- **NO PLACEHOLDER CODE**: Every function must have complete implementation
- **NO PASS STATEMENTS**: All methods must contain actual business logic
- **FULL FUNCTIONALITY**: Applications must be ready to run immediately
- **PRODUCTION-READY**: Code must follow production standards and best practices

### 2. Technology Stack Implementation:
Based on the specifications, implement:
- **Backend**: Complete API with all endpoints, database models, and business logic
- **Frontend**: Full user interface with all components and functionality
- **Database**: Complete schema with migrations and seed data
- **Authentication**: Full authentication and authorization system
- **Security**: Comprehensive security measures and validation
- **Testing**: Complete test suite with high coverage

### 3. File Structure and Organization:
Generate a complete, organized project structure:
```
project/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── models/
│   │   ├── api/
│   │   ├── services/
│   │   ├── utils/
│   │   └── config.py
│   ├── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── docker-compose.yml
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── utils/
│   │   └── App.js
│   ├── public/
│   ├── package.json
│   └── Dockerfile
├── database/
│   ├── migrations/
│   └── seeds/
└── docs/
```

### 4. Code Quality Standards:
- **Clean Code**: Follow clean code principles and best practices
- **Error Handling**: Comprehensive error handling and logging
- **Validation**: Input validation and data sanitization
- **Documentation**: Complete docstrings and comments
- **Type Hints**: Full type annotations for all functions
- **Testing**: Unit tests, integration tests, and end-to-end tests

### 5. Production Features:
- **Logging**: Comprehensive logging system
- **Monitoring**: Health checks and monitoring endpoints
- **Configuration**: Environment-based configuration
- **Security**: Authentication, authorization, and data protection
- **Performance**: Optimized queries and caching
- **Scalability**: Horizontal scaling support

## IMPLEMENTATION APPROACH:

### Phase 1: Backend Implementation
1. **Database Models**: Complete SQLAlchemy models with relationships
2. **API Endpoints**: Full RESTful API with all CRUD operations
3. **Business Logic**: Complete service layer with all business rules
4. **Authentication**: JWT-based authentication system
5. **Validation**: Pydantic models for request/response validation

### Phase 2: Frontend Implementation
1. **Component Architecture**: Complete React component hierarchy
2. **State Management**: Redux store with all actions and reducers
3. **API Integration**: Complete API service layer
4. **User Interface**: Full UI with all pages and forms
5. **Routing**: Complete routing with protected routes

### Phase 3: Integration and Testing
1. **Database Integration**: Complete database setup and migrations
2. **API Testing**: Complete API test suite
3. **Frontend Testing**: Component and integration tests
4. **End-to-End Testing**: Complete user workflow tests

## OUTPUT FORMAT:

For each file, provide complete, runnable code:

```python
# filename: backend/app/main.py
[complete FastAPI application code]
```

```python
# filename: backend/app/models/user.py
[complete SQLAlchemy model with all methods]
```

```javascript
# filename: frontend/src/components/UserRegistration.js
[complete React component with full functionality]
```

```json
# filename: frontend/package.json
[complete package.json with all dependencies]
```

```yaml
# filename: docker-compose.yml
[complete Docker Compose configuration]
```

## IMPLEMENTATION EXAMPLES:

### Backend API Endpoint Example:
```python
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

app = FastAPI()

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

@app.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    
    # Hash password
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    
    # Create new user
    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password.decode('utf-8')
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return UserResponse(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email,
        created_at=db_user.created_at
    )
```

### Frontend Component Example:
```javascript
import React, { useState } from 'react';
import { useDispatch } from 'react-redux';
import { registerUser } from '../services/authService';
import { setUser } from '../store/slices/authSlice';

const UserRegistration = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const dispatch = useDispatch();

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.username.trim()) {
      newErrors.username = 'Username is required';
    } else if (formData.username.length < 3) {
      newErrors.username = 'Username must be at least 3 characters';
    }
    
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
    }
    
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }
    
    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setLoading(true);
    
    try {
      const response = await registerUser({
        username: formData.username,
        email: formData.email,
        password: formData.password
      });
      
      dispatch(setUser(response.data));
      // Redirect to dashboard or show success message
    } catch (error) {
      setErrors({ general: error.response?.data?.detail || 'Registration failed' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="registration-form">
      <h2>Create Account</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="username">Username</label>
          <input
            type="text"
            id="username"
            value={formData.username}
            onChange={(e) => setFormData({...formData, username: e.target.value})}
            className={errors.username ? 'error' : ''}
          />
          {errors.username && <span className="error-message">{errors.username}</span>}
        </div>
        
        <div className="form-group">
          <label htmlFor="email">Email</label>
          <input
            type="email"
            id="email"
            value={formData.email}
            onChange={(e) => setFormData({...formData, email: e.target.value})}
            className={errors.email ? 'error' : ''}
          />
          {errors.email && <span className="error-message">{errors.email}</span>}
        </div>
        
        <div className="form-group">
          <label htmlFor="password">Password</label>
          <input
            type="password"
            id="password"
            value={formData.password}
            onChange={(e) => setFormData({...formData, password: e.target.value})}
            className={errors.password ? 'error' : ''}
          />
          {errors.password && <span className="error-message">{errors.password}</span>}
        </div>
        
        <div className="form-group">
          <label htmlFor="confirmPassword">Confirm Password</label>
          <input
            type="password"
            id="confirmPassword"
            value={formData.confirmPassword}
            onChange={(e) => setFormData({...formData, confirmPassword: e.target.value})}
            className={errors.confirmPassword ? 'error' : ''}
          />
          {errors.confirmPassword && <span className="error-message">{errors.confirmPassword}</span>}
        </div>
        
        {errors.general && <div className="error-message">{errors.general}</div>}
        
        <button type="submit" disabled={loading}>
          {loading ? 'Creating Account...' : 'Create Account'}
        </button>
      </form>
    </div>
  );
};

export default UserRegistration;
```

## QUALITY REQUIREMENTS:

1. **Complete Functionality**: Every feature must be fully implemented
2. **Production Ready**: Code must be deployable and maintainable
3. **Best Practices**: Follow industry standards and patterns
4. **Error Handling**: Comprehensive error handling and validation
5. **Security**: Implement security best practices
6. **Performance**: Optimized for performance and scalability
7. **Testing**: Include comprehensive test coverage
8. **Documentation**: Complete documentation and comments

IMPORTANT: 
- Generate complete, production-ready applications
- NO placeholder code or pass statements
- Every function must have full implementation
- Applications must be ready to run immediately
- Follow modern development practices and patterns

End your response with "TERMINATE" to indicate completion.
"""
    
    def generate_complete_application(self, specifications: Dict[str, Any], project_id: str) -> Dict[str, Any]:
        """
        Generate a complete, production-ready application based on specifications.
        
        Args:
            specifications: Detailed technical specifications from RequirementAgent
            project_id: Unique project identifier
            
        Returns:
            Dict containing complete application files and metadata
        """
        logger.info("Starting complete application generation")
        
        # Step 1: Create comprehensive generation prompt
        generation_prompt = self._create_generation_prompt(specifications)
        
        try:
            # Start the conversation with multiple rounds for complete implementation
            chat_result = self.user_proxy.initiate_chat(
                self.agent,
                message=generation_prompt
            )
            
            # Extract the LLM response
            from core.utils import extract_llm_response
            last_message = extract_llm_response(chat_result)
            
            # Extract and process all generated files
            generated_files = self._parse_generated_files(last_message)
            
            # Step 2: Validate and enhance the generated code
            validated_files = self._validate_and_enhance_code(generated_files)
            
            # Step 3: Save all files
            saved_files = self._save_generated_files(validated_files, project_id)
            
            # Step 4: Generate additional configuration files
            config_files = self._generate_configuration_files(specifications, project_id)
            saved_files.update(config_files)
            
            result = {
                "project_id": project_id,
                "generated_files": saved_files,
                "application_type": self._determine_application_type(specifications),
                "technology_stack": specifications.get("project_overview", {}).get("technology_stack", {}),
                "total_files": len(saved_files),
                "backend_files": len([f for f in saved_files.keys() if f.startswith("backend/")]),
                "frontend_files": len([f for f in saved_files.keys() if f.startswith("frontend/")]),
                "configuration_files": len([f for f in saved_files.keys() if f.endswith((".yml", ".yaml", ".json", ".env"))]),
                "deployment_ready": True
            }
            
            logger.info(f"Complete application generation finished. Generated {len(saved_files)} files.")
            return result
            
        except Exception as e:
            logger.error(f"Error in complete application generation: {e}")
            return self._generate_fallback_application(specifications, project_id, str(e))
    
    def _create_generation_prompt(self, specifications: Dict[str, Any]) -> str:
        """Create comprehensive generation prompt."""
        
        # Extract key information from specifications
        project_overview = specifications.get("project_overview", {})
        architecture = specifications.get("architecture", {})
        functional_reqs = specifications.get("functional_requirements", [])
        
        tech_stack = project_overview.get("technology_stack", {})
        backend_stack = tech_stack.get("backend", {})
        frontend_stack = tech_stack.get("frontend", {})
        
        prompt = f"""
Generate a complete, production-ready application based on the following specifications:

## PROJECT OVERVIEW:
- Name: {project_overview.get('name', 'Generated Application')}
- Description: {project_overview.get('description', 'N/A')}
- Version: {project_overview.get('version', '1.0.0')}

## TECHNOLOGY STACK:
Backend:
- Framework: {backend_stack.get('framework', 'FastAPI')}
- Database: {backend_stack.get('database', 'PostgreSQL')}
- Authentication: {backend_stack.get('authentication', 'JWT')}

Frontend:
- Framework: {frontend_stack.get('framework', 'React')}
- State Management: {frontend_stack.get('state_management', 'Redux Toolkit')}
- UI Library: {frontend_stack.get('ui_library', 'Material-UI')}

## FUNCTIONAL REQUIREMENTS:
"""
        
        for req in functional_reqs:
            prompt += f"""
- {req.get('id', 'N/A')}: {req.get('title', 'N/A')}
  Description: {req.get('description', 'N/A')}
  Priority: {req.get('priority', 'N/A')}
  Acceptance Criteria: {', '.join(req.get('acceptance_criteria', []))}
"""
        
        prompt += f"""
## ARCHITECTURE:
{json.dumps(architecture, indent=2)}

## IMPLEMENTATION REQUIREMENTS:

1. **Backend Implementation**:
   - Complete FastAPI application with all endpoints
   - Full database models with SQLAlchemy
   - Complete authentication system
   - Business logic implementation
   - Error handling and validation
   - API documentation with Swagger

2. **Frontend Implementation**:
   - Complete React application
   - All components and pages
   - State management with Redux
   - API integration
   - Form validation and error handling
   - Responsive design

3. **Database Implementation**:
   - Complete database schema
   - Migration files
   - Seed data
   - Database configuration

4. **Configuration Files**:
   - Docker and Docker Compose
   - Environment configuration
   - Dependencies and requirements
   - Deployment configuration

5. **Testing**:
   - Unit tests for backend
   - Component tests for frontend
   - Integration tests
   - End-to-end tests

## GENERATION INSTRUCTIONS:

Generate the complete application with the following structure:

```
project/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── models/
│   │   ├── api/
│   │   ├── services/
│   │   ├── utils/
│   │   └── config.py
│   ├── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── docker-compose.yml
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── utils/
│   │   └── App.js
│   ├── public/
│   ├── package.json
│   └── Dockerfile
├── database/
│   ├── migrations/
│   └── seeds/
└── docs/
```

## IMPORTANT REQUIREMENTS:

- **NO PLACEHOLDER CODE**: Every function must have complete implementation
- **NO PASS STATEMENTS**: All methods must contain actual business logic
- **FULL FUNCTIONALITY**: Applications must be ready to run immediately
- **PRODUCTION-READY**: Code must follow production standards
- **COMPLETE FEATURES**: All requirements must be fully implemented
- **ERROR HANDLING**: Comprehensive error handling and validation
- **SECURITY**: Implement security best practices
- **TESTING**: Include comprehensive test coverage

Please generate the complete application with all files and full implementation.

IMPORTANT: End your response with "TERMINATE" to indicate completion.
"""
        
        return prompt
    
    def _parse_generated_files(self, response: str) -> Dict[str, str]:
        """Parse generated files from the response."""
        import re
        
        files = {}
        
        # Extract code blocks with filenames
        code_blocks = re.findall(r'```(\w+)\s*# filename: ([^\n]+)\s*(.*?)```', response, re.DOTALL)
        
        for language, filename, content in code_blocks:
            files[filename] = content.strip()
        
        # Also look for code blocks without explicit filenames
        if not files:
            code_blocks = re.findall(r'```(\w+)\s*(.*?)```', response, re.DOTALL)
            for i, (language, content) in enumerate(code_blocks):
                if language in ['python', 'javascript', 'json', 'yaml', 'yml']:
                    # Try to infer filename from content
                    filename = self._infer_filename(content, language, i)
                    files[filename] = content.strip()
        
        return files
    
    def _infer_filename(self, content: str, language: str, index: int) -> str:
        """Infer filename from content."""
        if language == 'python':
            if 'FastAPI' in content or 'app = FastAPI()' in content:
                return f"backend/app/main.py"
            elif 'class' in content and 'BaseModel' in content:
                return f"backend/app/models/model_{index}.py"
            else:
                return f"backend/app/{index}.py"
        elif language == 'javascript':
            if 'React' in content or 'import React' in content:
                return f"frontend/src/components/Component{index}.js"
            else:
                return f"frontend/src/{index}.js"
        elif language == 'json':
            if 'dependencies' in content:
                return f"frontend/package.json"
            else:
                return f"config{index}.json"
        elif language in ['yaml', 'yml']:
            return f"docker-compose.yml"
        else:
            return f"file_{index}.{language}"
    
    def _validate_and_enhance_code(self, files: Dict[str, str]) -> Dict[str, str]:
        """Validate and enhance the generated code."""
        enhanced_files = {}
        
        for filename, content in files.items():
            # Validate Python code
            if filename.endswith('.py'):
                validation = validate_python_code(content)
                if validation["valid"]:
                    try:
                        formatted_content = format_code_with_black(content)
                        enhanced_files[filename] = formatted_content
                    except Exception as e:
                        logger.warning(f"Code formatting failed for {filename}: {e}")
                        enhanced_files[filename] = content
                else:
                    logger.warning(f"Code validation failed for {filename}: {validation['errors']}")
                    enhanced_files[filename] = content
            else:
                enhanced_files[filename] = content
        
        return enhanced_files
    
    def _save_generated_files(self, files: Dict[str, str], project_id: str) -> Dict[str, str]:
        """Save generated files and return content."""
        saved_files = {}
        
        for filename, content in files.items():
            project_dir = f"{config.output_dir}/{project_id}"
            filepath = save_to_file(content, filename, project_dir)
            # Return the content, not the filepath, for frontend display
            saved_files[filename] = content
        
        return saved_files
    
    def _generate_configuration_files(self, specifications: Dict[str, Any], project_id: str) -> Dict[str, str]:
        """Generate additional configuration files."""
        config_files = {}
        
        # Generate Docker Compose
        docker_compose = self._generate_docker_compose(specifications)
        config_files["docker-compose.yml"] = docker_compose
        
        # Generate README
        readme = self._generate_readme(specifications, project_id)
        config_files["README.md"] = readme
        
        # Generate .env.example
        env_example = self._generate_env_example(specifications)
        config_files[".env.example"] = env_example
        
        return config_files
    
    def _generate_docker_compose(self, specifications: Dict[str, Any]) -> str:
        """Generate Docker Compose configuration."""
        return """version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/app_db
      - SECRET_KEY=your-secret-key-here
    depends_on:
      - db
    volumes:
      - ./backend:/app
    networks:
      - app-network

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
      - /app/node_modules
    networks:
      - app-network

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=app_db
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    networks:
      - app-network

volumes:
  postgres_data:

networks:
  app-network:
    driver: bridge
"""
    
    def _generate_readme(self, specifications: Dict[str, Any], project_id: str) -> str:
        """Generate comprehensive README."""
        project_name = specifications.get("project_overview", {}).get("name", "Generated Application")
        
        return f"""# {project_name}

A complete, production-ready application generated by the Multi-Agentic Framework.

## Features

- Complete backend API with FastAPI
- Full frontend application with React
- Database integration with PostgreSQL
- Authentication and authorization
- Comprehensive testing suite
- Docker containerization
- Production deployment ready

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Running with Docker

1. Clone the repository
2. Copy `.env.example` to `.env` and configure
3. Run the application:

```bash
docker-compose up --build
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Local Development

#### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend
npm install
npm start
```

## Project Structure

```
project/
├── backend/          # FastAPI backend
├── frontend/         # React frontend
├── database/         # Database migrations and seeds
├── docs/            # Documentation
└── docker-compose.yml
```

## API Documentation

The API documentation is available at http://localhost:8000/docs when the backend is running.

## Testing

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

```bash
cd frontend
npm test
```

## Deployment

This application is ready for deployment to any cloud platform that supports Docker.

## License

MIT License
"""
    
    def _generate_env_example(self, specifications: Dict[str, Any]) -> str:
        """Generate environment variables example."""
        return """# Backend Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/app_db
SECRET_KEY=your-secret-key-here
DEBUG=False
LOG_LEVEL=INFO

# Frontend Configuration
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development

# Database Configuration
POSTGRES_DB=app_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password

# Redis Configuration
REDIS_URL=redis://localhost:6379

# External Services
PAYMENT_API_KEY=your-payment-api-key
EMAIL_SERVICE_API_KEY=your-email-api-key
"""
    
    def _determine_application_type(self, specifications: Dict[str, Any]) -> str:
        """Determine the type of application generated."""
        tech_stack = specifications.get("project_overview", {}).get("technology_stack", {})
        
        if tech_stack.get("frontend") and tech_stack.get("backend"):
            return "Full-Stack Web Application"
        elif tech_stack.get("backend"):
            return "Backend API"
        elif tech_stack.get("frontend"):
            return "Frontend Application"
        else:
            return "General Application"
    
    def _generate_fallback_application(self, specifications: Dict[str, Any], 
                                     project_id: str, error: str) -> Dict[str, Any]:
        """Generate fallback application when generation fails."""
        fallback_files = {
            "backend/app/main.py": self._generate_basic_fastapi_app(),
            "backend/requirements.txt": "fastapi==0.104.0\nuvicorn==0.24.0\nsqlalchemy==2.0.23",
            "frontend/src/App.js": self._generate_basic_react_app(),
            "frontend/package.json": '{"name": "app", "version": "1.0.0", "dependencies": {"react": "^18.0.0"}}',
            "README.md": "# Generated Application\n\nBasic application generated as fallback."
        }
        
        saved_files = self._save_generated_files(fallback_files, project_id)
        
        return {
            "project_id": project_id,
            "generated_files": saved_files,
            "application_type": "Basic Application",
            "technology_stack": {},
            "total_files": len(saved_files),
            "backend_files": 2,
            "frontend_files": 2,
            "configuration_files": 1,
            "deployment_ready": False,
            "error": error,
            "fallback_mode": True
        }
    
    def _generate_basic_fastapi_app(self) -> str:
        """Generate basic FastAPI application."""
        return '''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Generated API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
    
    def _generate_basic_react_app(self) -> str:
        """Generate basic React application."""
        return '''import React from 'react';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Generated Application</h1>
        <p>Welcome to your new application!</p>
      </header>
    </div>
  );
}

export default App;
''' 