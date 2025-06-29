import unittest

import sys
from pathlib import Path

# Add the verilog_python directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from verilog_python import Language, Preproc, Parser, SigParser, Netlist


class TestLanguage(unittest.TestCase):

    def setUp(self):
        self.lang = Language()

    def test_is_keyword(self):
        self.assertTrue(Language.is_keyword('module'))
        self.assertTrue(Language.is_keyword('always', '1364-1995'))
        self.assertFalse(Language.is_keyword('nonexistentkeyword'))
        self.assertFalse(Language.is_keyword('always', 'nonexistentstandard'))

    def test_is_compdirect(self):
        self.assertTrue(Language.is_compdirect('`define'))
        self.assertTrue(Language.is_compdirect('`include'))
        self.assertFalse(Language.is_compdirect('`nonexistentdirective'))

    def test_is_gateprim(self):
        self.assertTrue(Language.is_gateprim('and'))
        self.assertTrue(Language.is_gateprim('nand'))
        self.assertFalse(Language.is_gateprim('nonexistentgate'))

    def test_language_standard(self):
        with self.assertRaises(ValueError):
            Language.language_standard('nonexistentstandard')

    def test_language_maximum(self):
        self.assertEqual(Language.language_maximum(), '1800-2023')

    def test_number_value(self):
        self.assertEqual(Language.number_value("32'h1b"), 27)
        self.assertEqual(Language.number_value("4'b1111"), 15)
        self.assertEqual(Language.number_value("1'sh1"), 1)
        self.assertEqual(Language.number_value("32'sh1b"), 27)
        self.assertEqual(Language.number_value("123"), 123)
        self.assertIsNone(Language.number_value("invalid"))

    def test_number_bits(self):
        self.assertEqual(Language.number_bits("32'h1b"), 27)
        self.assertEqual(Language.number_bits("4'b1111"), 15)
        self.assertEqual(Language.number_bits("1'sh1"), -1)
        self.assertEqual(Language.number_bits("32'sh1b"), 27)
        self.assertIsNone(Language.number_bits("invalid"))

    def test_number_signed(self):
        self.assertTrue(Language.number_signed("32'sh1b"))
        self.assertFalse(Language.number_signed("32'h1b"))
        self.assertIsNone(Language.number_signed("invalid"))

    def test_split_bus(self):
        self.assertEqual(Language.split_bus("bus[3:0]"), ["bus[3]", "bus[2]", "bus[1]", "bus[0]"])
        self.assertEqual(Language.split_bus("single"), ["single"])

    def test_split_bus_nocomma(self):
        self.assertEqual(Language.split_bus_nocomma("bus[3:0]"), ["bus[3]", "bus[2]", "bus[1]", "bus[0]"])
        self.assertEqual(Language.split_bus_nocomma("single"), ["single"])

    def test_strip_comments(self):
        self.assertEqual(Language.strip_comments("This is a test // with a comment"), "This is a test ")
        self.assertEqual(Language.strip_comments("This is a test /* with a comment */"), "This is a test ")
        self.assertEqual(Language.strip_comments("This is a test"), "This is a test")

if __name__ == '__main__':
    unittest.main()
