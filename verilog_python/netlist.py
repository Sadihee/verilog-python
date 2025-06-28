"""
Verilog::Netlist - Design hierarchy and netlist management

This module reads and holds interconnect information about a whole
design database, providing hierarchy and signal connectivity information.
"""

from typing import Dict, List, Optional, Any, Set
from .language import Language
from .preproc import Preproc
from .parser import SigParser


class Net:
    """Represents a net (signal) in the design"""
    
    def __init__(self, name: str, net_type: str = 'wire', width: int = 1):
        self.name = name
        self.net_type = net_type
        self.width = width
        self.connections = []  # List of connected pins
        self.driver = None  # Driving pin
        self.loads = []  # Load pins
    
    def add_connection(self, pin):
        """Add a connection to this net"""
        self.connections.append(pin)
    
    def set_driver(self, pin):
        """Set the driving pin for this net"""
        self.driver = pin
    
    def add_load(self, pin):
        """Add a load pin to this net"""
        self.loads.append(pin)
    
    def __repr__(self):
        return f"Net({self.name}, {self.net_type}, width={self.width})"


class Port:
    """Represents a port in a module"""
    
    def __init__(self, name: str, direction: str, width: int = 1):
        self.name = name
        self.direction = direction  # 'input', 'output', 'inout'
        self.width = width
        self.net = None  # Connected net
    
    def connect_net(self, net: Net):
        """Connect this port to a net"""
        self.net = net
    
    def __repr__(self):
        return f"Port({self.name}, {self.direction}, width={self.width})"


class Pin:
    """Represents a pin connection on a cell"""
    
    def __init__(self, name: str, net: Optional[Net] = None):
        self.name = name
        self.net = net
        self.cell = None  # Parent cell
    
    def connect_net(self, net: Net):
        """Connect this pin to a net"""
        self.net = net
    
    def __repr__(self):
        return f"Pin({self.name}, net={self.net.name if self.net else None})"


class Cell:
    """Represents a cell (module instantiation) in the design"""
    
    def __init__(self, name: str, module_name: str):
        self.name = name
        self.module_name = module_name
        self.pins = {}  # Dictionary of pin name -> Pin object
        self.module = None  # Reference to the actual module
        self.parent_module = None  # Parent module containing this cell
    
    def add_pin(self, pin_name: str, net: Optional[Net] = None) -> Pin:
        """Add a pin to this cell"""
        pin = Pin(pin_name, net)
        pin.cell = self
        self.pins[pin_name] = pin
        return pin
    
    def get_pin(self, pin_name: str) -> Optional[Pin]:
        """Get a pin by name"""
        return self.pins.get(pin_name)
    
    def __repr__(self):
        return f"Cell({self.name}, module={self.module_name})"


class Module:
    """Represents a module in the design"""
    
    def __init__(self, name: str, keyword: str = 'module'):
        self.name = name
        self.keyword = keyword
        self.ports = {}  # Dictionary of port name -> Port object
        self.nets = {}  # Dictionary of net name -> Net object
        self.cells = {}  # Dictionary of cell name -> Cell object
        self.parameters = {}  # Dictionary of parameter name -> value
        self.parent_netlist = None  # Reference to parent netlist
        self.is_top = False
        self.filename = None
        self.line = 0
    
    def add_port(self, name: str, direction: str, width: int = 1) -> Port:
        """Add a port to this module"""
        port = Port(name, direction, width)
        self.ports[name] = port
        return port
    
    def add_net(self, name: str, net_type: str = 'wire', width: int = 1) -> Net:
        """Add a net to this module"""
        net = Net(name, net_type, width)
        self.nets[name] = net
        return net
    
    def add_cell(self, name: str, module_name: str) -> Cell:
        """Add a cell to this module"""
        cell = Cell(name, module_name)
        cell.parent_module = self
        self.cells[name] = cell
        return cell
    
    def add_parameter(self, name: str, value: str):
        """Add a parameter to this module"""
        self.parameters[name] = value
    
    def get_port(self, name: str) -> Optional[Port]:
        """Get a port by name"""
        return self.ports.get(name)
    
    def get_net(self, name: str) -> Optional[Net]:
        """Get a net by name"""
        return self.nets.get(name)
    
    def get_cell(self, name: str) -> Optional[Cell]:
        """Get a cell by name"""
        return self.cells.get(name)
    
    def __repr__(self):
        return f"Module({self.name}, ports={len(self.ports)}, nets={len(self.nets)}, cells={len(self.cells)})"

    def link(self):
        """Link a module's cells to their actual modules"""
        for cell_name, cell in self.cells.items():
            if cell.module_name in self.parent_netlist.modules:
                cell.module = self.parent_netlist.modules[cell.module_name]
            else:
                print(f"Warning: Module {cell.module_name} not found for cell {cell_name}")


