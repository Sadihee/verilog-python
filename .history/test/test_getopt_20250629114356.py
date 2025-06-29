import unittest
import os
import tempfile
from pathlib import Path
from your_module import Getopt  # Replace 'your_module' with the actual module name

class TestGetopt(unittest.TestCase):

    def setUp(self):
        self.getopt = Getopt(filename_expansion=False)

    def test_parameter(self):
        args = ['-D', 'TEST=1', '-I', 'include_path', 'file1.v', 'file2.v']
        remaining_args = self.getopt.parameter(args)
        self.assertEqual(remaining_args, [])
        self.assertEqual(self.getopt.defines, {'TEST': '1'})
        self.assertEqual(self.getopt.include_paths, ['include_path'])
        self.assertEqual(self.getopt.files, ['file1.v', 'file2.v'])

        args = ['+define+TEST=1', '+incdir+include_path', 'file1.v', 'file2.v']
        remaining_args = self.getopt.parameter(args)
        self.assertEqual(remaining_args, [])
        self.assertEqual(self.getopt.defines, {'TEST': '1'})
        self.assertEqual(self.getopt.include_paths, ['include_path'])
        self.assertEqual(self.getopt.files, ['file1.v', 'file2.v'])

        args = ['-f', 'file_list.txt', 'file1.v']
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write('file2.v\nfile3.v')
            f.flush()
            remaining_args = self.getopt.parameter(args)
            self.assertEqual(remaining_args, [])
            self.assertEqual(self.getopt.files, ['file1.v', 'file2.v', 'file3.v'])
            os.unlink(f.name)

    def test_handle_define(self):
        self.getopt._handle_define('-D', 'TEST=1')
        self.assertEqual(self.getopt.defines, {'TEST': '1'})

        self.getopt._handle_define('+define+TEST=1')
        self.assertEqual(self.getopt.defines, {'TEST': '1'})

        self.getopt._handle_define('+define+TEST')
        self.assertEqual(self.getopt.defines, {'TEST': '1'})

    def test_handle_include(self):
        self.getopt._handle_include('-I', 'include_path')
        self.assertEqual(self.getopt.include_paths, ['include_path'])

        self.getopt._handle_include('+incdir+include_path')
        self.assertEqual(self.getopt.include_paths, ['include_path'])

    def test_handle_file_list(self):
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write('file1.v\nfile2.v')
            f.flush()
            self.getopt._handle_file_list('-f', f.name)
            self.assertEqual(self.getopt.files, ['file1.v', 'file2.v'])
            os.unlink(f.name)

    def test_handle_library(self):
        self.getopt._handle_library('-y', 'library_path')
        self.assertEqual(self.getopt.options, {'libraries': ['library_path']})

    def test_handle_libext(self):
        self.getopt._handle_libext('+libext+.v+.sv')
        self.assertEqual(self.getopt.options, {'libext': ['.v', '.sv']})

    def test_handle_liborder(self):
        self.getopt._handle_liborder('+liborder+order')
        self.assertEqual(self.getopt.options, {'liborder': 'order'})

    def test_expand_filename(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            Path(temp_dir, 'file1.v').touch()
            Path(temp_dir, 'file2.v').touch()
            self.getopt.filename_expansion = True
            expanded_files = self.getopt._expand_filename(f'{temp_dir}/file*.v')
            self.assertEqual(len(expanded_files), 2)

    def test_defvalue(self):
        self.getopt.defines = {'TEST': '1'}
        self.assertEqual(self.getopt.defvalue('TEST'), '1')
        self.assertIsNone(self.getopt.defvalue('UNKNOWN'))

    def test_defvalue_nowarn(self):
        self.getopt.defines = {'TEST': '1'}
        self.assertEqual(self.getopt.defvalue_nowarn('TEST'), '1')
        self.assertIsNone(self.getopt.defvalue_nowarn('UNKNOWN'))

    def test_get_files(self):
        self.getopt.files = ['file1.v', 'file2.v']
        self.assertEqual(self.getopt.get_files(), ['file1.v', 'file2.v'])

    def test_get_defines(self):
        self.getopt.defines = {'TEST': '1'}
        self.assertEqual(self.getopt.get_defines(), {'TEST': '1'})

    def test_get_include_paths(self):
        self.getopt.include_paths = ['include_path']
        self.assertEqual(self.getopt.get_include_paths(), ['include_path'])

    def test_get_options(self):
        self.getopt.options = {'libraries': ['library_path']}
        self.assertEqual(self.getopt.get_options(), {'libraries': ['library_path']})

if __name__ == '__main__':
    unittest.main()
