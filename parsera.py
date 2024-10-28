from dataclasses import dataclass
from typing import List, Optional, Union
from errors import Errors
from tokenizer import Token

# AST Node classes
@dataclass
class ASTNode:
    pass

@dataclass
class NumberNode(ASTNode):
    value: float

@dataclass
class NameNode(ASTNode):
    value: str

@dataclass
class DeclarationNode(ASTNode):
    name: NameNode
    value: Union[NumberNode, NameNode]

@dataclass
class ConditionNode(ASTNode):
    left: Union[NameNode, NumberNode]
    operator: str
    right: Union[NameNode, NumberNode]

@dataclass
class IfNode(ASTNode):
    condition: ConditionNode
    body: List[ASTNode]

@dataclass
class FunctionCallNode(ASTNode):
    name: str
    arguments: List[Union[NameNode, NumberNode]]

@dataclass
class ProgramNode(ASTNode):
    statements: List[ASTNode]

class Parser:
    def __init__(self, tokens) -> None:
        self.err = Errors()
        self.current = 0
        self.errors = []
        self.tokens = tokens

    def pick(self) -> Token | None:
        if self.current < len(self.tokens):
            return self.tokens[self.current]
        return None

    def expect(self, *types) -> Token | None:
        token = self.pick()
        if token and token.type in types:
            self.current += 1
            return token
        self.errors.append(self.err.error(token))
        return None

    def parse_declaration(self) -> Optional[DeclarationNode]:
        """
        DECL : val NAME = NUMBER
        """
        start_token = self.pick()
        if not start_token or start_token.type != 'VAL':
            return None

        saved_pos = self.current

        val_token = self.expect('VAL')
        name_token = self.expect('NAME')
        eq_token = self.expect('EQ')
        number_token = self.expect('NUMBER')

        if not all([val_token, name_token, eq_token, number_token]):
            self.current = saved_pos
            return None

        return DeclarationNode(
            name=NameNode(name_token.value),
            value=NumberNode(float(number_token.value))
        )

    def parse_condition(self) -> Optional[ConditionNode]:
        start_pos = self.current

        left_token = self.expect("NAME", "NUMBER")
        cond_token = self.expect("COND")
        right_token = self.expect("NAME", "NUMBER")

        if not all([left_token, cond_token, right_token]):
            self.current = start_pos
            return None

        left_node = (NumberNode(float(left_token.value))
                    if left_token.type == "NUMBER"
                    else NameNode(left_token.value))

        right_node = (NumberNode(float(right_token.value))
                     if right_token.type == "NUMBER"
                     else NameNode(right_token.value))

        return ConditionNode(
            left=left_node,
            operator=cond_token.value,
            right=right_node
        )

    def parse_if(self) -> Optional[IfNode]:
        start_token = self.pick()
        if not start_token or start_token.type != "IF":
            return None

        start_pos = self.current

        if_token = self.expect("IF")
        condition = self.parse_condition()
        lbrace_token = self.expect("LBRACE")

        if not all([if_token, condition, lbrace_token]):
            self.current = start_pos
            return None

        # Parse the body of the if statement
        body_statements = []
        while self.pick() and self.pick().type != "RBRACE":
            statement = self.parse_statement()
            if statement:
                body_statements.append(statement)
            else:
                self.current = start_pos
                return None

        if not self.expect("RBRACE"):
            self.current = start_pos
            return None

        return IfNode(
            condition=condition,
            body=body_statements
        )

    def parse_function_call(self) -> Optional[FunctionCallNode]:
        start_token = self.pick()
        if start_token.type != "NAME":
            return None

        start_pos = self.current

        name_token = self.expect("NAME")
        lparens_token = self.expect("LPARENS")
        arg_token = self.expect("NAME", "NUMBER")
        rparens_token = self.expect("RPARENS")

        if not all([name_token, lparens_token, arg_token, rparens_token]):
            self.current = start_pos
            return None

        argument = (NumberNode(float(arg_token.value))
                   if arg_token.type == "NUMBER"
                   else NameNode(arg_token.value))

        return FunctionCallNode(
            name=name_token.value,
            arguments=[argument]
        )

    def parse_statement(self) -> Optional[ASTNode]:
        """Parse a single statement"""
        return (self.parse_declaration() or
                self.parse_if() or
                self.parse_function_call())

    def parse(self) -> Union[List[str], ProgramNode]:
        statements = []
        while self.pick():
            statement = self.parse_statement()
            if statement:
                statements.append(statement)
            else:
                return self.errors

        if self.errors:
            return self.errors

        return ProgramNode(statements=statements)

# Helper function to print the AST
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
        print(f"{indent}Condition: {node.left.value} {node.operator} {node.right.value}")

    elif isinstance(node, FunctionCallNode):
        print(f"{indent}Function Call: {node.name}")
        print(f"{indent}  Arguments:")
        for arg in node.arguments:
            print_ast(arg, level + 2)

    elif isinstance(node, NumberNode):
        print(f"{node.value}")

    elif isinstance(node, NameNode):
        print(f"{node.value}")