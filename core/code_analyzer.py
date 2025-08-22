"""
Code Analyzer for detecting TODOs, placeholders, and incomplete code.
"""

import re
import os
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass

@dataclass
class CodeIssue:
    """Represents a code issue that needs attention."""
    file_path: str
    line_number: int
    issue_type: str  # 'todo', 'placeholder', 'incomplete', 'missing_implementation'
    description: str
    code_snippet: str
    severity: str  # 'high', 'medium', 'low'
    context: str

class CodeAnalyzer:
    """Analyzes code for TODOs, placeholders, and incomplete implementations."""
    
    def __init__(self):
        # Patterns to detect incomplete code
        self.todo_patterns = [
            r'#\s*todo\s*:?\s*(.+)',
            r'#\s*implement\s*:?\s*(.+)',
            r'#\s*fix\s*:?\s*(.+)',
            r'#\s*complete\s*:?\s*(.+)',
            r'#\s*placeholder\s*:?\s*(.+)',
            r'#\s*missing\s*:?\s*(.+)',
            r'#\s*add\s*:?\s*(.+)',
            r'#\s*create\s*:?\s*(.+)',
            r'#\s*build\s*:?\s*(.+)',
            r'#\s*develop\s*:?\s*(.+)',
        ]
        
        # Patterns for incomplete function implementations
        self.incomplete_patterns = [
            r'def\s+\w+\s*\([^)]*\):\s*\n\s*pass\s*$',
            r'def\s+\w+\s*\([^)]*\):\s*\n\s*#\s*implement',
            r'def\s+\w+\s*\([^)]*\):\s*\n\s*#\s*todo',
            r'def\s+\w+\s*\([^)]*\):\s*\n\s*raise\s+NotImplementedError',
            r'def\s+\w+\s*\([^)]*\):\s*\n\s*return\s+None\s*#\s*temporary',
        ]
        
        # Patterns for missing implementations
        self.missing_patterns = [
            r'#\s*Implement\s+this\s+function',
            r'#\s*Add\s+implementation\s+here',
            r'#\s*Complete\s+this\s+function',
            r'#\s*Fill\s+in\s+the\s+implementation',
            r'#\s*TODO:\s+Implement',
            r'#\s*FIXME:\s+Implement',
        ]
    
    def analyze_code_files(self, generated_files: Dict[str, str]) -> List[CodeIssue]:
        """Analyze all generated code files for issues."""
        all_issues = []
        
        for file_path, content in generated_files.items():
            if self._is_code_file(file_path):
                issues = self._analyze_single_file(file_path, content)
                all_issues.extend(issues)
        
        return all_issues
    
    def _is_code_file(self, file_path: str) -> bool:
        """Check if file is a code file."""
        code_extensions = ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs', '.php', '.rb', '.go', '.rs']
        return any(file_path.endswith(ext) for ext in code_extensions)
    
    def _analyze_single_file(self, file_path: str, content: str) -> List[CodeIssue]:
        """Analyze a single file for issues."""
        issues = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Check for TODO patterns
            for pattern in self.todo_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    description = match.group(1).strip()
                    issue = CodeIssue(
                        file_path=file_path,
                        line_number=line_num,
                        issue_type='todo',
                        description=description,
                        code_snippet=line.strip(),
                        severity='medium',
                        context=self._get_context(lines, line_num)
                    )
                    issues.append(issue)
            
            # Check for missing implementation patterns
            for pattern in self.missing_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issue = CodeIssue(
                        file_path=file_path,
                        line_number=line_num,
                        issue_type='missing_implementation',
                        description='Missing implementation',
                        code_snippet=line.strip(),
                        severity='high',
                        context=self._get_context(lines, line_num)
                    )
                    issues.append(issue)
        
        # Check for incomplete function implementations
        incomplete_functions = self._find_incomplete_functions(content, file_path)
        issues.extend(incomplete_functions)
        
        # Check for empty or minimal implementations
        empty_implementations = self._find_empty_implementations(content, file_path)
        issues.extend(empty_implementations)
        
        return issues
    
    def _get_context(self, lines: List[str], line_num: int, context_lines: int = 3) -> str:
        """Get context around a specific line."""
        start = max(0, line_num - context_lines - 1)
        end = min(len(lines), line_num + context_lines)
        
        context_lines_list = []
        for i in range(start, end):
            prefix = ">>> " if i == line_num - 1 else "    "
            context_lines_list.append(f"{i+1:3d}{prefix}{lines[i]}")
        
        return "\n".join(context_lines_list)
    
    def _find_incomplete_functions(self, content: str, file_path: str) -> List[CodeIssue]:
        """Find incomplete function implementations."""
        issues = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # Check for function definitions
            func_match = re.match(r'def\s+(\w+)\s*\([^)]*\):', line)
            if func_match:
                func_name = func_match.group(1)
                
                # Look at the next few lines for incomplete patterns
                for j in range(i + 1, min(i + 5, len(lines))):
                    next_line = lines[j].strip()
                    
                    # Check for pass statements
                    if next_line == 'pass':
                        issue = CodeIssue(
                            file_path=file_path,
                            line_number=i + 1,
                            issue_type='incomplete',
                            description=f'Function "{func_name}" has empty implementation (pass)',
                            code_snippet=line.strip(),
                            severity='high',
                            context=self._get_context(lines, i + 1)
                        )
                        issues.append(issue)
                        break
                    
                    # Check for TODO comments
                    elif re.search(r'#\s*todo', next_line, re.IGNORECASE):
                        issue = CodeIssue(
                            file_path=file_path,
                            line_number=i + 1,
                            issue_type='incomplete',
                            description=f'Function "{func_name}" has TODO comment',
                            code_snippet=line.strip(),
                            severity='medium',
                            context=self._get_context(lines, i + 1)
                        )
                        issues.append(issue)
                        break
                    
                    # Check for NotImplementedError
                    elif 'NotImplementedError' in next_line:
                        issue = CodeIssue(
                            file_path=file_path,
                            line_number=i + 1,
                            issue_type='incomplete',
                            description=f'Function "{func_name}" raises NotImplementedError',
                            code_snippet=line.strip(),
                            severity='high',
                            context=self._get_context(lines, i + 1)
                        )
                        issues.append(issue)
                        break
        
        return issues
    
    def _find_empty_implementations(self, content: str, file_path: str) -> List[CodeIssue]:
        """Find empty or minimal implementations."""
        issues = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # Check for return None or return statements without logic
            if re.match(r'\s*return\s+None\s*$', line) or re.match(r'\s*return\s*$', line):
                # Look for function definition above
                for j in range(i - 1, max(0, i - 5), -1):
                    func_match = re.match(r'def\s+(\w+)\s*\([^)]*\):', lines[j])
                    if func_match:
                        func_name = func_match.group(1)
                        issue = CodeIssue(
                            file_path=file_path,
                            line_number=j + 1,
                            issue_type='empty_implementation',
                            description=f'Function "{func_name}" has minimal implementation',
                            code_snippet=lines[j].strip(),
                            severity='medium',
                            context=self._get_context(lines, j + 1)
                        )
                        issues.append(issue)
                        break
        
        return issues
    
    def generate_improvement_instructions(self, issues: List[CodeIssue]) -> List[str]:
        """Generate improvement instructions based on found issues."""
        instructions = []
        
        # Group issues by type
        todo_issues = [issue for issue in issues if issue.issue_type == 'todo']
        incomplete_issues = [issue for issue in issues if issue.issue_type == 'incomplete']
        missing_issues = [issue for issue in issues if issue.issue_type == 'missing_implementation']
        empty_issues = [issue for issue in issues if issue.issue_type == 'empty_implementation']
        
        if todo_issues:
            instructions.append(f"Complete {len(todo_issues)} TODO items found in the code:")
            for issue in todo_issues[:5]:  # Limit to first 5
                instructions.append(f"- {issue.file_path}:{issue.line_number} - {issue.description}")
        
        if incomplete_issues:
            instructions.append(f"Implement {len(incomplete_issues)} incomplete functions:")
            for issue in incomplete_issues[:5]:  # Limit to first 5
                instructions.append(f"- {issue.file_path}:{issue.line_number} - {issue.description}")
        
        if missing_issues:
            instructions.append(f"Add missing implementations for {len(missing_issues)} items:")
            for issue in missing_issues[:5]:  # Limit to first 5
                instructions.append(f"- {issue.file_path}:{issue.line_number} - {issue.description}")
        
        if empty_issues:
            instructions.append(f"Enhance {len(empty_issues)} empty or minimal implementations:")
            for issue in empty_issues[:5]:  # Limit to first 5
                instructions.append(f"- {issue.file_path}:{issue.line_number} - {issue.description}")
        
        if not instructions:
            instructions.append("No specific improvement instructions - code appears complete")
        
        return instructions
    
    def get_issues_summary(self, issues: List[CodeIssue]) -> Dict[str, Any]:
        """Get a summary of all issues found."""
        summary = {
            'total_issues': len(issues),
            'by_type': {},
            'by_severity': {},
            'by_file': {},
            'high_priority_issues': []
        }
        
        for issue in issues:
            # Count by type
            summary['by_type'][issue.issue_type] = summary['by_type'].get(issue.issue_type, 0) + 1
            
            # Count by severity
            summary['by_severity'][issue.severity] = summary['by_severity'].get(issue.severity, 0) + 1
            
            # Count by file
            summary['by_file'][issue.file_path] = summary['by_file'].get(issue.file_path, 0) + 1
            
            # High priority issues
            if issue.severity == 'high':
                summary['high_priority_issues'].append({
                    'file': issue.file_path,
                    'line': issue.line_number,
                    'description': issue.description,
                    'type': issue.issue_type
                })
        
        return summary 