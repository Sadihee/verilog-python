"""
Verilog::Preproc - Verilog preprocessor

This module reads Verilog files and preprocesses them according to
the Verilog specification, handling includes, defines, and other
preprocessor directives.
"""

import os
import re
import sys
from typing import List, Dict, Optional, TextIO, Iterator
from pathlib import Path


class Preproc:
    """Verilog preprocessor class"""
    
    def __init__(self, defines: Optional[Dict[str, str]] = None, 
                 include_paths: Optional[List[str]] = None):
        """Initialize preprocessor with defines and include paths"""
        self.defines = defines or {}
        self.include_paths = include_paths or []
        self.include_stack = []  # Track included files
        self.line_directives = []  # Track line directives
        self.conditional_stack = []  # Track ifdef/ifndef nesting
        
        # Preprocessor directive patterns
        self.directives = {
            'define': self._handle_define,
            'undef': self._handle_undef,
            'include': self._handle_include,
            'ifdef': self._handle_ifdef,
            'ifndef': self._handle_ifndef,
            'else': self._handle_else,
            'elsif': self._handle_elsif,
            'endif': self._handle_endif,
            'timescale': self._handle_timescale,
            'line': self._handle_line,
            'pragma': self._handle_pragma,
            'begin_keywords': self._handle_begin_keywords,
            'end_keywords': self._handle_end_keywords,
        }
    
    def preprocess_file(self, filename: str) -> str:
        """Preprocess a Verilog file and return the processed content"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return self.preprocess_stream(f, filename)
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {filename}")
    
    def preprocess_stream(self, stream: TextIO, filename: str = "<stream>") -> str:
        """Preprocess a file stream and return the processed content"""
        self.include_stack.append(filename)
        result = []
        
        try:
            for line_num, line in enumerate(stream, 1):
                processed_line = self._process_line(line, line_num, filename)
                if processed_line is not None:
                    result.append(processed_line)
        finally:
            self.include_stack.pop()
        
        return ''.join(result)
    
    def _process_line(self, line: str, line_num: int, filename: str) -> Optional[str]:
        """Process a single line of Verilog code"""
        # Handle line continuation
        if line.rstrip().endswith('\\'):
            # This is a continuation line
            return line.rstrip()[:-1] + ' '
        
        # Check for preprocessor directives
        directive_match = re.match(r'^\s*`(\w+)', line)
        if directive_match:
            directive = directive_match.group(1)
            if directive in self.directives:
                return self.directives[directive](line, line_num, filename)
            else:
                # Unknown directive, pass through
                return line
        
        # Check if we're in a conditional block that should be excluded
        if self.conditional_stack and not self.conditional_stack[-1]['active']:
            return None
        
        # Handle defines in the line
        return self._expand_defines(line)
    
    def _handle_define(self, line: str, line_num: int, filename: str) -> Optional[str]:
        """Handle `define directive"""
        # Skip if in inactive conditional block
        if self.conditional_stack and not self.conditional_stack[-1]['active']:
            return None
        
        # Parse define: `define name value
        match = re.match(r'^\s*`define\s+(\w+)(?:\s+(.+))?$', line)
        if match:
            name = match.group(1)
            value = match.group(2) or ''
            self.defines[name] = value.strip()
        
        return None  # Don't include define lines in output
    
    def _handle_undef(self, line: str, line_num: int, filename: str) -> Optional[str]:
        """Handle `undef directive"""
        if self.conditional_stack and not self.conditional_stack[-1]['active']:
            return None
        
        match = re.match(r'^\s*`undef\s+(\w+)', line)
        if match:
            name = match.group(1)
            if name in self.defines:
                del self.defines[name]
        
        return None
    
    def _handle_include(self, line: str, line_num: int, filename: str) -> Optional[str]:
        """Handle `include directive"""
        if self.conditional_stack and not self.conditional_stack[-1]['active']:
            return None
        
        # Parse include: `include "filename" or `include <filename>
        match = re.match(r'^\s*`include\s+["<]([^">]+)[">]', line)
        if match:
            include_file = match.group(1)
            resolved_file = self._resolve_include(include_file, filename)
            if resolved_file:
                try:
                    with open(resolved_file, 'r', encoding='utf-8') as f:
                        included_content = self.preprocess_stream(f, resolved_file)
                        return included_content
                except FileNotFoundError:
                    print(f"Warning: Include file not found: {include_file}", 
                          file=sys.stderr)
        
        return None
    
    def _handle_ifdef(self, line: str, line_num: int, filename: str) -> Optional[str]:
        """Handle `ifdef directive"""
        match = re.match(r'^\s*`ifdef\s+(\w+)', line)
        if match:
            name = match.group(1)
            active = name in self.defines
            self.conditional_stack.append({
                'type': 'ifdef',
                'active': active,
                'had_else': False
            })
        
        return None
    
    def _handle_ifndef(self, line: str, line_num: int, filename: str) -> Optional[str]:
        """Handle `ifndef directive"""
        match = re.match(r'^\s*`ifndef\s+(\w+)', line)
        if match:
            name = match.group(1)
            active = name not in self.defines
            self.conditional_stack.append({
                'type': 'ifndef',
                'active': active,
                'had_else': False
            })
        
        return None
    
    def _handle_else(self, line: str, line_num: int, filename: str) -> Optional[str]:
        """Handle `else directive"""
        if not self.conditional_stack:
            print(f"Warning: `else without matching `ifdef/`ifndef", file=sys.stderr)
            return None
        
        current = self.conditional_stack[-1]
        if current['had_else']:
            print(f"Warning: Multiple `else in conditional block", file=sys.stderr)
            return None
        
        current['active'] = not current['active']
        current['had_else'] = True
        
        return None
    
    def _handle_elsif(self, line: str, line_num: int, filename: str) -> Optional[str]:
        """Handle `elsif directive"""
        if not self.conditional_stack:
            print(f"Warning: `elsif without matching `ifdef/`ifndef", file=sys.stderr)
            return None
        
        current = self.conditional_stack[-1]
        if current['had_else']:
            print(f"Warning: `elsif after `else", file=sys.stderr)
            return None
        
        match = re.match(r'^\s*`elsif\s+(\w+)', line)
        if match:
            name = match.group(1)
            # Only active if previous conditions were false and this one is true
            current['active'] = not current.get('previous_active', False) and name in self.defines
            current['previous_active'] = current['active']
        
        return None
    
    def _handle_endif(self, line: str, line_num: int, filename: str) -> Optional[str]:
        """Handle `endif directive"""
        if not self.conditional_stack:
            print(f"Warning: `endif without matching `ifdef/`ifndef", file=sys.stderr)
            return None
        
        self.conditional_stack.pop()
        return None
    
    def _handle_timescale(self, line: str, line_num: int, filename: str) -> Optional[str]:
        """Handle `timescale directive"""
        # Pass through timescale directives
        return line
    
    def _handle_line(self, line: str, line_num: int, filename: str) -> Optional[str]:
        """Handle `line directive"""
        # Pass through line directives
        return line
    
    def _handle_pragma(self, line: str, line_num: int, filename: str) -> Optional[str]:
        """Handle `pragma directive"""
        # Pass through pragma directives
        return line
    
    def _handle_begin_keywords(self, line: str, line_num: int, filename: str) -> Optional[str]:
        """Handle `begin_keywords directive"""
        # Pass through keywords directives
        return line
    
    def _handle_end_keywords(self, line: str, line_num: int, filename: str) -> Optional[str]:
        """Handle `end_keywords directive"""
        # Pass through keywords directives
        return line
    
    def _resolve_include(self, include_file: str, current_file: str) -> Optional[str]:
        """Resolve an include file path"""
        # First check if it's an absolute path
        if os.path.isabs(include_file):
            return include_file if os.path.exists(include_file) else None
        
        # Check relative to current file
        current_dir = os.path.dirname(current_file)
        relative_path = os.path.join(current_dir, include_file)
        if os.path.exists(relative_path):
            return relative_path
        
        # Check include paths
        for include_path in self.include_paths:
            full_path = os.path.join(include_path, include_file)
            if os.path.exists(full_path):
                return full_path
        
        return None
    
    def _expand_defines(self, line: str) -> str:
        """Expand defines in a line of text"""
        # Simple define expansion - this could be made more sophisticated
        for name, value in self.defines.items():
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(name) + r'\b'
            line = re.sub(pattern, value, line)
        
        return line
    
    def get_defines(self) -> Dict[str, str]:
        """Get current defines dictionary"""
        return self.defines.copy()
    
    def add_define(self, name: str, value: str = '1') -> None:
        """Add a define"""
        self.defines[name] = value
    
    def remove_define(self, name: str) -> None:
        """Remove a define"""
        if name in self.defines:
            del self.defines[name] 