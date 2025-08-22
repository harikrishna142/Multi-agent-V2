"""
Enhanced Review Agent
Performs comprehensive code reviews for complete applications.
"""

import autogen
import os, re
import json
import time
from typing import Dict, Any, List
from core.config import get_agent_config, config
from core.utils import save_to_file, setup_logging, extract_llm_response

logger = setup_logging()

class ReviewAgent:
    """Enhanced review agent that performs comprehensive code reviews."""
    
    def __init__(self):
        self.agent_config = get_agent_config("review_agent")
        self.llm_config = config.get_llm_config()
        
        # Create the agent with enhanced system message
        enhanced_system_message = self._create_enhanced_system_message()
        
        self.agent = autogen.AssistantAgent(
            name=self.agent_config["name"],
            system_message=enhanced_system_message,
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
    
    def _create_enhanced_system_message(self) -> str:
        """Create enhanced system message for comprehensive code review."""
        
        return """You are an expert software engineer and code reviewer specializing in comprehensive code analysis and quality assessment. Your role is to perform thorough, professional code reviews that ensure code quality, security, and adherence to best practices.

## YOUR EXPERTISE AREAS:

### 1. **Code Quality Analysis**:
- **Readability**: Code clarity, naming conventions, and documentation
- **Maintainability**: Code structure, modularity, and organization
- **Best Practices**: Language-specific conventions and patterns
- **Code Smells**: Identification of anti-patterns and problematic code
- **Refactoring Opportunities**: Suggestions for code improvement

### 2. **Security Assessment**:
- **Input Validation**: Proper sanitization and validation of user inputs
- **Authentication & Authorization**: Secure user management and access control
- **Data Protection**: Encryption, secure storage, and privacy compliance
- **Vulnerability Detection**: Common security flaws and attack vectors
- **Security Best Practices**: Industry-standard security measures

### 3. **Performance Evaluation**:
- **Algorithm Efficiency**: Time and space complexity analysis
- **Resource Usage**: Memory, CPU, and network optimization
- **Scalability**: Code that can handle growth and increased load
- **Performance Bottlenecks**: Identification of slow operations
- **Optimization Opportunities**: Suggestions for performance improvements

### 4. **Functionality Verification**:
- **Requirement Compliance**: Code meets specified functional requirements
- **Feature Completeness**: All expected features are implemented
- **Edge Case Handling**: Proper handling of boundary conditions
- **Error Handling**: Comprehensive error management and recovery
- **Integration Testing**: Code works well with other components

### 5. **Architecture Review**:
- **Design Patterns**: Appropriate use of architectural patterns
- **Separation of Concerns**: Proper modularity and component isolation
- **Dependency Management**: Clean and manageable dependencies
- **Scalability Design**: Architecture supports future growth
- **Technology Stack**: Appropriate technology choices

## REVIEW METHODOLOGY:

### 1. **Systematic Analysis**:
- Review code file by file with attention to detail
- Cross-reference with project requirements and specifications
- Identify patterns and inconsistencies across the codebase
- Assess both individual components and overall system integration

### 2. **Quality Metrics**:
- **Code Coverage**: Adequate testing and validation
- **Complexity Analysis**: Cyclomatic complexity and maintainability
- **Documentation Quality**: Code comments, README, and API documentation
- **Error Handling**: Comprehensive exception management
- **Logging and Monitoring**: Proper debugging and observability

### 3. **Security Checklist**:
- Input validation and sanitization
- Authentication and authorization mechanisms
- Data encryption and secure storage
- SQL injection and XSS prevention
- CSRF protection and secure headers
- Rate limiting and DDoS protection

### 4. **Performance Assessment**:
- Algorithm efficiency and optimization
- Database query optimization
- Caching strategies and implementation
- Resource usage and memory management
- Load testing considerations



**YOUR MISSION**: Deliver comprehensive, professional code reviews that help developers create high-quality, secure, and maintainable software.

End your response with "TERMINATE" to indicate completion."""
    def review_code(self, specifications: Dict[str, Any], generated_files: Dict[str, Any], project_id: str) -> Dict[str, Any]:
        """Perform comprehensive code review with iterative feedback."""
        logger.info("Starting comprehensive code review with iterative feedback")
        
        try:
            # Import code analyzer
            from core.code_analyzer import CodeAnalyzer
            
            # Analyze code for TODOs and incomplete implementations
            analyzer = CodeAnalyzer()
            code_issues = analyzer.analyze_code_files(generated_files)
            issues_summary = analyzer.get_issues_summary(code_issues)
            
            # Generate specific improvement instructions
            improvement_instructions = analyzer.generate_improvement_instructions(code_issues)
            
            # Create review prompt with context and issues
            review_prompt = self._create_review_prompt(specifications, generated_files, code_issues)
            print(f"Found {len(code_issues)} code issues that need attention")
            
            # Perform review
            chat_result = self.user_proxy.initiate_chat(self.agent, message=review_prompt)
            last_message = extract_llm_response(chat_result)
            
            # Parse review results
            review_results = self._parse_review_results(last_message)
            
            # Add code analysis results to review
            review_results["code_issues"] = code_issues
            review_results["issues_summary"] = issues_summary
            review_results["improvement_instructions"] = improvement_instructions
            
            # Generate review files
            review_files = self._generate_review_files(review_results, project_id)
            
            # Calculate review metrics
            review_metrics = self._calculate_review_metrics(review_results)
            
            # Generate improvement recommendations
            recommendations = self._generate_recommendations(review_results, review_metrics)
            
            # Add improvement instructions to recommendations
            recommendations.extend(improvement_instructions)
            
            logger.info(f"Code review completed. Overall score: {review_metrics.get('overall_score', 0)}/100")
            logger.info(f"Found {len(code_issues)} code issues that need attention")
            
            saved_files = self._save_review_files(review_results, project_id)   
            return {
                "status": "completed",
                "review_summary": review_results.get("summary", "Review completed"),
                "review_metrics": review_metrics,
                "recommendations": recommendations,
                "review_files": review_files,
                "quality_score": review_metrics.get("overall_score", 0),
                "iterations": 1,  # Track iterations for orchestrator
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error in code review: {e}")
            return self._generate_fallback_review(project_id, str(e))
    
    def _create_review_prompt(self, specifications: Dict[str, Any], generated_files: Dict[str, Any], code_issues: List[Any] = None) -> str:
        """Create comprehensive review prompt."""
        project_overview = specifications.get("project_overview", {})
        functional_reqs = specifications.get("functional_requirements", [])
        
  
      
        prompt=f"""j"""
        prompt += f"""
## GENERATED CODE TO REVIEW:

The following code has been generated for this project. Please perform a comprehensive review:
 these are project REQUIREMENTS:
{specifications}
"""
        
        # Add generated files to review
        for filename, content in generated_files.items():
            prompt += f"""
### {filename}:
```{self._get_file_extension(filename)}
{content}
```
"""
        
        # Add code issues analysis if available
        if code_issues:
            prompt += f"""
## 🔍 CODE ISSUES DETECTED:

The following issues have been identified in the code that need attention:

"""
            
            for issue in code_issues[:10]:  # Limit to first 10 issues
                prompt += f"""
### Issue in {issue.file_path}:{issue.line_number}
- **Type**: {issue.issue_type}
- **Severity**: {issue.severity}
- **Description**: {issue.description}
- **Code**: {issue.code_snippet}
- **Context**: 
```
{issue.context}
```

"""
            
            prompt += """
## 🎯 PRIORITY FOCUS AREAS:

Please pay special attention to the following:

1. **Incomplete Implementations**: Functions with TODO comments, pass statements, or NotImplementedError
2. **Missing Functionality**: Areas marked with #implement or #todo
3. **Empty Implementations**: Functions that return None or have minimal logic
4. **Placeholder Code**: Code that needs to be replaced with actual implementation

For each issue found, provide specific instructions on how to complete the implementation.
"""
        
        prompt += """
## REVIEW REQUIREMENTS:

Perform a comprehensive review covering:

### 1. **Functionality Assessment**:
- Does the code implement all functional requirements?
- Are all acceptance criteria met?
- Are there any missing features or incomplete implementations?

### 2. **Code Quality**:
- Is the code readable and well-structured?
- Are proper naming conventions followed?
- Is the code modular and maintainable?
- Are there any code smells or anti-patterns?

### 3. **Security Analysis**:
- Are there any security vulnerabilities?
- Is input validation properly implemented?
- Are authentication and authorization handled correctly?
- Are sensitive data properly protected?

### 4. **Performance Evaluation**:
- Is the code efficient and optimized?
- Are there any performance bottlenecks?
- Is proper error handling implemented?
- Are resources managed correctly?

### 5. **Best Practices**:
- Does the code follow language and framework best practices?
- Are proper design patterns used?
- Is error handling comprehensive?
- Is logging and monitoring implemented?



## EXPECTED OUTPUT:

Provide a structured review with:

1. **Overall Assessment**: Summary of code quality and completeness
2. **Detailed Analysis**: File-by-file review with specific issues
3. **Security Issues**: List of security vulnerabilities and recommendations
4. **Performance Issues**: Performance problems and optimization suggestions
5. **Code Quality Issues**: Code quality problems and improvement suggestions
6. **Missing Features**: Any missing functionality or incomplete implementations
7. **Recommendations**: Specific recommendations for improvement
8. **Quality Scores**: Numerical scores for different aspects (0-100)

## REVIEW FORMAT:

```
# CODE REVIEW REPORT

## Overall Assessment
[Summary of findings]

## Quality Scores
- Overall Score: [0-100]
- Functionality Score: [0-100]
- Security Score: [0-100]
- Performance Score: [0-100]
- Code Quality Score: [0-100]
- Production Readiness Score: [0-100]

## Detailed Analysis
[File-by-file analysis]

## Security Issues
[List of security problems]

## Performance Issues
[List of performance problems]

## Code Quality Issues
[List of code quality problems]

## Missing Features
[List of missing functionality]

## Recommendations
[Specific improvement suggestions]
```

IMPORTANT: End your response with "TERMINATE" to indicate completion.
"""
        
        return prompt
    
    def _get_file_extension(self, filename: str) -> str:
        """Get file extension for syntax highlighting."""
        if '.' in filename:
            return filename.split('.')[-1]
        return 'text'
    
    def _parse_review_results(self, response: str) -> Dict[str, Any]:
        """Parse review results from agent response."""
        results = {
            "summary": "",
            "scores": {},
            "issues": [],
            "recommendations": []
        }
        
        lines = response.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('## Overall Assessment'):
                current_section = 'summary'
            elif line.startswith('## Quality Scores'):
                current_section = 'scores'
            elif line.startswith('## Security Issues'):
                current_section = 'security'
            elif line.startswith('## Performance Issues'):
                current_section = 'performance'
            elif line.startswith('## Code Quality Issues'):
                current_section = 'quality'
            elif line.startswith('## Recommendations'):
                current_section = 'recommendations'
            elif line.startswith('##'):
                current_section = None
            
            elif current_section == 'summary' and line and not line.startswith('#'):
                results["summary"] += line + " "
            elif current_section == 'scores' and ':' in line:
                try:
                    score_name, score_value = line.split(':', 1)
                    score_name = score_name.strip().replace(' Score', '').lower()
                    score_value = int(score_value.strip().replace('[', '').replace(']', ''))
                    results["scores"][score_name] = score_value
                except:
                    pass
            elif current_section in ['security', 'performance', 'quality'] and line and not line.startswith('#'):
                results["issues"].append({"type": current_section, "description": line})
            elif current_section == 'recommendations' and line and not line.startswith('#'):
                results["recommendations"].append(line)
        
        return results
    
    def _calculate_review_metrics(self, review_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate review metrics from parsed results."""
        scores = review_results.get("scores", {})
        
        # Calculate overall score as average of all scores
        score_values = list(scores.values())
        overall_score = sum(score_values) / len(score_values) if score_values else 0
        
        return {
            "overall_score": round(overall_score, 1),
            "functionality_score": scores.get("functionality", 0),
            "security_score": scores.get("security", 0),
            "performance_score": scores.get("performance", 0),
            "code_quality_score": scores.get("code_quality", 0),
            "production_readiness_score": scores.get("production_readiness", 0)
        }
    
    def _generate_recommendations(self, review_results: Dict[str, Any], metrics: Dict[str, Any]) -> List[str]:
        """Generate improvement recommendations based on review."""
        recommendations = review_results.get("recommendations", [])
        
        # Add score-based recommendations
        if metrics.get("security_score", 100) < 80:
            recommendations.append("Improve security measures and input validation")
        
        if metrics.get("performance_score", 100) < 80:
            recommendations.append("Optimize performance and add caching")
        
        if metrics.get("code_quality_score", 100) < 80:
            recommendations.append("Improve code structure and follow best practices")
        
        if metrics.get("production_readiness_score", 100) < 80:
            recommendations.append("Add production-ready configurations and monitoring")
        
        return recommendations
    
    def _generate_review_files(self, review_results: Dict[str, Any], project_id: str) -> Dict[str, str]:
        """Generate review files for the project."""
        import json
        from datetime import datetime
        
        review_files = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Generate comprehensive review report
        report_content = f"""# Code Review Report - {project_id}
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Overall Assessment
{review_results.get('summary', 'No summary provided')}

## Quality Scores
"""
        
        scores = review_results.get("scores", {})
        for score_name, score_value in scores.items():
            report_content += f"- **{score_name.title()} Score**: {score_value}/100\n"
        
        # Calculate overall score
        score_values = list(scores.values())
        overall_score = sum(score_values) / len(score_values) if score_values else 0
        report_content += f"- **Overall Score**: {round(overall_score, 1)}/100\n"
        
        report_content += f"""
## Issues Found
"""
        
        issues = review_results.get("issues", [])
        if issues:
            for issue in issues:
                report_content += f"- **{issue['type'].title()}**: {issue['description']}\n"
        else:
            report_content += "- No specific issues identified\n"
        
        report_content += f"""
## Recommendations
"""
        
        recommendations = review_results.get("recommendations", [])
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                report_content += f"{i}. {rec}\n"
        else:
            report_content += "- No specific recommendations provided\n"
        
        review_files["review_report.md"] = report_content
        
        # Generate JSON summary for programmatic access
        json_summary = {
            "project_id": project_id,
            "timestamp": timestamp,
            "overall_score": round(overall_score, 1),
            "scores": scores,
            "issues_count": len(issues),
            "recommendations_count": len(recommendations),
            "summary": review_results.get('summary', 'No summary provided')
        }
        
        review_files["review_summary.json"] = json.dumps(json_summary, indent=2)
        
        # Generate improvement checklist
        checklist_content = f"""# Code Improvement Checklist - {project_id}
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Security Improvements
- [ ] Implement input validation
- [ ] Add authentication and authorization
- [ ] Secure sensitive data handling
- [ ] Add security headers
- [ ] Implement rate limiting

## Performance Improvements
- [ ] Optimize database queries
- [ ] Add caching mechanisms
- [ ] Implement pagination
- [ ] Optimize file operations
- [ ] Add performance monitoring

## Code Quality Improvements
- [ ] Follow naming conventions
- [ ] Add comprehensive error handling
- [ ] Implement proper logging
- [ ] Add unit tests
- [ ] Improve code documentation

## Production Readiness
- [ ] Add environment configuration
- [ ] Implement health checks
- [ ] Add monitoring and alerting
- [ ] Configure logging
- [ ] Add deployment scripts
"""
        
        review_files["improvement_checklist.md"] = checklist_content
        
        return review_files
    
    def _save_review_files(self, review_results: Dict[str, Any], project_id: str) -> Dict[str, str]:
        """Save review files to disk and return saved file paths."""
        try:
            # Generate review files
            review_files = self._generate_review_files(review_results, project_id)
            
            # Save files to disk
            saved_files = {}
            project_dir = f"output/review_reports/{project_id}"
            os.makedirs(project_dir, exist_ok=True)
            
            for filename, content in review_files.items():
                # Use save_to_file with correct parameters: (content, filename, output_dir)
                file_path = save_to_file(content, filename, project_dir)
                saved_files[filename] = file_path
                logger.info(f"Saved review file: {file_path}")
            
            return saved_files
            
        except Exception as e:
            logger.error(f"Error saving review files: {e}")
            return {}
    
    def _generate_fallback_review(self, project_id: str, error: str) -> Dict[str, Any]:
        """Generate fallback review when review fails."""
        fallback_content = f"""# Code Review Report

## Review Status
Review failed due to error: {error}

## Fallback Assessment
- Quality Score: 75/100
- Security Score: 70/100
- Performance Score: 75/100

## General Recommendations
1. Implement comprehensive error handling
2. Add input validation for all user inputs
3. Use parameterized queries to prevent SQL injection
4. Implement proper authentication and authorization
5. Add comprehensive logging
6. Optimize database queries
7. Implement caching where appropriate
8. Add unit and integration tests
9. Follow security best practices
10. Document all API endpoints
"""
        
        saved_files = self._save_review_files({
            "summary": "Fallback review completed",
            "quality_score": 75,
            "security_score": 70,
            "performance_score": 75,
            "critical_issues": 0,
            "high_priority_issues": 0,
            "medium_priority_issues": 0,
            "low_priority_issues": 0,
            "recommendations": [
                "Implement comprehensive error handling",
                "Add input validation for all user inputs",
                "Use parameterized queries to prevent SQL injection"
            ],
            "full_review": fallback_content
        }, project_id)
        
        return {
            "project_id": project_id,
            "review_files": saved_files,
            "review_summary": "Fallback review completed",
            "quality_score": 75,
            "security_score": 70,
            "performance_score": 75,
            "critical_issues": 0,
            "high_priority_issues": 0,
            "medium_priority_issues": 0,
            "low_priority_issues": 0,
            "recommendations": [
                "Implement comprehensive error handling",
                "Add input validation for all user inputs",
                "Use parameterized queries to prevent SQL injection"
            ],
            "review_ready": False,
            "error": error,
            "fallback_mode": True
        }


# Utility functions for code validation and formatting
def validate_python_code(code: str) -> Dict[str, Any]:
    """
    Validate Python code syntax.
    
    Args:
        code: Python code string to validate
        
    Returns:
        Dict with validation results
    """
    try:
        import ast
        ast.parse(code)
        return {"valid": True, "errors": []}
    except SyntaxError as e:
        return {
            "valid": False, 
            "errors": [f"Syntax error at line {e.lineno}: {e.msg}"]
        }
    except Exception as e:
        return {
            "valid": False,
            "errors": [f"Validation error: {str(e)}"]
        }


def format_code_with_black(code: str) -> str:
    """
    Format Python code using black formatter.
    
    Args:
        code: Python code string to format
        
    Returns:
        Formatted code string
    """
    try:
        import black
        mode = black.FileMode()
        formatted_code = black.format_str(code, mode=mode)
        return formatted_code
    except ImportError:
        # If black is not available, return original code
        logger.warning("Black formatter not available, returning original code")
        return code
    except Exception as e:
        # If formatting fails, return original code
        logger.warning(f"Code formatting failed: {e}, returning original code")
        return code 