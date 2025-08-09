# OpenMath Solver (Research Scaffold)

This project is a practical scaffold for experimenting with automated reasoning on math problems. It does not "solve the unsolved problems of the world"; rather, it provides:

- A clean, extensible architecture for plugging in solvers (symbolic, SMT, search)
- A CLI for common tasks (equations, integrals, simplification, primality, simple logic)
- Basic verification utilities to sanity-check candidate solutions

## Philosophy and scope
- **Reality check**: Open mathematical problems are hard by definition. This tool does not claim to solve them. Instead it aims to be a useful foundation for programmatic math exploration and solver integration.
- **Extensibility first**: Add your own solvers (Lean/Coq bridges, heuristic search, SAT/SMT encodings) without changing the CLI.

## Quick start

```bash
# From the project root
pip install -r requirements.txt

# Examples
python -m omath.cli equation "x^2 - 4 = 0" --vars x
python -m omath.cli integral "sin(x)" --var x
python -m omath.cli simplify "(x^2-1)/(x-1)"
python -m omath.cli prime 97
python -m omath.cli logic "x + y == 3; x - y == 1" --dom int
```

## CLI
- `equation EXPRESSION --vars x y ...`: Solve algebraic equations (SymPy)
- `integral EXPRESSION --var x`: Compute indefinite integrals (SymPy)
- `simplify EXPRESSION`: Simplify algebraic expressions (SymPy)
- `prime N`: Primality test (SymPy)
- `logic CONSTRAINTS --dom {int,real}`: Solve simple systems of constraints using Z3. Constraints are separated by `;` and can use `==, <=, >=, <, >`. Variables are auto-detected.

## Tests
```bash
pytest -q
```

## Roadmap ideas
- Auto-formalization to Lean/Coq (via export)
- Property-based conjecture search and counterexample generation
- Heuristics/ML-guided tactic synthesis
- Richer Z3 translation (nonlinear arithmetic, quantifiers)
