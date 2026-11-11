import pytest
from sipl.parser import SIPLParser
from sipl.interpreter import SIPLInterpreter, SIPLLimitExceededError

@pytest.fixture
def parser():
    return SIPLParser()

@pytest.fixture
def interpreter():
    return SIPLInterpreter()

def test_power_program(parser, interpreter):
    """Тестування програми піднесення до степеня з методички (x^y)."""
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
    ast = parser.parse(code)
    final_state = interpreter.execute(ast, initial_state={"X": 5, "Y": 3})
    
    assert final_state["R"] == 125
    assert final_state["Y"] == 0
    assert final_state["X"] == 5

def test_if_statement(parser, interpreter):
    code = "begin if X > Y then Max := X else Max := Y end"
    ast = parser.parse(code)
    
    res1 = interpreter.execute(ast, {"X": 10, "Y": 20})
    assert res1["Max"] == 20

    res2 = interpreter.execute(ast, {"X": 30, "Y": 5})
    assert res2["Max"] == 30

def test_infinite_loop_protection(parser):
    """Перевірка спрацювання захисту max_steps."""
    infinite_code = "begin while 1 = 1 do skip end"
    ast = parser.parse(infinite_code)
    
    strict_interpreter = SIPLInterpreter(max_steps=100)
    with pytest.raises(SIPLLimitExceededError):
        strict_interpreter.execute(ast)