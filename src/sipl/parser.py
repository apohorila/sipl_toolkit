from pathlib import Path
from typing import Union, List
from lark import Lark, Transformer, v_args, UnexpectedInput, ParseError

from .ast import (
    SourceSpan, ASTNode, Program, Statement, SkipStmt, AssignStmt,
    SeqStmt, IfStmt, WhileStmt, BlockStmt, Aexp, NumExp, VarExp,
    BinOpExp, Bexp, CompExp, NotExp, OrExp
)

class SIPLSyntaxError(Exception):
    """Кастомна помилка синтаксису з точною прив'язкою до рядочка/колонки."""
    def __init__(self, message: str, line: int, column: int):
        super().__init__(f"Syntax Error at line {line}, col {column}: {message}")
        self.line = line
        self.column = column

def _get_span(meta) -> SourceSpan:
    return SourceSpan(
        line=meta.line,
        column=meta.column,
        end_line=getattr(meta, 'end_line', None),
        end_column=getattr(meta, 'end_column', None)
    )

@v_args(meta=True, inline=True)
class ASTTransformer(Transformer):
    def start(self, meta, prog):
        return prog

    def prog(self, meta, body):
        return Program(body=body, span=_get_span(meta))

    def sequence(self, meta, *stmts):
        stmts_list = list(stmts)
        if len(stmts_list) == 1:
            return stmts_list[0]
        return SeqStmt(statements=stmts_list, span=_get_span(meta))

    def assign_stmt(self, meta, var_token, expr):
        return AssignStmt(var_name=str(var_token), expr=expr, span=_get_span(meta))

    def if_stmt(self, meta, cond, then_b, else_b):
        return IfStmt(condition=cond, then_branch=then_b, else_branch=else_b, span=_get_span(meta))

    def while_stmt(self, meta, cond, body):
        return WhileStmt(condition=cond, body=body, span=_get_span(meta))

    def block_stmt(self, meta, body):
        return BlockStmt(body=body, span=_get_span(meta))

    def skip_stmt(self, meta):
        return SkipStmt(span=_get_span(meta))

    # Aexp
    def add_exp(self, meta, left, right):
        return BinOpExp(op="+", left=left, right=right, span=_get_span(meta))

    def sub_exp(self, meta, left, right):
        return BinOpExp(op="-", left=left, right=right, span=_get_span(meta))

    def mult_exp(self, meta, left, right):
        return BinOpExp(op="*", left=left, right=right, span=_get_span(meta))

    def num_exp(self, meta, num_token):
        return NumExp(value=int(num_token), span=_get_span(meta))

    def var_exp(self, meta, var_token):
        return VarExp(name=str(var_token), span=_get_span(meta))

    def par_aexp(self, meta, expr):
        return expr

    # Bexp
    def eq_bexp(self, meta, left, right):
        return CompExp(op="=", left=left, right=right, span=_get_span(meta))

    def gr_bexp(self, meta, left, right):
        return CompExp(op=">", left=left, right=right, span=_get_span(meta))

    def gre_bexp(self, meta, left, right):
        return CompExp(op=">=", left=left, right=right, span=_get_span(meta))

    def neg_bexp(self, meta, expr):
        return NotExp(expr=expr, span=_get_span(meta))

    def or_bexp_op(self, meta, left, right):
        return OrExp(left=left, right=right, span=_get_span(meta))

    def par_bexp(self, meta, expr):
        return expr

class SIPLParser:
    def __init__(self, grammar_path: Union[str, Path] = None):
        if grammar_path is None:
            grammar_path = Path(__file__).parent.parent.parent / "grammar" / "sipl.lark"
        
        with open(grammar_path, "r", encoding="utf-8") as f:
            grammar_content = f.read()

        self._lark = Lark(
            grammar_content,
            start="start",
            parser="earley",
            propagate_positions=True
        )
        self._transformer = ASTTransformer()

    def parse(self, code: str) -> Program:
        try:
            parse_tree = self._lark.parse(code)
            return self._transformer.transform(parse_tree)
        except UnexpectedInput as e:
            raise SIPLSyntaxError(message=f"Unexpected token/character", line=e.line, column=e.column) from e
        except ParseError as e:
            raise SIPLSyntaxError(message=str(e), line=1, column=1) from e