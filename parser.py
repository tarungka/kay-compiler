from errors import Errors
from tokenizer import Token

class Parser:

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
        # print(f"expecting {types} analyzing {token.type}")
        if token and token.type in types:
            self.current += 1
            # print("VALID!")
            return token
        # print("ERR - INVALID!")
        self.errors.append(self.err.error(token))
        return None

    def validate_decl(self) -> bool:
        """
        DECL : val NAME = NUMBER
        """
        start_token = self.pick()
        # print(f"Start token: {start_token}")
        if not start_token or start_token.type != 'VAL':
            # print("Not a start token")
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
        # print(f"Start token: {start_token}")
        if not start_token or start_token.type != "IF":
            return False

        start_pos = self.current

        # if COND {
        if not(self.expect("IF") and
               self.validate_cond() and
               self.expect("LBRACE")):
               return False


        if len(self.parse()) > 0:
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

    def parse(self):
        while self.pick():
            if not (self.validate_decl() or
                    self.validate_if() or
                    self.validate_fn()
                ):
                return self.errors
        return self.errors
