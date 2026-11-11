from typing import Dict, Any, Optional
from .ast import (
    Program, Statement, SkipStmt, AssignStmt, SeqStmt,
    IfStmt, WhileStmt, BlockStmt, Aexp, NumExp, VarExp,
    BinOpExp, Bexp, CompExp, NotExp, OrExp
)
from .events import (
    ExecutionTracer, BeforeStatementEvent, AfterStatementEvent,
    VariableChangeEvent, ConditionCheckEvent, ProgramFinishEvent
)

State = Dict[str, int]

class SIPLExecutionError(Exception):
    pass

class SIPLLimitExceededError(SIPLExecutionError):
    pass

def _span_to_dict(span) -> Optional[Dict[str, Any]]:
    if span is None:
        return None
    return {
        "line": span.line,
        "column": span.column,
        "end_line": span.end_line,
        "end_column": span.end_column
    }

class SIPLInterpreter:
    def __init__(self, max_steps: int = 10000):
        self.max_steps = max_steps
        self.steps_count = 0
        self.tracer: Optional[ExecutionTracer] = None

    def execute(
        self,
        prog: Program,
        initial_state: Optional[State] = None,
        tracer: Optional[ExecutionTracer] = None
    ) -> State:
        state: State = dict(initial_state) if initial_state else {}
        self.steps_count = 0
        self.tracer = tracer

        self._exec_stmt(prog.body, state)

        if self.tracer:
            self.tracer.emit(ProgramFinishEvent(
                event_type="ProgramFinish",
                final_state=dict(state),
                total_steps=self.steps_count
            ))

        return state

    def _tick(self):
        self.steps_count += 1
        if self.steps_count > self.max_steps:
            raise SIPLLimitExceededError(
                f"Execution limit exceeded: program ran for more than {self.max_steps} steps."
            )

    def _exec_stmt(self, stmt: Statement, state: State) -> None:
        self._tick()
        span_dict = _span_to_dict(stmt.span)
        stmt_type = type(stmt).__name__

        if self.tracer:
            self.tracer.emit(BeforeStatementEvent(
                event_type="BeforeStatement",
                stmt_type=stmt_type,
                state=dict(state),
                span=span_dict
            ))

        if isinstance(stmt, SkipStmt):
            pass

        elif isinstance(stmt, AssignStmt):
            old_val = state.get(stmt.var_name)
            val = self._eval_aexp(stmt.expr, state)
            state[stmt.var_name] = val
            if self.tracer:
                self.tracer.emit(VariableChangeEvent(
                    event_type="VariableChange",
                    var_name=stmt.var_name,
                    old_value=old_val,
                    new_value=val,
                    span=span_dict
                ))

        elif isinstance(stmt, SeqStmt):
            for s in stmt.statements:
                self._exec_stmt(s, state)

        elif isinstance(stmt, IfStmt):
            cond_val = self._eval_bexp(stmt.condition, state)
            if self.tracer:
                self.tracer.emit(ConditionCheckEvent(
                    event_type="ConditionCheck",
                    condition_repr=str(stmt.condition),
                    result=cond_val,
                    span=_span_to_dict(stmt.condition.span)
                ))
            if cond_val:
                self._exec_stmt(stmt.then_branch, state)
            else:
                self._exec_stmt(stmt.else_branch, state)

        elif isinstance(stmt, WhileStmt):
            while True:
                cond_val = self._eval_bexp(stmt.condition, state)
                if self.tracer:
                    self.tracer.emit(ConditionCheckEvent(
                        event_type="ConditionCheck",
                        condition_repr=str(stmt.condition),
                        result=cond_val,
                        span=_span_to_dict(stmt.condition.span)
                    ))
                if not cond_val:
                    break
                self._exec_stmt(stmt.body, state)

        elif isinstance(stmt, BlockStmt):
            self._exec_stmt(stmt.body, state)

        else:
            raise SIPLExecutionError(f"Unknown statement type: {type(stmt)}")

        if self.tracer:
            self.tracer.emit(AfterStatementEvent(
                event_type="AfterStatement",
                stmt_type=stmt_type,
                state=dict(state),
                span=span_dict
            ))

    def _eval_aexp(self, expr: Aexp, state: State) -> int:
        if isinstance(expr, NumExp):
            return expr.value
        elif isinstance(expr, VarExp):
            return state.get(expr.name, 0)
        elif isinstance(expr, BinOpExp):
            left_val = self._eval_aexp(expr.left, state)
            right_val = self._eval_aexp(expr.right, state)
            if expr.op == "+":
                return left_val + right_val
            elif expr.op == "-":
                return left_val - right_val
            elif expr.op == "*":
                return left_val * right_val
            else:
                raise SIPLExecutionError(f"Unknown arithmetic operator: {expr.op}")
        else:
            raise SIPLExecutionError(f"Unknown arithmetic expression: {type(expr)}")

    def _eval_bexp(self, expr: Bexp, state: State) -> bool:
        if isinstance(expr, CompExp):
            left_val = self._eval_aexp(expr.left, state)
            right_val = self._eval_aexp(expr.right, state)
            if expr.op == "=":
                return left_val == right_val
            elif expr.op == ">":
                return left_val > right_val
            elif expr.op == ">=":
                return left_val >= right_val
            else:
                raise SIPLExecutionError(f"Unknown comparison operator: {expr.op}")
        elif isinstance(expr, NotExp):
            return not self._eval_bexp(expr.expr, state)
        elif isinstance(expr, OrExp):
            return self._eval_bexp(expr.left, state) or self._eval_bexp(expr.right, state)
        else:
            raise SIPLExecutionError(f"Unknown boolean expression: {type(expr)}")