import os
import subprocess
from typing import List
from kast import ASTNode, ProgramNode, DeclarationNode, ConditionNode, IfNode, FunctionCallNode

class ELFGeneratorNASM:
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

class ELFGeneratorLLVM:
    def __init__(self, ast: ProgramNode):
        self.ast = ast

    def generate_llvm_ir(self) -> str:
        """
        Traverse the AST and generate LLVM IR code.
        """
        ir = []

        ir.append("; ModuleID = 'my_program'")
        ir.append("source_filename = \"my_program.c\"")
        ir.append("target datalayout = \"e-m:e-i64:64-f80:128-n8:16:32:64-S128\"")
        ir.append("target triple = \"x86_64-unknown-linux-gnu\"")
        ir.append("")

        def visit(node: ASTNode):
            if isinstance(node, DeclarationNode):
                ir.append(f"@{node.name.value} = common global float {node.value.value}, align 4")
            elif isinstance(node, ConditionNode):
                ir.append(f"load float, float* @{node.left.value}, align 4")
                ir.append(f"load float, float* @{node.right.value}, align 4")
                # Add LLVM IR for the condition operator
            elif isinstance(node, IfNode):
                # Add LLVM IR for the if statement
                visit(node.condition)
                ir.append("br i1 %cond, label %then, label %else")
                ir.append("then:")
                for stmt in node.body:
                    visit(stmt)
                ir.append("br label %end_if")
                ir.append("else:")
                ir.append("br label %end_if")
                ir.append("end_if:")
            elif isinstance(node, FunctionCallNode):
                # Add LLVM IR for the function call
                # for arg in node.arguments:
                #     ir.append(f"load float, float* @{arg.value}, align 4")
                ir.append(f"load float, float* @{node.parameter.value}, align 4")
                ir.append(f"call void @{node.name.value}()")
            else:
                raise ValueError(f"Unsupported node type: {type(node)}")

        for stmt in self.ast.statements:
            visit(stmt)

        return "\n".join(ir)

    def compile(self, ir: str, output_file: str) -> None:
        """
        Compile the LLVM IR code into an object file.
        """
        with open("temp.ll", "w") as f:
            f.write(ir)

        subprocess.run(["llc", "-filetype=obj", "temp.ll", "-o", output_file], check=True)

    def link(self, object_files: List[str], output_file: str) -> None:
        """
        Link the object files into a final executable.
        """
        subprocess.run(["ld", "-o", output_file] + object_files, check=True)

    def generate_executable(self, output_file: str) -> None:
        """
        Generate the final ELF executable from the AST.
        """
        ir = self.generate_llvm_ir()
        self.compile(ir, "program.o")
        self.link(["program.o"], output_file)