import sys
import unittest
from pathlib import Path
# Add the verilog_python directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from verilog_python import Parser,TokenType,Token,SigParser

class TestParser(unittest.TestCase):

    def setUp(self):
        self.parser = Parser()

    def test_tokenize(self):
        text = """
        module test(input a, output b);
            wire c;
            assign c = a | b;
        endmodule
        """
        tokens = self.parser.tokenize(text)
        print("***",tokens)
        print("***",tokens[0].type)
        print("***",TokenType.KEYWORD)
        self.assertGreater(len(tokens), 0)
        self.assertEqual(tokens[0].type, TokenType.KEYWORD)
        self.assertEqual(tokens[0].value, 'module')

    def test_parse(self):
        text = """
        module test(input a, output b);
            wire c;
            assign c = a | b;
        endmodule
        """
        self.parser.parse(text)

    def test_handle_keyword(self):
        token = Token(TokenType.KEYWORD, 'module', 1, 1)
        self.parser._handle_keyword(token)

    def test_handle_directive(self):
        token = Token(TokenType.DIRECTIVE, '`define', 1, 1)
        self.parser._handle_directive(token)

    def test_handle_identifier(self):
        token = Token(TokenType.IDENTIFIER, 'test', 1, 1)
        self.parser._handle_identifier(token)

    def test_parse_module(self):
        text = "module test(input a, output b);"
        self.parser.tokenize(text)
        self.parser._parse_module()

    def test_parse_endmodule(self):
        self.parser._parse_endmodule()

    def test_parse_port_declaration(self):
        token = Token(TokenType.KEYWORD, 'input', 1, 1)
        self.parser._parse_port_declaration(token)

    def test_parse_net_declaration(self):
        token = Token(TokenType.KEYWORD, 'wire', 1, 1)
        self.parser._parse_net_declaration(token)

    def test_parse_always(self):
        self.parser._parse_always()

    def test_parse_assign(self):
        self.parser._parse_assign()

    def test_parse_parameter(self):
        self.parser._parse_parameter()

    def test_get_tokens(self):
        text = "module test(input a, output b);"
        self.parser.tokenize(text)
        tokens = self.parser.get_tokens()
        self.assertGreater(len(tokens), 0)

    def test_peek(self):
        text = "module test(input a, output b);"
        self.parser.tokenize(text)
        token = self.parser.peek()
        self.assertEqual(token.type, TokenType.KEYWORD)
        self.assertEqual(token.value, 'module')

    def test_consume(self):
        text = "module test(input a, output b);"
        self.parser.tokenize(text)
        token = self.parser.consume(TokenType.KEYWORD, 'module')
        self.assertEqual(token.type, TokenType.KEYWORD)
        self.assertEqual(token.value, 'module')

class TestSigParser(unittest.TestCase):

    def setUp(self):
        self.sig_parser = SigParser()

    def test_parse_module(self):
        text = "module test(input a, output b);"
        self.sig_parser.tokenize(text)
        self.sig_parser._parse_module()
        self.assertEqual(self.sig_parser.current_module, 'test')

    def test_parse_port_declaration(self):
        text = "input a;"
        self.sig_parser.tokenize(text)
        token = Token(TokenType.KEYWORD, 'input', 1, 1)
        self.sig_parser._parse_port_declaration(token)
        self.assertEqual(len(self.sig_parser.current_ports), 1)
        self.assertEqual(self.sig_parser.current_ports[0]['name'], 'a')

    def test_parse_net_declaration(self):
        text = "wire c;"
        self.sig_parser.tokenize(text)
        token = Token(TokenType.KEYWORD, 'wire', 1, 1)
        self.sig_parser._parse_net_declaration(token)
        self.assertEqual(len(self.sig_parser.current_nets), 1)
        self.assertEqual(self.sig_parser.current_nets[0]['name'], 'c')

    def test_parse_parameter(self):
        text = "parameter SIZE = 10;"
        self.sig_parser.tokenize(text)
        self.sig_parser._parse_parameter()
        self.assertEqual(len(self.sig_parser.current_parameters), 1)
        self.assertEqual(self.sig_parser.current_parameters[0]['name'], 'SIZE')

    def test_get_module_info(self):
        text = """
        module test(input a, output b);
            wire c;
            parameter SIZE = 10;
        endmodule
        """
        self.sig_parser.tokenize(text)
        self.sig_parser.parse(text)
        module_info = self.sig_parser.get_module_info()
        self.assertEqual(module_info['name'], 'test')
        self.assertEqual(len(module_info['ports']), 2)
        self.assertEqual(len(module_info['nets']), 1)
        self.assertEqual(len(module_info['parameters']), 1)

if __name__ == '__main__':
    unittest.main()
