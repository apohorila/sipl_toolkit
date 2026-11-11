from typing import Union, Dict, Any
from pathlib import Path
from .ast import (
    ASTNode, Program, Statement, SkipStmt, AssignStmt, SeqStmt,
    IfStmt, WhileStmt, BlockStmt, NumExp, VarExp, BinOpExp,
    CompExp, NotExp, OrExp
)

class ASTVisualizer:
    """Генерує текстове та Graphviz DOT/SVG представлення з живого об'єкта AST."""

    def __init__(self, ast: Program):
        self.ast = ast
        self.node_counter = 0

    def to_text(self, node: ASTNode = None, indent: str = "") -> str:
        """Текстове дерево з відступами."""
        if node is None:
            node = self.ast

        span_str = f" [{node.span}]" if getattr(node, "span", None) else ""
        lines = []

        if isinstance(node, Program):
            lines.append(f"{indent}Program{span_str}")
            lines.append(self.to_text(node.body, indent + "  "))

        elif isinstance(node, SeqStmt):
            lines.append(f"{indent}SeqStmt{span_str}")
            for stmt in node.statements:
                lines.append(self.to_text(stmt, indent + "  "))

        elif isinstance(node, AssignStmt):
            lines.append(f"{indent}AssignStmt({node.var_name} :=){span_str}")
            lines.append(self.to_text(node.expr, indent + "  "))

        elif isinstance(node, IfStmt):
            lines.append(f"{indent}IfStmt{span_str}")
            lines.append(f"{indent}  Condition:")
            lines.append(self.to_text(node.condition, indent + "    "))
            lines.append(f"{indent}  Then:")
            lines.append(self.to_text(node.then_branch, indent + "    "))
            lines.append(f"{indent}  Else:")
            lines.append(self.to_text(node.else_branch, indent + "    "))

        elif isinstance(node, WhileStmt):
            lines.append(f"{indent}WhileStmt{span_str}")
            lines.append(f"{indent}  Condition:")
            lines.append(self.to_text(node.condition, indent + "    "))
            lines.append(f"{indent}  Body:")
            lines.append(self.to_text(node.body, indent + "    "))

        elif isinstance(node, BlockStmt):
            lines.append(f"{indent}BlockStmt{span_str}")
            lines.append(self.to_text(node.body, indent + "  "))

        elif isinstance(node, SkipStmt):
            lines.append(f"{indent}SkipStmt{span_str}")

        elif isinstance(node, BinOpExp):
            lines.append(f"{indent}BinOpExp('{node.op}'){span_str}")
            lines.append(self.to_text(node.left, indent + "  "))
            lines.append(self.to_text(node.right, indent + "  "))

        elif isinstance(node, CompExp):
            lines.append(f"{indent}CompExp('{node.op}'){span_str}")
            lines.append(self.to_text(node.left, indent + "  "))
            lines.append(self.to_text(node.right, indent + "  "))

        elif isinstance(node, NotExp):
            lines.append(f"{indent}NotExp('~'){span_str}")
            lines.append(self.to_text(node.expr, indent + "  "))

        elif isinstance(node, OrExp):
            lines.append(f"{indent}OrExp('\\/'){span_str}")
            lines.append(self.to_text(node.left, indent + "  "))
            lines.append(self.to_text(node.right, indent + "  "))

        elif isinstance(node, NumExp):
            lines.append(f"{indent}NumExp({node.value}){span_str}")

        elif isinstance(node, VarExp):
            lines.append(f"{indent}VarExp('{node.name}'){span_str}")

        return "\n".join(lines)

    def to_dot(self) -> str:
        """Генерує граф у форматі Graphviz DOT."""
        self.node_counter = 0
        dot_lines = [
            "digraph SIPL_AST {",
            '  node [shape=box, fontname="Courier", style="filled", fillcolor="#F0F4F8"];',
            '  edge [fontname="Courier"];'
        ]

        def _add_node(label: str, shape: str = "box", fillcolor: str = "#E1F5FE") -> int:
            self.node_counter += 1
            node_id = self.node_counter
            escaped_label = label.replace('"', '\\"')
            dot_lines.append(f'  node_{node_id} [label="{escaped_label}", shape={shape}, fillcolor="{fillcolor}"];')
            return node_id

        def _add_edge(parent_id: int, child_id: int, label: str = ""):
            edge_lbl = f' [label="{label}"]' if label else ""
            dot_lines.append(f'  node_{parent_id} -> node_{child_id}{edge_lbl};')

        def _traverse(node: ASTNode) -> int:
            span_lbl = f"\\nL{node.span.line}:C{node.span.column}" if getattr(node, "span", None) else ""

            if isinstance(node, Program):
                curr_id = _add_node(f"Program{span_lbl}", fillcolor="#D1C4E9")
                child_id = _traverse(node.body)
                _add_edge(curr_id, child_id)

            elif isinstance(node, SeqStmt):
                curr_id = _add_node(f"SeqStmt{span_lbl}", fillcolor="#BBDEFB")
                for idx, stmt in enumerate(node.statements, 1):
                    child_id = _traverse(stmt)
                    _add_edge(curr_id, child_id, label=str(idx))

            elif isinstance(node, AssignStmt):
                curr_id = _add_node(f"Assign (:=){span_lbl}\\nvar: {node.var_name}", fillcolor="#C8E6C9")
                child_id = _traverse(node.expr)
                _add_edge(curr_id, child_id, label="expr")

            elif isinstance(node, IfStmt):
                curr_id = _add_node(f"IfStmt{span_lbl}", fillcolor="#FFE0B2")
                cond_id = _traverse(node.condition)
                then_id = _traverse(node.then_branch)
                else_id = _traverse(node.else_branch)
                _add_edge(curr_id, cond_id, label="cond")
                _add_edge(curr_id, then_id, label="then")
                _add_edge(curr_id, else_id, label="else")

            elif isinstance(node, WhileStmt):
                curr_id = _add_node(f"WhileStmt{span_lbl}", fillcolor="#FFF9C4")
                cond_id = _traverse(node.condition)
                body_id = _traverse(node.body)
                _add_edge(curr_id, cond_id, label="cond")
                _add_edge(curr_id, body_id, label="body")

            elif isinstance(node, BlockStmt):
                curr_id = _add_node(f"BlockStmt{span_lbl}", fillcolor="#E1BEE7")
                child_id = _traverse(node.body)
                _add_edge(curr_id, child_id)

            elif isinstance(node, SkipStmt):
                curr_id = _add_node(f"Skip{span_lbl}", fillcolor="#CFD8DC")

            elif isinstance(node, BinOpExp):
                curr_id = _add_node(f"Op ({node.op}){span_lbl}", fillcolor="#DCEDC8")
                l_id = _traverse(node.left)
                r_id = _traverse(node.right)
                _add_edge(curr_id, l_id, label="left")
                _add_edge(curr_id, r_id, label="right")

            elif isinstance(node, CompExp):
                curr_id = _add_node(f"Comp ({node.op}){span_lbl}", fillcolor="#FFCCBC")
                l_id = _traverse(node.left)
                r_id = _traverse(node.right)
                _add_edge(curr_id, l_id, label="left")
                _add_edge(curr_id, r_id, label="right")

            elif isinstance(node, NotExp):
                curr_id = _add_node(f"Not (~){span_lbl}", fillcolor="#FFCCBC")
                child_id = _traverse(node.expr)
                _add_edge(curr_id, child_id)

            elif isinstance(node, OrExp):
                curr_id = _add_node(f"Or (\\\\/){span_lbl}", fillcolor="#FFCCBC")
                l_id = _traverse(node.left)
                r_id = _traverse(node.right)
                _add_edge(curr_id, l_id)
                _add_edge(curr_id, r_id)

            elif isinstance(node, NumExp):
                curr_id = _add_node(f"Num: {node.value}{span_lbl}", shape="ellipse", fillcolor="#F5F5F5")

            elif isinstance(node, VarExp):
                curr_id = _add_node(f"Var: {node.name}{span_lbl}", shape="ellipse", fillcolor="#F5F5F5")

            return curr_id

        _traverse(self.ast)
        dot_lines.append("}")
        return "\n".join(dot_lines)

    def generate_dot(self) -> str:
        return self.to_dot()