"""
Enhanced Multi-Agentic Framework Orchestrator
Coordinates enhanced agents for complete application generation.
"""

import autogen
import time
import json
import os
from typing import Dict, Any, List, Tuple
from core.config import get_agent_config, config
from core.utils import save_to_file, setup_logging
from agents.requirement_agent import RequirementAgent
from agents.coding_agent import CodingAgent
from agents.test_agent import TestAgent
from agents.deployment_agent import DeploymentAgent
from agents.documentation_agent import DocumentationAgent
from agents.review_agent import ReviewAgent

logger = setup_logging()

class EnhancedOrchestrator:
    """Enhanced orchestrator that coordinates agents for complete application generation."""
    
    def __init__(self):
        self.requirement_agent = RequirementAgent()
        self.coding_agent = CodingAgent()
        self.test_agent = TestAgent()
        self.deployment_agent = DeploymentAgent()
        self.documentation_agent = DocumentationAgent()
        self.review_agent = ReviewAgent()
        
        logger.info("Enhanced Multi-Agentic Framework initialized with all agents")
    
    def generate_complete_application(self, natural_language_input: str, project_id: str = None) -> Dict[str, Any]:
        """Generate a complete, production-ready application with iterative processing and feedback loops."""
        start_time = time.time()
        logger.info(f"Starting complete application generation with iterative processing for: {natural_language_input[:100]}...")
        
        try:
            # Phase 1: Iterative Requirement Analysis
            logger.info("Phase 1: Iterative Requirement Analysis")
            requirement_result = self._iterative_requirement_analysis(natural_language_input, project_id)
            
            if requirement_result.get("fallback_mode", False):
                logger.warning("Requirement analysis failed, using fallback specifications")
            
            specifications = requirement_result.get("specifications", {})
            # Use provided project_id or generate one
            if project_id is None:
                project_id = requirement_result.get("project_id", f"project_{int(time.time())}")
            else:
                # Update the requirement result with the provided project_id
                requirement_result["project_id"] = project_id
            
            # Phase 2: Iterative Code Generation with Review Feedback
            logger.info("Phase 2: Iterative Code Generation with Review Feedback")
            coding_result, review_result = self._iterative_code_generation_with_review(specifications, project_id)
            
            generated_files = coding_result.get("generated_files", {})
            
            # Phase 3: Comprehensive Testing
            logger.info("Phase 3: Comprehensive Testing")
            test_result = self.test_agent.generate_tests(specifications, project_id)
            
            if test_result.get("fallback_mode", False):
                logger.warning("Test generation failed, using fallback tests")
            
            test_files = test_result.get("test_files", {})
            
            # Phase 4: Production Deployment
            logger.info("Phase 4: Production Deployment")
            deployment_result = self.deployment_agent.generate_deployment(specifications, project_id)
            
            if deployment_result.get("fallback_mode", False):
                logger.warning("Deployment generation failed, using fallback deployment")
            
            deployment_files = deployment_result.get("deployment_files", {})
            
            # Phase 5: Complete Documentation
            logger.info("Phase 5: Complete Documentation")
            documentation_result = self.documentation_agent.generate_documentation(specifications, project_id)
            
            if documentation_result.get("fallback_mode", False):
                logger.warning("Documentation generation failed, using fallback documentation")
            
            documentation_files = documentation_result.get("documentation_files", {})
            
            # Combine all results
            all_files = {}
            all_files.update(generated_files)
            all_files.update(test_files)
            all_files.update(deployment_files)
            all_files.update(documentation_files)
            all_files.update(review_result.get("review_files", {}))
            
            # Debug logging to see what files were generated
            logger.info(f"Generated files summary:")
            logger.info(f"  - Coding agent: {len(generated_files)} files")
            logger.info(f"  - Test agent: {len(test_files)} files")
            logger.info(f"  - Deployment agent: {len(deployment_files)} files")
            logger.info(f"  - Documentation agent: {len(documentation_files)} files")
            logger.info(f"  - Review agent: {len(review_result.get('review_files', {}))} files")
            logger.info(f"  - Total files: {len(all_files)} files")
            
            if all_files:
                logger.info(f"Sample files: {list(all_files.keys())[:5]}")
            else:
                logger.warning("No files were generated by any agent!")
            
            # Generate comprehensive project summary
            project_summary = self._generate_project_summary(
                natural_language_input,
                requirement_result,
                coding_result,
                test_result,
                deployment_result,
                documentation_result,
                review_result,
                all_files
            )
            
            # Save project summary
            project_dir = f"{config.output_dir}/{project_id}"
            save_to_file(json.dumps(project_summary, indent=2), "project-summary.json", project_dir)
            
            # Save all generated files to the filesystem
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
            
            # Calculate generation time
            generation_time = time.time() - start_time
            
            # Final result
            result = {
                "project_id": project_id,
                "natural_language_input": natural_language_input,
                "generation_time": generation_time,
                "project_summary": project_summary,
                "all_files": all_files,
                "total_files": len(all_files),
                "specifications": specifications,
                "generated_files": generated_files,
                "test_files": test_files,
                "deployment_files": deployment_files,
                "documentation_files": documentation_files,
                "review_files": review_result.get("review_files", {}),
                "iterations": {
                    "requirement_iterations": requirement_result.get("iterations", 1),
                    "code_review_iterations": review_result.get("iterations", 1)
                },
                "metrics": {
                    "backend_files": len([f for f in generated_files.keys() if f.startswith("backend/")]),
                    "frontend_files": len([f for f in generated_files.keys() if f.startswith("frontend/")]),
                    "test_files": len(test_files),
                    "deployment_files": len(deployment_files),
                    "documentation_files": len(documentation_files),
                    "review_files": len(review_result.get("review_files", {})),
                    "total_requirements": len(specifications.get("functional_requirements", [])),
                    "technology_stack": specifications.get("project_overview", {}).get("technology_stack", {}),
                    "application_type": coding_result.get("application_type", "Unknown"),
                    "deployment_ready": deployment_result.get("deployment_ready", False),
                    "test_coverage": test_result.get("test_coverage", {}),
                    "review_scores": review_result.get("review_metrics", {})
                },
                "status": "completed",
                "success": True
            }
            
            logger.info(f"Complete application generation finished successfully in {generation_time:.2f} seconds")
            logger.info(f"Generated {len(all_files)} total files")
            logger.info(f"Project ID: {project_id}")
            
            # Create ZIP file automatically
            try:
                import zipfile
                zip_filepath = os.path.join(project_dir, "project.zip")
                with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, _, files in os.walk(project_dir):
                        for file in files:
                            if file != "project.zip":  # Don't include the ZIP file itself
                                file_path = os.path.join(root, file)
                                arcname = os.path.relpath(file_path, project_dir)
                                zipf.write(file_path, arcname)
                logger.info(f"ZIP package created automatically: {zip_filepath}")
            except Exception as e:
                logger.warning(f"Failed to create automatic ZIP package: {e}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in complete application generation: {e}")
            return self._generate_error_result(natural_language_input, str(e), time.time() - start_time)
    
    def _iterative_requirement_analysis(self, natural_language_input: str, project_id: str) -> Dict[str, Any]:
        """Iteratively refine requirements based on feedback."""
        max_iterations = 3
        iterations = 0
        
        while iterations < max_iterations:
            iterations += 1
            logger.info(f"Requirement Analysis Iteration {iterations}")
            
            requirement_result = self.requirement_agent.analyze_requirements(natural_language_input, project_id)
            
            if not requirement_result.get("fallback_mode", False):
                # Check if requirements are complete enough
                specifications = requirement_result.get("specifications", {})
                if self._validate_requirements(specifications):
                    logger.info(f"Requirements validated successfully after {iterations} iterations")
                    requirement_result["iterations"] = iterations
                    return requirement_result
                else:
                    logger.info(f"Requirements incomplete, refining in iteration {iterations + 1}")
                    # Add feedback for refinement
                    natural_language_input = self._add_requirement_feedback(natural_language_input, specifications)
            
            logger.warning(f"Requirement analysis iteration {iterations} failed")
        
        logger.error("Requirement analysis failed after all iterations, using fallback")
        return {"fallback_mode": True, "specifications": {}, "project_id": project_id, "iterations": iterations}
    
    def _iterative_code_generation_with_review(self, specifications: Dict[str, Any], project_id: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Iteratively generate code and refine based on review feedback."""
        max_iterations = 3
        iterations = 0
        
        while iterations < max_iterations:
            iterations += 1
            logger.info(f"Code Generation and Review Iteration {iterations}")
            
            # Generate code
            coding_result = self.coding_agent.generate_code(specifications, project_id)
            
            if coding_result.get("fallback_mode", False):
                logger.warning(f"Code generation failed in iteration {iterations}")
                continue
            
            generated_files = coding_result.get("generated_files", {})
            
            # Review the generated code
            review_result = self.review_agent.review_code(specifications, generated_files, project_id)
            
            if review_result.get("fallback_mode", False):
                logger.warning(f"Code review failed in iteration {iterations}")
                continue
            
            # Check if code passes review
            review_scores = review_result.get("review_metrics", {})
            overall_score = review_scores.get("overall_score", 0)
            
            if overall_score >= 80:  # Acceptable quality threshold
                logger.info(f"Code passed review with score {overall_score} after {iterations} iterations")
                coding_result["iterations"] = iterations
                review_result["iterations"] = iterations
                return coding_result, review_result
            else:
                logger.info(f"Code failed review with score {overall_score}, refining in iteration {iterations + 1}")
                # Add review feedback to specifications for next iteration
                specifications = self._add_review_feedback(specifications, review_result)
        
        logger.error("Code generation and review failed after all iterations, using fallback")
        return (
            {"fallback_mode": True, "generated_files": {}, "project_id": project_id, "iterations": iterations},
            {"fallback_mode": True, "review_files": {}, "iterations": iterations}
        )
    
    def _validate_requirements(self, specifications: Dict[str, Any]) -> bool:
        """Validate if requirements are complete enough."""
        project_overview = specifications.get("project_overview", {})
        functional_reqs = specifications.get("functional_requirements", [])
        architecture = specifications.get("architecture", {})
        
        # Check if we have essential components
        has_name = bool(project_overview.get("name"))
        has_description = bool(project_overview.get("description"))
        has_tech_stack = bool(project_overview.get("technology_stack"))
        has_functional_reqs = len(functional_reqs) > 0
        has_architecture = bool(architecture.get("api_specification"))
        
        return has_name and has_description and has_tech_stack and has_functional_reqs and has_architecture
    
    def _add_requirement_feedback(self, natural_language_input: str, specifications: Dict[str, Any]) -> str:
        """Add feedback to requirements for refinement."""
        feedback = "\n\nPlease provide more specific details about:"
        
        if not specifications.get("project_overview", {}).get("technology_stack"):
            feedback += "\n- Technology stack preferences (backend, frontend, database)"
        
        if not specifications.get("functional_requirements"):
            feedback += "\n- Specific functional requirements and features"
        
        if not specifications.get("architecture", {}).get("api_specification"):
            feedback += "\n- API endpoints and data models"
        
        return natural_language_input + feedback
    
    def _add_review_feedback(self, specifications: Dict[str, Any], review_result: Dict[str, Any]) -> Dict[str, Any]:
        """Add review feedback to specifications for code refinement."""
        recommendations = review_result.get("recommendations", [])
        
        # Add review feedback to specifications
        if "review_feedback" not in specifications:
            specifications["review_feedback"] = []
        
        specifications["review_feedback"].extend(recommendations)
        
        # Add specific improvement areas
        review_scores = review_result.get("review_metrics", {})
        if review_scores.get("security_score", 100) < 80:
            specifications["review_feedback"].append("Improve security measures and input validation")
        
        if review_scores.get("performance_score", 100) < 80:
            specifications["review_feedback"].append("Optimize performance and add caching")
        
        if review_scores.get("code_quality_score", 100) < 80:
            specifications["review_feedback"].append("Improve code structure and follow best practices")
        
        return specifications
    
    def _generate_project_summary(self, natural_language_input: str, 
                                requirement_result: Dict[str, Any],
                                coding_result: Dict[str, Any],
                                test_result: Dict[str, Any],
                                deployment_result: Dict[str, Any],
                                documentation_result: Dict[str, Any],
                                review_result: Dict[str, Any],
                                all_files: Dict[str, str]) -> Dict[str, Any]:
        """Generate comprehensive project summary."""
        
        specifications = requirement_result.get("specifications", {})
        project_overview = specifications.get("project_overview", {})
        
        summary = {
            "project_info": {
                "name": project_overview.get("name", "Generated Application"),
                "description": project_overview.get("description", natural_language_input),
                "version": project_overview.get("version", "1.0.0"),
                "generation_timestamp": time.time(),
                "project_id": requirement_result.get("project_id", "unknown")
            },
            "technology_stack": specifications.get("project_overview", {}).get("technology_stack", {}),
            "architecture": specifications.get("architecture", {}),
            "functional_requirements": specifications.get("functional_requirements", []),
            "non_functional_requirements": specifications.get("non_functional_requirements", []),
            "generation_results": {
                "requirement_analysis": {
                    "status": "completed" if not requirement_result.get("fallback_mode") else "fallback",
                    "total_requirements": len(specifications.get("functional_requirements", [])),
                    "technology_stack_complete": bool(specifications.get("project_overview", {}).get("technology_stack"))
                },
                "code_generation": {
                    "status": "completed" if not coding_result.get("fallback_mode") else "fallback",
                    "total_files": len(coding_result.get("generated_files", {})),
                    "backend_files": len([f for f in coding_result.get("generated_files", {}).keys() if f.startswith("backend/")]),
                    "frontend_files": len([f for f in coding_result.get("generated_files", {}).keys() if f.startswith("frontend/")]),
                    "application_type": coding_result.get("application_type", "Unknown"),
                    "deployment_ready": coding_result.get("deployment_ready", False)
                },
                "testing": {
                    "status": "completed" if not test_result.get("fallback_mode") else "fallback",
                    "total_test_files": len(test_result.get("test_files", {})),
                    "unit_tests": test_result.get("unit_tests", 0),
                    "integration_tests": test_result.get("integration_tests", 0),
                    "e2e_tests": test_result.get("e2e_tests", 0),
                    "test_coverage": test_result.get("test_coverage", {})
                },
                "deployment": {
                    "status": "completed" if not deployment_result.get("fallback_mode") else "fallback",
                    "total_deployment_files": len(deployment_result.get("deployment_files", {})),
                    "docker_files": deployment_result.get("docker_files", 0),
                    "kubernetes_files": deployment_result.get("kubernetes_files", 0),
                    "ci_cd_files": deployment_result.get("ci_cd_files", 0),
                    "monitoring_files": deployment_result.get("monitoring_files", 0),
                    "deployment_ready": deployment_result.get("deployment_ready", False)
                },
                "documentation": {
                    "status": "completed" if not documentation_result.get("fallback_mode") else "fallback",
                    "total_documentation_files": len(documentation_result.get("documentation_files", {})),
                    "readme_files": documentation_result.get("readme_files", 0),
                    "api_docs": documentation_result.get("api_docs", 0),
                    "user_guides": documentation_result.get("user_guides", 0),
                    "developer_docs": documentation_result.get("developer_docs", 0),
                    "deployment_docs": documentation_result.get("deployment_docs", 0)
                },
                "code_review": {
                    "status": "completed" if not review_result.get("fallback_mode") else "fallback",
                    "total_review_files": len(review_result.get("review_files", {})),
                    "critical_issues": review_result.get("critical_issues", 0),
                    "high_priority_issues": review_result.get("high_priority_issues", 0),
                    "medium_priority_issues": review_result.get("medium_priority_issues", 0),
                    "low_priority_issues": review_result.get("low_priority_issues", 0),
                    "security_score": review_result.get("security_score", 0),
                    "performance_score": review_result.get("performance_score", 0),
                    "code_quality_score": review_result.get("code_quality_score", 0),
                    "test_coverage_score": review_result.get("test_coverage_score", 0),
                    "overall_score": review_result.get("overall_score", 0)
                }
            },
            "file_structure": {
                "total_files": len(all_files),
                "file_categories": {
                    "backend": len([f for f in all_files.keys() if f.startswith("backend/")]),
                    "frontend": len([f for f in all_files.keys() if f.startswith("frontend/")]),
                    "tests": len([f for f in all_files.keys() if "test" in f.lower()]),
                    "deployment": len([f for f in all_files.keys() if any(x in f.lower() for x in ["docker", "k8s", "kubernetes", "deploy", "pipeline"])]),
                    "documentation": len([f for f in all_files.keys() if f.endswith((".md", ".txt", ".rst"))]),
                    "configuration": len([f for f in all_files.keys() if f.endswith((".yml", ".yaml", ".json", ".env", ".ini", ".conf"))])
                }
            },
            "quality_metrics": {
                "production_ready": all([
                    coding_result.get("deployment_ready", False),
                    deployment_result.get("deployment_ready", False),
                    review_result.get("overall_score", 0) > 70
                ]),
                "test_coverage_adequate": test_result.get("test_coverage", {}).get("expected_coverage", {}).get("overall", 0) >= 80,
                "documentation_complete": documentation_result.get("documentation_ready", False),
                "security_score_adequate": review_result.get("security_score", 0) >= 80,
                "performance_score_adequate": review_result.get("performance_score", 0) >= 75
            },
            "next_steps": self._generate_next_steps(
                requirement_result, coding_result, test_result, 
                deployment_result, documentation_result, review_result
            )
        }
        
        return summary
    
    def _generate_next_steps(self, requirement_result: Dict[str, Any],
                           coding_result: Dict[str, Any],
                           test_result: Dict[str, Any],
                           deployment_result: Dict[str, Any],
                           documentation_result: Dict[str, Any],
                           review_result: Dict[str, Any]) -> List[str]:
        """Generate next steps based on generation results."""
        
        next_steps = []
        
        # Check for fallback modes and suggest improvements
        if requirement_result.get("fallback_mode"):
            next_steps.append("Improve requirement analysis with more detailed specifications")
        
        if coding_result.get("fallback_mode"):
            next_steps.append("Enhance code generation for complete implementation")
        
        if test_result.get("fallback_mode"):
            next_steps.append("Generate comprehensive test suites")
        
        if deployment_result.get("fallback_mode"):
            next_steps.append("Create production-ready deployment configurations")
        
        if documentation_result.get("fallback_mode"):
            next_steps.append("Generate complete documentation")
        
        if review_result.get("fallback_mode"):
            next_steps.append("Perform comprehensive code review")
        
        # Check quality metrics
        if review_result.get("security_score", 0) < 80:
            next_steps.append("Address security vulnerabilities identified in code review")
        
        if review_result.get("performance_score", 0) < 75:
            next_steps.append("Optimize performance based on review recommendations")
        
        if test_result.get("test_coverage", {}).get("expected_coverage", {}).get("overall", 0) < 80:
            next_steps.append("Increase test coverage to meet quality standards")
        
        if not coding_result.get("deployment_ready", False):
            next_steps.append("Make application deployment-ready")
        
        # Add standard next steps
        next_steps.extend([
            "Review and customize generated code for specific requirements",
            "Set up development environment and run the application",
            "Configure production environment variables and secrets",
            "Deploy to staging environment for testing",
            "Perform user acceptance testing",
            "Deploy to production environment",
            "Set up monitoring and alerting",
            "Establish maintenance and update procedures"
        ])
        
        return next_steps
    
    def _generate_error_result(self, natural_language_input: str, error: str, generation_time: float) -> Dict[str, Any]:
        """Generate error result when generation fails."""
        
        return {
            "project_id": f"error_project_{int(time.time())}",
            "natural_language_input": natural_language_input,
            "generation_time": generation_time,
            "error": error,
            "status": "failed",
            "success": False,
            "all_files": {},
            "total_files": 0,
            "metrics": {
                "backend_files": 0,
                "frontend_files": 0,
                "test_files": 0,
                "deployment_files": 0,
                "documentation_files": 0,
                "review_files": 0,
                "total_requirements": 0,
                "technology_stack": {},
                "application_type": "Error",
                "deployment_ready": False,
                "test_coverage": {},
                "review_scores": {}
            }
        }
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents."""
        
        return {
            "requirement_agent": {
                "status": "ready",
                "capabilities": [
                    "Detailed requirement analysis",
                    "Technology stack specification",
                    "Architecture design",
                    "Database schema design",
                    "API specification"
                ]
            },
            "coding_agent": {
                "status": "ready",
                "capabilities": [
                    "Complete application generation",
                    "Backend implementation",
                    "Frontend implementation",
                    "Database integration",
                    "Authentication system"
                ]
            },
            "test_agent": {
                "status": "ready",
                "capabilities": [
                    "Unit test generation",
                    "Integration test generation",
                    "End-to-end test generation",
                    "Test configuration",
                    "Test utilities"
                ]
            },
            "deployment_agent": {
                "status": "ready",
                "capabilities": [
                    "Docker configuration",
                    "Kubernetes manifests",
                    "CI/CD pipelines",
                    "Monitoring setup",
                    "Security configuration"
                ]
            },
            "documentation_agent": {
                "status": "ready",
                "capabilities": [
                    "API documentation",
                    "User guides",
                    "Developer documentation",
                    "Deployment guides",
                    "Project documentation"
                ]
            },
            "review_agent": {
                "status": "ready",
                "capabilities": [
                    "Security review",
                    "Performance analysis",
                    "Code quality assessment",
                    "Testing review",
                    "Production readiness"
                ]
            }
        }
    
    def get_framework_capabilities(self) -> Dict[str, Any]:
        """Get framework capabilities and features."""
        
        return {
            "framework_name": "Enhanced Multi-Agentic Framework",
            "version": "2.0.0",
            "description": "Complete application generation framework with production-ready output",
            "key_features": [
                "Complete application generation (no skeleton code)",
                "Production-ready implementations",
                "Comprehensive testing suites",
                "Complete deployment configurations",
                "Professional documentation",
                "Security-focused code review",
                "Multi-technology stack support",
                "Scalable architecture design"
            ],
            "supported_technologies": {
                "backend": ["FastAPI", "Django", "Flask", "Express.js", "Spring Boot"],
                "frontend": ["React", "Vue.js", "Angular", "Next.js", "Nuxt.js"],
                "database": ["PostgreSQL", "MySQL", "MongoDB", "Redis"],
                "deployment": ["Docker", "Kubernetes", "AWS", "Azure", "GCP"],
                "testing": ["pytest", "Jest", "Cypress", "Playwright"]
            },
            "quality_standards": [
                "90%+ code coverage",
                "Security best practices",
                "Performance optimization",
                "Clean code principles",
                "Production deployment ready",
                "Comprehensive documentation"
            ],
            "phases": [
                "Phase 1: Enhanced Requirement Analysis",
                "Phase 2: Complete Application Generation", 
                "Phase 3: Comprehensive Testing",
                "Phase 4: Production Deployment",
                "Phase 5: Complete Documentation",
                "Phase 6: Comprehensive Code Review"
            ]
        } 