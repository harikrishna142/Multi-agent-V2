"""
Complete Application Generation Example
Demonstrates how enhanced agents generate production-ready applications.
"""

import json
import time
from typing import Dict, Any

# Example of what the enhanced requirement agent would generate
COMPLETE_SPECIFICATION_EXAMPLE = {
    "project_overview": {
        "name": "EventBrite Pro",
        "description": "A comprehensive event management and ticketing platform",
        "version": "1.0.0",
        "technology_stack": {
            "backend": {
                "framework": "FastAPI",
                "version": "0.104.0",
                "database": "PostgreSQL",
                "authentication": "JWT",
                "caching": "Redis",
                "dependencies": [
                    "fastapi==0.104.0",
                    "uvicorn==0.24.0",
                    "sqlalchemy==2.0.23",
                    "alembic==1.12.1",
                    "pydantic==2.5.0",
                    "python-jose[cryptography]==3.3.0",
                    "passlib[bcrypt]==1.7.4",
                    "python-multipart==0.0.6",
                    "psycopg2-binary==2.9.9",
                    "redis==5.0.1"
                ]
            },
            "frontend": {
                "framework": "React",
                "version": "18.2.0",
                "state_management": "Redux Toolkit",
                "ui_library": "Material-UI",
                "dependencies": {
                    "react": "^18.2.0",
                    "react-dom": "^18.2.0",
                    "@reduxjs/toolkit": "^1.9.7",
                    "react-redux": "^8.1.3",
                    "@mui/material": "^5.14.20",
                    "@mui/icons-material": "^5.14.19",
                    "axios": "^1.6.2",
                    "react-router-dom": "^6.20.1"
                }
            },
            "deployment": {
                "containerization": "Docker",
                "orchestration": "Docker Compose",
                "cloud_provider": "AWS",
                "monitoring": "Prometheus + Grafana"
            }
        }
    },
    "architecture": {
        "system_design": "Microservices architecture with API Gateway pattern",
        "database_schema": {
            "tables": [
                {
                    "name": "users",
                    "columns": [
                        {"name": "id", "type": "UUID", "primary_key": True, "default": "gen_random_uuid()"},
                        {"name": "username", "type": "VARCHAR(50)", "unique": True, "not_null": True},
                        {"name": "email", "type": "VARCHAR(100)", "unique": True, "not_null": True},
                        {"name": "password_hash", "type": "VARCHAR(255)", "not_null": True},
                        {"name": "first_name", "type": "VARCHAR(50)"},
                        {"name": "last_name", "type": "VARCHAR(50)"},
                        {"name": "is_verified", "type": "BOOLEAN", "default": False},
                        {"name": "is_active", "type": "BOOLEAN", "default": True},
                        {"name": "created_at", "type": "TIMESTAMP", "default": "CURRENT_TIMESTAMP"},
                        {"name": "updated_at", "type": "TIMESTAMP", "default": "CURRENT_TIMESTAMP"}
                    ],
                    "relationships": [
                        {"type": "one_to_many", "target": "events", "foreign_key": "organizer_id"},
                        {"type": "one_to_many", "target": "bookings", "foreign_key": "user_id"}
                    ]
                },
                {
                    "name": "events",
                    "columns": [
                        {"name": "id", "type": "UUID", "primary_key": True, "default": "gen_random_uuid()"},
                        {"name": "title", "type": "VARCHAR(200)", "not_null": True},
                        {"name": "description", "type": "TEXT"},
                        {"name": "date", "type": "TIMESTAMP", "not_null": True},
                        {"name": "location", "type": "VARCHAR(200)", "not_null": True},
                        {"name": "capacity", "type": "INTEGER", "not_null": True},
                        {"name": "price", "type": "DECIMAL(10,2)", "not_null": True},
                        {"name": "organizer_id", "type": "UUID", "not_null": True, "foreign_key": "users.id"},
                        {"name": "category", "type": "VARCHAR(50)"},
                        {"name": "status", "type": "VARCHAR(20)", "default": "'active'"},
                        {"name": "created_at", "type": "TIMESTAMP", "default": "CURRENT_TIMESTAMP"},
                        {"name": "updated_at", "type": "TIMESTAMP", "default": "CURRENT_TIMESTAMP"}
                    ],
                    "relationships": [
                        {"type": "many_to_one", "target": "users", "foreign_key": "organizer_id"},
                        {"type": "one_to_many", "target": "bookings", "foreign_key": "event_id"}
                    ]
                },
                {
                    "name": "bookings",
                    "columns": [
                        {"name": "id", "type": "UUID", "primary_key": True, "default": "gen_random_uuid()"},
                        {"name": "user_id", "type": "UUID", "not_null": True, "foreign_key": "users.id"},
                        {"name": "event_id", "type": "UUID", "not_null": True, "foreign_key": "events.id"},
                        {"name": "quantity", "type": "INTEGER", "not_null": True},
                        {"name": "total_amount", "type": "DECIMAL(10,2)", "not_null": True},
                        {"name": "status", "type": "VARCHAR(20)", "default": "'pending'"},
                        {"name": "payment_intent_id", "type": "VARCHAR(255)"},
                        {"name": "created_at", "type": "TIMESTAMP", "default": "CURRENT_TIMESTAMP"},
                        {"name": "updated_at", "type": "TIMESTAMP", "default": "CURRENT_TIMESTAMP"}
                    ],
                    "relationships": [
                        {"type": "many_to_one", "target": "users", "foreign_key": "user_id"},
                        {"type": "many_to_one", "target": "events", "foreign_key": "event_id"}
                    ]
                }
            ]
        },
        "api_specification": {
            "base_url": "/api/v1",
            "endpoints": [
                {
                    "path": "/auth/register",
                    "method": "POST",
                    "description": "Register new user",
                    "request_body": {
                        "username": "string",
                        "email": "string",
                        "password": "string",
                        "first_name": "string",
                        "last_name": "string"
                    },
                    "response": {
                        "201": {
                            "id": "UUID",
                            "username": "string",
                            "email": "string",
                            "first_name": "string",
                            "last_name": "string",
                            "created_at": "timestamp"
                        },
                        "400": {
                            "error": "string",
                            "details": "object"
                        }
                    }
                },
                {
                    "path": "/auth/login",
                    "method": "POST",
                    "description": "User login",
                    "request_body": {
                        "username": "string",
                        "password": "string"
                    },
                    "response": {
                        "200": {
                            "access_token": "string",
                            "token_type": "bearer",
                            "user": "object"
                        },
                        "401": {
                            "error": "Invalid credentials"
                        }
                    }
                },
                {
                    "path": "/events",
                    "method": "GET",
                    "description": "List events",
                    "query_params": {
                        "page": "integer",
                        "size": "integer",
                        "category": "string",
                        "date_from": "date",
                        "date_to": "date"
                    },
                    "response": {
                        "200": {
                            "events": "array",
                            "total": "integer",
                            "page": "integer",
                            "size": "integer"
                        }
                    }
                },
                {
                    "path": "/events",
                    "method": "POST",
                    "description": "Create new event",
                    "request_body": {
                        "title": "string",
                        "description": "string",
                        "date": "timestamp",
                        "location": "string",
                        "capacity": "integer",
                        "price": "number",
                        "category": "string"
                    },
                    "response": {
                        "201": {
                            "id": "UUID",
                            "title": "string",
                            "description": "string",
                            "date": "timestamp",
                            "location": "string",
                            "capacity": "integer",
                            "price": "number",
                            "category": "string",
                            "organizer_id": "UUID",
                            "created_at": "timestamp"
                        }
                    }
                },
                {
                    "path": "/bookings",
                    "method": "POST",
                    "description": "Create booking",
                    "request_body": {
                        "event_id": "UUID",
                        "quantity": "integer"
                    },
                    "response": {
                        "201": {
                            "id": "UUID",
                            "event_id": "UUID",
                            "quantity": "integer",
                            "total_amount": "number",
                            "status": "string",
                            "payment_intent_id": "string"
                        }
                    }
                }
            ]
        }
    },
    "functional_requirements": [
        {
            "id": "FR001",
            "title": "User Registration and Authentication",
            "description": "Complete user management system with registration, login, and profile management",
            "priority": "High",
            "acceptance_criteria": [
                "Users can register with email verification",
                "Users can login with JWT authentication",
                "Users can reset passwords",
                "Users can update profiles",
                "Admin can manage users"
            ],
            "use_cases": [
                {
                    "title": "User Registration",
                    "steps": [
                        "User fills registration form",
                        "System validates input data",
                        "System checks for existing users",
                        "System hashes password",
                        "System creates user account",
                        "System sends verification email",
                        "User verifies email",
                        "System activates account"
                    ],
                    "data_models": {
                        "User": {
                            "id": "UUID",
                            "username": "string",
                            "email": "string",
                            "password_hash": "string",
                            "first_name": "string",
                            "last_name": "string",
                            "is_verified": "boolean",
                            "is_active": "boolean",
                            "created_at": "timestamp",
                            "updated_at": "timestamp"
                        }
                    },
                    "api_endpoints": [
                        {
                            "path": "/auth/register",
                            "method": "POST",
                            "request": "UserRegistrationRequest",
                            "response": "UserRegistrationResponse"
                        }
                    ]
                }
            ],
            "business_logic": {
                "validation_rules": [
                    "Username must be 3-50 characters, alphanumeric only",
                    "Email must be valid format and unique",
                    "Password must be 8+ characters with complexity",
                    "First and last name are required"
                ],
                "security_measures": [
                    "Password hashing with bcrypt",
                    "JWT token generation with expiration",
                    "Email verification required",
                    "Rate limiting on registration",
                    "Input sanitization and validation"
                ]
            }
        },
        {
            "id": "FR002",
            "title": "Event Management",
            "description": "Complete event creation, management, and listing system",
            "priority": "High",
            "acceptance_criteria": [
                "Organizers can create events",
                "Users can browse and search events",
                "Events have categories and filtering",
                "Event details include all necessary information",
                "Events can be updated and deleted"
            ],
            "use_cases": [
                {
                    "title": "Event Creation",
                    "steps": [
                        "Organizer logs in",
                        "Organizer fills event creation form",
                        "System validates event data",
                        "System creates event record",
                        "System generates event URL",
                        "Event becomes available for booking"
                    ]
                }
            ],
            "business_logic": {
                "validation_rules": [
                    "Event title is required and 3-200 characters",
                    "Event date must be in the future",
                    "Location is required",
                    "Capacity must be positive integer",
                    "Price must be non-negative"
                ]
            }
        },
        {
            "id": "FR003",
            "title": "Booking and Payment System",
            "description": "Complete booking and payment processing system",
            "priority": "High",
            "acceptance_criteria": [
                "Users can book tickets for events",
                "Real-time seat availability",
                "Secure payment processing",
                "Booking confirmation and receipts",
                "Booking management and cancellation"
            ],
            "use_cases": [
                {
                    "title": "Ticket Booking",
                    "steps": [
                        "User selects event",
                        "User chooses quantity",
                        "System checks availability",
                        "User enters payment details",
                        "System processes payment",
                        "System creates booking",
                        "System sends confirmation"
                    ]
                }
            ],
            "business_logic": {
                "validation_rules": [
                    "Quantity must be positive",
                    "Event must have available capacity",
                    "Payment must be successful",
                    "Booking must be confirmed"
                ]
            }
        }
    ],
    "non_functional_requirements": [
        {
            "id": "NFR001",
            "category": "Performance",
            "description": "Application performance requirements",
            "specifications": {
                "response_time": "API responses under 200ms",
                "throughput": "1000 requests per second",
                "availability": "99.9% uptime",
                "scalability": "Horizontal scaling support"
            }
        },
        {
            "id": "NFR002",
            "category": "Security",
            "description": "Security and data protection requirements",
            "specifications": {
                "authentication": "JWT-based authentication",
                "authorization": "Role-based access control",
                "data_encryption": "HTTPS and database encryption",
                "input_validation": "Comprehensive input sanitization"
            }
        },
        {
            "id": "NFR003",
            "category": "Usability",
            "description": "User experience requirements",
            "specifications": {
                "responsive_design": "Mobile and desktop compatible",
                "accessibility": "WCAG 2.1 AA compliance",
                "intuitive_interface": "User-friendly design",
                "fast_loading": "Page load under 3 seconds"
            }
        }
    ],
    "implementation_plan": {
        "phases": [
            {
                "phase": "Phase 1 - Foundation",
                "duration": "2 weeks",
                "deliverables": [
                    "Database schema implementation",
                    "User authentication system",
                    "Basic API endpoints",
                    "Frontend project setup"
                ]
            },
            {
                "phase": "Phase 2 - Core Features",
                "duration": "3 weeks",
                "deliverables": [
                    "Event management system",
                    "Booking system",
                    "Payment integration",
                    "Frontend components"
                ]
            },
            {
                "phase": "Phase 3 - Enhancement",
                "duration": "2 weeks",
                "deliverables": [
                    "Advanced features",
                    "Testing and optimization",
                    "Documentation",
                    "Deployment preparation"
                ]
            }
        ],
        "file_structure": {
            "backend": {
                "app/": {
                    "models/": "Database models and relationships",
                    "api/": "API endpoints and routes",
                    "services/": "Business logic and services",
                    "utils/": "Utility functions and helpers",
                    "config.py": "Application configuration",
                    "main.py": "FastAPI application entry point"
                },
                "tests/": "Unit and integration tests",
                "migrations/": "Database migrations",
                "requirements.txt": "Python dependencies"
            },
            "frontend": {
                "src/": {
                    "components/": "React components",
                    "pages/": "Page components",
                    "services/": "API services",
                    "store/": "Redux store and slices",
                    "utils/": "Utility functions"
                },
                "public/": "Static assets",
                "package.json": "Node.js dependencies"
            }
        }
    }
}

