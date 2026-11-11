# Changelog

All notable changes to the **SIPL Toolkit** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-11-11

### Added
- **CORE-01**: EBNF Lark grammar specification (`grammar/sipl.lark`) and comprehensive test suite.
- **CORE-02**: Typed AST dataclasses with `SourceSpan` positional tracking and syntax error diagnostic mapping.
- **CORE-03**: State-based recursive interpreter with `max_steps` infinite loop safety protection.
- **CORE-04**: Execution event model (`ExecutionTracer`) for step-by-step state and condition tracking.
- **CORE-05**: Command-Line Interface (`sipl.cli`) supporting `check`, `parse`, `run`, `trace`, `export-ast`, `semantic-term` with `--json` support.
- **VIS-01**: AST visualizer exporting to indented plain text and Graphviz DOT formats.
- **SEM-01**: Recursive formal semantic term generator matching course theory notation.
- **REL-01/02**: GitHub Actions CI workflow and SemVer release structure.