#!/usr/bin/env python3
"""
vppreproc - Verilog preprocessor

This tool reads Verilog files and outputs preprocessed output,
handling includes, defines, and other preprocessor directives.
"""

import sys
import argparse
from pathlib import Path

# Add the parent directory to the path so we can import verilog_python
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from verilog_python import Preproc, Getopt


def main():
    """Main function for vppreproc tool"""
    parser = argparse.ArgumentParser(
        description="Preprocess Verilog files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  vppreproc design.v
  vppreproc -DDEBUG=1 design.v
  vppreproc -I include_path design.v
  vppreproc --defines-only design.v
        """
    )
    
    parser.add_argument('files', nargs='*', help='Verilog files to preprocess')
    parser.add_argument('-D', '--define', action='append', help='Define macro')
    parser.add_argument('-I', '--include', action='append', help='Include path')
    parser.add_argument('--defines-only', action='store_true', help='Show only defines')
    parser.add_argument('--includes-only', action='store_true', help='Show only includes')
    parser.add_argument('--no-expand', action='store_true', help='Don\'t expand defines')
    parser.add_argument('-o', '--output', help='Output file (default: stdout)')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    parser.add_argument('--version', action='version', version='vppreproc 1.0.0')
    
    args = parser.parse_args()
    
    # Handle file list from -f option (simplified)
    if not args.files:
        parser.error("No input files specified")
    
    # Create preprocessor
    defines = {}
    include_paths = []
    
    # Process defines
    if args.define:
        for define in args.define:
            if '=' in define:
                name, value = define.split('=', 1)
                defines[name] = value
            else:
                defines[define] = '1'
    
    # Process include paths
    if args.include:
        include_paths.extend(args.include)
    
    preproc = Preproc(defines=defines, include_paths=include_paths)
    
    # Output handling
    output_file = sys.stdout
    if args.output:
        try:
            output_file = open(args.output, 'w')
        except Exception as e:
            print(f"Error opening output file: {e}", file=sys.stderr)
            sys.exit(1)
    
    try:
        # Show defines only
        if args.defines_only:
            output_file.write("Defines:\n")
            output_file.write("========\n")
            for name, value in preproc.get_defines().items():
                output_file.write(f"`define {name} {value}\n")
            return
        
        # Show includes only
        if args.includes_only:
            output_file.write("Include Paths:\n")
            output_file.write("==============\n")
            for path in include_paths:
                output_file.write(f"  {path}\n")
            return
        
        # Process files
        for filename in args.files:
            if args.debug:
                print(f"Processing {filename}", file=sys.stderr)
            
            try:
                # Read and preprocess the file
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if args.no_expand:
                    # Just handle directives, don't expand defines
                    processed_content = preproc.preprocess_stream(f, filename)
                else:
                    # Full preprocessing
                    processed_content = preproc.preprocess_stream(f, filename)
                
                # Output the processed content
                output_file.write(processed_content)
                
            except FileNotFoundError:
                print(f"Error: File not found: {filename}", file=sys.stderr)
                sys.exit(1)
            except Exception as e:
                print(f"Error processing {filename}: {e}", file=sys.stderr)
                sys.exit(1)
    
    finally:
        if args.output and output_file != sys.stdout:
            output_file.close()


if __name__ == '__main__':
    main() 