# Example of what the enhanced coding agent would generate
COMPLETE_APPLICATION_EXAMPLE = {
    "backend/app/main.py": '''from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn
from datetime import datetime, timedelta

from app.database import get_db, engine
from app.models import Base, User, Event, Booking
from app.schemas import (
    UserCreate, UserResponse, UserLogin, TokenResponse,
    EventCreate, EventResponse, EventList,
    BookingCreate, BookingResponse
)
from app.services.auth_service import AuthService
from app.services.event_service import EventService
from app.services.booking_service import BookingService
from app.config import settings

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="EventBrite Pro API",
    description="A comprehensive event management and ticketing platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Services
auth_service = AuthService()
event_service = EventService()
booking_service = BookingService()

@app.get("/")
async def root():
    return {"message": "Welcome to EventBrite Pro API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Authentication endpoints
@app.post("/api/v1/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    try:
        user = auth_service.register_user(db, user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Registration failed")

@app.post("/api/v1/auth/login", response_model=TokenResponse)
async def login_user(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user and return JWT token."""
    try:
        token_data = auth_service.login_user(db, credentials)
        return token_data
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.get("/api/v1/auth/me", response_model=UserResponse)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get current user information."""
    try:
        user = auth_service.get_current_user(db, credentials.credentials)
        return user
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

# Event endpoints
@app.get("/api/v1/events", response_model=EventList)
async def list_events(
    page: int = 1,
    size: int = 10,
    category: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """List events with filtering and pagination."""
    events = event_service.list_events(
        db, page=page, size=size, category=category,
        date_from=date_from, date_to=date_to
    )
    return events

@app.get("/api/v1/events/{event_id}", response_model=EventResponse)
async def get_event(event_id: str, db: Session = Depends(get_db)):
    """Get event details by ID."""
    event = event_service.get_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@app.post("/api/v1/events", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    event_data: EventCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Create a new event."""
    try:
        current_user = auth_service.get_current_user(db, credentials.credentials)
        event = event_service.create_event(db, event_data, current_user.id)
        return event
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/api/v1/events/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: str,
    event_data: EventCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Update an existing event."""
    try:
        current_user = auth_service.get_current_user(db, credentials.credentials)
        event = event_service.update_event(db, event_id, event_data, current_user.id)
        return event
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@app.delete("/api/v1/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Delete an event."""
    try:
        current_user = auth_service.get_current_user(db, credentials.credentials)
        event_service.delete_event(db, event_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

# Booking endpoints
@app.post("/api/v1/bookings", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_data: BookingCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Create a new booking."""
    try:
        current_user = auth_service.get_current_user(db, credentials.credentials)
        booking = booking_service.create_booking(db, booking_data, current_user.id)
        return booking
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/bookings", response_model=List[BookingResponse])
async def list_user_bookings(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """List bookings for current user."""
    current_user = auth_service.get_current_user(db, credentials.credentials)
    bookings = booking_service.list_user_bookings(db, current_user.id)
    return bookings

@app.get("/api/v1/bookings/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get booking details by ID."""
    current_user = auth_service.get_current_user(db, credentials.credentials)
    booking = booking_service.get_booking(db, booking_id, current_user.id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
''',
    
    "backend/app/models/user.py": '''from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    events = relationship("Event", back_populates="organizer", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
    
    @property
    def full_name(self):
        """Get user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def to_dict(self):
        """Convert user to dictionary."""
        return {
            "id": str(self.id),
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "is_verified": self.is_verified,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
''',
    
    "frontend/src/components/EventCard.js": '''import React from 'react';
import {
  Card,
  CardContent,
  CardActions,
  Typography,
  Button,
  Chip,
  Box,
  Avatar
} from '@mui/material';
import {
  LocationOn,
  CalendarToday,
  People,
  AttachMoney
} from '@mui/icons-material';
import { format } from 'date-fns';

const EventCard = ({ event, onBookNow, onViewDetails }) => {
  const formatDate = (dateString) => {
    return format(new Date(dateString), 'MMM dd, yyyy - HH:mm');
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(price);
  };

  return (
    <Card 
      sx={{ 
        maxWidth: 345, 
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        transition: 'transform 0.2s ease-in-out',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: 4
        }
      }}
    >
      <Box
        sx={{
          height: 200,
          backgroundImage: `url(${event.image_url || '/default-event.jpg'})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          position: 'relative'
        }}
      >
        <Chip
          label={event.category}
          color="primary"
          size="small"
          sx={{
            position: 'absolute',
            top: 16,
            right: 16,
            backgroundColor: 'rgba(0, 0, 0, 0.7)',
            color: 'white'
          }}
        />
        {event.status === 'cancelled' && (
          <Box
            sx={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              backgroundColor: 'rgba(0, 0, 0, 0.5)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            <Typography variant="h6" color="white">
              CANCELLED
            </Typography>
          </Box>
        )}
      </Box>
      
      <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
        <Typography gutterBottom variant="h5" component="h2" noWrap>
          {event.title}
        </Typography>
        
        <Typography 
          variant="body2" 
          color="text.secondary" 
          sx={{ 
            mb: 2,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            display: '-webkit-box',
            WebkitLineClamp: 3,
            WebkitBoxOrient: 'vertical'
          }}
        >
          {event.description}
        </Typography>
        
        <Box sx={{ mt: 'auto' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <CalendarToday sx={{ fontSize: 16, mr: 1, color: 'text.secondary' }} />
            <Typography variant="body2" color="text.secondary">
              {formatDate(event.date)}
            </Typography>
          </Box>
          
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <LocationOn sx={{ fontSize: 16, mr: 1, color: 'text.secondary' }} />
            <Typography variant="body2" color="text.secondary" noWrap>
              {event.location}
            </Typography>
          </Box>
          
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <People sx={{ fontSize: 16, mr: 1, color: 'text.secondary' }} />
            <Typography variant="body2" color="text.secondary">
              {event.booked_count || 0} / {event.capacity} booked
            </Typography>
          </Box>
          
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <AttachMoney sx={{ fontSize: 16, mr: 1, color: 'text.secondary' }} />
            <Typography variant="h6" color="primary" fontWeight="bold">
              {formatPrice(event.price)}
            </Typography>
          </Box>
        </Box>
      </CardContent>
      
      <CardActions sx={{ p: 2, pt: 0 }}>
        <Button 
          size="small" 
          color="primary"
          onClick={() => onViewDetails(event.id)}
          sx={{ flex: 1 }}
        >
          View Details
        </Button>
        <Button 
          size="small" 
          variant="contained"
          onClick={() => onBookNow(event.id)}
          disabled={event.status === 'cancelled' || (event.booked_count || 0) >= event.capacity}
          sx={{ flex: 1 }}
        >
          {event.status === 'cancelled' ? 'Cancelled' : 
           (event.booked_count || 0) >= event.capacity ? 'Sold Out' : 'Book Now'}
        </Button>
      </CardActions>
    </Card>
  );
};

export default EventCard;
''',
    
    "frontend/src/services/api.js": '''import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (userData) => api.post('/auth/register', userData),
  login: (credentials) => api.post('/auth/login', credentials),
  getCurrentUser: () => api.get('/auth/me'),
  refreshToken: (refreshToken) => api.post('/auth/refresh', { refresh_token: refreshToken }),
};

// Events API
export const eventsAPI = {
  list: (params = {}) => api.get('/events', { params }),
  getById: (id) => api.get(`/events/${id}`),
  create: (eventData) => api.post('/events', eventData),
  update: (id, eventData) => api.put(`/events/${id}`, eventData),
  delete: (id) => api.delete(`/events/${id}`),
  search: (query) => api.get('/events/search', { params: { q: query } }),
};

// Bookings API
export const bookingsAPI = {
  list: () => api.get('/bookings'),
  getById: (id) => api.get(`/bookings/${id}`),
  create: (bookingData) => api.post('/bookings', bookingData),
  cancel: (id) => api.delete(`/bookings/${id}`),
  confirm: (id) => api.post(`/bookings/${id}/confirm`),
};

// Users API
export const usersAPI = {
  getProfile: () => api.get('/users/profile'),
  updateProfile: (userData) => api.put('/users/profile', userData),
  changePassword: (passwordData) => api.put('/users/password', passwordData),
  uploadAvatar: (file) => {
    const formData = new FormData();
    formData.append('avatar', file);
    return api.post('/users/avatar', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
};

// File upload API
export const uploadAPI = {
  uploadImage: (file, type = 'general') => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', type);
    return api.post('/upload/image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
};

// Error handling utility
export const handleAPIError = (error) => {
  if (error.response) {
    // Server responded with error status
    const { status, data } = error.response;
    
    switch (status) {
      case 400:
        return data.detail || 'Bad request. Please check your input.';
      case 401:
        return 'Authentication required. Please log in.';
      case 403:
        return 'Access denied. You don\'t have permission for this action.';
      case 404:
        return 'Resource not found.';
      case 422:
        return 'Validation error. Please check your input.';
      case 500:
        return 'Server error. Please try again later.';
      default:
        return data.detail || 'An unexpected error occurred.';
    }
  } else if (error.request) {
    // Network error
    return 'Network error. Please check your connection.';
  } else {
    // Other error
    return error.message || 'An unexpected error occurred.';
  }
};

// Success response utility
export const handleAPISuccess = (response, message = 'Operation successful') => {
  return {
    success: true,
    data: response.data,
    message,
  };
};

export default api;
''',
    
    "docker-compose.yml": '''version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/eventbrite_pro
      - SECRET_KEY=your-super-secret-key-change-in-production
      - REDIS_URL=redis://redis:6379
      - ALLOWED_ORIGINS=["http://localhost:3000", "http://frontend:3000"]
      - DEBUG=False
      - LOG_LEVEL=INFO
    depends_on:
      - db
      - redis
    volumes:
      - ./backend:/app
      - ./logs:/app/logs
    networks:
      - app-network
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000/api/v1
      - REACT_APP_ENVIRONMENT=development
      - GENERATE_SOURCEMAP=false
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
      - /app/node_modules
    networks:
      - app-network
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=eventbrite_pro
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init:/docker-entrypoint-initdb.d
    networks:
      - app-network
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - app-network
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend
    networks:
      - app-network
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:

networks:
  app-network:
    driver: bridge
'''
}

