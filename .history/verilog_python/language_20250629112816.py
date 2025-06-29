"""
Verilog::Language - Verilog language utilities

This module provides general utilities for using the Verilog Language,
such as parsing numbers or determining what keywords exist.
"""

import re
from typing import Dict, List, Optional, Union, Tuple


class Language:
    """Verilog language utilities class"""
    
    VERSION = '1.0.0'
    
    # Language standards
    STANDARDS = [
        '1364-1995', '1364-2001', '1364-2005', 
        '1800-2005', '1800-2009', '1800-2012', 
        '1800-2017', '1800-2023', 'VAMS'
    ]
    
    # Keywords by language standard
    KEYWORDS = {
        '1364-1995': {
            'always', 'and', 'assign', 'begin', 'buf', 'bufif0', 'bufif1',
            'case', 'casex', 'casez', 'cmos', 'deassign', 'default', 'defparam',
            'disable', 'else', 'end', 'endcase', 'endfunction', 'endmodule',
            'endprimitive', 'endspecify', 'endtable', 'endtask', 'event',
            'for', 'force', 'forever', 'fork', 'function', 'highz0', 'highz1',
            'if', 'initial', 'inout', 'input', 'integer', 'join', 'large',
            'macromodule', 'medium', 'module', 'nand', 'negedge', 'nmos',
            'nor', 'not', 'notif0', 'notif1', 'or', 'output', 'parameter',
            'pmos', 'posedge', 'primitive', 'pull0', 'pull1', 'pulldown',
            'pullup', 'rcmos', 'real', 'realtime', 'reg', 'release', 'repeat',
            'rnmos', 'rpmos', 'rtran', 'rtranif0', 'rtranif1', 'scalared',
            'small', 'specify', 'strength', 'strong0', 'strong1', 'supply0',
            'supply1', 'table', 'task', 'time', 'tran', 'tranif0', 'tranif1',
            'tri', 'tri0', 'tri1', 'triand', 'trior', 'trireg', 'vectored',
            'wait', 'wand', 'weak0', 'weak1', 'while', 'wire', 'wor', 'xnor', 'xor'
        },
        '1364-2001': {
            'automatic', 'cell', 'config', 'design', 'edge', 'endconfig',
            'endgenerate', 'generate', 'genvar', 'ifnone', 'incdir', 'include',
            'instance', 'liblist', 'library', 'localparam', 'noshowcancelled',
            'pulsestyle_ondetect', 'pulsestyle_onevent', 'showcancelled',
            'signed', 'specparam', 'unsigned', 'use'
        },
        '1364-2005': {
            'uwire'
        },
        '1800-2005': {
            'alias', 'always_comb', 'always_ff', 'always_latch', 'assert',
            'assume', 'before', 'bind', 'bins', 'binsof', 'bit', 'break',
            'byte', 'chandle', 'class', 'clocking', 'const', 'constraint',
            'context', 'continue', 'cover', 'covergroup', 'coverpoint',
            'cross', 'dist', 'do', 'endclass', 'endclocking', 'endgroup',
            'endinterface', 'endpackage', 'endprogram', 'endproperty',
            'endsequence', 'enum', 'expect', 'export', 'extends', 'extern',
            'final', 'first_match', 'foreach', 'forkjoin', 'iff',
            'ignore_bins', 'illegal_bins', 'import', 'inside', 'int',
            'interface', 'intersect', 'join_any', 'join_none', 'local',
            'logic', 'longint', 'matches', 'modport', 'new', 'null',
            'package', 'packed', 'priority', 'program', 'property',
            'protected', 'rand', 'randc', 'randcase', 'randsequence',
            'ref', 'return', 'sequence', 'shortint', 'shortreal',
            'solve', 'static', 'string', 'struct', 'super', 'tagged',
            'this', 'type', 'typedef', 'union', 'unique', 'var',
            'virtual', 'void', 'wait_order', 'wildcard', 'with'
        }
    }
    
    # Compiler directives
    COMPDIRECTS = {
        '`begin_keywords', '`celldefine', '`default_nettype', '`define',
        '`else', '`elsif', '`end_keywords', '`endcelldefine', '`endif',
        '`ifdef', '`ifndef', '`include', '`line', '`nounconnected_drive',
        '`pragma', '`resetall', '`timescale', '`unconnected_drive',
        '`undef', '`undefineall'
    }
    
    # Gate primitives
    GATEPRIMS = {
        'and', 'nand', 'or', 'nor', 'xor', 'xnor', 'buf', 'not',
        'bufif0', 'bufif1', 'notif0', 'notif1', 'pullup', 'pulldown',
        'cmos', 'rcmos', 'nmos', 'pmos', 'rnmos', 'rpmos', 'tran',
        'rtran', 'tranif0', 'tranif1', 'rtranif0', 'rtranif1'
    }
    
    def __init__(self, standard: Optional[str] = None):
        """Initialize Language with optional standard specification"""
        self.standard = standard
        self._all_keywords = self._build_keyword_set()
    
    def _build_keyword_set(self) -> set:
        """Build complete keyword set based on standard"""
        keywords = set()
        if self.standard:
            # Add keywords up to specified standard
            for std in self.STANDARDS:
                if std in self.KEYWORDS:
                    keywords.update(self.KEYWORDS[std])
                if std == self.standard:
                    break
        else:
            # Add all keywords
            for std_keywords in self.KEYWORDS.values():
                keywords.update(std_keywords)
        return keywords
    
    @classmethod
    def is_keyword(cls, symbol: str, standard: Optional[str] = None) -> bool:
        """Return true if the given symbol string is a Verilog reserved keyword"""
        if not standard in cls.STANDARDS:
            return False
        
        if standard:
            lang = cls(standard)
        else:
            lang = cls()
        return symbol in lang._all_keywords
    
    @classmethod
    def is_compdirect(cls, symbol: str) -> bool:
        """Return true if the given symbol string is a Verilog compiler directive"""
        return symbol in cls.COMPDIRECTS
    
    @classmethod
    def is_gateprim(cls, symbol: str) -> bool:
        """Return true if the given symbol is a built in gate primitive"""
        return symbol in cls.GATEPRIMS
    
    @classmethod
    def language_standard(cls, standard: str) -> None:
        """Set the language standard for keyword checking"""
        if standard not in cls.STANDARDS:
            raise ValueError(f"Unknown language standard: {standard}")
        cls._current_standard = standard
    
    @classmethod
    def language_maximum(cls) -> str:
        """Returns the greatest language currently standardized"""
        return '1800-2023'
    
    @classmethod
    def number_value(cls, number_string: str) -> Optional[int]:
        """Return the numeric value of a Verilog value, or None if incorrectly formed"""
        try:
            # Handle signed numbers: 1'sh1, 32'sh1b, etc.
            signed_match = re.match(r'(\d+)\'s([bdh])([0-9a-fA-F_xXzZ]+)', number_string)
            if signed_match:
                size, base, value = signed_match.groups()
                # Convert to integer based on base
                if base == 'b':
                    # Binary
                    value = value.replace('_', '').replace('x', '0').replace('z', '0')
                    return int(value, 2)
                elif base == 'd':
                    # Decimal
                    value = value.replace('_', '').replace('x', '0').replace('z', '0')
                    return int(value, 10)
                elif base == 'h':
                    # Hexadecimal
                    value = value.replace('_', '').replace('x', '0').replace('z', '0')
                    return int(value, 16)
            
            # Handle unsigned numbers: 32'h1b, 4'b111, etc.
            unsigned_match = re.match(r'(\d+)\'([bdh])([0-9a-fA-F_xXzZ]+)', number_string)
            if unsigned_match:
                size, base, value = unsigned_match.groups()
                # Convert to integer based on base
                if base == 'b':
                    # Binary
                    value = value.replace('_', '').replace('x', '0').replace('z', '0')
                    return int(value, 2)
                elif base == 'd':
                    # Decimal
                    value = value.replace('_', '').replace('x', '0').replace('z', '0')
                    return int(value, 10)
                elif base == 'h':
                    # Hexadecimal
                    value = value.replace('_', '').replace('x', '0').replace('z', '0')
                    return int(value, 16)
            
            # Handle simple decimal numbers
            if re.match(r'^\d+$', number_string):
                return int(number_string)
            
            return None
        except (ValueError, AttributeError):
            return None
    
    @classmethod
    def unsigned_to_signed(cls, x:int, n:int) -> int:
        if (x >> (n - 1)) == 1:
            signed_x = (1 << n) - x
            return -signed_x
        else:
            return x
    
    @classmethod
    def number_bits(cls, number_string: str) -> Optional[int]:
        """Return the number of bits in a value string, or None if incorrectly formed"""
        # Handle signed numbers: 1'sh1, 32'sh1b, etc.
        signed_match = re.match(r'(\d+)\'(s\w)([a-f0-9A-F_]+)', number_string)
        
        if signed_match:
            print(signed_match.groups())
            if signed_match.group(2) == 'sb':
                # Binary
                value = signed_match.group(3).replace('_', '').replace('x', '0').replace('z', '0')
                return cls.unsigned_to_signed(int(value, 2), int(signed_match.group(1)))
            elif signed_match.group(2) == 'sd':
                # Decimal
                value = signed_match.group(3).replace('_', '').replace('x', '0').replace('z', '0')
                return cls.unsigned_to_signed(int(value, 10), int(signed_match.group(1)))
            elif signed_match.group(2) == 'sh':
                # Hexadecimal
                value = signed_match.group(3).replace('_', '').replace('x', '0').replace('z', '0')
                return cls.unsigned_to_signed(int(value, 16), int(signed_match.group(1)))
        
        # Handle unsigned numbers: 32'h1b, 4'b111, etc.
        unsigned_match = re.match(r'(\d+)\'(\w)([a-f0-9A-F_]+)', number_string)
        if unsigned_match:
            # print(unsigned_match.group(2))
            if unsigned_match.group(2) == 'b':
                # Binary
                value = unsigned_match.group(3).replace('_', '').replace('x', '0').replace('z', '0')
                return int(value, 2)
            elif unsigned_match.group(2) == 'd':
                # Decimal
                value = unsigned_match.group(3).replace('_', '').replace('x', '0').replace('z', '0')
                return int(value, 10)
            elif unsigned_match.group(2) == 'h':
                # Hexadecimal
                value = unsigned_match.group(3).replace('_', '').replace('x', '0').replace('z', '0')
                return int(value, 16)
        return None
    
    @classmethod
    def number_signed(cls, number_string: str) -> Optional[bool]:
        """Return true if the Verilog value is signed, else None"""
        # Check for signed notation: 1'sh1, 32'sh1b, etc.
        if re.match(r'\d+\'s[bdh]', number_string):
            return True
        return None
    
    @classmethod
    def split_bus(cls, bus: str) -> List[str]:
        """Return a list of expanded arrays"""
        # Simple implementation for basic bus expansion
        # This is a simplified version - full implementation would be more complex
        match = re.match(r'(\w+)\[(\d+):(\d+)\]', bus)
        if match:
            name, high, low = match.groups()
            high, low = int(high), int(low)
            result = []
            for i in range(high, low - 1, -1):
                result.append(f"{name}[{i}]")
            return result
        return [bus]
    
    @classmethod
    def split_bus_nocomma(cls, bus: str) -> List[str]:
        """As with split_bus, but faster for simple decimal colon separated arrays"""
        return cls.split_bus(bus)
    
    @classmethod
    def strip_comments(cls, text: str) -> str:
        """Return text with any // or /**/ comments stripped"""
        # Remove // comments
        text = re.sub(r'//.*$', '', text, flags=re.MULTILINE)
        # Remove /* */ comments
        text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
        return text 









 
    
