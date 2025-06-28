# Verilog-Python

A Python implementation of the verilog-perl library, providing parsing and utilities for the Verilog Language.

## Overview

Verilog-Python is a Python translation of the mature verilog-perl library, offering comprehensive Verilog language support including:

- **Language Utilities**: Keyword checking, number parsing, and language standard support
- **Preprocessing**: Full Verilog preprocessor with defines, includes, and conditional compilation
- **Parsing**: Tokenization and parsing of Verilog files with callback support
- **Netlist Management**: Design hierarchy and connectivity analysis
- **Command-line Tools**: Utilities for hierarchy display and preprocessing

## Features

### Core Components

- **Language**: Verilog language utilities and keyword checking
- **Parser**: Tokenization and parsing of Verilog files
- **Preproc**: Preprocessing of Verilog files
- **Netlist**: Design hierarchy and netlist management
- **Getopt**: Command line option handling

### Command-line Tools

- **vhier**: Display Verilog design hierarchy
- **vppreproc**: Preprocess Verilog files

### Language Support

- Verilog 1995, 2001, 2005 standards
- SystemVerilog 2005, 2009, 2012, 2017, 2023 standards
- VAMS support

## Installation

### From Source

```bash
git clone https://github.com/Sadihee/verilog-python.git
cd verilog-python
pip install -e .
```

### Development Installation

```bash
pip install -e ".[dev]"
```

## Quick Start

### Basic Usage

```python
from verilog_python import Language, Preproc, Parser, Netlist

# Check if a symbol is a Verilog keyword
is_keyword = Language.is_keyword("wire")  # True

# Parse a Verilog number
value = Language.number_value("4'b111")  # 8

# Preprocess a Verilog file
preproc = Preproc(defines={"DEBUG": "1"})
processed = preproc.preprocess_file("design.v")

# Parse Verilog content
parser = Parser()
parser.parse(processed)

# Create and analyze a netlist
netlist = Netlist()
netlist.read_file("design.v")
netlist.link()
netlist.dump()
```

### Command-line Tools

```bash
# Display hierarchy
vhier design.v

# Show modules
vhier --modules design.v

# Preprocess a file
vppreproc design.v

# Preprocess with defines
vppreproc -DDEBUG=1 -I include_path design.v
```

## API Reference

### Language Module

```python
from verilog_python import Language

# Keyword checking
Language.is_keyword("wire", "1364-2001")
Language.is_compdirect("`define")
Language.is_gateprim("and")

# Number parsing
Language.number_value("4'b111")     # 8
Language.number_bits("32'h1b")      # 32
Language.number_signed("1'sh1")     # True

# Bus expansion
Language.split_bus("[31:29]")       # ['[31]', '[30]', '[29]']

# Comment stripping
Language.strip_comments("a/*b*/c")  # "ac"
```

### Preproc Module

```python
from verilog_python import Preproc

# Create preprocessor with defines and include paths
preproc = Preproc(
    defines={"DEBUG": "1", "WIDTH": "32"},
    include_paths=["include", "src"]
)

# Preprocess a file
processed = preproc.preprocess_file("design.v")

# Preprocess from stream
with open("design.v", "r") as f:
    processed = preproc.preprocess_stream(f, "design.v")
```

### Parser Module

```python
from verilog_python import Parser, SigParser

# Basic parsing with callbacks
def on_module_begin(name, line):
    print(f"Module {name} at line {line}")

parser = Parser(callbacks={
    'module_begin': on_module_begin
})
parser.parse(verilog_content)

# Signal parsing
sig_parser = SigParser()
sig_parser.parse(verilog_content)
module_info = sig_parser.get_module_info()
```

### Netlist Module

```python
from verilog_python import Netlist

# Create and populate netlist
netlist = Netlist()
netlist.read_file("design.v")
netlist.link()

# Access modules
modules = netlist.get_modules()
top_modules = netlist.get_top_modules()

# Find specific module
module = netlist.find_module("top_module")

# Dump structure
netlist.dump()

