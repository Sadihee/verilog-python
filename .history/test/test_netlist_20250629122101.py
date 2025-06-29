import unittest
import os
import tempfile

import sys
from pathlib import Path
# Add the verilog_python directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from verilog_python import Netlist, Net, Port, Pin, Cell, Module  # Replace 'your_module' with the actual module name

class TestNet(unittest.TestCase):

    def setUp(self):
        self.net = Net("test_net", "wire", 1)

    def test_add_connection(self):
        pin = Pin("test_pin")
        self.net.add_connection(pin)
        self.assertIn(pin, self.net.connections)

    def test_set_driver(self):
        pin = Pin("test_pin")
        self.net.set_driver(pin)
        self.assertEqual(self.net.driver, pin)

    def test_add_load(self):
        pin = Pin("test_pin")
        self.net.add_load(pin)
        self.assertIn(pin, self.net.loads)

class TestPort(unittest.TestCase):

    def setUp(self):
        self.port = Port("test_port", "input", 1)

    def test_connect_net(self):
        net = Net("test_net")
        self.port.connect_net(net)
        self.assertEqual(self.port.net, net)

class TestPin(unittest.TestCase):

    def setUp(self):
        self.pin = Pin("test_pin")

    def test_connect_net(self):
        net = Net("test_net")
        self.pin.connect_net(net)
        self.assertEqual(self.pin.net, net)

class TestCell(unittest.TestCase):

    def setUp(self):
        self.cell = Cell("test_cell", "test_module")

    def test_add_pin(self):
        pin = self.cell.add_pin("test_pin")
        self.assertIn("test_pin", self.cell.pins)
        self.assertEqual(pin.name, "test_pin")

    def test_get_pin(self):
        pin = self.cell.add_pin("test_pin")
        retrieved_pin = self.cell.get_pin("test_pin")
        self.assertEqual(pin, retrieved_pin)

class TestModule(unittest.TestCase):

    def setUp(self):
        self.module = Module("test_module")

    def test_add_port(self):
        port = self.module.add_port("test_port", "input", 1)
        self.assertIn("test_port", self.module.ports)
        self.assertEqual(port.name, "test_port")

    def test_add_net(self):
        net = self.module.add_net("test_net", "wire", 1)
        self.assertIn("test_net", self.module.nets)
        self.assertEqual(net.name, "test_net")

    def test_add_cell(self):
        cell = self.module.add_cell("test_cell", "test_module")
        self.assertIn("test_cell", self.module.cells)
        self.assertEqual(cell.name, "test_cell")

    def test_add_parameter(self):
        self.module.add_parameter("test_param", "1")
        self.assertIn("test_param", self.module.parameters)
        self.assertEqual(self.module.parameters["test_param"], "1")

    def test_get_port(self):
        port = self.module.add_port("test_port", "input", 1)
        retrieved_port = self.module.get_port("test_port")
        self.assertEqual(port, retrieved_port)

    def test_get_net(self):
        net = self.module.add_net("test_net", "wire", 1)
        retrieved_net = self.module.get_net("test_net")
        self.assertEqual(net, retrieved_net)

    def test_get_cell(self):
        cell = self.module.add_cell("test_cell", "test_module")
        retrieved_cell = self.module.get_cell("test_cell")
        self.assertEqual(cell, retrieved_cell)

class TestNetlist(unittest.TestCase):

    def setUp(self):
        self.netlist = Netlist()

    def test_read_file(self):
        # Create a temporary file and write some Verilog content to it
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("module test(input a, output b); endmodule")
            temp_file_path = f.name

        try:
            # Read the file using the Netlist class
            self.netlist.read_file(temp_file_path)
            self.assertEqual(len(self.netlist.modules), 1)
        finally:
            # Ensure the file is closed and then deleted
            os.unlink(temp_file_path)

    def test_link(self):
        module1 = Module("module1")
        module2 = Module("module2")
        cell = module1.add_cell("cell1", "module2")
        self.netlist.modules["module1"] = module1
        self.netlist.modules["module2"] = module2
        module1.parent_netlist = self.netlist
        module2.parent_netlist = self.netlist
        self.netlist._need_link.append(module1)
        self.netlist.link()
        self.assertEqual(cell.module, module2)

    def test_find_module(self):
        module = Module("test_module")
        self.netlist.modules["test_module"] = module
        found_module = self.netlist.find_module("test_module")
        self.assertEqual(module, found_module)

    def test_get_modules(self):
        module1 = Module("module1")
        module2 = Module("module2")
        self.netlist.modules["module1"] = module1
        self.netlist.modules["module2"] = module2
        modules = self.netlist.get_modules()
        self.assertEqual(len(modules), 2)

    def test_get_top_modules(self):
        module1 = Module("module1")
        module2 = Module("module2")
        cell = module1.add_cell("cell1", "module2")
        self.netlist.modules["module1"] = module1
        self.netlist.modules["module2"] = module2
        module1.parent_netlist = self.netlist
        module2.parent_netlist = self.netlist
        top_modules = self.netlist.get_top_modules()
        self.assertEqual(len(top_modules), 1)
        self.assertEqual(top_modules[0], module1)

    def test_dump(self):
        # Create a module
        module = Module("test_module")
        module.add_port("port1", "input")
        module.add_net("net1", "wire")
        cell = module.add_cell("cell1", "sub_module")
        cell.add_pin("pin1")

        # Add the module to the netlist
        self.netlist.modules["test_module"] = module

        # Capture the output of the dump method
        print("***",self.netlist.dump())
        with self.assertLogs() as log:
            self.netlist.dump()

            # Combine all log output into a single string
            log_output = '\n'.join(log.output)

            # Check if the log output contains the expected strings
            print("***",log_output)
            
            self.assertIn("Module: test_module", log_output)
            self.assertIn("Ports: 1", log_output)
            self.assertIn("input port1", log_output)
            self.assertIn("Nets: 1", log_output)
            self.assertIn("wire net1", log_output)
            self.assertIn("Cells: 1", log_output)
            self.assertIn("cell1 (sub_module)", log_output)
    def test_verilog_text(self):
        module = Module("test_module")
        module.add_port("a", "input")
        module.add_port("b", "output")
        module.add_net("c", "wire")
        self.netlist.modules["test_module"] = module
        verilog_text = self.netlist.verilog_text()
        self.assertIn("module test_module (a, b);", verilog_text)
        self.assertIn("input a;", verilog_text)
        self.assertIn("output b;", verilog_text)
        self.assertIn("wire c;", verilog_text)

if __name__ == '__main__':
    unittest.main()