class Netlist:
    """Main netlist class that manages the entire design hierarchy"""
    
    def __init__(self, options: Optional[Any] = None):
        """Initialize netlist with options"""
        self.modules = {}  # Dictionary of module name -> Module object
        self.files = {}  # Dictionary of filename -> file info
        self.options = options
        self.preproc = Preproc()
        self.parser = SigParser()
        self.language = Language()
        
        # Configuration options
        self.implicit_wires_ok = True
        self.link_read = True
        self.use_vars = True
        self.keep_comments = False
        self.synthesis = False
        
        # Internal state
        self._need_link = []
        self._relink = False
    
    def read_file(self, filename: str) -> None:
        """Read a Verilog file and add its modules to the netlist"""
        try:
            # Preprocess the file
            preprocessed_content = self.preproc.preprocess_file(filename)
            
            # Parse the preprocessed content
            self._parse_file_content(preprocessed_content, filename)
            
            # Track the file
            self.files[filename] = {
                'modules': [],
                'content': preprocessed_content
            }
            
        except FileNotFoundError:
            print(f"Warning: File not found: {filename}")
        except Exception as e:
            print(f"Error reading file {filename}: {e}")
    
    def _parse_file_content(self, content: str, filename: str) -> None:
        """Parse the content of a file and extract modules"""
        # Set up callbacks for the parser
        callbacks = {
            'module_begin': self._on_module_begin,
            'module_end': self._on_module_end,
            'signal_declaration': self._on_signal_declaration,
            'parameter_declaration': self._on_parameter_declaration,
        }
        
        self.parser.callbacks = callbacks
        self.parser.parse(content)
        
        # Get module info from the parser
        module_info = self.parser.get_module_info()
        if module_info['name']:
            self._create_module_from_info(module_info, filename)
    
    def _on_module_begin(self, name: str, line: int) -> None:
        """Callback when a module begins"""
        # This will be handled in _create_module_from_info
        pass
    
    def _on_module_end(self) -> None:
        """Callback when a module ends"""
        pass
    
    def _on_signal_declaration(self, signal_type: str, name: str, 
                              type_info: str, line: int) -> None:
        """Callback when a signal is declared"""
        # This will be handled in _create_module_from_info
        pass
    
    def _on_parameter_declaration(self, name: str, line: int) -> None:
        """Callback when a parameter is declared"""
        # This will be handled in _create_module_from_info
        pass
    
    def _create_module_from_info(self, module_info: Dict[str, Any], filename: str) -> None:
        """Create a module from parser information"""
        module_name = module_info['name']
        module = Module(module_name)
        module.filename = filename
        
        # Add ports
        for port_info in module_info['ports']:
            port = module.add_port(
                port_info['name'],
                port_info['direction'],
                width=1  # Default width, could be parsed from the declaration
            )
        
        # Add nets
        for net_info in module_info['nets']:
            net = module.add_net(
                net_info['name'],
                net_info['type'],
                width=1  # Default width, could be parsed from the declaration
            )
        
        # Add parameters
        for param_info in module_info['parameters']:
            module.add_parameter(param_info['name'], '1')  # Default value
        
        # Add to netlist
        self.modules[module_name] = module
        module.parent_netlist = self
        
        # Track for linking
        self._need_link.append(module)
    
    def link(self) -> None:
        """Link all modules in the netlist"""
        # Link modules that need linking
        while self._need_link:
            module = self._need_link.pop()
            module.link()
        
        # Relink if needed
        self._relink = True
        while self._relink:
            self._relink = False
            for module in self.modules.values():
                module.link()
    
    def find_module(self, name: str) -> Optional[Module]:
        """Find a module by name"""
        return self.modules.get(name)
    
    def get_modules(self) -> List[Module]:
        """Get all modules in the netlist"""
        return list(self.modules.values())
    
    def get_top_modules(self) -> List[Module]:
        """Get top-level modules (those not instantiated by other modules)"""
        top_modules = []
        instantiated_modules = set()
        
        # Find all instantiated modules
        for module in self.modules.values():
            for cell in module.cells.values():
                if cell.module:
                    instantiated_modules.add(cell.module.name)
        
        # Return modules that are not instantiated
        for module in self.modules.values():
            if module.name not in instantiated_modules:
                top_modules.append(module)
        
        return top_modules
    
    def dump(self) -> None:
        """Dump the netlist structure for debugging"""
        print("Netlist Dump:")
        print("=============")
        
        for module_name, module in self.modules.items():
            print(f"\nModule: {module_name}")
            print(f"  Ports: {len(module.ports)}")
            for port_name, port in module.ports.items():
                print(f"    {port.direction} {port_name}")
            
            print(f"  Nets: {len(module.nets)}")
            for net_name, net in module.nets.items():
                print(f"    {net.net_type} {net_name}")
            
            print(f"  Cells: {len(module.cells)}")
            for cell_name, cell in module.cells.items():
                print(f"    {cell_name} ({cell.module_name})")
    
    def verilog_text(self) -> str:
        """Generate Verilog text representation of the netlist"""
        lines = []
        
        for module in self.modules.values():
            lines.append(f"module {module.name} (")
            
            # Port declarations
            port_names = list(module.ports.keys())
            if port_names:
                lines.append("  " + ", ".join(port_names))
            lines.append(");")
            
            # Port directions
            for port_name, port in module.ports.items():
                lines.append(f"  {port.direction} {port_name};")
            
            # Net declarations
            for net_name, net in module.nets.items():
                if net_name not in module.ports:
                    lines.append(f"  {net.net_type} {net_name};")
            
            # Cell instantiations
            for cell_name, cell in module.cells.items():
                lines.append(f"  {cell.module_name} {cell_name} (")
                pin_connections = []
                for pin_name, pin in cell.pins.items():
                    if pin.net:
                        pin_connections.append(f"    .{pin_name}({pin.net.name})")
                lines.append(",\n".join(pin_connections))
                lines.append("  );")
            
            lines.append("endmodule")
            lines.append("")
        
        return "\n".join(lines) 