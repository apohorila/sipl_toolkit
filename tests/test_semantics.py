import pytest
from sipl.parser import SIPLParser
from sipl.semantics import build_semantic_term

def test_power_program_semantic_term():
    """Тестування генерації семантичного терму для програми x^y з прикладів методички (ПР-2, с. 15-16)."""
    code = """
    begin
        R := 1;
        while Y > 0 do
        begin
            R := R * X;
            Y := Y - 1
        end
    end
    """
    parser = SIPLParser()
    ast = parser.parse(code)
    
    term = build_semantic_term(ast)
    

    assert "AS^{R}(\\overline{1})" in term
    assert "WH(S^2(gr, Y\\Rightarrow, \\overline{0})" in term
    assert "AS^{R}(S^2(mult, R\\Rightarrow, X\\Rightarrow))" in term
    assert "AS^{Y}(S^2(sub, Y\\Rightarrow, \\overline{1}))" in term

def test_if_semantic_term():
    code = "begin if X > Y then Z := X else Z := Y end"
    parser = SIPLParser()
    ast = parser.parse(code)
    
    term = build_semantic_term(ast)
    assert term == "IF(S^2(gr, X\\Rightarrow, Y\\Rightarrow), AS^{Z}(X\\Rightarrow), AS^{Z}(Y\\Rightarrow))"