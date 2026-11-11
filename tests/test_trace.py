import pytest
from sipl.parser import SIPLParser
from sipl.interpreter import SIPLInterpreter
from sipl.events import ExecutionTracer

def test_execution_trace():
    code = """
    begin
        X := 2;
        Y := 3;
        if X > Y then Max := X else Max := Y
    end
    """
    parser = SIPLParser()
    ast = parser.parse(code)
    
    interpreter = SIPLInterpreter()
    tracer = ExecutionTracer()
    
    final_state = interpreter.execute(ast, tracer=tracer)
    assert final_state["Max"] == 3
    
  
    trace_list = tracer.to_list()
    assert len(trace_list) > 0
    
    
    event_types = [e["event_type"] for e in trace_list]
    assert "BeforeStatement" in event_types
    assert "VariableChange" in event_types
    assert "ConditionCheck" in event_types
    assert "ProgramFinish" in event_types
    
   
    var_changes = [e for e in trace_list if e["event_type"] == "VariableChange"]
    max_change = [e for e in var_changes if e["var_name"] == "Max"][0]
    assert max_change["new_value"] == 3