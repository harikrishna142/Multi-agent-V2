"""
Validation module for Multi-Agentic Framework using Pydantic.
Ensures proper data validation and schema enforcement between agents.
"""

import json
import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ValidationError, Field
from core.utils import setup_logging

logger = setup_logging()

# ============================================================================
# REQUIREMENT ANALYSIS VALIDATION
# ============================================================================

class FunctionalRequirement(BaseModel):
    """Schema for functional requirements."""
    id: str = Field(..., description="Unique identifier for the requirement")
    title: str = Field(..., description="Title of the functional requirement")
    description: str = Field(..., description="Detailed description of the requirement")
    priority: str = Field(..., description="Priority level (High/Medium/Low)")
    acceptance_criteria: List[str] = Field(default_factory=list, description="Acceptance criteria for the requirement")

class NonFunctionalRequirement(BaseModel):
    """Schema for non-functional requirements."""
    id: str = Field(..., description="Unique identifier for the requirement")
    title: str = Field(..., description="Title of the non-functional requirement")
    description: str = Field(..., description="Detailed description of the requirement")
    category: str = Field(..., description="Category of the requirement (Performance/Security/Usability/etc.)")

class RequirementAnalysis(BaseModel):
    """Schema for complete requirement analysis."""
    project_name: str = Field(..., description="Name of the project")
    description: str = Field(..., description="Detailed project description")
    functional_requirements: List[FunctionalRequirement] = Field(default_factory=list, description="List of functional requirements")
    non_functional_requirements: List[NonFunctionalRequirement] = Field(default_factory=list, description="List of non-functional requirements")
    technical_constraints: List[str] = Field(default_factory=list, description="Technical constraints")
    assumptions: List[str] = Field(default_factory=list, description="Project assumptions")
    dependencies: List[str] = Field(default_factory=list, description="Project dependencies")
    estimated_complexity: str = Field(..., description="Estimated project complexity")
    suggested_architecture: str = Field(..., description="Suggested technical architecture")
    key_components: List[str] = Field(default_factory=list, description="Key system components")
    original_requirement: Optional[str] = Field(None, description="Original natural language requirement")
    analysis_timestamp: Optional[str] = Field(None, description="Timestamp of analysis")

# ============================================================================
# CODE GENERATION VALIDATION
# ============================================================================

class GeneratedFile(BaseModel):
    """Schema for generated code files."""
    filename: str = Field(..., description="Name of the generated file")
    content: str = Field(..., description="File content")
    file_type: str = Field(..., description="Type of file (python/config/docs/etc.)")

class CodeGenerationResult(BaseModel):
    """Schema for code generation results."""
    project_id: str = Field(..., description="Project identifier")
    generated_files: List[GeneratedFile] = Field(default_factory=list, description="List of generated files")
    total_files: int = Field(..., description="Total number of files generated")

# ============================================================================
# CODE REVIEW VALIDATION
# ============================================================================

class CodeIssue(BaseModel):
    """Schema for code review issues."""
    file: str = Field(..., description="File where issue was found")
    line: Optional[str] = Field(None, description="Line number or approximate location")
    issue: str = Field(..., description="Description of the issue")
    severity: str = Field(..., description="Severity level (Critical/High/Medium/Low)")
    suggestion: str = Field(..., description="Suggested fix or improvement")

class CodeReviewResult(BaseModel):
    """Schema for code review results."""
    overall_score: int = Field(..., ge=0, le=100, description="Overall code quality score")
    passes_review: bool = Field(..., description="Whether code passes quality threshold")
    critical_issues: List[CodeIssue] = Field(default_factory=list, description="Critical issues found")
    high_priority_issues: List[CodeIssue] = Field(default_factory=list, description="High priority issues found")
    medium_priority_issues: List[CodeIssue] = Field(default_factory=list, description="Medium priority issues found")
    low_priority_issues: List[CodeIssue] = Field(default_factory=list, description="Low priority issues found")
    positive_aspects: List[str] = Field(default_factory=list, description="Positive aspects of the code")
    recommendations: List[str] = Field(default_factory=list, description="General recommendations")
    requires_revision: bool = Field(..., description="Whether code requires revision")
    revision_notes: Optional[str] = Field(None, description="Specific revision instructions")

# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def extract_all_json_objects(text: str) -> List[str]:
    """Extract all JSON objects from text using brace counting."""
    json_objects = []
    brace_count = 0
    json_start = -1
    
    for i, char in enumerate(text):
        if char == '{':
            if brace_count == 0:
                json_start = i
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0 and json_start != -1:
                json_objects.append(text[json_start:i+1])
                json_start = -1
    
    return json_objects

def validate_requirement_analysis(raw_output: str) -> RequirementAnalysis:
    """
    Validate and extract requirement analysis from LLM output.
    
    Args:
        raw_output: Raw output from the LLM
        
    Returns:
        Validated RequirementAnalysis object
        
    Raises:
        ValueError: If no valid requirement analysis can be extracted
    """
    logger.info("Validating requirement analysis output")
    
    # Extract all JSON objects from the response
    json_objects = extract_all_json_objects(raw_output)
    logger.info(f"Found {len(json_objects)} JSON objects in response")
    
    # Try to validate each JSON object, prioritizing those with actual content
    valid_candidates = []
    
    for i, json_str in enumerate(json_objects):
        try:
            logger.info(f"Attempting to validate JSON object {i+1}")
            data = json.loads(json_str)
            
            # Validate against schema
            validated = RequirementAnalysis(**data)
            
            # Check if it has actual content (not template)
            has_content = (
                validated.project_name and validated.project_name.strip() and 
                validated.description and validated.description.strip() and
                validated.project_name != "Generated Project"
            )
            
            if has_content:
                logger.info(f"Found valid requirement analysis: {validated.project_name}")
                valid_candidates.append(validated)
            else:
                logger.info(f"JSON object {i+1} is empty template, skipping")
                
        except json.JSONDecodeError as e:
            logger.info(f"JSON object {i+1} is not valid JSON: {e}")
            continue
        except ValidationError as e:
            logger.info(f"JSON object {i+1} failed validation: {e}")
            continue
    
    # Return the first valid candidate (should be the actual analysis)
    if valid_candidates:
        logger.info(f"Successfully validated requirement analysis: {valid_candidates[0].project_name}")
        return valid_candidates[0]
    
    # If no valid JSON found, raise error
    raise ValueError("No valid requirement analysis found in LLM output")

def validate_code_generation_result(raw_output: str, project_id: str) -> CodeGenerationResult:
    """
    Validate code generation result from LLM output.
    
    Args:
        raw_output: Raw output from the LLM
        project_id: Project identifier
        
    Returns:
        Validated CodeGenerationResult object
    """
    # Implementation for code generation validation
    # This would extract and validate generated code files
    pass

def validate_code_review_result(raw_output: str) -> CodeReviewResult:
    """
    Validate code review result from LLM output.
    
    Args:
        raw_output: Raw output from the LLM
        
    Returns:
        Validated CodeReviewResult object
    """
    # Implementation for code review validation
    # This would extract and validate review results
    pass

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def is_valid_json_structure(data: Dict[str, Any], required_fields: List[str]) -> bool:
    """
    Check if data has the required fields and they're not empty.
    
    Args:
        data: Dictionary to validate
        required_fields: List of required field names
        
    Returns:
        True if all required fields exist and are not empty
    """
    for field in required_fields:
        if field not in data:
            return False
        value = data[field]
        if isinstance(value, str) and not value.strip():
            return False
        if isinstance(value, list) and len(value) == 0:
            return False
    return True

def sanitize_llm_output(raw_output: str) -> str:
    """
    Clean up LLM output to improve JSON extraction.
    
    Args:
        raw_output: Raw LLM output
        
    Returns:
        Cleaned output string
    """
    # Remove markdown code blocks
    cleaned = re.sub(r'```json\s*', '', raw_output)
    cleaned = re.sub(r'```\s*', '', cleaned)
    
    # Remove extra whitespace
    cleaned = re.sub(r'\n\s*\n', '\n', cleaned)
    
    return cleaned.strip() 