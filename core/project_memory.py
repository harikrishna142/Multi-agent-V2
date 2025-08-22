"""
Project Memory System using RAG (Retrieval-Augmented Generation)
Maintains context and history across agent iterations.
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import pickle

@dataclass
class CodeSnippet:
    """Represents a code snippet with metadata."""
    content: str
    file_path: str
    line_start: int
    line_end: int
    snippet_type: str  # 'function', 'class', 'todo', 'placeholder'
    context: str
    timestamp: datetime

@dataclass
class ProjectMemory:
    """Project memory with code history and context."""
    project_id: str
    code_snippets: List[CodeSnippet]
    iteration_history: List[Dict[str, Any]]
    current_iteration: int
    max_iterations: int
    specifications: Dict[str, Any]
    review_feedback: List[str]
    improvement_instructions: List[str]

class ProjectMemoryManager:
    """Manages project memory using RAG for context retrieval."""
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.memory_file = f"output/project_memory/{project_id}/memory.pkl"
        self.code_index_file = f"output/project_memory/{project_id}/code_index.json"
        self.memory = self._load_or_create_memory()
        
    def _load_or_create_memory(self) -> ProjectMemory:
        """Load existing memory or create new one."""
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                print(f"Failed to load memory: {e}")
        
        return ProjectMemory(
            project_id=self.project_id,
            code_snippets=[],
            iteration_history=[],
            current_iteration=0,
            max_iterations=3,
            specifications={},
            review_feedback=[],
            improvement_instructions=[]
        )
    
    def save_memory(self):
        """Save memory to disk."""
        try:
            with open(self.memory_file, 'wb') as f:
                pickle.dump(self.memory, f)
            
            # Also save code index for quick retrieval
            self._save_code_index()
        except Exception as e:
            print(f"Failed to save memory: {e}")
    
    def _save_code_index(self):
        """Save code index for quick retrieval."""
        index = {
            'project_id': self.project_id,
            'snippets': [
                {
                    'content': snippet.content,
                    'file_path': snippet.file_path,
                    'line_start': snippet.line_start,
                    'line_end': snippet.line_end,
                    'snippet_type': snippet.snippet_type,
                    'context': snippet.context,
                    'timestamp': snippet.timestamp.isoformat()
                }
                for snippet in self.memory.code_snippets
            ],
            'iteration_history': self.memory.iteration_history,
            'current_iteration': self.memory.current_iteration,
            'review_feedback': self.memory.review_feedback,
            'improvement_instructions': self.memory.improvement_instructions
        }
        
        with open(self.code_index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
    
    def add_code_snippet(self, content: str, file_path: str, line_start: int, 
                        line_end: int, snippet_type: str, context: str = ""):
        """Add a code snippet to memory."""
        snippet = CodeSnippet(
            content=content,
            file_path=file_path,
            line_start=line_start,
            line_end=line_end,
            snippet_type=snippet_type,
            context=context,
            timestamp=datetime.now()
        )
        self.memory.code_snippets.append(snippet)
        self.save_memory()
    
    def add_iteration_record(self, iteration_data: Dict[str, Any]):
        """Add iteration record to history."""
        iteration_data['timestamp'] = datetime.now().isoformat()
        iteration_data['iteration_number'] = self.memory.current_iteration
        self.memory.iteration_history.append(iteration_data)
        self.save_memory()
    
    def add_review_feedback(self, feedback: str):
        """Add review feedback."""
        self.memory.review_feedback.append(feedback)
        self.save_memory()
    
    def add_improvement_instruction(self, instruction: str):
        """Add improvement instruction."""
        self.memory.improvement_instructions.append(instruction)
        self.save_memory()
    
    def get_code_context(self, query: str = "") -> str:
        """Get relevant code context using RAG."""
        if not self.memory.code_snippets:
            return "No code context available."
        
        # Simple RAG implementation - filter and rank snippets
        relevant_snippets = []
        
        for snippet in self.memory.code_snippets:
            relevance_score = 0
            
            # Check if query matches snippet content
            if query.lower() in snippet.content.lower():
                relevance_score += 3
            
            # Prioritize TODOs and placeholders
            if snippet.snippet_type in ['todo', 'placeholder']:
                relevance_score += 5
            
            # Prioritize recent snippets
            if snippet.timestamp:
                time_diff = (datetime.now() - snippet.timestamp).total_seconds()
                if time_diff < 3600:  # Last hour
                    relevance_score += 2
            
            if relevance_score > 0:
                relevant_snippets.append((snippet, relevance_score))
        
        # Sort by relevance score
        relevant_snippets.sort(key=lambda x: x[1], reverse=True)
        
        # Build context string
        context_parts = []
        context_parts.append(f"# Project Context for {self.project_id}")
        context_parts.append(f"Current Iteration: {self.memory.current_iteration}/{self.memory.max_iterations}")
        
        if self.memory.review_feedback:
            context_parts.append("\n## Recent Review Feedback:")
            for feedback in self.memory.review_feedback[-3:]:  # Last 3 feedback items
                context_parts.append(f"- {feedback}")
        
        if self.memory.improvement_instructions:
            context_parts.append("\n## Improvement Instructions:")
            for instruction in self.memory.improvement_instructions[-3:]:  # Last 3 instructions
                context_parts.append(f"- {instruction}")
        
        context_parts.append("\n## Relevant Code Snippets:")
        
        for snippet, score in relevant_snippets[:10]:  # Top 10 most relevant
            context_parts.append(f"\n### {snippet.file_path} (lines {snippet.line_start}-{snippet.line_end})")
            context_parts.append(f"Type: {snippet.snippet_type}")
            context_parts.append(f"Relevance Score: {score}")
            context_parts.append("```")
            context_parts.append(snippet.content)
            context_parts.append("```")
            if snippet.context:
                context_parts.append(f"Context: {snippet.context}")
        
        return "\n".join(context_parts)
    
    def get_iteration_summary(self) -> str:
        """Get summary of all iterations."""
        if not self.memory.iteration_history:
            return "No iterations recorded yet."
        
        summary_parts = []
        summary_parts.append(f"# Iteration Summary for {self.project_id}")
        summary_parts.append(f"Total Iterations: {len(self.memory.iteration_history)}")
        summary_parts.append(f"Current Iteration: {self.memory.current_iteration}")
        
        for i, iteration in enumerate(self.memory.iteration_history):
            summary_parts.append(f"\n## Iteration {i + 1}")
            summary_parts.append(f"Timestamp: {iteration.get('timestamp', 'N/A')}")
            summary_parts.append(f"Status: {iteration.get('status', 'N/A')}")
            
            if 'quality_score' in iteration:
                summary_parts.append(f"Quality Score: {iteration['quality_score']}")
            
            if 'issues_found' in iteration:
                summary_parts.append(f"Issues Found: {iteration['issues_found']}")
            
            if 'improvements_made' in iteration:
                improvements = iteration['improvements_made']
                if isinstance(improvements, list):
                    summary_parts.append(f"Improvements Made: {len(improvements)}")
                else:
                    summary_parts.append(f"Improvements Made: {improvements}")
        
        return "\n".join(summary_parts)
    
    def increment_iteration(self):
        """Increment current iteration."""
        self.memory.current_iteration += 1
        self.save_memory()
    
    def can_continue_iterations(self) -> bool:
        """Check if more iterations are allowed."""
        return self.memory.current_iteration < self.memory.max_iterations
    
    def get_project_specifications(self) -> Dict[str, Any]:
        """Get project specifications."""
        return self.memory.specifications
    
    def set_project_specifications(self, specifications: Dict[str, Any]):
        """Set project specifications."""
        self.memory.specifications = specifications
        self.save_memory() 