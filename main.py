"""
Enhanced Multi-Agentic Framework - Main Application
Demonstrates complete application generation with production-ready output.
"""

import asyncio
import json
import time
from typing import Dict, Any
from core.orchestrator import EnhancedOrchestrator
from core.config import config
from core.utils import setup_logging

logger = setup_logging()

def print_banner():
    """Print application banner."""
    print("=" * 80)
    print("🚀 ENHANCED MULTI-AGENTIC FRAMEWORK v2.0")
    print("   Complete Application Generation with Production-Ready Output")
    print("=" * 80)
    print()

def print_phase_1_info():
    """Print Phase 1 implementation information."""
    print("📋 PHASE 1 IMPLEMENTATION: Enhanced Prompts for Complete Applications")
    print("-" * 60)
    print("✅ Enhanced Requirement Agent: Detailed technical specifications")
    print("✅ Enhanced Coding Agent: Complete, production-ready applications")
    print("✅ Enhanced Test Agent: Comprehensive test suites")
    print("✅ Enhanced Deployment Agent: Production deployment configurations")
    print("✅ Enhanced Documentation Agent: Professional documentation")
    print("✅ Enhanced Review Agent: Security and quality analysis")
    print("✅ Enhanced Orchestrator: Coordinated multi-agent workflow")
    print()

def print_example_inputs():
    """Print example natural language inputs."""
    print("💡 EXAMPLE NATURAL LANGUAGE INPUTS:")
    print("-" * 40)
    examples = [
        "Create a complete e-commerce platform with user authentication, product catalog, shopping cart, payment processing, and order management. Include admin panel for product and order management.",
        
        "Build a comprehensive project management application with user registration, team collaboration, task management, file sharing, real-time notifications, and reporting dashboard.",
        
        "Develop a complete event management system with event creation, ticket booking, payment processing, attendee management, and analytics dashboard. Include email notifications and QR code generation.",
        
        "Create a full-stack blog platform with user authentication, article creation and editing, comment system, user profiles, search functionality, and admin panel for content moderation.",
        
        "Build a complete inventory management system with product tracking, supplier management, purchase orders, sales tracking, reporting, and barcode scanning functionality."
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example}")
        print()
    
    print("🎯 KEY DIFFERENCES FROM BASIC VERSION:")
    print("-" * 40)
    print("❌ Basic Version: Generates skeleton code with pass statements")
    print("✅ Enhanced Version: Generates complete, functional applications")
    print("❌ Basic Version: No real implementation")
    print("✅ Enhanced Version: Full business logic implementation")
    print("❌ Basic Version: No database integration")
    print("✅ Enhanced Version: Complete database schema and operations")
    print("❌ Basic Version: No authentication system")
    print("✅ Enhanced Version: JWT-based authentication and authorization")
    print("❌ Basic Version: No frontend implementation")
    print("✅ Enhanced Version: Complete React application with UI")
    print("❌ Basic Version: No deployment configuration")
    print("✅ Enhanced Version: Docker and cloud deployment ready")
    print("❌ Basic Version: No testing")
    print("✅ Enhanced Version: Comprehensive test suites")
    print("❌ Basic Version: No documentation")
    print("✅ Enhanced Version: Professional documentation")
    print("❌ Basic Version: No code review")
    print("✅ Enhanced Version: Security and quality analysis")
    print()

