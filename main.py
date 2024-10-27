import re
from dataclasses import dataclass
from typing import List

@dataclass
class Token:
    type: str
    value: str
    line: int
    start: int
    end: int
    column: int

class Errors:

    def error(self, token: Token) -> str:
        return f"{token.line}:{token.column} Unexpected '{token.value}' of type {token.type}"

class Tokenizer:

    def __init__(self, token_regex):
        self.TOKENS = token_regex
        self.TOKEN_REGEX = "|".join(f'(?P<{name}>{pattern})' for name, pattern in self.TOKENS)

    def tokenize(self, code: str) -> List[Token]:
        """
        Tokenize the input string based on the grammar defined
        """
        lineNumber = 1
        column = 1
        tokens = []
        for t in re.finditer(self.TOKEN_REGEX,code):
            tokenType = t.lastgroup
            tokenValue = t.group()

            start = t.start()
            end = t.end()

            column += 1
            if tokenType == "NEWLINE":
                lineNumber += 1
                column = 1
                continue
            if tokenType == "WHITESPACE":
                continue
            if tokenType == "WHITESPACE_TAB":
                column += 4
                continue

            tkn = Token(type=tokenType, value=tokenValue, line=lineNumber, start=start, end=end, column=column)

            tokens.append(tkn)
        return tokens

class Validator:

    def __init__(self, tokens) -> None:
        self.err = Errors()
        self.current = 0
        self.errors = []
        self.tokens = tokens

    def pick(self) -> Token | None:
        if self.current < len(self.tokens):
            return self.tokens[self.current]
        else:
            return None

    def expect(self, *types) -> Token | None:
        """
        expect only asserts if the current token is an expected type(s)
        it does not increment the iterator
        """
        token = self.pick()
        print(f"expecting {types} analyzing {token.type}")
        if token and token.type in types:
            self.current += 1
            print("VALID!")
            return token
        print("ERR - INVALID!")
        self.errors.append(self.err.error(token))
        return None

    def validate_decl(self) -> bool:
        """
        DECL : val NAME = NUMBER
        """
        start_token = self.pick()
        print(f"Start token: {start_token}")
        if not start_token or start_token.type != 'VAL':
            print("Not a start token")
            return False

        saved_pos = self.current

        if not (self.expect('VAL') and
                self.expect('NAME') and
                self.expect('EQ') and
                self.expect('NUMBER')):
            self.current = saved_pos
            return False

        return True

    def validate_cond(self):
        start_pos = self.current

        if not((self.expect("NAME","NUMBER")) and
                self.expect("COND") and
               (self.expect("NAME","NUMBER"))
            ):
            self.current = start_pos
            return False

        return True


    def validate_if(self):
        start_token = self.pick() # very first token is the start token
        print(f"Start token: {start_token}")
        if not start_token or start_token.type != "IF":
            return False

        start_pos = self.current

        # if COND {
        if not(self.expect("IF") and
               self.validate_cond() and
               self.expect("LBRACE")):
               return False


        if len(self.validate()) > 0:
            return self.errors

        # }
        if not(self.expect("RBRACE")
            ):
            self.current = start_pos
            return False

        return True

    def validate_fn(self) -> bool:
        start_token = self.pick()
        if start_token.type != "NAME":
            return False

        start_pos = self.current

        if not (self.expect("NAME") and
                self.expect("LPARENS") and
                self.expect("NAME", "NUMBER") and
                self.expect("RPARENS")
            ):
            self.current = start_pos
            return False

        return True

    def validate(self):
        while self.pick():
            if not (self.validate_decl() or
                    self.validate_if() or
                    self.validate_fn()
                ):
                # self.current += 1
                return self.errors

# code = """
# val x = 3

# if a = 3 {
#     print(a)
# }
# """

code = """
val x = 3

if x > 3 {
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

tkz = Tokenizer(regex_tokens)
code_tokens = tkz.tokenize(code)
# print("The code tokens are:", code_tokens)

vld = Validator(code_tokens)
errors = vld.validate()

print(errors)