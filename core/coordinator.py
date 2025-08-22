"""
Main Coordinator for the Multi-Agentic Coding Framework.
Orchestrates all agents in the pipeline to process requirements into complete software solutions.
"""

import asyncio
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import io

from core.config import config
from core.utils import setup_logging, generate_project_id, create_project_structure, save_json
from agents.requirement_agent import RequirementAgent
from agents.coding_agent import CodingAgent
from agents.review_agent import ReviewAgent
from agents.documentation_agent import DocumentationAgent
from agents.test_agent import TestAgent
from agents.deployment_agent import DeploymentAgent
from agents.ui_agent import StreamlitUIAgent

logger = setup_logging()

class MultiAgentCoordinator:
    """Main coordinator that orchestrates all agents in the pipeline."""
    
    def __init__(self):
        self.requirement_agent = RequirementAgent()
        self.coding_agent = CodingAgent()
        self.review_agent = ReviewAgent()
        self.documentation_agent = DocumentationAgent()
        self.test_agent = TestAgent()
        self.deployment_agent = DeploymentAgent()
        self.ui_agent = StreamlitUIAgent()
        
        self.project_results = {}
    
    def process_requirement(self, natural_language_requirement: str) -> Dict[str, Any]:
        """
        Process a natural language requirement through the complete agent pipeline.
        
        Args:
            natural_language_requirement: The original requirement in natural language
            
        Returns:
            Dict containing all results from the pipeline
        """
        logger.info("Starting multi-agent processing pipeline")
        
        # Generate unique project ID
        project_id = generate_project_id(natural_language_requirement)
        logger.info(f"Generated project ID: {project_id}")
        
        # Create project structure
        project_dirs = create_project_structure(project_id, config.output_dir)
        
        # Initialize results
        results = {
            "project_id": project_id,
            "original_requirement": natural_language_requirement,
            "start_time": datetime.now().isoformat(),
            "agents": {},
            "final_status": "processing"
        }
        
        try:
            # Step 1: Requirement Analysis
            logger.info("Step 1: Requirement Analysis")
            requirement_results = self.requirement_agent.analyze_requirements(natural_language_requirement, project_id)
            results["agents"]["requirement_analysis"] = {
                "status": "completed",
                "results": requirement_results,
                "timestamp": datetime.now().isoformat()
            }
            
            # Step 2: Code Generation
            logger.info("Step 2: Code Generation")
            logger.info(f"Requirement results type: {type(requirement_results)}")
            logger.info(f"Requirement results keys: {list(requirement_results.keys()) if isinstance(requirement_results, dict) else 'Not a dict'}")
            
            # Extract specifications from requirement results
            specifications = requirement_results.get("specifications", requirement_results)
            
            # Ensure specifications is a dictionary
            if not isinstance(specifications, dict):
                logger.error(f"Specifications is not a dict: {type(specifications)}")
                specifications = {
                    "project_overview": {
                        "name": "Fallback Project",
                        "description": natural_language_requirement,
                        "technology_stack": {
                            "backend_framework": "flask",
                            "frontend_framework": "react",
                            "database": "sqlite"
                        }
                    },
                    "functional_requirements": [
                        {
                            "name": "Basic Functionality",
                            "description": "Implement basic application features",
                            "priority": "High"
                        }
                    ]
                }
            
            code_results = self.coding_agent.generate_code(specifications, project_id)
            results["agents"]["code_generation"] = {
                "status": "completed",
                "results": code_results,
                "timestamp": datetime.now().isoformat()
            }
            
            # Step 3: Code Review (with iteration if needed)
            logger.info("Step 3: Code Review")
            print(code_results)
            review_results = self.review_agent.review_code(
                specifications, code_results, project_id
            )
            results["agents"]["code_review"] = {
                "status": "completed",
                "results": review_results,
                "timestamp": datetime.now().isoformat()
            }
            
            # Step 4: Documentation Generation
            logger.info("Step 4: Documentation Generation")
            doc_results = self.documentation_agent.generate_documentation(
                specifications, code_results, project_id
            )
            results["agents"]["documentation"] = {
                "status": "completed",
                "results": doc_results,
                "timestamp": datetime.now().isoformat()
            }
            
            # Step 5: Test Generation
            logger.info("Step 5: Test Generation")
            test_results = self.test_agent.generate_tests(
                specifications, code_results, project_id
            )
            results["agents"]["test_generation"] = {
                "status": "completed",
                "results": test_results,
                "timestamp": datetime.now().isoformat()
            }
            
            # Step 6: Deployment Configuration
            logger.info("Step 6: Deployment Configuration")
            deployment_results = self.deployment_agent.generate_deployment(
                specifications, code_results, project_id
            )
            results["agents"]["deployment_config"] = {
                "status": "completed",
                "results": deployment_results,
                "timestamp": datetime.now().isoformat()
            }
            
            # Combine all generated files
            all_files = {}
            all_files.update(code_results.get("generated_files", {}))
            all_files.update(test_results.get("test_files", {}))
            all_files.update(deployment_results.get("deployment_files", {}))
            all_files.update(doc_results.get("documentation_files", {}))
            all_files.update(review_results.get("review_files", {}))
            
            # Save all files to disk
            self._save_all_files(all_files, project_id)
            
            # Create ZIP file automatically
            self._create_project_zip(project_id)
            
            # Finalize results
            results["end_time"] = datetime.now().isoformat()
            results["final_status"] = "completed"
            results["project_summary"] = self._generate_project_summary(results)
            results["all_files"] = all_files
            results["total_files"] = len(all_files)
            
            # Save complete results
            self._save_complete_results(results, project_id)
            
            logger.info(f"Multi-agent processing completed successfully for project {project_id}")
            return results
            
        except Exception as e:
            logger.error(f"Error in multi-agent processing: {e}")
            results["end_time"] = datetime.now().isoformat()
            results["final_status"] = "failed"
            results["error"] = str(e)
            
            # Save partial results
            self._save_complete_results(results, project_id)
            
            return results
    
    def process_requirement_with_progress(self, natural_language_requirement: str, progress_callback=None) -> Dict[str, Any]:
        """
        Process a natural language requirement with real-time progress updates.
        
        Args:
            natural_language_requirement: The original requirement in natural language
            progress_callback: Optional callback function to report progress updates
            
        Returns:
            Dict containing all results from the pipeline
        """
        logger.info("Starting multi-agent processing pipeline with progress tracking")
        
        def update_progress(step: str, message: str, progress: float, details: List[str] = None):
            """Helper function to update progress"""
            if progress_callback:
                progress_callback({
                    "step": step,
                    "message": message,
                    "progress": progress,
                    "details": details or []
                })
            logger.info(f"Progress: {step} - {message} ({progress:.1%})")
        
        # Generate unique project ID
        project_id = generate_project_id(natural_language_requirement)
        logger.info(f"Generated project ID: {project_id}")
        
        update_progress("initialization", "Initializing project structure", 0.05, ["Generating project ID", "Creating directories"])
        
        # Create project structure
        project_dirs = create_project_structure(project_id, config.output_dir)
        
        # Initialize results
        results = {
            "project_id": project_id,
            "original_requirement": natural_language_requirement,
            "start_time": datetime.now().isoformat(),
            "agents": {},
            "final_status": "processing",
            "progress_updates": []
        }
        
        try:
            # Step 1: Requirement Analysis
            update_progress("requirement_analysis", "Analyzing requirements and creating specifications", 0.1, 
                          ["Extracting functional requirements", "Defining technical architecture", "Identifying technology stack"])
            
            requirement_results = self.requirement_agent.analyze_requirements(natural_language_requirement, project_id)
            results["agents"]["requirement_analysis"] = {
                "status": "completed",
                "results": requirement_results,
                "timestamp": datetime.now().isoformat()
            }
            
            update_progress("requirement_analysis", "Requirement analysis completed", 0.2, 
                          ["Technical specifications created", "Project structure defined", "Technology stack identified"])
            
            # Step 2: Code Generation
            update_progress("code_generation", "Generating complete application code", 0.25, 
                          ["Creating backend API", "Building frontend components", "Implementing business logic"])
            
            # Extract specifications from requirement results
            specifications = requirement_results.get("specifications", requirement_results)
            
            # Ensure specifications is a dictionary
            if not isinstance(specifications, dict):
                logger.error(f"Specifications is not a dict: {type(specifications)}")
                specifications = {
                    "project_overview": {
                        "name": "Fallback Project",
                        "description": natural_language_requirement,
                        "technology_stack": {
                            "backend_framework": "flask",
                            "frontend_framework": "react",
                            "database": "sqlite"
                        }
                    },
                    "functional_requirements": [
                        {
                            "name": "Basic Functionality",
                            "description": "Implement basic application features",
                            "priority": "high"
                        }
                    ]
                }
            
            coding_results = self.coding_agent.generate_code(specifications, project_id)
            results["agents"]["code_generation"] = {
                "status": "completed",
                "results": coding_results,
                "timestamp": datetime.now().isoformat()
            }
            
            update_progress("code_generation", "Code generation completed", 0.4, 
                          ["Backend API created", "Frontend components built", "Database schema implemented"])
            
            # Step 3: Code Review and Iterative Improvement
            update_progress("code_review", "Performing code review and iterative improvements", 0.45, 
                          ["Analyzing code quality", "Identifying improvements", "Performing iterative enhancements"])
            
            # Get generated files for review
            generated_files = coding_results.get("generated_files", {})
            
            # Perform iterative code review and improvement
            review_results = self._perform_code_review_with_iteration(
                coding_results, specifications, project_id, progress_callback
            )
            
            results["agents"]["code_review"] = {
                "status": "completed",
                "results": review_results,
                "timestamp": datetime.now().isoformat()
            }
            
            update_progress("code_review", "Code review and improvements completed", 0.6, 
                          ["Code quality assessed", "Improvements implemented", "Security analysis completed"])
            
            # Step 4: Test Generation
            update_progress("test_generation", "Generating comprehensive test suites", 0.65, 
                          ["Creating unit tests", "Building integration tests", "Setting up test configuration"])
            
            test_results = self.test_agent.generate_tests(specifications, generated_files, project_id)
            results["agents"]["test_generation"] = {
                "status": "completed",
                "results": test_results,
                "timestamp": datetime.now().isoformat()
            }
            
            update_progress("test_generation", "Test generation completed", 0.75, 
                          ["Unit tests created", "Integration tests built", "Test coverage achieved"])
            
            # Step 5: Documentation Generation
            update_progress("documentation", "Generating professional documentation", 0.8, 
                          ["Creating API documentation", "Writing user guides", "Preparing deployment guides"])
            
            documentation_results = self.documentation_agent.generate_documentation(specifications, generated_files, project_id)
            results["agents"]["documentation"] = {
                "status": "completed",
                "results": documentation_results,
                "timestamp": datetime.now().isoformat()
            }
            
            update_progress("documentation", "Documentation generation completed", 0.85, 
                          ["API docs created", "User guides written", "README files prepared"])
            
            # Step 6: Deployment Configuration
            update_progress("deployment", "Creating deployment configurations", 0.9, 
                          ["Docker configuration", "Kubernetes manifests", "CI/CD pipelines"])
            
            deployment_results = self.deployment_agent.generate_deployment(specifications, generated_files, project_id)
            results["agents"]["deployment"] = {
                "status": "completed",
                "results": deployment_results,
                "timestamp": datetime.now().isoformat()
            }
            
            update_progress("deployment", "Deployment configuration completed", 0.95, 
                          ["Docker files created", "K8s manifests prepared", "CI/CD configured"])
            
            # Step 7: Final Integration and ZIP Creation
            update_progress("finalization", "Finalizing project and creating download package", 0.98, 
                          ["Integrating all components", "Creating comprehensive ZIP", "Preparing project summary"])
            
            # Create comprehensive project ZIP
            self._create_project_zip(project_id)
            
            # Update final status
            results["final_status"] = "completed"
            results["end_time"] = datetime.now().isoformat()
            
            update_progress("finalization", "Project generation completed successfully!", 1.0, 
                          ["All components integrated", "Download package ready", "Project ready for deployment"])
            
            logger.info("Multi-agent processing pipeline completed successfully")
            
        except Exception as e:
            logger.error(f"Error in multi-agent processing pipeline: {e}")
            results["final_status"] = "failed"
            results["error"] = str(e)
            results["end_time"] = datetime.now().isoformat()
            
            update_progress("error", f"Processing failed: {str(e)}", 1.0, 
                          ["Error occurred during processing", "Check logs for details", "Try again with different requirements"])
        
        return results
    
    def _perform_code_review_with_iteration(self, code_results: Dict[str, Any], 
                                          specifications: Dict[str, Any], 
                                          project_id: str, 
                                          progress_callback=None) -> Dict[str, Any]:
        """Perform code review with iteration if improvements are needed."""
        from core.project_memory import ProjectMemoryManager
        
        # Initialize project memory
        memory_manager = ProjectMemoryManager(project_id)
        memory_manager.set_project_specifications(specifications)
        
        max_iterations = 3  # Fixed to 3 iterations as requested
        current_iteration = 0
        
        while current_iteration < max_iterations:
            logger.info(f"Code review iteration {current_iteration + 1}/{max_iterations}")
            
            # Update progress for current iteration
            if progress_callback:
                progress_callback({
                    "step": "code_review",
                    "message": f"Code review iteration {current_iteration + 1}/{max_iterations}",
                    "progress": 0.45 + (current_iteration * 0.05),
                    "details": [f"Analyzing code quality", f"Checking for improvements", f"Iteration {current_iteration + 1}"]
                })
            
            # Get generated files from code results
            generated_files = code_results.get("generated_files", {})
            
            # Add current code to memory
            for file_path, content in generated_files.items():
                memory_manager.add_code_snippet(
                    content=content,
                    file_path=file_path,
                    line_start=1,
                    line_end=len(content.split('\n')),
                    snippet_type='function',
                    context=f"Iteration {current_iteration + 1} code"
                )
            
            # Get project context for review agent
            project_context = memory_manager.get_code_context()
            
            # Perform code review with context
            review_results = self.review_agent.review_code(specifications, generated_files, project_id)
            
            # Check if code has issues that need fixing
            code_issues = review_results.get("code_issues", [])
            needs_iteration = review_results.get("needs_iteration", False)
            
            # Record iteration in memory
            iteration_record = {
                "iteration": current_iteration + 1,
                "quality_score": review_results.get("quality_score", 0),
                "issues_found": len(code_issues),
                "status": "completed" if not needs_iteration else "needs_improvement",
                "recommendations": review_results.get("recommendations", [])
            }
            memory_manager.add_iteration_record(iteration_record)
            
            # If no issues found or quality is acceptable, stop iterations
            if not needs_iteration or len(code_issues) == 0:
                logger.info(f"Code review passed - no issues found or quality acceptable")
                review_results["iterations"] = current_iteration + 1
                review_results["final_status"] = "completed"
                return review_results
            
            # If we haven't reached max iterations, continue with improvements
            if current_iteration < max_iterations - 1:
                logger.info(f"Code revision needed - {len(code_issues)} issues found - regenerating code")
                
                # Get improvement instructions
                improvement_instructions = review_results.get("improvement_instructions", [])
                
                # Add to memory
                for instruction in improvement_instructions:
                    memory_manager.add_improvement_instruction(instruction)
                
                # Get project context for coding agent
                coding_context = memory_manager.get_code_context("incomplete implementation")
                
                # Create enhanced specifications with context and instructions
                enhanced_specifications = specifications.copy()
                enhanced_specifications["project_context"] = coding_context
                enhanced_specifications["improvement_instructions"] = improvement_instructions
                enhanced_specifications["current_iteration"] = current_iteration + 1
                enhanced_specifications["max_iterations"] = max_iterations
                enhanced_specifications["existing_code"] = generated_files
                
                # Update progress for code regeneration
                if progress_callback:
                    progress_callback({
                        "step": "code_generation",
                        "message": f"Regenerating code with improvements (iteration {current_iteration + 1})",
                        "progress": 0.5 + (current_iteration * 0.02),
                        "details": ["Applying improvement instructions", "Updating existing code", "Enhancing implementation"]
                    })
                
                # Regenerate code with enhanced context
                code_results = self.coding_agent.generate_code(enhanced_specifications, project_id)
                
                current_iteration += 1
                memory_manager.increment_iteration()
            else:
                logger.warning("Maximum iterations reached - accepting current code")
                review_results["iterations"] = current_iteration + 1
                review_results["max_iterations_reached"] = True
                review_results["final_status"] = "max_iterations_reached"
                return review_results
        
        return review_results
    
    def _generate_project_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive project summary."""
        summary = {
            "project_id": results["project_id"],
            "status": results["final_status"],
            "total_agents": len(results["agents"]),
            "completed_agents": len([agent for agent in results["agents"].values() 
                                   if agent.get("status") == "completed"]),
            "agent_summary": {},
            "files_generated": {},
            "quality_metrics": {}
        }
        
        # Agent summary
        for agent_name, agent_results in results["agents"].items():
            summary["agent_summary"][agent_name] = {
                "status": agent_results.get("status", "unknown"),
                "timestamp": agent_results.get("timestamp", ""),
                "has_error": "error" in agent_results.get("results", {})
            }
        
        # Files generated summary
        for agent_name, agent_results in results["agents"].items():
            agent_data = agent_results.get("results", {})
            
            if "generated_files" in agent_data:
                summary["files_generated"][agent_name] = len(agent_data["generated_files"])
            elif "generated_documentation" in agent_data:
                summary["files_generated"][agent_name] = len(agent_data["generated_documentation"])
            elif "generated_tests" in agent_data:
                summary["files_generated"][agent_name] = len(agent_data["generated_tests"])
            elif "generated_configs" in agent_data:
                summary["files_generated"][agent_name] = len(agent_data["generated_configs"])
            elif "generated_ui" in agent_data:
                summary["files_generated"][agent_name] = len(agent_data["generated_ui"])
        
        # Quality metrics
        if "code_review" in results["agents"]:
            review_data = results["agents"]["code_review"]["results"]
            summary["quality_metrics"]["code_quality_score"] = review_data.get("overall_score", 0)
            summary["quality_metrics"]["passes_review"] = review_data.get("passes_review", False)
            summary["quality_metrics"]["critical_issues"] = len(review_data.get("critical_issues", []))
            summary["quality_metrics"]["total_issues"] = (
                len(review_data.get("critical_issues", [])) +
                len(review_data.get("high_priority_issues", [])) +
                len(review_data.get("medium_priority_issues", [])) +
                len(review_data.get("low_priority_issues", []))
            )
        
        if "test_generation" in results["agents"]:
            test_data = results["agents"]["test_generation"]["results"]
            summary["quality_metrics"]["test_coverage"] = test_data.get("test_coverage", {})
        
        return summary
    
    def _save_complete_results(self, results: Dict[str, Any], project_id: str) -> str:
        """Save complete results to a JSON file."""
        filename = f"{project_id}_complete_results.json"
        return save_json(results, filename, config.output_dir)
    
    def get_project_status(self, project_id: str) -> Dict[str, Any]:
        """Get the status of a specific project."""
        try:
            results_file = f"{config.output_dir}/{project_id}_complete_results.json"
            with open(results_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"error": "Project not found"}
        except Exception as e:
            return {"error": f"Error loading project: {e}"}
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """List all processed projects."""
        import os
        import glob
        
        projects = []
        results_files = glob.glob(f"{config.output_dir}/*_complete_results.json")
        
        for results_file in results_files:
            try:
                # Try UTF-8 first, then fallback to other encodings
                try:
                    with open(results_file, 'r', encoding='utf-8') as f:
                        results = json.load(f)
                except UnicodeDecodeError:
                    # Try with error handling
                    with open(results_file, 'r', encoding='utf-8', errors='ignore') as f:
                        results = json.load(f)
                
                projects.append({
                    "project_id": results.get("project_id"),
                    "status": results.get("final_status"),
                    "start_time": results.get("start_time"),
                    "end_time": results.get("end_time"),
                    "original_requirement": results.get("original_requirement", "")[:100] + "..."
                })
            except Exception as e:
                logger.warning(f"Error loading project from {results_file}: {e}")
                # Add a placeholder entry for corrupted projects
                project_id = os.path.basename(results_file).replace('_complete_results.json', '')
                projects.append({
                    "project_id": project_id,
                    "status": "corrupted",
                    "start_time": "N/A",
                    "end_time": "N/A",
                    "original_requirement": "Project file corrupted - unable to load"
                })
        
        return sorted(projects, key=lambda x: x.get("start_time", ""), reverse=True)
    
    def get_agent_outputs(self, project_id: str, agent_name: str) -> Dict[str, Any]:
        """Get specific outputs from a particular agent."""
        try:
            results = self.get_project_status(project_id)
            if "error" in results:
                return results
            
            agent_results = results.get("agents", {}).get(agent_name, {})
            if not agent_results:
                return {"error": f"Agent {agent_name} not found in project {project_id}"}
            
            return agent_results.get("results", {})
        except Exception as e:
            return {"error": f"Error retrieving agent outputs: {e}"}
    
    def regenerate_agent_output(self, project_id: str, agent_name: str) -> Dict[str, Any]:
        """Regenerate output from a specific agent."""
        try:
            # Get original results
            results = self.get_project_status(project_id)
            if "error" in results:
                return results
            
            # Get original requirement
            original_requirement = results.get("original_requirement")
            if not original_requirement:
                return {"error": "Original requirement not found"}
            
            # Regenerate based on agent type
            if agent_name == "requirement_analysis":
                new_results = self.requirement_agent.analyze_requirement(original_requirement)
            elif agent_name == "code_generation":
                req_results = self.get_agent_outputs(project_id, "requirement_analysis")
                new_results = self.coding_agent.generate_code(req_results, project_id)
            elif agent_name == "code_review":
                req_results = self.get_agent_outputs(project_id, "requirement_analysis")
                code_results = self.get_agent_outputs(project_id, "code_generation")
                new_results = self.review_agent.review_code(code_results, req_results)
            elif agent_name == "documentation":
                req_results = self.get_agent_outputs(project_id, "requirement_analysis")
                code_results = self.get_agent_outputs(project_id, "code_generation")
                new_results = self.documentation_agent.generate_documentation(
                    code_results, req_results, project_id
                )
            elif agent_name == "test_generation":
                req_results = self.get_agent_outputs(project_id, "requirement_analysis")
                code_results = self.get_agent_outputs(project_id, "code_generation")
                new_results = self.test_agent.generate_tests(
                    code_results, req_results, project_id
                )
            elif agent_name == "deployment_config":
                req_results = self.get_agent_outputs(project_id, "requirement_analysis")
                code_results = self.get_agent_outputs(project_id, "code_generation")
                new_results = self.deployment_agent.generate_deployment(
                    code_results, req_results, project_id
                )
            elif agent_name == "ui_generation":
                req_results = self.get_agent_outputs(project_id, "requirement_analysis")
                code_results = self.get_agent_outputs(project_id, "code_generation")
                new_results = self.ui_agent.generate_ui(
                    code_results, req_results, project_id
                )
            else:
                return {"error": f"Unknown agent: {agent_name}"}
            
            # Update the results
            results["agents"][agent_name]["results"] = new_results
            results["agents"][agent_name]["timestamp"] = datetime.now().isoformat()
            
            # Save updated results
            self._save_complete_results(results, project_id)
            
            return {
                "status": "success",
                "agent": agent_name,
                "project_id": project_id,
                "results": new_results
            }
            
        except Exception as e:
            return {"error": f"Error regenerating agent output: {e}"} 

    def _save_all_files(self, all_files: Dict[str, str], project_id: str) -> None:
        """Save all generated files to disk."""
        import os
        
        project_dir = f"{config.output_dir}/{project_id}"
        os.makedirs(project_dir, exist_ok=True)
        
        logger.info(f"Saving {len(all_files)} generated files to {project_dir}")
        
        for filename, content in all_files.items():
            try:
                # Create nested directories if needed
                file_path = os.path.join(project_dir, filename)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                # Save the file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                logger.info(f"Saved file: {filename}")
            except Exception as e:
                logger.error(f"Failed to save file {filename}: {e}")
    
    def _create_project_zip(self, project_id: str) -> None:
        """Create a comprehensive ZIP file with all generated files from all agents."""
        import zipfile
        import os
        from datetime import datetime
        
        try:
            # Create a comprehensive project directory
            comprehensive_dir = f"output/comprehensive_projects/{project_id}"
            os.makedirs(comprehensive_dir, exist_ok=True)
            
            # Define all agent directories to collect files from
            agent_directories = {
                "code": f"output/projects/{project_id}",
                "review": f"output/review_reports/{project_id}",
                "documentation": f"output/documentation/{project_id}",
                "tests": f"output/tests/{project_id}",
                "deployment": f"output/deployment/{project_id}"
            }
            
            # Handle requirements separately to only include current project files
            requirements_dir = f"output/requirement_specifications"
            if os.path.exists(requirements_dir):
                # Find only the current project's requirement files
                current_project_requirements = []
                for file in os.listdir(requirements_dir):
                    if project_id in file and file.endswith('.json'):
                        current_project_requirements.append(file)
                
                if current_project_requirements:
                    agent_directories["requirements"] = {
                        "dir": requirements_dir,
                        "files": current_project_requirements
                    }
            
            # Collect all files from all agents
            collected_files = {}
            
            for agent_name, agent_dir in agent_directories.items():
                if isinstance(agent_dir, dict):
                    # Special handling for requirements (filtered files)
                    if agent_name == "requirements":
                        requirements_dir = agent_dir["dir"]
                        requirement_files = agent_dir["files"]
                        
                        for file in requirement_files:
                            source_path = os.path.join(requirements_dir, file)
                            organized_path = f"{agent_name}/{file}"
                            collected_files[organized_path] = source_path
                            logger.info(f"Added requirement file: {organized_path}")
                else:
                    # Regular directory handling
                    if os.path.exists(agent_dir):
                        logger.info(f"Collecting files from {agent_name}: {agent_dir}")
                        
                        # Walk through the agent directory
                        for root, dirs, files in os.walk(agent_dir):
                            for file in files:
                                if file.endswith('.zip'):  # Skip ZIP files
                                    continue
                                    
                                source_path = os.path.join(root, file)
                                # Create relative path within the agent directory
                                relative_path = os.path.relpath(source_path, agent_dir)
                                # Create organized path in comprehensive directory
                                organized_path = f"{agent_name}/{relative_path}"
                                
                                collected_files[organized_path] = source_path
            
            # Create the comprehensive ZIP file
            zip_filepath = os.path.join(comprehensive_dir, f"{project_id}_complete_project.zip")
            
            with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add all collected files to ZIP
                for organized_path, source_path in collected_files.items():
                    try:
                        zipf.write(source_path, organized_path)
                        logger.info(f"Added to ZIP: {organized_path}")
                    except Exception as e:
                        logger.warning(f"Failed to add {source_path} to ZIP: {e}")
                
                # Add a comprehensive README file
                readme_content = self._generate_comprehensive_readme(project_id, collected_files)
                zipf.writestr("README.md", readme_content)
                
                # Add project summary
                summary_content = self._generate_project_summary_for_zip(project_id)
                zipf.writestr("PROJECT_SUMMARY.md", summary_content)
            
            logger.info(f"Comprehensive ZIP package created: {zip_filepath}")
            logger.info(f"Total files included: {len(collected_files)}")
            
            # Also create a simple ZIP in the original location for backward compatibility
            simple_zip_path = f"output/projects/{project_id}/project.zip"
            os.makedirs(os.path.dirname(simple_zip_path), exist_ok=True)
            
            with zipfile.ZipFile(simple_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for organized_path, source_path in collected_files.items():
                    try:
                        zipf.write(source_path, organized_path)
                    except Exception as e:
                        logger.warning(f"Failed to add {source_path} to simple ZIP: {e}")
            
            logger.info(f"Simple ZIP package also created: {simple_zip_path}")
            
        except Exception as e:
            logger.error(f"Failed to create comprehensive ZIP package: {e}")
            import traceback
            traceback.print_exc()
    
    def _generate_comprehensive_readme(self, project_id: str, collected_files: Dict[str, str]) -> str:
        """Generate a comprehensive README for the ZIP package."""
        from datetime import datetime
        
        # Count files by category
        file_counts = {}
        for file_path in collected_files.keys():
            category = file_path.split('/')[0] if '/' in file_path else 'other'
            file_counts[category] = file_counts.get(category, 0) + 1
        
        readme_content = f"""# Complete Project Package - {project_id}

Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 📦 Package Contents

