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

from .preproc import Preproc

from .getopt import Getopt

from .parser import Parser
from .parser import SigParser
from .parser import TokenType
from .parser import Token

from .netlist import Netlist
from .netlist import Net
from .netlist import Port
from .netlist import Pin
from .netlist import Cell
from .netlist import Module




__all__ = [
    'Language',
    'Parser', 
    'SigParser',
    'Preproc',
    'Netlist',
    'Getopt'
] 