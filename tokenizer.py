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

class Tokenizer:
    """Tokenize the input"""

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
