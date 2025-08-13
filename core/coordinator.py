"""
Main Coordinator for the Multi-Agentic Coding Framework.
Orchestrates all agents in the pipeline to process requirements into complete software solutions.
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from core.config import config
from core.utils import setup_logging, generate_project_id, create_project_structure, save_json
from agents.requirement_agent import RequirementAnalysisAgent
from agents.coding_agent import CodingAgent
from agents.review_agent import CodeReviewAgent
from agents.documentation_agent import DocumentationAgent
from agents.test_agent import TestCaseGenerationAgent
from agents.deployment_agent import DeploymentConfigurationAgent
from agents.ui_agent import StreamlitUIAgent

logger = setup_logging()

class MultiAgentCoordinator:
    """Main coordinator that orchestrates all agents in the pipeline."""
    
    def __init__(self):
        self.requirement_agent = RequirementAnalysisAgent()
        self.coding_agent = CodingAgent()
        self.review_agent = CodeReviewAgent()
        self.documentation_agent = DocumentationAgent()
        self.test_agent = TestCaseGenerationAgent()
        self.deployment_agent = DeploymentConfigurationAgent()
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
            requirement_results = self.requirement_agent.analyze_requirement(natural_language_requirement)
            results["agents"]["requirement_analysis"] = {
                "status": "completed",
                "results": requirement_results,
                "timestamp": datetime.now().isoformat()
            }
            
            # Save requirements
            self.requirement_agent.save_requirements(requirement_results, project_id)
            
            # Step 2: Code Generation
            logger.info("Step 2: Code Generation")
            logger.info(f"Requirement results type: {type(requirement_results)}")
            logger.info(f"Requirement results keys: {list(requirement_results.keys()) if isinstance(requirement_results, dict) else 'Not a dict'}")
            logger.info(f"Project name: {requirement_results.get('project_name', 'N/A') if isinstance(requirement_results, dict) else 'N/A'}")
            logger.info(f"Description: {requirement_results.get('description', 'N/A') if isinstance(requirement_results, dict) else 'N/A'}")
            logger.info(f"Functional requirements count: {len(requirement_results.get('functional_requirements', [])) if isinstance(requirement_results, dict) else 0}")
            if isinstance(requirement_results, dict) and requirement_results.get('functional_requirements'):
                for i, req in enumerate(requirement_results['functional_requirements']):
                    logger.info(f"FR{i+1}: {req.get('title', 'N/A')} - {req.get('description', 'N/A')[:100]}...")
            code_results = self.coding_agent.generate_code(requirement_results, project_id)
            results["agents"]["code_generation"] = {
                "status": "completed",
                "results": code_results,
                "timestamp": datetime.now().isoformat()
            }
            
            # Step 3: Code Review (with iteration if needed)
            logger.info("Step 3: Code Review")
            review_results = self._perform_code_review_with_iteration(
                code_results, requirement_results, project_id
            )
            results["agents"]["code_review"] = {
                "status": "completed",
                "results": review_results,
                "timestamp": datetime.now().isoformat()
            }
            
            # Step 4: Documentation Generation
            logger.info("Step 4: Documentation Generation")
            doc_results = self.documentation_agent.generate_documentation(
                code_results, requirement_results, project_id
            )
            results["agents"]["documentation"] = {
                "status": "completed",
                "results": doc_results,
                "timestamp": datetime.now().isoformat()
            }
            
            # Step 5: Test Generation
            logger.info("Step 5: Test Generation")
            test_results = self.test_agent.generate_tests(
                code_results, requirement_results, project_id
            )
            results["agents"]["test_generation"] = {
                "status": "completed",
                "results": test_results,
                "timestamp": datetime.now().isoformat()
            }
            
            # Step 6: Deployment Configuration
            logger.info("Step 6: Deployment Configuration")
            deployment_results = self.deployment_agent.generate_deployment_config(
                code_results, requirement_results, project_id
            )
            results["agents"]["deployment_config"] = {
                "status": "completed",
                "results": deployment_results,
                "timestamp": datetime.now().isoformat()
            }
            
            # Step 7: UI Generation
            logger.info("Step 7: UI Generation")
            ui_results = self.ui_agent.generate_ui(
                code_results, requirement_results, project_id
            )
            results["agents"]["ui_generation"] = {
                "status": "completed",
                "results": ui_results,
                "timestamp": datetime.now().isoformat()
            }
            
            # Finalize results
            results["end_time"] = datetime.now().isoformat()
            results["final_status"] = "completed"
            results["project_summary"] = self._generate_project_summary(results)
            
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
    
    def _perform_code_review_with_iteration(self, code_results: Dict[str, Any], 
                                          requirements: Dict[str, Any], 
                                          project_id: str) -> Dict[str, Any]:
        """Perform code review with iteration if improvements are needed."""
        max_iterations = config.max_iterations
        current_iteration = 0
        
        while current_iteration < max_iterations:
            logger.info(f"Code review iteration {current_iteration + 1}/{max_iterations}")
            
            # Perform code review
            review_results = self.review_agent.review_code(code_results, requirements)
            
            # Check if revision is needed
            if not review_results.get("requires_revision", False):
                logger.info("Code review passed - no revision needed")
                review_results["iterations"] = current_iteration + 1
                return review_results
            
            # If revision is needed and we haven't reached max iterations
            if current_iteration < max_iterations - 1:
                logger.info("Code revision needed - regenerating code")
                
                # Get revision notes
                revision_notes = review_results.get("revision_notes", "")
                
                # Regenerate code with feedback
                code_results = self.coding_agent.generate_code_with_feedback(
                    requirements, project_id, review_results
                )
                
                current_iteration += 1
            else:
                logger.warning("Maximum iterations reached - accepting current code")
                review_results["iterations"] = current_iteration + 1
                review_results["max_iterations_reached"] = True
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
                with open(results_file, 'r') as f:
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
                new_results = self.deployment_agent.generate_deployment_config(
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