async def generate_complete_application(natural_language_input: str) -> Dict[str, Any]:
    """
    Generate a complete, production-ready application.
    
    Args:
        natural_language_input: Natural language description of the project
        
    Returns:
        Dict containing complete application and all artifacts
    """
    print(f"🎯 GENERATING COMPLETE APPLICATION")
    print(f"Input: {natural_language_input}")
    print("-" * 60)
    
    # Initialize enhanced orchestrator
    orchestrator = EnhancedOrchestrator()
    
    # Get framework capabilities
    capabilities = orchestrator.get_framework_capabilities()
    print(f"Framework: {capabilities['framework_name']} v{capabilities['version']}")
    print(f"Description: {capabilities['description']}")
    print()
    
    # Start generation
    start_time = time.time()
    result = orchestrator.generate_complete_application(natural_language_input)
    generation_time = time.time() - start_time
    
    # Display results
    print("✅ GENERATION COMPLETED")
    print("-" * 40)
    print(f"Project ID: {result.get('project_id', 'N/A')}")
    print(f"Generation Time: {generation_time:.2f} seconds")
    print(f"Status: {result.get('status', 'N/A')}")
    print(f"Success: {result.get('success', False)}")
    print()
    
    # Display metrics
    metrics = result.get('metrics', {})
    print("📊 GENERATION METRICS:")
    print("-" * 30)
    print(f"Total Files: {result.get('total_files', 0)}")
    print(f"Backend Files: {metrics.get('backend_files', 0)}")
    print(f"Frontend Files: {metrics.get('frontend_files', 0)}")
    print(f"Test Files: {metrics.get('test_files', 0)}")
    print(f"Deployment Files: {metrics.get('deployment_files', 0)}")
    print(f"Documentation Files: {metrics.get('documentation_files', 0)}")
    print(f"Review Files: {metrics.get('review_files', 0)}")
    print(f"Total Requirements: {metrics.get('total_requirements', 0)}")
    print(f"Application Type: {metrics.get('application_type', 'N/A')}")
    print(f"Deployment Ready: {metrics.get('deployment_ready', False)}")
    print()
    
    # Display quality metrics
    review_scores = metrics.get('review_scores', {})
    if review_scores:
        print("🔍 QUALITY METRICS:")
        print("-" * 20)
        print(f"Security Score: {review_scores.get('security_score', 0)}/100")
        print(f"Performance Score: {review_scores.get('performance_score', 0)}/100")
        print(f"Code Quality Score: {review_scores.get('code_quality_score', 0)}/100")
        print(f"Test Coverage Score: {review_scores.get('test_coverage_score', 0)}/100")
        print(f"Overall Score: {review_scores.get('overall_score', 0)}/100")
        print()
    
    # Display test coverage
    test_coverage = metrics.get('test_coverage', {})
    if test_coverage:
        expected_coverage = test_coverage.get('expected_coverage', {})
        print("🧪 TEST COVERAGE:")
        print("-" * 20)
        print(f"Unit Tests: {expected_coverage.get('unit_tests', 0)}%")
        print(f"Integration Tests: {expected_coverage.get('integration_tests', 0)}%")
        print(f"End-to-End Tests: {expected_coverage.get('e2e_tests', 0)}%")
        print(f"Overall Coverage: {expected_coverage.get('overall', 0)}%")
        print()
    
    # Display technology stack
    tech_stack = metrics.get('technology_stack', {})
    if tech_stack:
        print("🛠️ TECHNOLOGY STACK:")
        print("-" * 20)
        backend = tech_stack.get('backend', {})
        frontend = tech_stack.get('frontend', {})
        deployment = tech_stack.get('deployment', {})
        
        if backend:
            print(f"Backend: {backend.get('framework', 'N/A')}")
            print(f"Database: {backend.get('database', 'N/A')}")
            print(f"Authentication: {backend.get('authentication', 'N/A')}")
        
        if frontend:
            print(f"Frontend: {frontend.get('framework', 'N/A')}")
            print(f"State Management: {frontend.get('state_management', 'N/A')}")
            print(f"UI Library: {frontend.get('ui_library', 'N/A')}")
        
        if deployment:
            print(f"Containerization: {deployment.get('containerization', 'N/A')}")
            print(f"Orchestration: {deployment.get('orchestration', 'N/A')}")
            print(f"Cloud Provider: {deployment.get('cloud_provider', 'N/A')}")
        print()
    
    # Display file structure
    all_files = result.get('all_files', {})
    if all_files:
        print("📁 GENERATED FILE STRUCTURE:")
        print("-" * 30)
        
        # Group files by category
        file_categories = {
            "Backend": [f for f in all_files.keys() if f.startswith("backend/")],
            "Frontend": [f for f in all_files.keys() if f.startswith("frontend/")],
            "Tests": [f for f in all_files.keys() if "test" in f.lower()],
            "Deployment": [f for f in all_files.keys() if any(x in f.lower() for x in ["docker", "k8s", "kubernetes", "deploy", "pipeline"])],
            "Documentation": [f for f in all_files.keys() if f.endswith((".md", ".txt", ".rst"))],
            "Configuration": [f for f in all_files.keys() if f.endswith((".yml", ".yaml", ".json", ".env", ".ini", ".conf"))]
        }
        
        for category, files in file_categories.items():
            if files:
                print(f"{category} ({len(files)} files):")
                for file in files[:5]:  # Show first 5 files per category
                    print(f"  - {file}")
                if len(files) > 5:
                    print(f"  - ... and {len(files) - 5} more files")
                print()
    
    # Display next steps
    project_summary = result.get('project_summary', {})
    next_steps = project_summary.get('next_steps', [])
    if next_steps:
        print("🚀 NEXT STEPS:")
        print("-" * 15)
        for i, step in enumerate(next_steps[:10], 1):  # Show first 10 steps
            print(f"{i}. {step}")
        if len(next_steps) > 10:
            print(f"... and {len(next_steps) - 10} more steps")
        print()
    
    # Display error if any
    if not result.get('success', False):
        error = result.get('error', 'Unknown error')
        print(f"❌ ERROR: {error}")
        print()
    
    return result

