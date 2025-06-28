"""
Verilog::Parser - Verilog parser and tokenizer

This module provides tokenization and parsing of Verilog files,
with callback support for various language constructs.
"""

import re
from typing import List, Dict, Optional, Callable, Any, Tuple
from enum import Enum, auto


class TokenType(Enum):
    """Token types for Verilog parsing"""
    KEYWORD = auto()
    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()
    OPERATOR = auto()
    DELIMITER = auto()
    DIRECTIVE = auto()
    COMMENT = auto()
    WHITESPACE = auto()
    NEWLINE = auto()
    EOF = auto()


class Token:
    """Represents a token in the Verilog source"""
    
    def __init__(self, type_: TokenType, value: str, line: int, column: int):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column
    
    def __repr__(self):
        return f"Token({self.type.name}, '{self.value}', line={self.line}, col={self.column})"


class Parser:
    """Verilog parser with tokenization and callback support"""
    
    def __init__(self, callbacks: Optional[Dict[str, Callable]] = None):
        """Initialize parser with optional callbacks"""
        self.callbacks = callbacks or {}
        self.tokens = []
        self.current_token = 0
        self.line = 1
        self.column = 1
        
        # Token patterns
        self.patterns = [
            (TokenType.COMMENT, r'//.*$|/\*.*?\*/'),
            (TokenType.STRING, r'"[^"]*"'),
            (TokenType.NUMBER, r'\d+\'[bdh][0-9a-fA-F_xXzZ]+|\d+'),
            (TokenType.DIRECTIVE, r'`\w+'),
            (TokenType.KEYWORD, r'\b(module|endmodule|input|output|inout|wire|reg|always|assign|begin|end|if|else|case|endcase|for|while|function|endfunction|task|endtask|parameter|localparam|integer|real|time|initial|final)\b'),
            (TokenType.IDENTIFIER, r'\b[a-zA-Z_][a-zA-Z0-9_$]*\b'),
            (TokenType.OPERATOR, r'[+\-*/%<>=!&|^~]+'),
            (TokenType.DELIMITER, r'[(){}\[\];,.#:]'),
            (TokenType.WHITESPACE, r'\s+'),
        ]
        
        # Compile patterns
        self.compiled_patterns = []
        for token_type, pattern in self.patterns:
            self.compiled_patterns.append((token_type, re.compile(pattern)))
    
    def tokenize(self, text: str) -> List[Token]:
        """Tokenize Verilog text into tokens"""
        self.tokens = []
        self.current_token = 0
        self.line = 1
        self.column = 1
        
        pos = 0
        while pos < len(text):
            token = self._next_token(text, pos)
            if token:
                self.tokens.append(token)
                pos += len(token.value)
                if token.type == TokenType.NEWLINE:
                    self.line += 1
                    self.column = 1
                else:
                    self.column += len(token.value)
            else:
                # Skip unknown characters
                pos += 1
                self.column += 1
        
        # Add EOF token
        self.tokens.append(Token(TokenType.EOF, '', self.line, self.column))
        return self.tokens
    
    def _next_token(self, text: str, pos: int) -> Optional[Token]:
        """Get the next token from the text starting at pos"""
        remaining = text[pos:]
        
        for token_type, pattern in self.compiled_patterns:
            match = pattern.match(remaining)
            if match:
                value = match.group(0)
                
                # Handle comments specially
                if token_type == TokenType.COMMENT:
                    if value.startswith('//'):
                        # Single line comment
                        return Token(TokenType.COMMENT, value, self.line, self.column)
                    else:
                        # Multi-line comment
                        lines = value.count('\n')
                        return Token(TokenType.COMMENT, value, self.line, self.column)
                
                # Handle whitespace
                if token_type == TokenType.WHITESPACE:
                    if '\n' in value:
                        return Token(TokenType.NEWLINE, '\n', self.line, self.column)
                    else:
                        return Token(TokenType.WHITESPACE, value, self.line, self.column)
                
                return Token(token_type, value, self.line, self.column)
        
        return None
    
    def parse(self, text: str) -> None:
        """Parse Verilog text and invoke callbacks"""
        self.tokenize(text)
        self.current_token = 0
        
        while self.current_token < len(self.tokens):
            token = self.tokens[self.current_token]
            
            if token.type == TokenType.EOF:
                break
            
            # Handle different token types
            if token.type == TokenType.KEYWORD:
                self._handle_keyword(token)
            elif token.type == TokenType.DIRECTIVE:
                self._handle_directive(token)
            elif token.type == TokenType.IDENTIFIER:
                self._handle_identifier(token)
            
            self.current_token += 1
    
    def _handle_keyword(self, token: Token) -> None:
        """Handle keyword tokens"""
        keyword = token.value.lower()
        
        if keyword == 'module':
            self._parse_module()
        elif keyword == 'endmodule':
            self._parse_endmodule()
        elif keyword in ['input', 'output', 'inout']:
            self._parse_port_declaration(token)
        elif keyword in ['wire', 'reg']:
            self._parse_net_declaration(token)
        elif keyword == 'always':
            self._parse_always()
        elif keyword == 'assign':
            self._parse_assign()
        elif keyword == 'parameter':
            self._parse_parameter()
    
    def _handle_directive(self, token: Token) -> None:
        """Handle directive tokens"""
        directive = token.value[1:]  # Remove backtick
        if 'directive' in self.callbacks:
            self.callbacks['directive'](directive, token.line, token.column)
    
    def _handle_identifier(self, token: Token) -> None:
        """Handle identifier tokens"""
        if 'identifier' in self.callbacks:
            self.callbacks['identifier'](token.value, token.line, token.column)
    
    def _parse_module(self) -> None:
        """Parse module declaration"""
        if 'module_begin' not in self.callbacks:
            return
        
        # Skip to module name
        while (self.current_token < len(self.tokens) and 
               self.tokens[self.current_token].type != TokenType.IDENTIFIER):
            self.current_token += 1
        
        if self.current_token < len(self.tokens):
            module_name = self.tokens[self.current_token].value
            self.callbacks['module_begin'](module_name, self.tokens[self.current_token].line)
    
    def _parse_endmodule(self) -> None:
        """Parse endmodule"""
        if 'module_end' in self.callbacks:
            self.callbacks['module_end']()
    
    def _parse_port_declaration(self, token: Token) -> None:
        """Parse port declaration (input/output/inout)"""
        if 'port_declaration' not in self.callbacks:
            return
        
        direction = token.value.lower()
        
        # Skip to port name
        while (self.current_token < len(self.tokens) and 
               self.tokens[self.current_token].type != TokenType.IDENTIFIER):
            self.current_token += 1
        
        if self.current_token < len(self.tokens):
            port_name = self.tokens[self.current_token].value
            self.callbacks['port_declaration'](direction, port_name, token.line)
    
    def _parse_net_declaration(self, token: Token) -> None:
        """Parse net declaration (wire/reg)"""
        if 'net_declaration' not in self.callbacks:
            return
        
        net_type = token.value.lower()
        
        # Skip to net name
        while (self.current_token < len(self.tokens) and 
               self.tokens[self.current_token].type != TokenType.IDENTIFIER):
            self.current_token += 1
        
        if self.current_token < len(self.tokens):
            net_name = self.tokens[self.current_token].value
            self.callbacks['net_declaration'](net_type, net_name, token.line)
    
    def _parse_always(self) -> None:
        """Parse always block"""
        if 'always_begin' in self.callbacks:
            self.callbacks['always_begin'](self.tokens[self.current_token].line)
    
    def _parse_assign(self) -> None:
        """Parse assign statement"""
        if 'assign' in self.callbacks:
            self.callbacks['assign'](self.tokens[self.current_token].line)
    
    def _parse_parameter(self) -> None:
        """Parse parameter declaration"""
        if 'parameter' not in self.callbacks:
            return
        
        # Skip to parameter name
        while (self.current_token < len(self.tokens) and 
               self.tokens[self.current_token].type != TokenType.IDENTIFIER):
            self.current_token += 1
        
        if self.current_token < len(self.tokens):
            param_name = self.tokens[self.current_token].value
            self.callbacks['parameter'](param_name, self.tokens[self.current_token].line)
    
    def get_tokens(self) -> List[Token]:
        """Get the list of tokens"""
        return self.tokens.copy()
    
    def peek(self, offset: int = 0) -> Optional[Token]:
        """Peek at a token without consuming it"""
        index = self.current_token + offset
        if 0 <= index < len(self.tokens):
            return self.tokens[index]
        return None
    
    def consume(self, expected_type: Optional[TokenType] = None, 
                expected_value: Optional[str] = None) -> Optional[Token]:
        """Consume a token, optionally checking type and value"""
        if self.current_token >= len(self.tokens):
            return None
        
        token = self.tokens[self.current_token]
        
        if expected_type and token.type != expected_type:
            return None
        
        if expected_value and token.value != expected_value:
            return None
        
        self.current_token += 1
        return token


