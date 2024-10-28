from errors import Errors
from tokenizer import Token
from kast import *

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

    def parse_decl(self) -> DeclarationNode | None:
        """
        DECL : val NAME = NUMBER
        """
        start_token = self.pick()
        # print(f"Start token: {start_token}")
        if not start_token or start_token.type != 'VAL':
            # print("Not a start token")
            return False

        saved_pos = self.current


        val_token = self.expect('VAL')
        name_token = self.expect("NAME")
        eq_token = self.expect('EQ')
        nn_token = self.expect("NUMBER")

        if not (all([val_token, name_token, eq_token, nn_token])):
            self.current = saved_pos
            return None

        name_node = NameNode(name_token.value)
        value_node = NumberNode(nn_token.value)

        return DeclarationNode(name=name_node, value=value_node)

    def parse_cond(self) -> ConditionNode | None:
        start_pos = self.current

        l_nn_token = self.expect("NAME","NUMBER")
        cond_token = self.expect("COND")
        r_nn_token = self.expect("NAME","NUMBER")

        if not(all([l_nn_token, cond_token, r_nn_token])):
            self.current = start_pos
            return None

        left_node = NameNode(l_nn_token.value) if l_nn_token.type == "NAME" else NumberNode(float(l_nn_token.value))
        op_node = cond_token.value
        right_node = NameNode(r_nn_token.value) if r_nn_token.type == "NAME" else NumberNode(float(r_nn_token.value))
        return ConditionNode(left=left_node, op=op_node, right=right_node)


    def parse_if(self):
        start_token = self.pick() # very first token is the start token
        # print(f"Start token: {start_token}")
        if not start_token or start_token.type != "IF":
            return False

        start_pos = self.current

        if_token = self.expect("IF")
        condition = self.parse_cond()
        l_brace_token = self.expect("LBRACE")
        # if COND {
        if not(all([if_token, condition, l_brace_token])):
               self.current = start_pos
               return None

        body_statements = []
        while self.pick() and self.pick().type != "RBRACE":
            statement = self.parse_statement()
            if statement:
                body_statements.append(statement)
            else:
                self.current = start_pos
                return None

        # }
        if not(self.expect("RBRACE")):
            self.current = start_pos
            return None

        return IfNode(condition=condition, body=body_statements)

    def parse_statement(self) -> ASTNode | None:
        return (self.parse_if() or
                self.parse_decl() or
                self.parse_function_call())


    def parse_function_call(self) -> bool:
        start_token = self.pick()
        if start_token.type != "NAME":
            return False

        start_pos = self.current

        name_token = self.expect("NAME")
        l_paren_token = self.expect("LPARENS")
        para_token = self.expect("NAME", "NUMBER")
        r_paren_token = self.expect("RPARENS")
        if not (all([name_token, l_paren_token, para_token, r_paren_token])):
            self.current = start_pos
            return None

        name_node = NameNode(name_token.value)
        parameter_node = NameNode(para_token.value) if para_token.value == "NAME" else NumberNode(float(para_token.value))
        return FunctionCallNode(name=name_node, parameter=parameter_node)

    def parse(self) -> ProgramNode | List[str]:
        statements = []
        while self.pick():
            statement = self.parse_statement()
            if statement:
                statements.append(statement)
            else:
                return self.errors

        return ProgramNode(statements=statements)


def print_ast(node: ASTNode, level: int = 0) -> None:
    indent = "  " * level

    if isinstance(node, ProgramNode):
        print(f"{indent}Program:")
        for stmt in node.statements:
            print_ast(stmt, level + 1)

    elif isinstance(node, DeclarationNode):
        print(f"{indent}Declaration:")
        print(f"{indent}  Name: {node.name.value}")
        print(f"{indent}  Value:", end=" ")
        print_ast(node.value, 0)

    elif isinstance(node, IfNode):
        print(f"{indent}If:")
        print(f"{indent}  Condition:")
        print_ast(node.condition, level + 2)
        print(f"{indent}  Body:")
        for stmt in node.body:
            print_ast(stmt, level + 2)

    elif isinstance(node, ConditionNode):
        print(f"{indent}Condition: {node.left.value} {node.op} {node.right.value}")

    elif isinstance(node, FunctionCallNode):
        print(f"{indent}Function Call: {node.name.value}") # function call is always name
        print(f"{indent}  Arguments: {node.parameter.value}") # both NameNode and NumberNode have value attrib
        # print(f"{indent}  Arguments:", end=" ")
        # for arg in node.parameter:
        #     print_ast(arg, level + 2)

    elif isinstance(node, NumberNode):
        print(f"{node.value}")

    elif isinstance(node, NameNode):
        print(f"{node.value}")