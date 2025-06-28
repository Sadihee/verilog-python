#!/usr/bin/env python3
"""
vhier - Verilog hierarchy display tool

This tool reads Verilog files and outputs a tree of all filenames,
modules, and cells referenced by those files.
"""

import sys
import argparse
from pathlib import Path

# Add the parent directory to the path so we can import verilog_python
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from verilog_python import Netlist, Getopt, Language


def main():
    """Main function for vhier tool"""
    parser = argparse.ArgumentParser(
        description="Display Verilog design hierarchy",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  vhier design.v
  vhier --cells design.v
  vhier --modules design.v
  vhier --forest design.v
        """
    )
    
    parser.add_argument('files', nargs='+', help='Verilog files to analyze')
    parser.add_argument('--cells', action='store_true', help='Show cell hierarchy')
    parser.add_argument('--modules', action='store_true', help='Show module names')
    parser.add_argument('--module-files', action='store_true', help='Show module file mapping')
    parser.add_argument('--includes', action='store_true', help='Show include files')
    parser.add_argument('--input-files', action='store_true', help='Show input files')
    parser.add_argument('--resolve-files', action='store_true', help='Show resolved filenames')
    parser.add_argument('--missing', action='store_true', default=True, help='Show missing modules')
    parser.add_argument('--missing-modules', action='store_true', help='Show missing module details')
    parser.add_argument('--top-module', help='Specify top module')
    parser.add_argument('--synthesis', action='store_true', help='Synthesis mode')
    parser.add_argument('--forest', action='store_true', help='Show hierarchy forest')
    parser.add_argument('--instance', action='store_true', help='Show instance names')
    parser.add_argument('--xml', action='store_true', help='Output in XML format')
    parser.add_argument('--language', help='Language standard (1364-1995, 1364-2001, etc.)')
    parser.add_argument('--sv', action='store_true', help='SystemVerilog mode')
    parser.add_argument('-o', '--output', help='Output file (default: stdout)')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    parser.add_argument('--version', action='version', version='vhier 1.0.0')
    
    args = parser.parse_args()
    
    # Set language standard
    if args.sv:
        Language.language_standard('1800-2023')
    elif args.language:
        Language.language_standard(args.language)
    
    # Create netlist
    netlist = Netlist()
    
    # Read files
    for filename in args.files:
        if args.debug:
            print(f"Reading {filename}", file=sys.stderr)
        try:
            netlist.read_file(filename)
        except Exception as e:
            print(f"Error reading {filename}: {e}", file=sys.stderr)
    
    # Link the design
    netlist.link()
    
    # Output handling
    output_file = sys.stdout
    if args.output:
        try:
            output_file = open(args.output, 'w')
        except Exception as e:
            print(f"Error opening output file: {e}", file=sys.stderr)
            sys.exit(1)
    
    try:
        if args.xml:
            output_file.write("<vhier>\n")
        
        # Show cells hierarchy
        if args.cells or args.forest:
            if args.xml:
                output_file.write(" <cells>\n")
            else:
                output_file.write("Cell Hierarchy:\n")
                output_file.write("===============\n")
            
            for module in netlist.get_top_modules():
                show_hierarchy(output_file, module, "", args.instance, args.xml)
            
            if args.xml:
                output_file.write(" </cells>\n")
        
        # Show module names
        if args.modules:
            if args.xml:
                output_file.write(" <modules>\n")
            else:
                output_file.write("\nModule Names:\n")
                output_file.write("=============\n")
            
            for module in netlist.get_modules():
                if args.xml:
                    output_file.write(f"  <module>{module.name}</module>\n")
                else:
                    output_file.write(f"  {module.name}\n")
            
            if args.xml:
                output_file.write(" </modules>\n")
        
        # Show module file mapping
        if args.module_files:
            if args.xml:
                output_file.write(" <module_files>\n")
            else:
                output_file.write("\nModule File Mapping:\n")
                output_file.write("===================\n")
            
            for module in netlist.get_modules():
                filename = module.filename or "unknown"
                if args.xml:
                    output_file.write(f"  <module_file module=\"{module.name}\" file=\"{filename}\"/>\n")
                else:
                    output_file.write(f"  {module.name}: {filename}\n")
            
            if args.xml:
                output_file.write(" </module_files>\n")
        
        # Show input files
        if args.input_files:
            if args.xml:
                output_file.write(" <input_files>\n")
            else:
                output_file.write("\nInput Files:\n")
                output_file.write("============\n")
            
            for filename in args.files:
                if args.xml:
                    output_file.write(f"  <file>{filename}</file>\n")
                else:
                    output_file.write(f"  {filename}\n")
            
            if args.xml:
                output_file.write(" </input_files>\n")
        
        if args.xml:
            output_file.write("</vhier>\n")
    
    finally:
        if args.output and output_file != sys.stdout:
            output_file.close()


def show_hierarchy(output_file, module, indent="", show_instance=False, xml=False):
    """Show hierarchy for a module"""
    if xml:
        output_file.write(f"{indent}<module name=\"{module.name}\">\n")
    else:
        instance_info = f" ({module.name})" if show_instance else ""
        output_file.write(f"{indent}{module.name}{instance_info}\n")
    
    # Show cells
    for cell_name, cell in module.cells.items():
        if xml:
            output_file.write(f"{indent}  <cell name=\"{cell_name}\" module=\"{cell.module_name}\">\n")
            if cell.module:
                show_hierarchy(output_file, cell.module, indent + "    ", show_instance, xml)
            output_file.write(f"{indent}  </cell>\n")
        else:
            cell_info = f" ({cell.module_name})" if show_instance else ""
            output_file.write(f"{indent}  {cell_name}{cell_info}\n")
            if cell.module:
                show_hierarchy(output_file, cell.module, indent + "    ", show_instance, xml)
    
    if xml:
        output_file.write(f"{indent}</module>\n")


if __name__ == '__main__':
    main() 