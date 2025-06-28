#!/usr/bin/env python3
"""
Test example demonstrating verilog-python functionality

This script shows how to use the main components of the verilog-python library.
"""

import sys
from pathlib import Path

# Add the verilog_python directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from verilog_python import Language, Preproc, Parser, Netlist


def test_language_utilities():
    """Test language utilities"""
    print("=== Language Utilities Test ===")
    
    # Test keyword checking
    print(f"Is 'wire' a keyword? {Language.is_keyword('wire')}")
    print(f"Is 'my_signal' a keyword? {Language.is_keyword('my_signal')}")
    print(f"Is '`define' a compiler directive? {Language.is_compdirect('`define')}")
    print(f"Is 'and' a gate primitive? {Language.is_gateprim('and')}")
    
    # Test number parsing
    print(f"Value of '4'b111': {Language.number_value('4\'b111')}")
    print(f"Bits in '32'h1b': {Language.number_bits('32\'h1b')}")
    print(f"Is '1'sh1' signed? {Language.number_signed('1\'sh1')}")
    
    # Test bus expansion
    print(f"Bus expansion '[31:29]': {Language.split_bus('[31:29]')}")
    
    # Test comment stripping
    print(f"Strip comments: {Language.strip_comments('a/*b*/c')}")
    print()


def test_preprocessor():
    """Test preprocessor functionality"""
    print("=== Preprocessor Test ===")
    
    # Create a simple Verilog file for testing
    test_verilog = '''
    `define DEBUG 1
    `define WIDTH 32

    module test_module (
        input clk,
        input rst,
        output reg [WIDTH-1:0] count
    );

    `ifdef DEBUG
        initial $display("Debug mode enabled");
    `endif

    always @(posedge clk or posedge rst) begin
        if (rst) begin
            count <= 0;
        end else begin
            count <= count + 1;
        end
    end

    endmodule
    '''
    
    # Write test file
    with open('test_module.v', 'w') as f:
        f.write(test_verilog)
    
    # Test preprocessing
    preproc = Preproc(defines={'DEBUG': '1', 'WIDTH': '32'})
    
    try:
        processed = preproc.preprocess_file('test_module.v')
        print("Preprocessed content:")
        print(processed)
        print()
    except Exception as e:
        print(f"Preprocessing error: {e}")
        print()


def test_parser():
    """Test parser functionality"""
    print("=== Parser Test ===")
    
    # Simple Verilog content
    verilog_content = '''
    module simple_counter (
        input clk,
        input rst,
        output reg [7:0] count
    );

    wire enable;
    reg [7:0] next_count;

    assign enable = 1'b1;

    always @(posedge clk or posedge rst) begin
        if (rst) begin
            count <= 8'h00;
        end else if (enable) begin
            count <= next_count;
        end
    end

    always @(*) begin
        next_count = count + 1;
    end

    endmodule
    '''
    
    # Test basic parsing
    parser = Parser()
    parser.parse(verilog_content)
    
    print(f"Parsed {len(parser.get_tokens())} tokens")
    
    # Test signal parsing
    sig_parser = SigParser()
    sig_parser.parse(verilog_content)
    module_info = sig_parser.get_module_info()
    
    print(f"Module: {module_info['name']}")
    print(f"Ports: {len(module_info['ports'])}")
    print(f"Nets: {len(module_info['nets'])}")
    print(f"Parameters: {len(module_info['parameters'])}")
    
    for port in module_info['ports']:
        print(f"  Port: {port['direction']} {port['name']} {port['width']}")
    
    for net in module_info['nets']:
        print(f"  Net: {net['type']} {net['name']} {net['width']}")
    print()


def test_netlist():
    """Test netlist functionality"""
    print("=== Netlist Test ===")
    
    # Create a simple design with multiple modules
    design_files = {
        'counter.v': '''
    module counter (
        input clk,
        input rst,
        output reg [7:0] count
    );

    always @(posedge clk or posedge rst) begin
        if (rst) begin
            count <= 8'h00;
        end else begin
            count <= count + 1;
        end
    end

    endmodule
    ''',
            'top.v': '''
    module top (
        input clk,
        input rst,
        output [7:0] count
    );

    counter u_counter (
        .clk(clk),
        .rst(rst),
        .count(count)
    );

    endmodule
    '''
    }
    
    # Write test files
    for filename, content in design_files.items():
        with open(filename, 'w') as f:
            f.write(content)
    
    # Create and populate netlist
    netlist = Netlist()
    
    for filename in design_files.keys():
        try:
            netlist.read_file(filename)
            print(f"Read {filename}")
        except Exception as e:
            print(f"Error reading {filename}: {e}")
    
    # Link the design
    netlist.link()
    
    # Analyze the design
    print(f"Found {len(netlist.get_modules())} modules:")
    for module in netlist.get_modules():
        print(f"  {module.name}: {len(module.ports)} ports, {len(module.nets)} nets, {len(module.cells)} cells")
    
    print(f"Top modules: {[m.name for m in netlist.get_top_modules()]}")
    print()


def cleanup_test_files():
    """Clean up test files"""
    test_files = ['test_module.v', 'counter.v', 'top.v']
    for filename in test_files:
        try:
            Path(filename).unlink()
        except FileNotFoundError:
            pass


def main():
    """Main test function"""
    print("Verilog-Python Test Example")
    print("=" * 40)
    print()
    
    try:
        test_language_utilities()
        test_preprocessor()
        test_parser()
        test_netlist()
        
        print("All tests completed successfully!")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        cleanup_test_files()


if __name__ == '__main__':
    main() 