class SigParser(Parser):
    """Signal parser that builds upon Parser to provide signal-specific callbacks"""
    
    def __init__(self, callbacks: Optional[Dict[str, Callable]] = None):
        """Initialize signal parser"""
        super().__init__(callbacks)
        self.current_module = None
        self.current_ports = []
        self.current_nets = []
        self.current_parameters = []
    
    def _parse_module(self) -> None:
        """Parse module declaration with signal tracking"""
        super()._parse_module()
        
        # Reset module state
        self.current_module = None
        self.current_ports = []
        self.current_nets = []
        self.current_parameters = []
        
        # Get module name
        while (self.current_token < len(self.tokens) and 
               self.tokens[self.current_token].type != TokenType.IDENTIFIER):
            self.current_token += 1
        
        if self.current_token < len(self.tokens):
            self.current_module = self.tokens[self.current_token].value
    
    def _parse_port_declaration(self, token: Token) -> None:
        """Parse port declaration with signal tracking"""
        super()._parse_port_declaration(token)
        
        direction = token.value.lower()
        
        # Get port name
        while (self.current_token < len(self.tokens) and 
               self.tokens[self.current_token].type != TokenType.IDENTIFIER):
            self.current_token += 1
        
        if self.current_token < len(self.tokens):
            port_name = self.tokens[self.current_token].value
            port_info = {
                'name': port_name,
                'direction': direction,
                'line': token.line
            }
            self.current_ports.append(port_info)
            
            if 'signal_declaration' in self.callbacks:
                self.callbacks['signal_declaration']('port', port_name, direction, token.line)
    
    def _parse_net_declaration(self, token: Token) -> None:
        """Parse net declaration with signal tracking"""
        super()._parse_net_declaration(token)
        
        net_type = token.value.lower()
        
        # Get net name
        while (self.current_token < len(self.tokens) and 
               self.tokens[self.current_token].type != TokenType.IDENTIFIER):
            self.current_token += 1
        
        if self.current_token < len(self.tokens):
            net_name = self.tokens[self.current_token].value
            net_info = {
                'name': net_name,
                'type': net_type,
                'line': token.line
            }
            self.current_nets.append(net_info)
            
            if 'signal_declaration' in self.callbacks:
                self.callbacks['signal_declaration']('net', net_name, net_type, token.line)
    
    def _parse_parameter(self) -> None:
        """Parse parameter declaration with signal tracking"""
        super()._parse_parameter()
        
        # Get parameter name
        while (self.current_token < len(self.tokens) and 
               self.tokens[self.current_token].type != TokenType.IDENTIFIER):
            self.current_token += 1
        
        if self.current_token < len(self.tokens):
            param_name = self.tokens[self.current_token].value
            param_info = {
                'name': param_name,
                'line': self.tokens[self.current_token].line
            }
            self.current_parameters.append(param_info)
            
            if 'parameter_declaration' in self.callbacks:
                self.callbacks['parameter_declaration'](param_name, self.tokens[self.current_token].line)
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get information about the current module"""
        return {
            'name': self.current_module,
            'ports': self.current_ports,
            'nets': self.current_nets,
            'parameters': self.current_parameters
        } 