This ZIP file contains a complete project generated by the Multi-Agentic Coding Framework, including all code, documentation, tests, and deployment configurations.

### 📁 Directory Structure

"""
        
        # Add directory structure
        for category, count in file_counts.items():
            readme_content += f"- **{category.title()}** ({count} files)\n"
        
        readme_content += f"""
### 🔍 What's Included

#### 📄 Code Files (`code/`)
- Complete application source code
- Backend and frontend implementations
- Configuration files
- Database schemas

#### 📋 Review Reports (`review/`)
- Code quality analysis
- Security assessments
- Performance evaluations
- Improvement recommendations

#### 📚 Documentation (`documentation/`)
- Project README files
- API documentation
- User guides
- Developer guides
- Deployment guides

#### 🧪 Test Suites (`tests/`)
- Unit tests
- Integration tests
- End-to-end tests
- Test configurations

#### 🚀 Deployment Configs (`deployment/`)
- Docker configurations
- Kubernetes manifests
- CI/CD pipelines
- Environment configurations

#### 📋 Requirements (`requirements/`)
- Project specifications
- Technical requirements
- Architecture documents

## 🚀 Getting Started

1. **Extract the ZIP file** to your desired location
2. **Navigate to the `code/` directory** to find the main application
3. **Check the `documentation/` directory** for setup instructions
4. **Review the `deployment/` directory** for deployment options
5. **Run tests** from the `tests/` directory

