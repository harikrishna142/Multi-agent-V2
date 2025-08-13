"""
Code Review Agent for the Multi-Agentic Coding Framework.
Reviews generated code for correctness, efficiency, security, and best practices.
"""

import autogen
import re
from typing import Dict, Any, List
from core.config import get_agent_config, config
from core.utils import setup_logging, load_from_file, validate_python_code

logger = setup_logging()

class CodeReviewAgent:
    """Agent responsible for reviewing generated code."""
    
    def __init__(self):
        self.agent_config = get_agent_config("review_agent")
        self.llm_config = config.get_llm_config()
        
        # Create the agent
        self.agent = autogen.AssistantAgent(
            name=self.agent_config["name"],
            system_message=self.agent_config["system_message"],
            llm_config=self.llm_config
        )
        
        # Create user proxy for interaction
        self.user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=10,
            is_termination_msg=lambda x: "TERMINATE" in x.get("content", ""),
            code_execution_config={"work_dir": "workspace", "use_docker": False},
            llm_config=self.llm_config
        )
    
    def review_code(self, generated_code: Dict[str, Any], requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Review the generated code for quality, correctness, and adherence to requirements.
        
        Args:
            generated_code: Output from CodingAgent containing generated files
            requirements: Original requirements for context
            
        Returns:
            Dict containing review results and recommendations
        """
        logger.info("Starting code review")
        
        # Load the actual code content
        code_files = {}
        for filename, filepath in generated_code.get("generated_files", {}).items():
            try:
                code_files[filename] = load_from_file(filepath)
            except Exception as e:
                logger.warning(f"Could not load file {filename}: {e}")
                code_files[filename] = f"# Error loading file: {e}"
        
        # Create the review prompt
        review_prompt = f"""
Please review the following generated Python code for correctness, efficiency, security, and adherence to requirements.

ORIGINAL REQUIREMENTS:
{self._format_requirements_for_review(requirements)}

GENERATED CODE FILES:
{self._format_code_for_review(code_files)}

Please provide a comprehensive review covering:

1. **Correctness**: Does the code implement the requirements correctly?
2. **Efficiency**: Are there performance issues or inefficient patterns?
3. **Security**: Are there security vulnerabilities or unsafe practices?
4. **Code Quality**: Does the code follow best practices and standards?
5. **Error Handling**: Is proper error handling implemented?
6. **Documentation**: Is the code well-documented?
7. **Maintainability**: Is the code maintainable and readable?

For each issue found, provide:
- Severity (Critical/High/Medium/Low)
- Description of the issue
- Specific code location (file and line if possible)
- Suggested fix or improvement

Please provide your review in the following JSON format:

{{
    "overall_score": 0-100,
    "passes_review": true/false,
    "critical_issues": [
        {{
            "file": "filename.py",
            "line": "approximate line",
            "issue": "description",
            "severity": "Critical",
            "suggestion": "how to fix"
        }}
    ],
    "high_priority_issues": [...],
    "medium_priority_issues": [...],
    "low_priority_issues": [...],
    "positive_aspects": [
        "good practice 1",
        "good practice 2"
    ],
    "recommendations": [
        "general recommendation 1",
        "general recommendation 2"
    ],
    "requires_revision": true/false,
    "revision_notes": "specific instructions for coding agent"
}}

IMPORTANT: End your response with the word "TERMINATE" to indicate completion.
"""
        
        try:
            # Start the conversation
            chat_result = self.user_proxy.initiate_chat(
                self.agent,
                message=review_prompt
            )
            
            # Extract the LLM response using utility function
            from core.utils import extract_llm_response
            last_message = extract_llm_response(chat_result)
            
            # Parse the review response
            review_result = self._parse_review_response(last_message)
            
            # Add automated validation results
            automated_validation = self._perform_automated_validation(code_files)
            review_result["automated_validation"] = automated_validation
            
            # Determine if revision is needed
            review_result["requires_revision"] = self._determine_revision_needed(review_result)
            
            logger.info(f"Code review completed. Overall score: {review_result.get('overall_score', 0)}")
            return review_result
            
        except Exception as e:
            logger.error(f"Error in code review: {e}")
            return {
                "overall_score": 0,
                "passes_review": False,
                "critical_issues": [{"issue": f"Review failed: {e}", "severity": "Critical"}],
                "high_priority_issues": [],
                "medium_priority_issues": [],
                "low_priority_issues": [],
                "positive_aspects": [],
                "recommendations": ["Fix the review process and try again"],
                "requires_revision": True,
                "revision_notes": f"Review process failed with error: {e}",
                "error": str(e)
            }
    
    def _format_requirements_for_review(self, requirements: Dict[str, Any]) -> str:
        """Format requirements for the review context."""
        formatted = f"""
Project: {requirements.get('project_name', 'N/A')}
Description: {requirements.get('description', 'N/A')}

Functional Requirements:
"""
        
        for req in requirements.get('functional_requirements', []):
            formatted += f"""
- {req.get('id', 'N/A')}: {req.get('title', 'N/A')}
  Description: {req.get('description', 'N/A')}
  Priority: {req.get('priority', 'N/A')}
  Acceptance Criteria: {', '.join(req.get('acceptance_criteria', []))}
"""
        
        formatted += f"""
Non-Functional Requirements:
"""
        
        for req in requirements.get('non_functional_requirements', []):
            formatted += f"""
- {req.get('id', 'N/A')}: {req.get('title', 'N/A')}
  Category: {req.get('category', 'N/A')}
  Description: {req.get('description', 'N/A')}
"""
        
        return formatted
    
    def _format_code_for_review(self, code_files: Dict[str, str]) -> str:
        """Format code files for review."""
        formatted = ""
        
        for filename, content in code_files.items():
            formatted += f"""
=== FILE: {filename} ===
{content}
=== END FILE: {filename} ===

"""
        
        return formatted
    
    def _parse_review_response(self, response: str) -> Dict[str, Any]:
        """Parse the review response and extract structured data."""
        import re
        import json
        
        # Try to extract JSON from the response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                json_str = json_match.group()
                review_data = json.loads(json_str)
                return review_data
            except json.JSONDecodeError:
                pass
        
        # If JSON parsing fails, create a basic structure
        return {
            "overall_score": 50,  # Default score
            "passes_review": False,
            "critical_issues": [],
            "high_priority_issues": [],
            "medium_priority_issues": [],
            "low_priority_issues": [],
            "positive_aspects": [],
            "recommendations": ["Review response could not be parsed properly"],
            "requires_revision": True,
            "revision_notes": "Unable to parse review response. Manual review recommended.",
            "raw_response": response
        }
    
    def _perform_automated_validation(self, code_files: Dict[str, str]) -> Dict[str, Any]:
        """Perform automated validation checks on the code."""
        validation_results = {
            "syntax_validation": {},
            "security_checks": {},
            "code_quality_metrics": {}
        }
        
        for filename, content in code_files.items():
            if filename.endswith('.py'):
                # Syntax validation
                syntax_result = validate_python_code(content)
                validation_results["syntax_validation"][filename] = syntax_result
                
                # Security checks
                security_issues = self._check_security_issues(content, filename)
                validation_results["security_checks"][filename] = security_issues
                
                # Code quality metrics
                quality_metrics = self._calculate_quality_metrics(content, filename)
                validation_results["code_quality_metrics"][filename] = quality_metrics
        
        return validation_results
    
    def _check_security_issues(self, code: str, filename: str) -> Dict[str, Any]:
        """Check for common security issues in the code."""
        security_issues = {
            "issues": [],
            "risk_level": "low"
        }
        
        # Check for common security vulnerabilities
        security_patterns = {
            "sql_injection": r"execute\(.*\+.*\)|cursor\.execute\(.*\+.*\)",
            "eval_usage": r"eval\(",
            "exec_usage": r"exec\(",
            "shell_execution": r"os\.system\(|subprocess\.call\(|subprocess\.Popen\(",
            "hardcoded_secrets": r"password.*=.*['\"][^'\"]+['\"]|api_key.*=.*['\"][^'\"]+['\"]",
            "unsafe_deserialization": r"pickle\.loads\(|yaml\.load\(",
        }
        
        for issue_type, pattern in security_patterns.items():
            matches = re.findall(pattern, code, re.IGNORECASE)
            if matches:
                security_issues["issues"].append({
                    "type": issue_type,
                    "matches": len(matches),
                    "description": f"Potential {issue_type} vulnerability found"
                })
        
        # Determine risk level
        if len(security_issues["issues"]) > 3:
            security_issues["risk_level"] = "high"
        elif len(security_issues["issues"]) > 1:
            security_issues["risk_level"] = "medium"
        
        return security_issues
    
    def _calculate_quality_metrics(self, code: str, filename: str) -> Dict[str, Any]:
        """Calculate code quality metrics."""
        lines = code.split('\n')
        
        metrics = {
            "total_lines": len(lines),
            "code_lines": len([line for line in lines if line.strip() and not line.strip().startswith('#')]),
            "comment_lines": len([line for line in lines if line.strip().startswith('#')]),
            "empty_lines": len([line for line in lines if not line.strip()]),
            "functions": len(re.findall(r'def\s+', code)),
            "classes": len(re.findall(r'class\s+', code)),
            "imports": len(re.findall(r'import\s+|from\s+', code)),
            "docstrings": len(re.findall(r'""".*?"""', code, re.DOTALL)),
        }
        
        # Calculate ratios
        if metrics["total_lines"] > 0:
            metrics["comment_ratio"] = metrics["comment_lines"] / metrics["total_lines"]
            metrics["code_ratio"] = metrics["code_lines"] / metrics["total_lines"]
        else:
            metrics["comment_ratio"] = 0
            metrics["code_ratio"] = 0
        
        return metrics
    
    def _determine_revision_needed(self, review_result: Dict[str, Any]) -> bool:
        """Determine if code revision is needed based on review results."""
        # Check for critical issues
        if review_result.get("critical_issues"):
            return True
        
        # Check overall score
        overall_score = review_result.get("overall_score", 0)
        if overall_score < 70:
            return True
        
        # Check if review explicitly says revision is needed
        if review_result.get("requires_revision", False):
            return True
        
        return False
    
    def get_review_summary(self, review_result: Dict[str, Any]) -> str:
        """Generate a human-readable summary of the review."""
        summary = f"""
# Code Review Summary

## Overall Assessment
- **Score**: {review_result.get('overall_score', 'N/A')}/100
- **Passes Review**: {'✅ Yes' if review_result.get('passes_review') else '❌ No'}
- **Requires Revision**: {'✅ Yes' if review_result.get('requires_revision') else '❌ No'}

## Issues Found
"""
        
        # Critical issues
        if review_result.get("critical_issues"):
            summary += "\n### Critical Issues\n"
            for issue in review_result["critical_issues"]:
                summary += f"- **{issue.get('file', 'N/A')}**: {issue.get('issue', 'N/A')}\n"
        
        # High priority issues
        if review_result.get("high_priority_issues"):
            summary += "\n### High Priority Issues\n"
            for issue in review_result["high_priority_issues"]:
                summary += f"- **{issue.get('file', 'N/A')}**: {issue.get('issue', 'N/A')}\n"
        
        # Medium priority issues
        if review_result.get("medium_priority_issues"):
            summary += "\n### Medium Priority Issues\n"
            for issue in review_result["medium_priority_issues"]:
                summary += f"- **{issue.get('file', 'N/A')}**: {issue.get('issue', 'N/A')}\n"
        
        # Positive aspects
        if review_result.get("positive_aspects"):
            summary += "\n### Positive Aspects\n"
            for aspect in review_result["positive_aspects"]:
                summary += f"- ✅ {aspect}\n"
        
        # Recommendations
        if review_result.get("recommendations"):
            summary += "\n### Recommendations\n"
            for rec in review_result["recommendations"]:
                summary += f"- 💡 {rec}\n"
        
        # Revision notes
        if review_result.get("revision_notes"):
            summary += f"\n### Revision Notes\n{review_result['revision_notes']}\n"
        
        return summary 