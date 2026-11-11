import pytest
from sipl.parser import SIPLParser, SIPLSyntaxError
from sipl.ast import Program, SeqStmt, AssignStmt, WhileStmt, BinOpExp, NumExp, VarExp

@pytest.fixture
def parser():
    return SIPLParser()

def test_ast_structure_and_spans(parser):
    code = """begin
    R := 1;
    while Y > 0 do
        R := R * X
end"""
    ast = parser.parse(code)
    
    assert isinstance(ast, Program)
    assert ast.span is not None
    assert ast.span.line == 1

    assert isinstance(ast.body, SeqStmt)
    assert len(ast.body.statements) == 2

    stmt1 = ast.body.statements[0]
    assert isinstance(stmt1, AssignStmt)
    assert stmt1.var_name == "R"
    assert isinstance(stmt1.expr, NumExp)
    assert stmt1.expr.value == 1
    assert stmt1.span.line == 2

    stmt2 = ast.body.statements[1]
    assert isinstance(stmt2, WhileStmt)
    assert stmt2.span.line == 3

def test_syntax_error_diagnostics(parser):
    bad_code = "begin\n  X = 5\nend" 
    
    with pytest.raises(SIPLSyntaxError) as exc_info:
        parser.parse(bad_code)
    
    err = exc_info.value
    assert err.line == 2
    assert "Syntax Error at line 2" in str(err)