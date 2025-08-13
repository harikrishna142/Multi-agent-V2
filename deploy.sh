#!/bin/bash

# Deployment script for Multi-Agentic Coding Framework
# This script sets up and deploys the framework

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[HEADER]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python_version() {
    if command_exists python3; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        REQUIRED_VERSION="3.8"
        
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
            print_status "Python $PYTHON_VERSION is installed and compatible"
            return 0
        else
            print_error "Python $PYTHON_VERSION is installed but version 3.8+ is required"
            return 1
        fi
    else
        print_error "Python 3 is not installed"
        return 1
    fi
}

# Function to install Python dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt
        print_status "Dependencies installed successfully"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
}

# Function to set up environment
setup_environment() {
    print_status "Setting up environment..."
    
    # Create output directory
    mkdir -p output
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        if [ -f "env_example.txt" ]; then
            cp env_example.txt .env
            print_warning "Created .env file from template. Please update with your API keys."
        else
            print_warning "No .env template found. Please create .env file manually."
        fi
    fi
    
    # Set permissions
    chmod +x deploy.sh
    chmod +x run_tests.sh
}

# Function to run tests
run_tests() {
    print_status "Running tests..."
    
    if command_exists pytest; then
        pytest tests/ -v
        print_status "Tests completed"
    else
        print_warning "pytest not found. Skipping tests."
    fi
}

# Function to start the application
start_application() {
    print_status "Starting Multi-Agentic Coding Framework..."
    
    if command_exists streamlit; then
        print_status "Starting Streamlit application..."
        streamlit run app.py --server.port 8501 --server.address 0.0.0.0
    else
        print_error "Streamlit not found. Please install it first: pip install streamlit"
        exit 1
    fi
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  install     Install dependencies and set up environment"
    echo "  test        Run tests"
    echo "  start       Start the application"
    echo "  deploy      Full deployment (install + test + start)"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 install    # Install dependencies"
    echo "  $0 deploy     # Full deployment"
    echo "  $0 start      # Start the application"
}

# Main deployment function
main_deploy() {
    print_header "Multi-Agentic Coding Framework Deployment"
    print_status "Starting deployment process..."
    
    # Check Python version
    if ! check_python_version; then
        print_error "Python version check failed. Please install Python 3.8+"
        exit 1
    fi
    
    # Install dependencies
    install_dependencies
    
    # Setup environment
    setup_environment
    
    # Run tests
    run_tests
    
    print_status "Deployment completed successfully!"
    print_status "You can now start the application with: $0 start"
}

# Parse command line arguments
case "${1:-deploy}" in
    install)
        print_header "Installing Multi-Agentic Coding Framework"
        check_python_version
        install_dependencies
        setup_environment
        print_status "Installation completed!"
        ;;
    test)
        print_header "Running Tests"
        run_tests
        ;;
    start)
        print_header "Starting Application"
        start_application
        ;;
    deploy)
        main_deploy
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        print_error "Unknown option: $1"
        show_usage
        exit 1
        ;;
esac 