## 📖 Documentation

- **README.md** (this file) - Package overview
- **PROJECT_SUMMARY.md** - Detailed project summary
- **documentation/** - Complete project documentation

## 🔧 Quick Start

```bash
# Navigate to the code directory
cd code/

# Install dependencies (if applicable)
pip install -r requirements.txt  # Python
npm install                     # Node.js

# Run the application
python app.py                   # Python
npm start                       # Node.js
```

## 🧪 Running Tests

```bash
# Navigate to tests directory
cd tests/

# Run tests
pytest                         # Python
npm test                       # Node.js
```

## 🚀 Deployment

Check the `deployment/` directory for:
- Docker configurations
- Kubernetes manifests
- CI/CD pipelines
- Environment setup

## 📞 Support

This project was generated by the Multi-Agentic Coding Framework.
For questions or issues, refer to the documentation in the `documentation/` directory.

---
*Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
        
        return readme_content
    
    def _generate_project_summary_for_zip(self, project_id: str) -> str:
        """Generate a project summary for the ZIP package."""
        import json
        import os
        
        summary_content = f"""# Project Summary - {project_id}

## 📊 Project Overview

This document provides a comprehensive summary of the generated project.

## 📁 File Statistics

"""
        
        # Count files by category
        agent_directories = {
            "Code Files": f"output/projects/{project_id}",
            "Review Reports": f"output/review_reports/{project_id}",
            "Documentation": f"output/documentation/{project_id}",
            "Test Suites": f"output/tests/{project_id}",
            "Deployment Configs": f"output/deployment/{project_id}",
            "Requirements": f"output/requirement_specifications"
        }
        
        for category, directory in agent_directories.items():
            if os.path.exists(directory):
                file_count = 0
                for root, dirs, files in os.walk(directory):
                    file_count += len([f for f in files if not f.endswith('.zip')])
                
                summary_content += f"- **{category}**: {file_count} files\n"
            else:
                summary_content += f"- **{category}**: 0 files (directory not found)\n"
        
        # Try to load project results if available
        results_file = f"output/projects/{project_id}/results.json"
        if os.path.exists(results_file):
            try:
                with open(results_file, 'r', encoding='utf-8') as f:
                    results = json.load(f)
                
                summary_content += f"""
## 📈 Project Metrics

- **Project ID**: {results.get('project_id', project_id)}
- **Status**: {results.get('final_status', 'Unknown')}
- **Total Agents**: {len(results.get('agents', {}))}
- **Completed Agents**: {len([a for a in results.get('agents', {}).values() if a.get('status') == 'completed'])}

## 🤖 Agent Summary

"""
                
                for agent_name, agent_data in results.get('agents', {}).items():
                    status = agent_data.get('status', 'unknown')
                    timestamp = agent_data.get('timestamp', 'N/A')
                    summary_content += f"- **{agent_name.title()}**: {status} ({timestamp})\n"
                
            except Exception as e:
                summary_content += f"\n## ⚠️ Note\nCould not load detailed project results: {e}\n"
        
        summary_content += f"""
## 📋 Next Steps

1. **Review the code** in the `code/` directory
2. **Read the documentation** in the `documentation/` directory
3. **Run the tests** in the `tests/` directory
4. **Deploy the application** using files in the `deployment/` directory

## 🔗 Related Files

- **README.md** - Package overview and getting started guide
- **code/** - Complete application source code
- **documentation/** - Project documentation and guides
- **tests/** - Test suites and configurations
- **deployment/** - Deployment configurations and scripts
- **review/** - Code review reports and analysis

---
*Generated by Multi-Agentic Coding Framework*
"""
        
        return summary_content
    
    def download_project(self, project_id: str) -> bytes:
        """Download project as a comprehensive ZIP file."""
        import zipfile
        import os
        import io
        
        try:
            # First, try to find the comprehensive ZIP
            comprehensive_zip_path = f"output/comprehensive_projects/{project_id}/{project_id}_complete_project.zip"
            
            if os.path.exists(comprehensive_zip_path):
                logger.info(f"Found comprehensive ZIP: {comprehensive_zip_path}")
                with open(comprehensive_zip_path, 'rb') as f:
                    return f.read()
            
            # If comprehensive ZIP doesn't exist, try the simple ZIP
            simple_zip_path = f"output/projects/{project_id}/project.zip"
            
            if os.path.exists(simple_zip_path):
                logger.info(f"Found simple ZIP: {simple_zip_path}")
                with open(simple_zip_path, 'rb') as f:
                    return f.read()
            
            # If no ZIP exists, create one on-the-fly
            logger.info(f"No existing ZIP found, creating comprehensive ZIP for {project_id}")
            
            # Create comprehensive ZIP in memory
            zip_buffer = io.BytesIO()
            
            # Define all agent directories to collect files from
            agent_directories = {
                "code": f"output/projects/{project_id}",
                "review": f"output/review_reports/{project_id}",
                "documentation": f"output/documentation/{project_id}",
                "tests": f"output/tests/{project_id}",
                "deployment": f"output/deployment/{project_id}"
            }
            
            # Handle requirements separately to only include current project files
            requirements_dir = f"output/requirement_specifications"
            if os.path.exists(requirements_dir):
                # Find only the current project's requirement files
                current_project_requirements = []
                for file in os.listdir(requirements_dir):
                    if project_id in file and file.endswith('.json'):
                        current_project_requirements.append(file)
                
                if current_project_requirements:
                    agent_directories["requirements"] = {
                        "dir": requirements_dir,
                        "files": current_project_requirements
                    }
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Collect and add all files from all agents
                for agent_name, agent_dir in agent_directories.items():
                    if isinstance(agent_dir, dict):
                        # Special handling for requirements (filtered files)
                        if agent_name == "requirements":
                            requirements_dir = agent_dir["dir"]
                            requirement_files = agent_dir["files"]
                            
                            for file in requirement_files:
                                source_path = os.path.join(requirements_dir, file)
                                organized_path = f"{agent_name}/{file}"
                                
                                try:
                                    zipf.write(source_path, organized_path)
                                    logger.info(f"Added to ZIP: {organized_path}")
                                except Exception as e:
                                    logger.warning(f"Failed to add {source_path} to ZIP: {e}")
                    else:
                        # Regular directory handling
                        if os.path.exists(agent_dir):
                            logger.info(f"Adding files from {agent_name}: {agent_dir}")
                            
                            for root, dirs, files in os.walk(agent_dir):
                                for file in files:
                                    if file.endswith('.zip'):  # Skip ZIP files
                                        continue
                                        
                                    source_path = os.path.join(root, file)
                                    relative_path = os.path.relpath(source_path, agent_dir)
                                    organized_path = f"{agent_name}/{relative_path}"
                                    
                                    try:
                                        zipf.write(source_path, organized_path)
                                        logger.info(f"Added to ZIP: {organized_path}")
                                    except Exception as e:
                                        logger.warning(f"Failed to add {source_path} to ZIP: {e}")
                
                # Add comprehensive README
                collected_files = {f"{agent_name}/file": "path" for agent_name in agent_directories.keys()}
                readme_content = self._generate_comprehensive_readme(project_id, collected_files)
                zipf.writestr("README.md", readme_content)
                
                # Add project summary
                summary_content = self._generate_project_summary_for_zip(project_id)
                zipf.writestr("PROJECT_SUMMARY.md", summary_content)
            
            zip_buffer.seek(0)
            return zip_buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error creating comprehensive ZIP for project {project_id}: {e}")
            raise 

    def get_project_history(self) -> List[Dict[str, Any]]:
        """Get project history - alias for list_projects."""
        return self.list_projects()
    
    def cleanup_corrupted_projects(self) -> Dict[str, Any]:
        """Clean up corrupted project files."""
        import os
        import glob
        
        cleanup_report = {
            "total_projects": 0,
            "corrupted_projects": 0,
            "fixed_projects": 0,
            "errors": []
        }
        
        try:
            # Find all project directories
            project_dirs = glob.glob(f"{config.output_dir}/project_*")
            cleanup_report["total_projects"] = len(project_dirs)
            
            for project_dir in project_dirs:
                project_id = os.path.basename(project_dir)
                results_file = os.path.join(project_dir, "results.json")
                
                if os.path.exists(results_file):
                    try:
                        # Try to read the JSON file
                        with open(results_file, 'r', encoding='utf-8') as f:
                            json.load(f)
                    except (json.JSONDecodeError, UnicodeDecodeError) as e:
                        cleanup_report["corrupted_projects"] += 1
                        try:
                            # Try to fix by re-encoding
                            with open(results_file, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                            with open(results_file, 'w', encoding='utf-8') as f:
                                f.write(content)
                            cleanup_report["fixed_projects"] += 1
                        except Exception as fix_error:
                            cleanup_report["errors"].append(f"Failed to fix {project_id}: {fix_error}")
            
            return cleanup_report
            
        except Exception as e:
            cleanup_report["errors"].append(f"Cleanup failed: {e}")
            return cleanup_report
    
    def debug_output_directory(self) -> Dict[str, Any]:
        """Debug the output directory structure."""
        import os
        import glob
        
        debug_info = {
            "output_dir": config.output_dir,
            "exists": os.path.exists(config.output_dir),
            "total_projects": 0,
            "project_list": [],
            "errors": []
        }
        
        try:
            if os.path.exists(config.output_dir):
                # Count project directories
                project_dirs = glob.glob(f"{config.output_dir}/project_*")
                debug_info["total_projects"] = len(project_dirs)
                
                for project_dir in project_dirs:
                    project_id = os.path.basename(project_dir)
                    project_info = {
                        "project_id": project_id,
                        "exists": True,
                        "file_count": 0,
                        "total_size": 0,
                        "has_results": False
                    }
                    
                    try:
                        files = os.listdir(project_dir)
                        project_info["file_count"] = len(files)
                        
                        for file in files:
                            file_path = os.path.join(project_dir, file)
                            if os.path.isfile(file_path):
                                project_info["total_size"] += os.path.getsize(file_path)
                            if file == "results.json":
                                project_info["has_results"] = True
                        
                        debug_info["project_list"].append(project_info)
                    except Exception as e:
                        project_info["error"] = str(e)
                        debug_info["project_list"].append(project_info)
            
            return debug_info
            
        except Exception as e:
            debug_info["errors"].append(f"Debug failed: {e}")
            return debug_info
    
    def debug_project_files(self, project_id: str) -> Dict[str, Any]:
        """Debug a specific project's files."""
        import os
        
        debug_info = {
            "project_id": project_id,
            "exists": False,
            "file_count": 0,
            "files": [],
            "total_size": 0,
            "errors": []
        }
        
        try:
            project_dir = f"{config.output_dir}/{project_id}"
            debug_info["exists"] = os.path.exists(project_dir)
            
            if debug_info["exists"]:
                files = os.listdir(project_dir)
                debug_info["file_count"] = len(files)
                
                for file in files:
                    file_path = os.path.join(project_dir, file)
                    file_info = {
                        "name": file,
                        "size": os.path.getsize(file_path) if os.path.isfile(file_path) else 0,
                        "type": "file" if os.path.isfile(file_path) else "directory"
                    }
                    debug_info["files"].append(file_info)
                    debug_info["total_size"] += file_info["size"]
            
            return debug_info
            
        except Exception as e:
            debug_info["errors"].append(f"Debug failed: {e}")
            return debug_info
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents."""
        return {
            "requirement_agent": "active",
            "coding_agent": "active", 
            "review_agent": "active",
            "documentation_agent": "active",
            "test_agent": "active",
            "deployment_agent": "active",
            "ui_agent": "active"
        }
    
    def get_framework_capabilities(self) -> Dict[str, Any]:
        """Get framework capabilities."""
        return {
            "backend_frameworks": ["Flask", "FastAPI", "Django", "Spring Boot", "Express.js"],
            "frontend_frameworks": ["React", "Vue.js", "Angular", "Next.js"],
            "databases": ["SQLite", "PostgreSQL", "MySQL", "MongoDB"],
            "deployment": ["Docker", "Kubernetes", "AWS", "Azure", "GCP"]
        } 