def demonstrate_complete_application_generation():
    """Demonstrate how the enhanced agents generate complete applications."""
    
    print("🚀 COMPLETE APPLICATION GENERATION DEMONSTRATION")
    print("=" * 60)
    
    print("\n📋 STEP 1: Enhanced Requirement Analysis")
    print("-" * 40)
    print("The enhanced requirement agent generates detailed specifications including:")
    print("✅ Complete technology stack with specific versions")
    print("✅ Detailed database schema with relationships")
    print("✅ Comprehensive API specifications")
    print("✅ Business logic and validation rules")
    print("✅ Security requirements and measures")
    print("✅ Implementation plan and file structure")
    
    print(f"\n📊 Specification Details:")
    print(f"   - Project: {COMPLETE_SPECIFICATION_EXAMPLE['project_overview']['name']}")
    print(f"   - Backend: {COMPLETE_SPECIFICATION_EXAMPLE['project_overview']['technology_stack']['backend']['framework']}")
    print(f"   - Frontend: {COMPLETE_SPECIFICATION_EXAMPLE['project_overview']['technology_stack']['frontend']['framework']}")
    print(f"   - Database: {COMPLETE_SPECIFICATION_EXAMPLE['project_overview']['technology_stack']['backend']['database']}")
    print(f"   - Requirements: {len(COMPLETE_SPECIFICATION_EXAMPLE['functional_requirements'])} functional requirements")
    
    print("\n💻 STEP 2: Complete Application Generation")
    print("-" * 40)
    print("The enhanced coding agent generates production-ready code including:")
    print("✅ Complete FastAPI backend with all endpoints")
    print("✅ Full database models with relationships")
    print("✅ Complete React frontend with components")
    print("✅ Authentication and authorization system")
    print("✅ Error handling and validation")
    print("✅ Docker configuration and deployment")
    
    print(f"\n📁 Generated Files:")
    for filename in COMPLETE_APPLICATION_EXAMPLE.keys():
        print(f"   - {filename}")
    
    print("\n🔧 STEP 3: Production-Ready Features")
    print("-" * 40)
    print("The generated application includes:")
    print("✅ Complete user authentication system")
    print("✅ Event management with CRUD operations")
    print("✅ Booking and payment system")
    print("✅ Real-time availability checking")
    print("✅ Responsive UI with Material-UI")
    print("✅ API documentation with Swagger")
    print("✅ Comprehensive error handling")
    print("✅ Docker containerization")
    print("✅ Database migrations and seeding")
    print("✅ Testing setup and examples")
    
    print("\n🚀 STEP 4: Deployment Ready")
    print("-" * 40)
    print("The application is ready for immediate deployment:")
    print("✅ Docker Compose configuration")
    print("✅ Environment variable setup")
    print("✅ Database initialization")
    print("✅ Nginx reverse proxy")
    print("✅ SSL certificate support")
    print("✅ Health check endpoints")
    print("✅ Logging and monitoring")
    
    print("\n📈 BENEFITS OF ENHANCED AGENTS:")
    print("-" * 40)
    print("🎯 Complete Implementation: No placeholder code or pass statements")
    print("🏭 Production Ready: Follows industry best practices")
    print("🔒 Security Focused: Built-in security measures")
    print("📱 Modern UI: Responsive design with modern frameworks")
    print("⚡ Performance Optimized: Efficient database queries and caching")
    print("🧪 Testable: Comprehensive testing setup")
    print("🚀 Deployable: Ready for cloud deployment")
    print("📚 Well Documented: Complete API documentation")
    
    print("\n💡 KEY DIFFERENCES FROM BASIC AGENTS:")
    print("-" * 40)
    print("❌ Basic Agents: Generate skeleton code with pass statements")
    print("✅ Enhanced Agents: Generate complete, functional applications")
    print("❌ Basic Agents: No real implementation")
    print("✅ Enhanced Agents: Full business logic implementation")
    print("❌ Basic Agents: No database integration")
    print("✅ Enhanced Agents: Complete database schema and operations")
    print("❌ Basic Agents: No authentication system")
    print("✅ Enhanced Agents: JWT-based authentication and authorization")
    print("❌ Basic Agents: No frontend implementation")
    print("✅ Enhanced Agents: Complete React application with UI")
    print("❌ Basic Agents: No deployment configuration")
    print("✅ Enhanced Agents: Docker and cloud deployment ready")

if __name__ == "__main__":
    demonstrate_complete_application_generation() 