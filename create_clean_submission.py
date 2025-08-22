#!/usr/bin/env python3
"""
Script to create a clean ZIP file for assignment submission.
Only includes essential project files, excluding virtual environment and output files.
"""

import os
import zipfile
from datetime import datetime

def create_clean_submission_zip():
    """Create a clean ZIP file for assignment submission."""
    
    # Define the submission filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    submission_filename = f"Multi_Agentic_Coding_Framework_Clean_Submission_{timestamp}.zip"
    
    # Essential files to include
    essential_files = [
        # Core application files
        "app.py",
        "requirements.txt",
        "README.md",
        "LICENSE",
        ".env.example",
        ".gitignore",
        
        # Core framework
        "core/config.py",
        "core/coordinator.py",
        "core/utils.py",
        "core/validation.py",
        
        # Agents
        "agents/requirement_agent.py",
        "agents/coding_agent.py",
        "agents/review_agent.py",
        "agents/documentation_agent.py",
        "agents/test_agent.py",
        "agents/deployment_agent.py",
        "agents/ui_agent.py",
        
        # Templates and examples
        "templates/README_template.md",
        "examples/simple_calculator.py",
        
        # Documentation
        "INTERVIEW_GUIDE.md",
        "PROJECT_SUMMARY.md",
        "SETUP_GUIDE.md",
        
        # Deployment scripts
        "deploy.sh",
        "run_tests.sh",
        
        # Test files
        "test_basic.py",
        "tests/test_framework.py",
        
        # Submission documentation
        "SUBMISSION_README.md",
    ]
    
    print(f"Creating clean submission ZIP: {submission_filename}")
    
    with zipfile.ZipFile(submission_filename, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file_path in essential_files:
            if os.path.exists(file_path):
                try:
                    zip_file.write(file_path, file_path)
                    print(f"✅ Added: {file_path}")
                except Exception as e:
                    print(f"❌ Error adding {file_path}: {e}")
            else:
                print(f"⚠️  File not found: {file_path}")
    
    # Get file size
    file_size = os.path.getsize(submission_filename)
    file_size_mb = file_size / (1024 * 1024)
    
    print(f"\n🎉 Clean submission ZIP created successfully!")
    print(f"📁 Filename: {submission_filename}")
    print(f"📊 Size: {file_size_mb:.2f} MB ({file_size:,} bytes)")
    
    # List contents for verification
    print(f"\n📋 Contents:")
    with zipfile.ZipFile(submission_filename, 'r') as zip_file:
        file_list = zip_file.namelist()
        for file_path in sorted(file_list):
            print(f"  - {file_path}")
    
    print(f"\n📦 Total files: {len(file_list)}")
    print(f"✅ Ready for submission!")
    
    return submission_filename

if __name__ == "__main__":
    submission_file = create_clean_submission_zip()
    print(f"\n🎯 Clean assignment submission ready!")
    print(f"📤 Submit the file: {submission_file}") 