async def demonstrate_enhanced_capabilities():
    """Demonstrate enhanced framework capabilities."""
    print("🎯 DEMONSTRATING ENHANCED CAPABILITIES")
    print("=" * 50)
    
    # Example 1: E-commerce Platform
    print("📦 EXAMPLE 1: E-commerce Platform")
    print("-" * 30)
    ecommerce_input = """Create a complete e-commerce platform with user authentication, 
    product catalog, shopping cart, payment processing, and order management. 
    Include admin panel for product and order management."""
    
    result1 = await generate_complete_application(ecommerce_input)
    
    print("\n" + "="*80 + "\n")
    
    # Example 2: Project Management Application
    print("📋 EXAMPLE 2: Project Management Application")
    print("-" * 40)
    project_input = """Build a comprehensive project management application with user registration, 
    team collaboration, task management, file sharing, real-time notifications, and reporting dashboard."""
    
    result2 = await generate_complete_application(project_input)
    
    # Summary
    print("📊 DEMONSTRATION SUMMARY")
    print("=" * 30)
    print(f"Example 1 (E-commerce): {result1.get('total_files', 0)} files generated")
    print(f"Example 2 (Project Management): {result2.get('total_files', 0)} files generated")
    print(f"Total Generation Time: {result1.get('generation_time', 0) + result2.get('generation_time', 0):.2f} seconds")
    print()

async def main():
    """Main application entry point."""
    print_banner()
    print_phase_1_info()
    print_example_inputs()
    
    # Check if user wants to run demonstration
    print("🤔 Would you like to run the enhanced framework demonstration?")
    print("1. Run demonstration with example applications")
    print("2. Enter custom natural language input")
    print("3. Exit")
    
    try:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            await demonstrate_enhanced_capabilities()
        elif choice == "2":
            print("\n💬 Enter your natural language description:")
            custom_input = input("> ").strip()
            if custom_input:
                await generate_complete_application(custom_input)
            else:
                print("❌ No input provided. Exiting.")
        elif choice == "3":
            print("👋 Goodbye!")
        else:
            print("❌ Invalid choice. Exiting.")
    
    except KeyboardInterrupt:
        print("\n\n👋 Application interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.error(f"Application error: {e}")

if __name__ == "__main__":
    # Run the application
    asyncio.run(main()) 