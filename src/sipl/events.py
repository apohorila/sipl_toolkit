from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional
from .ast import SourceSpan

State = Dict[str, int]

@dataclass
class SIPLEvent:
    event_type: str
    span: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class BeforeStatementEvent(SIPLEvent):
    stmt_type: str = ""
    state: Optional[State] = None

@dataclass
class AfterStatementEvent(SIPLEvent):
    stmt_type: str = ""
    state: Optional[State] = None

@dataclass
class VariableChangeEvent(SIPLEvent):
    var_name: str = ""
    old_value: Optional[int] = None
    new_value: int = 0

@dataclass
class ConditionCheckEvent(SIPLEvent):
    condition_repr: str = ""
    result: bool = False

@dataclass
class ProgramFinishEvent(SIPLEvent):
    final_state: Optional[State] = None
    total_steps: int = 0

class ExecutionTracer:
    """Збирає події під час виконання SIPL програми."""
    def __init__(self):
        self.events: List[SIPLEvent] = []

    def emit(self, event: SIPLEvent):
        self.events.append(event)

    def to_list(self) -> List[Dict[str, Any]]:
        return [e.to_dict() for e in self.events]