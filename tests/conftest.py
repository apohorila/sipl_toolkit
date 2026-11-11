import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sipl.parser import SIPLParser
from sipl.interpreter import SIPLInterpreter

@pytest.fixture(scope="session")
def parser():
    return SIPLParser()

@pytest.fixture
def interpreter():
    return SIPLInterpreter()