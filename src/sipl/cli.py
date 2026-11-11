import sys
import argparse
import json
from pathlib import Path
from typing import Dict, Any

from .parser import SIPLParser, SIPLSyntaxError
from .interpreter import SIPLInterpreter, SIPLExecutionError
from .events import ExecutionTracer
from .ast import SourceSpan

def _ast_to_dict(node: Any) -> Any:
    if hasattr(node, "__dataclass_fields__"):
        res = {"type": type(node).__name__}
        for field in node.__dataclass_fields__:
            val = getattr(node, field)
            if field == "span":
                if val:
                    res["span"] = {
                        "line": val.line,
                        "column": val.column,
                        "end_line": val.end_line,
                        "end_column": val.end_column
                    }
                else:
                    res["span"] = None
            else:
                res[field] = _ast_to_dict(val)
        return res
    elif isinstance(node, list):
        return [_ast_to_dict(x) for x in node]
    else:
        return node

def parse_initial_state(state_str: str) -> Dict[str, int]:
    if not state_str:
        return {}
    try:
        return json.loads(state_str)
    except json.JSONDecodeError:
        # Підтримка формату X=5,Y=3
        res = {}
        parts = state_str.split(",")
        for part in parts:
            if "=" in part:
                k, v = part.split("=", 1)
                res[k.strip()] = int(v.strip())
        return res

def main():
    parser = argparse.ArgumentParser(description="SIPL Programming Language Toolkit CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    check_parser = subparsers.add_parser("check", help="Check syntax of a SIPL file")
    check_parser.add_argument("file", type=str, help="Path to .sipl file")
    check_parser.add_argument("--json", action="store_true", help="Output in JSON format")


    parse_cmd = subparsers.add_parser("parse", help="Parse SIPL file and output AST")
    parse_cmd.add_argument("file", type=str, help="Path to .sipl file")
    parse_cmd.add_argument("--json", action="store_true", help="Output in JSON format")

    run_cmd = subparsers.add_parser("run", help="Execute a SIPL program")
    run_cmd.add_argument("file", type=str, help="Path to .sipl file")
    run_cmd.add_argument("--state", type=str, default="", help="Initial state as JSON or 'X=5,Y=3'")
    run_cmd.add_argument("--max-steps", type=int, default=10000, help="Max execution steps")
    run_cmd.add_argument("--json", action="store_true", help="Output in JSON format")


    trace_cmd = subparsers.add_parser("trace", help="Execute program and return execution trace")
    trace_cmd.add_argument("file", type=str, help="Path to .sipl file")
    trace_cmd.add_argument("--state", type=str, default="", help="Initial state as JSON or 'X=5,Y=3'")
    trace_cmd.add_argument("--max-steps", type=int, default=10000, help="Max execution steps")
    trace_cmd.add_argument("--json", action="store_true", help="Output in JSON format")

    export_cmd = subparsers.add_parser("export-ast", help="Export AST to DOT format or text tree")
    export_cmd.add_argument("file", type=str, help="Path to .sipl file")
    export_cmd.add_argument("--format", choices=["dot", "text"], default="dot", help="Export format")

    sem_cmd = subparsers.add_parser("semantic-term", help="Build formal semantic term of SIPL program")
    sem_cmd.add_argument("file", type=str, help="Path to .sipl file")


    args = parser.parse_args()

    file_path = Path(args.file)
    if not file_path.exists():
        err_msg = {"error": f"File not found: {args.file}"}
        if args.json:
            print(json.dumps(err_msg, ensure_ascii=False))
        else:
            print(f"Error: {args.file} not found", file=sys.stderr)
        sys.exit(1)

    code = file_path.read_text(encoding="utf-8")
    sipl_parser = SIPLParser()

    if args.command == "check":
        try:
            sipl_parser.parse(code)
            if args.json:
                print(json.dumps({"status": "ok", "message": "Syntax is valid"}, ensure_ascii=False))
            else:
                print("Syntax is valid.")
            sys.exit(0)
    
        except SIPLSyntaxError as e:
            if args.json:
                print(json.dumps({"status": "error", "line": e.line, "column": e.column, "message": str(e)}, ensure_ascii=False))
            else:
                print(f"Syntax Error: {e}", file=sys.stderr)
            sys.exit(1)


    elif args.command == "parse":
        try:
            ast = sipl_parser.parse(code)
            ast_dict = _ast_to_dict(ast)
            if args.json:
                print(json.dumps({"status": "ok", "ast": ast_dict}, indent=2, ensure_ascii=False))
            else:
                print(json.dumps(ast_dict, indent=2, ensure_ascii=False))
            sys.exit(0)
        except SIPLSyntaxError as e:
            if args.json:
                print(json.dumps({"status": "error", "line": e.line, "column": e.column, "message": str(e)}, ensure_ascii=False))
            else:
                print(f"Syntax Error: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "run":
        try:
            ast = sipl_parser.parse(code)
            initial_state = parse_initial_state(args.state)
            interpreter = SIPLInterpreter(max_steps=args.max_steps)
            final_state = interpreter.execute(ast, initial_state=initial_state)

            if args.json:
                print(json.dumps({"status": "ok", "final_state": final_state, "steps": interpreter.steps_count}, indent=2, ensure_ascii=False))
            else:
                print(f"Execution finished in {interpreter.steps_count} steps.")
                print("Final State:")
                for k, v in final_state.items():
                    print(f"  {k} = {v}")
            sys.exit(0)
        except (SIPLSyntaxError, SIPLExecutionError) as e:
            if args.json:
                print(json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False))
            else:
                print(f"Execution Error: {e}", file=sys.stderr)
            sys.exit(1)


    elif args.command == "trace":
        try:
            ast = sipl_parser.parse(code)
            initial_state = parse_initial_state(args.state)
            interpreter = SIPLInterpreter(max_steps=args.max_steps)
            tracer = ExecutionTracer()
            final_state = interpreter.execute(ast, initial_state=initial_state, tracer=tracer)

            trace_data = tracer.to_list()
            if args.json:
                print(json.dumps({"status": "ok", "final_state": final_state, "trace": trace_data}, indent=2, ensure_ascii=False))
            else:
                print(f"Trace recorded ({len(trace_data)} events). Final state: {final_state}")
                for idx, ev in enumerate(trace_data, 1):
                    print(f"{idx}. [{ev['event_type']}] {ev}")
            sys.exit(0)
        except (SIPLSyntaxError, SIPLExecutionError) as e:
            if args.json:
                print(json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False))
            else:
                print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.command == "export-ast":
        try:
            ast = sipl_parser.parse(code)
            from .visualization import ASTVisualizer
            visualizer = ASTVisualizer(ast)

            if args.format == "dot":
                print(visualizer.generate_dot())
            else:
                print(visualizer.to_text())
            sys.exit(0)
        except SIPLSyntaxError as e:
            print(f"Syntax Error: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.command == "semantic-term":
        try:
            ast = sipl_parser.parse(code)
            from .semantics import build_semantic_term
            term = build_semantic_term(ast)
            print(f"Semantic Term:\n{term}")
            sys.exit(0)
        except SIPLSyntaxError as e:
            print(f"Syntax Error: {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()