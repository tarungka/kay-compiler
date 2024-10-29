#!/usr/bin/python3
import sys
import os
from tokenizer import Tokenizer
# from parsera import Parser, print_ast, ProgramNode
from parser import Parser, print_ast
from kast import ProgramNode
from elf import ELFGeneratorLLVM

regex_tokens = [
    ("IF", r'if'),
    ("VAL", r'val'),
    ("COND", r'==|>=|<=|>|<|!='),
    ("EQ", r'='),
    ("LBRACE", r'\{'),
    ("RBRACE", r'\}'),
    ("LPARENS", r'\('),
    ("RPARENS", r'\)'),
    ("NUMBER", r'[0-9]+'),
    ("NAME", r'[a-z]+'),
    ("WHITESPACE", r'[ ]+'),
    ("WHITESPACE_TAB", r'[\t]+'), # assuming tab is 4 spaces long
    ("NEWLINE", r'\n'),
]



if __name__ == "__main__":

    if len(sys.argv) == 1:
        print("Usage: main.py code.kay out_file.out")
        exit(0)

    src_code_f_name = sys.argv[1]
    src_code_exec_f_name = "main.out"
    try:
        src_code_exec_f_name = sys.argv[2]
    except IndexError:
        pass
    with open(src_code_f_name) as f:

        code = f.read()
        print(f"The code is: {code}")
        tkz = Tokenizer(regex_tokens)
        code_tokens = tkz.tokenize(code)

        parser = Parser(code_tokens)
        ast = parser.parse()

        if isinstance(ast, ProgramNode):
            print("The code is good :)")
            print_ast(ast)
        else:
            print("Parsing errors:", ast)
            exit(0)

        elf_generator = ELFGeneratorLLVM(ast)
        # assembly_code = elf_generator.generate_assembly()
        # elf_generator.assemble(assembly=assembly_code, output_file="main.s")
        # elf_generator.link(["main.s"], "main.ld")
        elf_generator.generate_executable("main.out")
