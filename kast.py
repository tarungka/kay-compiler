from dataclasses import dataclass
from typing import List, Optional, Union


@dataclass
class ASTNode:
    pass

@dataclass
class NumberNode(ASTNode):
    value: float # assume all number are floats

@dataclass
class NameNode(ASTNode):
    value: str # fn names, var names, etc

@dataclass
class DeclarationNode(ASTNode):
    name: NameNode
    value: NumberNode | NameNode # val x=3; val x=a

@dataclass
class ConditionNode(ASTNode):
    left: NameNode | NumberNode
    op: str
    right: NameNode | NumberNode

@dataclass
class FunctionCallNode(ASTNode):
    name: str
    parameter: NameNode | NumberNode # print(a); print(1)

@dataclass
class ProgramNode(ASTNode):
    """Root node holding all the statements"""
    statements: List[ASTNode]

