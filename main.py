from tokenizer import Tokenizer
from parser import Parser

# code = """
# val x = 3

# if a = 3 {
#     print(a)
# }
# """

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
    tkz = Tokenizer(regex_tokens)
    code_tokens = tkz.tokenize(code)

    parser = Parser(code_tokens)
    errors = parser.parse()

    if (len(errors) > 0):
        print(errors)
        exit(1)



