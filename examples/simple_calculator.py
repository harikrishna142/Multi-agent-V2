"""
Simple Calculator Example for Multi-Agentic Coding Framework
This example demonstrates how to use the framework to generate a simple calculator application.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.coordinator import MultiAgentCoordinator

def main():
    """Example: Generate a simple calculator application."""
    
    print("🤖 Multi-Agentic Coding Framework - Calculator Example")
    print("=" * 60)
    
    # Example requirement
    requirement = """
    Create a simple calculator application that can perform basic arithmetic operations 
    (addition, subtraction, multiplication, division) with a user-friendly interface. 
    The application should:
    1. Accept two numbers as input
    2. Allow users to select an operation (+, -, *, /)
    3. Display the result
    4. Handle division by zero errors
    5. Include input validation
    6. Have a clean, intuitive interface
    """
    
    print("📋 Requirement:")
    print(requirement)
    print("\n🚀 Starting multi-agent processing...")
    
    try:
        # Initialize coordinator
        coordinator = MultiAgentCoordinator()
        
        # Process the requirement
        results = coordinator.process_requirement(requirement)
        
        # Display results
        print("\n✅ Processing completed!")
        print(f"📁 Project ID: {results.get('project_id', 'N/A')}")
        print(f"📊 Status: {results.get('final_status', 'N/A')}")
        
        # Show agent results
        print("\n🤖 Agent Results:")
        for agent_name, agent_data in results.get("agents", {}).items():
            status = agent_data.get("status", "unknown")
            print(f"  - {agent_name.replace('_', ' ').title()}: {status}")
        
        # Show generated files
        if "code_generation" in results.get("agents", {}):
            code_results = results["agents"]["code_generation"]["results"]
            if "generated_files" in code_results:
                print(f"\n📄 Generated Files ({len(code_results['generated_files'])}):")
                for filename in code_results["generated_files"].keys():
                    print(f"  - {filename}")
        
        # Show quality metrics
        if "code_review" in results.get("agents", {}):
            review_results = results["agents"]["code_review"]["results"]
            score = review_results.get("overall_score", 0)
            print(f"\n🎯 Code Quality Score: {score}/100")
        
        print("\n🎉 Example completed successfully!")
        print("📁 Check the 'output' directory for generated files.")
        
    except Exception as e:
        print(f"\n❌ Error during processing: {e}")
        print("💡 Make sure you have set up your OpenAI API key in the .env file.")

if __name__ == "__main__":
    main() 