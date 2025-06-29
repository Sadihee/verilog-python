import unittest
import os
import tempfile
from your_module import Preproc  # Replace 'your_module' with the actual module name

class TestPreproc(unittest.TestCase):

    def setUp(self):
        self.preproc = Preproc()

    def test_preprocess_file(self):
        # Create a temporary file with some Verilog content
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("module test(input a, output b);\nendmodule")
            temp_file_path = f.name

        try:
            # Preprocess the file
            result = self.preproc.preprocess_file(temp_file_path)
            self.assertIn("module test(input a, output b);", result)
            self.assertIn("endmodule", result)
        finally:
            # Clean up the temporary file
            os.unlink(temp_file_path)

    def test_preprocess_stream(self):
        # Create a temporary file with some Verilog content
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as f:
            f.write("module test(input a, output b);\nendmodule")
            f.seek(0)  # Move the file pointer back to the beginning
            temp_file_path = f.name

        try:
            # Preprocess the stream
            result = self.preproc.preprocess_stream(f, temp_file_path)
            self.assertIn("module test(input a, output b);", result)
            self.assertIn("endmodule", result)
        finally:
            # Clean up the temporary file
            os.unlink(temp_file_path)

    def test_handle_define(self):
        line = "`define TEST 1"
        result = self.preproc._handle_define(line, 1, "test_file")
        self.assertIsNone(result)
        self.assertEqual(self.preproc.defines["TEST"], "1")

    def test_handle_undef(self):
        self.preproc.defines["TEST"] = "1"
        line = "`undef TEST"
        result = self.preproc._handle_undef(line, 1, "test_file")
        self.assertIsNone(result)
        self.assertNotIn("TEST", self.preproc.defines)

    def test_handle_include(self):
        # Create a temporary include file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("module included(input a, output b);\nendmodule")
            temp_file_path = f.name

        try:
            # Add the directory of the temporary file to include paths
            self.preproc.include_paths.append(os.path.dirname(temp_file_path))

            # Create a line with an include directive
            line = f"`include \"{os.path.basename(temp_file_path)}\""
            result = self.preproc._handle_include(line, 1, "test_file")
            self.assertIn("module included(input a, output b);", result)
            self.assertIn("endmodule", result)
        finally:
            # Clean up the temporary file
            os.unlink(temp_file_path)

    def test_handle_ifdef(self):
        self.preproc.defines["TEST"] = "1"
        line = "`ifdef TEST"
        result = self.preproc._handle_ifdef(line, 1, "test_file")
        self.assertIsNone(result)
        self.assertTrue(self.preproc.conditional_stack[-1]['active'])

    def test_handle_ifndef(self):
        line = "`ifndef TEST"
        result = self.preproc._handle_ifndef(line, 1, "test_file")
        self.assertIsNone(result)
        self.assertTrue(self.preproc.conditional_stack[-1]['active'])

    def test_handle_else(self):
        self.preproc.conditional_stack.append({'type': 'ifdef', 'active': False, 'had_else': False})
        line = "`else"
        result = self.preproc._handle_else(line, 1, "test_file")
        self.assertIsNone(result)
        self.assertTrue(self.preproc.conditional_stack[-1]['active'])

    def test_handle_elsif(self):
        self.preproc.conditional_stack.append({'type': 'ifdef', 'active': False, 'had_else': False})
        self.preproc.defines["TEST"] = "1"
        line = "`elsif TEST"
        result = self.preproc._handle_elsif(line, 1, "test_file")
        self.assertIsNone(result)
        self.assertTrue(self.preproc.conditional_stack[-1]['active'])

    def test_handle_endif(self):
        self.preproc.conditional_stack.append({'type': 'ifdef', 'active': True, 'had_else': False})
        line = "`endif"
        result = self.preproc._handle_endif(line, 1, "test_file")
        self.assertIsNone(result)
        self.assertEqual(len(self.preproc.conditional_stack), 0)

    def test_handle_timescale(self):
        line = "`timescale 1ns/1ps"
        result = self.preproc._handle_timescale(line, 1, "test_file")
        self.assertEqual(result, line)

    def test_handle_line(self):
        line = "`line 1 \"test_file\""
        result = self.preproc._handle_line(line, 1, "test_file")
        self.assertEqual(result, line)

    def test_handle_pragma(self):
        line = "`pragma some_pragma"
        result = self.preproc._handle_pragma(line, 1, "test_file")
        self.assertEqual(result, line)

    def test_handle_begin_keywords(self):
        line = "`begin_keywords \"keyword1\" \"keyword2\""
        result = self.preproc._handle_begin_keywords(line, 1, "test_file")
        self.assertEqual(result, line)

    def test_handle_end_keywords(self):
        line = "`end_keywords"
        result = self.preproc._handle_end_keywords(line, 1, "test_file")
        self.assertEqual(result, line)

    def test_resolve_include(self):
        # Create a temporary include file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("module included(input a, output b);\nendmodule")
            temp_file_path = f.name

        try:
            # Resolve the include file
            resolved_path = self.preproc._resolve_include(os.path.basename(temp_file_path), "test_file")
            self.assertEqual(resolved_path, temp_file_path)
        finally:
            # Clean up the temporary file
            os.unlink(temp_file_path)

    def test_expand_defines(self):
        self.preproc.defines["TEST"] = "value"
        line = "This is a TEST line"
        result = self.preproc._expand_defines(line)
        self.assertEqual(result, "This is a value line")

    def test_get_defines(self):
        self.preproc.defines["TEST"] = "1"
        defines = self.preproc.get_defines()
        self.assertEqual(defines, {"TEST": "1"})

    def test_add_define(self):
        self.preproc.add_define("TEST", "1")
        self.assertEqual(self.preproc.defines["TEST"], "1")

    def test_remove_define(self):
        self.preproc.defines["TEST"] = "1"
        self.preproc.remove_define("TEST")
        self.assertNotIn("TEST", self.preproc.defines)

if __name__ == '__main__':
    unittest.main()
