#!/usr/bin/python3
import sys
import os
from tokenizer import Tokenizer
from parsera import Parser, print_ast, ProgramNode
# from parser import Parser

code = """
val x = 3

if x > 3 {
    val b = 10
    somefn(b)
    print(a)
}
"""

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

        # if (len(errors) > 0):
        #     print(errors)
        #     exit(1)

        print("The code is good :)")

        if isinstance(ast, ProgramNode):
            print_ast(ast)
        else:
            print("Parsing errors:", ast)
