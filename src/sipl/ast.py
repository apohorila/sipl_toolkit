from dataclasses import dataclass
from typing import Optional, List

@dataclass(frozen=True)
class SourceSpan:
    """Зберігає позицію вузла в початковому коді SIPL."""
    line: int
    column: int
    end_line: Optional[int] = None
    end_column: Optional[int] = None

    def __str__(self) -> str:
        return f"line {self.line}, col {self.column}"

@dataclass(kw_only=True)
class ASTNode:
    """Базовий клас для всіх вузлів AST."""
    span: Optional[SourceSpan] = None


class Aexp(ASTNode):
    pass

@dataclass(kw_only=True)
class NumExp(Aexp):
    value: int

@dataclass(kw_only=True)
class VarExp(Aexp):
    name: str

@dataclass(kw_only=True)
class BinOpExp(Aexp):
    op: str  # '+', '-', '*'
    left: Aexp
    right: Aexp

class Bexp(ASTNode):
    pass

@dataclass(kw_only=True)
class CompExp(Bexp):
    op: str  # '=', '>', '>='
    left: Aexp
    right: Aexp

@dataclass(kw_only=True)
class NotExp(Bexp):
    expr: Bexp

@dataclass(kw_only=True)
class OrExp(Bexp):
    left: Bexp
    right: Bexp

class Statement(ASTNode):
    pass

@dataclass(kw_only=True)
class SkipStmt(Statement):
    pass

@dataclass(kw_only=True)
class AssignStmt(Statement):
    var_name: str
    expr: Aexp

@dataclass(kw_only=True)
class SeqStmt(Statement):
    statements: List[Statement]

@dataclass(kw_only=True)
class IfStmt(Statement):
    condition: Bexp
    then_branch: Statement
    else_branch: Statement

@dataclass(kw_only=True)
class WhileStmt(Statement):
    condition: Bexp
    body: Statement

@dataclass(kw_only=True)
class BlockStmt(Statement):
    body: Statement

@dataclass(kw_only=True)
class Program(ASTNode):
    body: Statement