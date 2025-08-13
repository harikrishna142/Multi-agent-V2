#!/bin/bash

# Test runner script for Multi-Agentic Coding Framework

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check if pytest is installed
check_pytest() {
    if ! command -v pytest >/dev/null 2>&1; then
        print_error "pytest is not installed. Please install it first:"
        echo "pip install pytest pytest-cov"
        exit 1
    fi
}

# Run unit tests
run_unit_tests() {
    print_status "Running unit tests..."
    pytest tests/ -v --tb=short
}

# Run tests with coverage
run_coverage_tests() {
    print_status "Running tests with coverage..."
    pytest tests/ -v --cov=core --cov=agents --cov-report=html --cov-report=term
}

# Run specific test file
run_specific_test() {
    local test_file=$1
    print_status "Running specific test: $test_file"
    pytest "$test_file" -v
}

# Run all tests
run_all_tests() {
    print_header "Running All Tests"
    
    # Check pytest installation
    check_pytest
    
    # Run unit tests
    run_unit_tests
    
    # Run coverage tests
    run_coverage_tests
    
    print_status "All tests completed!"
}

# Show usage
show_usage() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  unit        Run unit tests only"
    echo "  coverage    Run tests with coverage report"
    echo "  specific    Run a specific test file"
    echo "  all         Run all tests (default)"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 unit                           # Run unit tests"
    echo "  $0 coverage                       # Run with coverage"
    echo "  $0 specific tests/test_framework.py  # Run specific test"
    echo "  $0 all                            # Run all tests"
}

# Parse command line arguments
case "${1:-all}" in
    unit)
        print_header "Running Unit Tests"
        check_pytest
        run_unit_tests
        ;;
    coverage)
        print_header "Running Tests with Coverage"
        check_pytest
        run_coverage_tests
        ;;
    specific)
        if [ -z "$2" ]; then
            print_error "Please specify a test file"
            show_usage
            exit 1
        fi
        print_header "Running Specific Test"
        check_pytest
        run_specific_test "$2"
        ;;
    all)
        run_all_tests
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