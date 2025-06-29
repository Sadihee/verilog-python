"""
Verilog-Python - Python implementation of Verilog language utilities

This is a Python translation of the verilog-perl library, providing
parsing and utilities for the Verilog Language.

Main components:
- Language: Verilog language utilities and keyword checking
- Parser: Tokenization and parsing of Verilog files
- Preproc: Preprocessing of Verilog files
- Netlist: Design hierarchy and netlist management
- Getopt: Command line option handling
"""

__version__ = '1.0.0'

from .language import Language
from .parser import Parser, SigParser
from .preproc import Preproc
from .netlist import Netlist
from .getopt import Getopt

__all__ = [
    'Language',
    'Parser', 
    'SigParser',
    'Preproc',
    'Netlist',
    'Getopt'
] 