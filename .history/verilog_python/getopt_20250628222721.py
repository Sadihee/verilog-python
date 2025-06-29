"""
Verilog::Getopt - Standardized handling of options similar to Verilog/VCS and cc/GCC

This module provides command line option parsing and file handling for
Verilog tools, similar to the behavior of commercial Verilog tools.
"""

import os
import re
import sys
from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path


class Getopt:
    """Command line option handling for Verilog tools"""
    
    def __init__(self, filename_expansion: bool = True):
        """Initialize Getopt with options"""
        self.filename_expansion = filename_expansion
        self.defines = {}  # -D defines
        self.include_paths = []  # -I include paths
        self.files = []  # Input files
        self.depend_files = []  # Files for dependency tracking
        self.options = {}  # Other options
        
        # Common Verilog tool options
        self.option_patterns = {
            '-D': self._handle_define,
            '-I': self._handle_include,
            '-f': self._handle_file_list,
            '-y': self._handle_library,
            '+incdir+': self._handle_include,
            '+define+': self._handle_define,
            '+libext+': self._handle_libext,
            '+liborder+': self._handle_liborder,
        }
    
    def parameter(self, args: List[str]) -> List[str]:
        """Process command line parameters and return remaining args"""
        processed_args = []
        i = 0
        
        while i < len(args):
            arg = args[i]
            
            # Handle known option patterns
            handled = False
            for pattern, handler in self.option_patterns.items():
                if arg.startswith(pattern):
                    if pattern in ['-D', '-I', '-f', '-y']:
                        # These take a value
                        if i + 1 < len(args):
                            handler(arg, args[i + 1])
                            i += 2
                        else:
                            raise ValueError(f"Option {arg} requires a value")
                    else:
                        # These have the value in the same argument
                        handler(arg)
                        i += 1
                    handled = True
                    break
            
            if not handled:
                # Check for +define+ and +incdir+ patterns
                if arg.startswith('+define+'):
                    self._handle_define(arg)
                    i += 1
                elif arg.startswith('+incdir+'):
                    self._handle_include(arg)
                    i += 1
                elif arg.startswith('+libext+'):
                    self._handle_libext(arg)
                    i += 1
                elif arg.startswith('+liborder+'):
                    self._handle_liborder(arg)
                    i += 1
                elif arg.startswith('-'):
                    # Unknown option, pass through
                    processed_args.append(arg)
                    i += 1
                else:
                    # File argument
                    if self.filename_expansion:
                        expanded_files = self._expand_filename(arg)
                        self.files.extend(expanded_files)
                        self.depend_files.extend(expanded_files)
                    else:
                        self.files.append(arg)
                        self.depend_files.append(arg)
                    i += 1
        
        return processed_args
    
    def _handle_define(self, option: str, value: Optional[str] = None) -> None:
        """Handle -D or +define+ options"""
        if value is None:
            # +define+ format
            if '=' in option:
                name, val = option.split('=', 1)
                name = name.replace('+define+', '')
                self.defines[name] = val
            else:
                name = option.replace('+define+', '')
                self.defines[name] = '1'
        else:
            # -D format
            if '=' in value:
                name, val = value.split('=', 1)
                self.defines[name] = val
            else:
                self.defines[value] = '1'
    
    def _handle_include(self, option: str, value: Optional[str] = None) -> None:
        """Handle -I or +incdir+ options"""
        if value is None:
            # +incdir+ format
            path = option.replace('+incdir+', '')
            self.include_paths.append(path)
        else:
            # -I format
            self.include_paths.append(value)
    
    def _handle_file_list(self, option: str, filename: str) -> None:
        """Handle -f file list option"""
        try:
            with open(filename, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Expand any options in the file
                        if line.startswith('-'):
                            # This is an option, not a file
                            continue
                        if self.filename_expansion:
                            expanded_files = self._expand_filename(line)
                            self.files.extend(expanded_files)
                            self.depend_files.extend(expanded_files)
                        else:
                            self.files.append(line)
                            self.depend_files.append(line)
        except FileNotFoundError:
            raise ValueError(f"File list not found: {filename}")
    
    def _handle_library(self, option: str, library_path: str) -> None:
        """Handle -y library option"""
        self.options['libraries'] = self.options.get('libraries', [])
        self.options['libraries'].append(library_path)
    
    def _handle_libext(self, option: str) -> None:
        """Handle +libext+ option"""
        extensions = option.replace('+libext+', '').split('+')
        self.options['libext'] = extensions
    
    def _handle_liborder(self, option: str) -> None:
        """Handle +liborder+ option"""
        order = option.replace('+liborder+', '')
        self.options['liborder'] = order
    
    def _expand_filename(self, filename: str) -> List[str]:
        """Expand filename patterns (globbing)"""
        try:
            # Use pathlib for cross-platform globbing
            path = Path(filename)
            if '*' in filename or '?' in filename:
                # This is a pattern, expand it
                parent = path.parent
                pattern = path.name
                if parent.exists():
                    return [str(p) for p in parent.glob(pattern)]
                else:
                    return []
            else:
                # Single file
                return [filename] if Path(filename).exists() else []
        except Exception:
            return [filename]
    
    def defvalue(self, symbol: str) -> Optional[str]:
        """Get the value of a define, with warning if not found"""
        if symbol in self.defines:
            return self.defines[symbol]
        print(f"Warning: Define '{symbol}' not found", file=sys.stderr)
        return None
    
    def defvalue_nowarn(self, symbol: str) -> Optional[str]:
        """Get the value of a define, without warning if not found"""
        return self.defines.get(symbol)
    
    def get_files(self) -> List[str]:
        """Get the list of input files"""
        return self.files.copy()
    
    def get_defines(self) -> Dict[str, str]:
        """Get the dictionary of defines"""
        return self.defines.copy()
    
    def get_include_paths(self) -> List[str]:
        """Get the list of include paths"""
        return self.include_paths.copy()
    
    def get_options(self) -> Dict[str, Any]:
        """Get the dictionary of other options"""
        return self.options.copy() 