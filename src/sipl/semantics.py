from .ast import (
    ASTNode, Program, Statement, SkipStmt, AssignStmt, SeqStmt,
    IfStmt, WhileStmt, BlockStmt, Aexp, NumExp, VarExp, BinOpExp,
    Bexp, CompExp, NotExp, OrExp
)

class SemanticTermBuilder:
    """Побудова семантичного терму програми у формальній нотації курсу (ПР-2)."""

    def build(self, node: ASTNode) -> str:
        if isinstance(node, Program):
            return self.build(node.body)

        elif isinstance(node, SkipStmt):
            return "id"

        elif isinstance(node, AssignStmt):
            a_term = self._build_aexp(node.expr)
            return f"AS^{{{node.var_name}}}({a_term})"

        elif isinstance(node, SeqStmt):
            terms = [self.build(s) for s in node.statements]
            return " · ".join(terms)

        elif isinstance(node, IfStmt):
            b_term = self._build_bexp(node.condition)
            then_term = self.build(node.then_branch)
            else_term = self.build(node.else_branch)
            return f"IF({b_term}, {then_term}, {else_term})"

        elif isinstance(node, WhileStmt):
            b_term = self._build_bexp(node.condition)
            body_term = self.build(node.body)
            return f"WH({b_term}, {body_term})"

        elif isinstance(node, BlockStmt):
            return self.build(node.body)

        else:
            raise ValueError(f"Unknown AST node for semantic term: {type(node)}")

    def _build_aexp(self, expr: Aexp) -> str:
        if isinstance(expr, NumExp):
            return f"\\overline{{{expr.value}}}"

        elif isinstance(expr, VarExp):
            return f"{expr.name}\\Rightarrow"

        elif isinstance(expr, BinOpExp):
            op_map = {"+": "add", "-": "sub", "*": "mult"}
            op_name = op_map.get(expr.op, expr.op)
            left_term = self._build_aexp(expr.left)
            right_term = self._build_aexp(expr.right)
            return f"S^2({op_name}, {left_term}, {right_term})"

        else:
            raise ValueError(f"Unknown Aexp node: {type(expr)}")

    def _build_bexp(self, expr: Bexp) -> str:
        if isinstance(expr, CompExp):
            op_map = {"=": "eq", ">": "gr", ">=": "gre"}
            op_name = op_map.get(expr.op, expr.op)
            left_term = self._build_aexp(expr.left)
            right_term = self._build_aexp(expr.right)
            return f"S^2({op_name}, {left_term}, {right_term})"

        elif isinstance(expr, NotExp):
            sub_term = self._build_bexp(expr.expr)
            return f"S^1(neg, {sub_term})"

        elif isinstance(expr, OrExp):
            left_term = self._build_bexp(expr.left)
            right_term = self._build_bexp(expr.right)
            return f"S^2(or, {left_term}, {right_term})"

        else:
            raise ValueError(f"Unknown Bexp node: {type(expr)}")

def build_semantic_term(ast: ASTNode) -> str:
    return SemanticTermBuilder().build(ast)