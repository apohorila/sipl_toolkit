import pytest
from sipl.parser import SIPLParser
from sipl.visualization import ASTVisualizer

def test_ast_visualization():
    code = "begin R := 1; while Y > 0 do R := R * X end"
    parser = SIPLParser()
    ast = parser.parse(code)
    
    visualizer = ASTVisualizer(ast)
    

    text_tree = visualizer.to_text()
    assert "Program" in text_tree
    assert "AssignStmt(R :=)" in text_tree
    assert "WhileStmt" in text_tree

    dot_output = visualizer.generate_dot()
    assert "digraph SIPL_AST {" in dot_output
    assert "node_" in dot_output
    assert "Assign (:=)" in dot_output
    assert "WhileStmt" in dot_output