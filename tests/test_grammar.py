import pytest
from pathlib import Path
from lark import Lark, ParseError, UnexpectedInput, UnexpectedToken

GRAMMAR_PATH = Path(__file__).parent.parent / "grammar" / "sipl.lark"

@pytest.fixture(scope="module")
def parser():
    with open(GRAMMAR_PATH, "r", encoding="utf-8") as f:
        grammar_content = f.read()
    return Lark(grammar_content, start="start", parser="earley")



VALID_PROGRAMS = [
    "begin skip end",
    
    "begin X := 5 end",
    
    "begin R := 1; Y := Y - 1 end",
    
    """
    begin
        R := 1;
        while Y > 0 do
        begin
            R := R * X;
            Y := Y - 1
        end
    end
    """,
    
    "begin if X > Y then Z := X else Z := Y end",
    
    "begin A := (X + 2) * (Y - 3) + 10 end",
    
    "begin if (X = 0) \\/ ~(Y > 5) then skip else X := X - 1 end",
    
    "begin while X >= Y do X := X - Y end",
    
    """
    begin
        begin
            begin
                skip
            end
        end
    end
    """,
    
    "begin temp_var := -42 + counter * 2 end",
    
    """
    begin
        F := 1;
        I := 1;
        while I > N do
        begin
            F := F * I;
            I := I + 1
        end
    end
    """
]

@pytest.mark.parametrize("code", VALID_PROGRAMS)
def test_valid_programs(parser, code):
    """Перевірка, що всі коректні SIPL програми успішно парсяться."""
    tree = parser.parse(code)
    assert tree is not None




INVALID_PROGRAMS = [

    "X := 5",
    
    "begin X := 5",
    
    "begin X := (1 + 2 end",
    
    "begin X = 5 end",
    
    "begin if X > 0 then Y := 1 end",

    "begin X := 1; ; Y := 2 end",

    "begin while X > 0 X := X - 1 end",

    "begin if X = 1 OR Y = 2 then skip else skip end",

    "begin X := 5 ++ 3 end",

    "",

    "begin end"
]

@pytest.mark.parametrize("code", INVALID_PROGRAMS)
def test_invalid_programs(parser, code):
    """Перевірка, що некоректні програми викидають помилку парсингу."""
    with pytest.raises((ParseError, UnexpectedInput, UnexpectedToken)):
        parser.parse(code)