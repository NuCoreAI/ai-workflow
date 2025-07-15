# format rag 

from nodedef import NodeProperty
from cmd import Command
from editor import Editor

class RagFormatter:
    def __init__(self, indent_str: str = "    ", prefix: str = ""):
        self.lines = []
        self.level = 0
        self.indent_str = indent_str
        self.prefix = prefix

    def write(self, line: str = ""):
        indent = self.indent_str * self.level
        self.lines.append(f"{indent}{line}")

    def write_lines(self, lines: list[str]):
        for line in lines:
            self.write(line)

    def section(self, title: str):
        self.write(f"***{title}***")

    def block(self, level_increase: int = 2):
        class BlockContext:
            def __init__(self, writer: RagFormatter):
                self.writer = writer

            def __enter__(self):
                self.writer.level += level_increase

            def __exit__(self, exc_type, exc_val, exc_tb):
                self.writer.level -= level_increase

        return BlockContext(self)
    
    def add_device_section(self, device_name:str, device_id: str):
        self.section(f"Device")
        self.write(f"Name: {device_name}")
        self.write(f"ID: {device_id}")

    def add_properties_section(self):
        with self.block():
            self.section("Properties")

    def add_accept_commands_section(self):
        with self.block():
            self.section("Accept Commands")
    
    def add_send_commands_section(self):
        with self.block():
            self.section("Send Commands")

    def add_property(self, prop: NodeProperty):
        with self.block(level_increase=4):
            self.write(f"{prop.name}")
            if prop.editor and prop.editor.ranges:
                for range in prop.editor.ranges:
                    with self.block():
                        if range.get_description():
                            self.write(f"{range.get_description()}")
                        if range.names:
                            with self.block(): 
                                #self.write("Permissible values:")
                                for name in range.get_names():
                                    self.write(name)

    def add_command(self, command):
        with self.block(level_increase=4):
            self.write(f"{command.name} [{command.id}]")
            if command.parameters:
                with self.block():
                    i=1
                    with self.block():
                        for param in command.parameters:
                            self.write(f"Parameter {i}: {param.name if param.name else param.id} [{param.id}]")
                            i += 1
                            if param.editor and param.editor.ranges:
                                for range in param.editor.ranges:
                                    with self.block():
                                        if range.get_description():
                                            self.write(f"{range.get_description()}")
                                        if range.names:
                                            with self.block(): 
                                                #self.write("Permissible values:")
                                                for name in range.get_names():
                                                    self.write(name)

    def format_node(self, node):
        self.add_device_section(node.name, node.address)
        if node.node_def:
            if node.node_def.properties:
                self.add_properties_section()
                for prop in node.node_def.properties:
                    self.add_property(prop)

            if node.node_def.cmds.accepts:
                self.add_accept_commands_section()
                for cmd in node.node_def.cmds.accepts:
                    self.add_command(cmd)

            if node.node_def.cmds.sends:
                self.add_send_commands_section()
                for cmd in node.node_def.cmds.sends:
                    self.add_command(cmd)

    def format(self, nodes):
        for node in nodes:
            self.format_node(node)


    def get_output(self) -> str:
        return "\n".join(self.lines)
