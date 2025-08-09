from typing import Any, Dict, List
from sympy import symbols, Eq, sympify, solveset, S, integrate, simplify, isprime
from omath.core.problem import Problem
from omath.core.results import Result


class SympySolver:
    SUPPORTED_KINDS = {"equation", "integral", "simplify", "prime"}

    def supports(self, problem: Problem) -> bool:
        return problem.kind in self.SUPPORTED_KINDS

    def solve(self, problem: Problem) -> Result:
        if problem.kind == "equation":
            return self._solve_equation(problem)
        if problem.kind == "integral":
            return self._integrate(problem)
        if problem.kind == "simplify":
            return self._simplify(problem)
        if problem.kind == "prime":
            return self._isprime(problem)
        return Result(success=False, summary=f"Unsupported kind: {problem.kind}")

    def _symbol_map(self, var_names: List[str]) -> Dict[str, Any]:
        if not var_names:
            return {}
        syms = symbols(var_names)
        if isinstance(syms, (tuple, list)):
            return {name: sym for name, sym in zip(var_names, syms)}
        return {var_names[0]: syms}

    def _solve_equation(self, problem: Problem) -> Result:
        var_map = self._symbol_map(problem.variables)
        expr_text = problem.text
        if "=" in expr_text:
            left, right = expr_text.split("=", 1)
            eq = Eq(sympify(left, locals=var_map), sympify(right, locals=var_map))
        else:
            # Interpret as expression == 0
            eq = Eq(sympify(expr_text, locals=var_map), 0)

        # Prefer solveset for set semantics
        main_var = list(var_map.values())[0] if var_map else None
        if main_var is None:
            return Result(False, "No variables provided for equation solving")

        sol = solveset(eq, main_var, domain=S.Complexes)
        return Result(True, f"Solutions for {main_var}", {"solutions": list(sol)})

    def _integrate(self, problem: Problem) -> Result:
        var_map = self._symbol_map(problem.variables or [problem.metadata.get("var", "x")])
        var = list(var_map.values())[0] if var_map else symbols("x")
        expr = sympify(problem.text, locals=var_map)
        res = integrate(expr, var)
        return Result(True, f"Integral with respect to {var}", {"integral": res})

    def _simplify(self, problem: Problem) -> Result:
        expr = sympify(problem.text)
        res = simplify(expr)
        return Result(True, "Simplified expression", {"simplified": res})

    def _isprime(self, problem: Problem) -> Result:
        n = int(problem.text.strip())
        res = isprime(n)
        return Result(True, "Primality test", {"n": n, "is_prime": res})