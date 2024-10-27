from tokenizer import Token

class Errors:

    def error(self, token: Token) -> str:
        return f"{token.line}:{token.column} Unexpected '{token.value}' of type {token.type}"