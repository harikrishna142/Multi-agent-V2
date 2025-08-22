"""
Context Manager for Multi-Agent Framework
Provides agents with relevant context, templates, and code examples.
"""

import os
import json
import glob
from typing import Dict, List, Any, Optional
from core.utils import setup_logging

logger = setup_logging()

class ContextManager:
    """Manages context injection for agents."""
    
    def __init__(self):
        self.templates_dir = "templates"
        self.examples_dir = "examples"
        self.framework_templates = self._load_framework_templates()
        self.code_patterns = self._load_code_patterns()
    
    def _load_framework_templates(self) -> Dict[str, Any]:
        """Load framework-specific templates and boilerplate."""
        return {
            "flask": {
                "app_structure": {
                    "app.py": """from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({"message": "API is running"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)""",
                    "requirements.txt": """Flask==2.3.3
Flask-CORS==4.0.0
python-dotenv==1.0.0""",
                    "config.py": """import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'"""
                },
                "auth_template": """from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

@login_manager.user_loader
def load_user(user_id):
    # Load user from database
    return User(user_id, "user", "hash")

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    # Implement login logic
    return jsonify({"message": "Login successful"})""",
                "crud_template": """from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

class Model(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/api/items', methods=['GET'])
def get_items():
    items = Model.query.all()
    return jsonify([{"id": item.id, "name": item.name} for item in items])

@app.route('/api/items', methods=['POST'])
def create_item():
    data = request.get_json()
    item = Model(name=data['name'], description=data.get('description'))
    db.session.add(item)
    db.session.commit()
    return jsonify({"id": item.id, "name": item.name}), 201"""
            },
            "react": {
                "app_structure": {
                    "package.json": """{
  "name": "react-app",
  "version": "0.1.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "axios": "^1.4.0"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  }
}""",
                    "src/App.js": """import React from 'react';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Welcome to React App</h1>
      </header>
    </div>
  );
}

export default App;""",
                    "src/index.js": """import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);"""
                },
                "auth_template": """import React, { useState } from 'react';
import axios from 'axios';

function Login() {
  const [credentials, setCredentials] = useState({ username: '', password: '' });

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('/api/login', credentials);
      localStorage.setItem('token', response.data.token);
      // Handle successful login
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  return (
    <form onSubmit={handleLogin}>
      <input
        type="text"
        placeholder="Username"
        value={credentials.username}
        onChange={(e) => setCredentials({...credentials, username: e.target.value})}
      />
      <input
        type="password"
        placeholder="Password"
        value={credentials.password}
        onChange={(e) => setCredentials({...credentials, password: e.target.value})}
      />
      <button type="submit">Login</button>
    </form>
  );
}

export default Login;""",
                "crud_template": """import React, { useState, useEffect } from 'react';
import axios from 'axios';

function ItemList() {
  const [items, setItems] = useState([]);
  const [newItem, setNewItem] = useState({ name: '', description: '' });

  useEffect(() => {
    fetchItems();
  }, []);

  const fetchItems = async () => {
    try {
      const response = await axios.get('/api/items');
      setItems(response.data);
    } catch (error) {
      console.error('Failed to fetch items:', error);
    }
  };

  const createItem = async (e) => {
    e.preventDefault();
    try {
      await axios.post('/api/items', newItem);
      setNewItem({ name: '', description: '' });
      fetchItems();
    } catch (error) {
      console.error('Failed to create item:', error);
    }
  };

  return (
    <div>
      <form onSubmit={createItem}>
        <input
          type="text"
          placeholder="Name"
          value={newItem.name}
          onChange={(e) => setNewItem({...newItem, name: e.target.value})}
        />
        <input
          type="text"
          placeholder="Description"
          value={newItem.description}
          onChange={(e) => setNewItem({...newItem, description: e.target.value})}
        />
        <button type="submit">Create Item</button>
      </form>
      
      <ul>
        {items.map(item => (
          <li key={item.id}>{item.name} - {item.description}</li>
        ))}
      </ul>
    </div>
  );
}

export default ItemList;"""
            }
        }
    
    def _load_code_patterns(self) -> Dict[str, Any]:
        """Load common code patterns and examples."""
        return {
            "authentication": {
                "jwt": """import jwt
from datetime import datetime, timedelta

def create_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, 'secret_key', algorithm='HS256')

def verify_token(token):
    try:
        payload = jwt.decode(token, 'secret_key', algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None""",
                "bcrypt": """import bcrypt

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed)"""
            },
            "database": {
                "sqlalchemy": """from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

engine = create_engine('sqlite:///app.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)""",
                "mongodb": """from pymongo import MongoClient
from datetime import datetime

client = MongoClient('mongodb://localhost:27017/')
db = client['app_database']

class User:
    def __init__(self, username, email):
        self.username = username
        self.email = email
        self.created_at = datetime.utcnow()
    
    def save(self):
        return db.users.insert_one(self.__dict__)"""
            },
            "api": {
                "rest": """from flask import Flask, request, jsonify
from functools import wraps

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'No token provided'}), 401
        # Verify token logic here
        return f(*args, **kwargs)
    return decorated

@app.route('/api/protected', methods=['GET'])
@require_auth
def protected_route():
    return jsonify({'message': 'Access granted'})""",
                "graphql": """import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType

class User(SQLAlchemyObjectType):
    class Meta:
        model = UserModel

class Query(graphene.ObjectType):
    users = graphene.List(User)
    
    def resolve_users(self, info):
        return UserModel.query.all()

schema = graphene.Schema(query=Query)"""
            }
        }
    
    def get_framework_context(self, framework: str, features: List[str]) -> str:
        """Get framework-specific context and templates."""
        if framework not in self.framework_templates:
            return ""
        
        context = f"Framework: {framework.upper()}\n\n"
        templates = self.framework_templates[framework]
        
        # Add app structure
        if "app_structure" in templates:
            context += "## Application Structure:\n"
            for filename, content in templates["app_structure"].items():
                context += f"\n### {filename}:\n```\n{content}\n```\n"
        
        # Add feature-specific templates
        for feature in features:
            if feature in templates:
                context += f"\n## {feature.upper()} Template:\n```\n{templates[feature]}\n```\n"
        
        return context
    
    def get_code_patterns(self, patterns: List[str]) -> str:
        """Get relevant code patterns."""
        context = "## Code Patterns:\n\n"
        
        for pattern in patterns:
            if pattern in self.code_patterns:
                context += f"### {pattern.upper()}:\n```\n{self.code_patterns[pattern]}\n```\n"
        
        return context
    
    def get_project_context(self, project_dir: str) -> str:
        """Get context from existing project files."""
        if not os.path.exists(project_dir):
            return ""
        
        context = "## Existing Project Context:\n\n"
        
        # Read key files
        key_files = [
            "requirements.txt", "package.json", "app.py", "main.py", 
            "README.md", "config.py", "settings.py"
        ]
        
        for filename in key_files:
            filepath = os.path.join(project_dir, filename)
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        context += f"### {filename}:\n```\n{content}\n```\n"
                except Exception as e:
                    logger.warning(f"Could not read {filepath}: {e}")
        
        return context
    
    def build_agent_context(self, 
                           framework: str, 
                           features: List[str], 
                           patterns: List[str], 
                           project_dir: str = None) -> str:
        """Build comprehensive context for agents."""
        context = "# AGENT CONTEXT\n\n"
        
        # Add framework context
        context += self.get_framework_context(framework, features)
        
        # Add code patterns
        context += self.get_code_patterns(patterns)
        
        # Add project context if available
        if project_dir:
            context += self.get_project_context(project_dir)
        
        return context

# Global context manager instance
context_manager = ContextManager() 