# Generate Verilog
verilog_text = netlist.verilog_text()
```

## Examples

### Simple Module Analysis

```python
from verilog_python import Netlist

# Create netlist and read design
netlist = Netlist()
netlist.read_file("counter.v")
netlist.link()

# Analyze the design
for module in netlist.get_modules():
    print(f"Module: {module.name}")
    print(f"  Ports: {len(module.ports)}")
    print(f"  Nets: {len(module.nets)}")
    print(f"  Cells: {len(module.cells)}")
    
    # Show ports
    for port_name, port in module.ports.items():
        print(f"    {port.direction} {port_name}")
```

### Custom Parser Callbacks

```python
from verilog_python import Parser

class DesignAnalyzer:
    def __init__(self):
        self.modules = []
        self.signals = []
        
    def on_module_begin(self, name, line):
        self.modules.append({'name': name, 'line': line})
        
    def on_signal_declaration(self, signal_type, name, type_info, line):
        self.signals.append({
            'type': signal_type,
            'name': name,
            'type_info': type_info,
            'line': line
        })

# Use the analyzer
analyzer = DesignAnalyzer()
parser = Parser(callbacks={
    'module_begin': analyzer.on_module_begin,
    'signal_declaration': analyzer.on_signal_declaration
})

parser.parse(verilog_content)
print(f"Found {len(analyzer.modules)} modules")
print(f"Found {len(analyzer.signals)} signals")
```

### Preprocessing with Custom Defines

```python
from verilog_python import Preproc

# Set up preprocessor with project-specific defines
preproc = Preproc(
    defines={
        'PROJECT_NAME': '"MyProject"',
        'VERSION': '1.0',
        'DEBUG': '1',
        'SIMULATION': '1'
    },
    include_paths=[
        'include',
        'src/common',
        'src/modules'
    ]
)

# Process multiple files
files = ['top.v', 'counter.v', 'alu.v']
for filename in files:
    try:
        processed = preproc.preprocess_file(filename)
        with open(f"{filename}.pp", 'w') as f:
            f.write(processed)
        print(f"Preprocessed {filename}")
    except Exception as e:
        print(f"Error processing {filename}: {e}")
```

## Command-line Tools

### vhier - Hierarchy Display

```bash
# Basic hierarchy
vhier design.v

# Show cell hierarchy
vhier --cells design.v

# Show module names
vhier --modules design.v

# Show module file mapping
vhier --module-files design.v

# XML output
vhier --xml design.v

# Specify top module
vhier --top-module top_module design.v
```

### vppreproc - Preprocessor

```bash
# Basic preprocessing
vppreproc design.v

# With defines
vppreproc -DDEBUG=1 -DWIDTH=32 design.v

# With include paths
vppreproc -I include_path design.v

# Show defines only
vppreproc --defines-only design.v

# Output to file
vppreproc -o design.pp design.v
```

## Language Standards

The library supports multiple Verilog and SystemVerilog standards:

- **1364-1995**: Original Verilog standard
- **1364-2001**: Verilog 2001 standard
- **1364-2005**: Verilog 2005 standard
- **1800-2005**: SystemVerilog 2005
- **1800-2009**: SystemVerilog 2009
- **1800-2012**: SystemVerilog 2012
- **1800-2017**: SystemVerilog 2017
- **1800-2023**: SystemVerilog 2023
- **VAMS**: Verilog-AMS

Set the language standard:

```python
Language.language_standard('1800-2017')
```

## Comparison with verilog-perl

This Python implementation provides the same core functionality as verilog-perl:

| Feature | verilog-perl | verilog-python |
|---------|-------------|----------------|
| Language utilities | ✅ | ✅ |
| Preprocessing | ✅ | ✅ |
| Parsing | ✅ | ✅ |
| Netlist management | ✅ | ✅ |
| Command-line tools | ✅ | ✅ |
| Language standards | ✅ | ✅ |

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black verilog_python/
```

### Type Checking

```bash
mypy verilog_python/
```

### Linting

```bash
flake8 verilog_python/
```

## See Also

- [verilog-perl](https://www.veripool.org/verilog-perl) - Original Perl implementation
