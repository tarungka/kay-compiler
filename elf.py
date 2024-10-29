import os
import subprocess
from typing import List
from kast import ASTNode, ProgramNode, DeclarationNode, ConditionNode, IfNode, FunctionCallNode

class ELFGenerator:
    def __init__(self, ast: ProgramNode):
        self.ast = ast

    def generate_assembly(self) -> str:
        """
        Traverse the AST and generate x86-64 assembly code.
        """
        assembly = []

        def visit(node: ASTNode):
            if isinstance(node, DeclarationNode):
                assembly.append(f"mov rax, {node.value.value}")
                assembly.append(f"mov [{node.name.value}], rax")
            elif isinstance(node, ConditionNode):
                assembly.append(f"mov rax, [{node.left.value}]")
                assembly.append(f"cmp rax, [{node.right.value}]")
                # Add assembly for the condition operator
            elif isinstance(node, IfNode):
                # Add assembly for the if statement
                visit(node.condition)
                assembly.append("je end_if")
                for stmt in node.body:
                    visit(stmt)
                assembly.append("end_if:")
            elif isinstance(node, FunctionCallNode):
                # Add assembly for the function call
                # for arg in node.parameter:
                #     assembly.append(f"push [{arg.value}]")
                assembly.append(f"push [{node.parameter.value}]")
                assembly.append(f"call {node.name.value}")
                assembly.append("pop rax")  # Clean up stack
            else:
                raise ValueError(f"Unsupported node type: {type(node)}")

        for stmt in self.ast.statements:
            visit(stmt)

        return "\n".join(assembly)

    def assemble(self, assembly: str, output_file: str) -> None:
        """
        Assemble the generated assembly code into an object file.
        """
        with open("temp.s", "w") as f:
            f.write(assembly)

        subprocess.run(["nasm", "-f", "elf64", "temp.s"], check=True)
        os.rename("temp.o", output_file)

    def link(self, object_files: List[str], output_file: str) -> None:
        """
        Link the object files into a final executable.
        """
        subprocess.run(["ld", "-o", output_file] + object_files, check=True)

    def generate_executable(self, output_file: str) -> None:
        """
        Generate the final ELF executable from the AST.
        """
        assembly = self.generate_assembly()
        self.assemble(assembly, "program.o")
        self.link(["program.o"], output_file)