from typing import Dict, List, Tuple
from sympy import symbols, sympify
import z3
from omath.core.problem import Problem
from omath.core.results import Result


class Z3Solver:
    SUPPORTED_KINDS = {"logic"}

    def supports(self, problem: Problem) -> bool:
        return problem.kind in self.SUPPORTED_KINDS

    def solve(self, problem: Problem) -> Result:
        constraints_str = problem.text
        domain = (problem.domain or "int").lower()
        var_names = sorted(list(set(problem.variables or self._infer_vars(constraints_str))))

        if not var_names:
            return Result(False, "No variables found")

        var_map_sympy = {name: sym for name, sym in zip(var_names, symbols(var_names))}

        if domain == "int":
            var_map_z3 = {name: z3.Int(name) for name in var_names}
        else:
            var_map_z3 = {name: z3.Real(name) for name in var_names}

        try:
            z3_constraints = [self._to_z3(self._parse_constraint(c.strip(), var_map_sympy), var_map_z3)
                              for c in constraints_str.split(";") if c.strip()]
        except Exception as e:
            return Result(False, f"Failed to parse constraints: {e}")

        solver = z3.Solver()
        for c in z3_constraints:
            solver.add(c)

        status = solver.check()
        if status == z3.sat:
            model = solver.model()
            assignment = {name: model[var_map_z3[name]].as_long() if domain == "int" else model[var_map_z3[name]].as_decimal(20)
                          for name in var_names}
            return Result(True, "Satisfiable", {"assignment": assignment})
        elif status == z3.unsat:
            return Result(False, "Unsatisfiable")
        else:
            return Result(False, "Unknown")

    def _infer_vars(self, constraints_str: str) -> List[str]:
        tokens = set()
        curr = []
        for ch in constraints_str:
            if ch.isalpha() or ch.isdigit() or ch == "_":
                curr.append(ch)
            else:
                if curr:
                    token = "".join(curr)
                    if token and not token[0].isdigit():
                        tokens.add(token)
                curr = []
        if curr:
            token = "".join(curr)
            if token and not token[0].isdigit():
                tokens.add(token)
        # Exclude known keywords/operators
        for kw in ["and", "or", "not", "sin", "cos", "tan", "log", "exp"]:
            tokens.discard(kw)
        return list(tokens)

    def _parse_constraint(self, c: str, var_map_sympy: Dict[str, any]):
        # Supports ==, <=, >=, <, >
        ops = ["<=", ">=", "==", "<", ">"]
        for op in ops:
            if op in c:
                left, right = c.split(op, 1)
                left_expr = sympify(left, locals=var_map_sympy)
                right_expr = sympify(right, locals=var_map_sympy)
                return (op, left_expr, right_expr)
        raise ValueError(f"No relational operator in: {c}")

    def _to_z3(self, parsed, var_map_z3: Dict[str, any]):
        op, left_expr, right_expr = parsed
        left_z3 = self._expr_to_z3(left_expr, var_map_z3)
        right_z3 = self._expr_to_z3(right_expr, var_map_z3)
        if op == "==":
            return left_z3 == right_z3
        if op == "<=":
            return left_z3 <= right_z3
        if op == ">=":
            return left_z3 >= right_z3
        if op == "<":
            return left_z3 < right_z3
        if op == ">":
            return left_z3 > right_z3
        raise ValueError(f"Unknown operator: {op}")

    def _expr_to_z3(self, expr, var_map_z3: Dict[str, any]):
        # Handle numbers
        if expr.is_Number:
            if expr.is_Integer:
                return z3.IntVal(int(expr))
            return z3.RealVal(float(expr))
        # Handle symbols
        if expr.is_Symbol:
            return var_map_z3[str(expr)]
        # Handle addition and multiplication and power (limited)
        if expr.is_Add:
            args = [self._expr_to_z3(arg, var_map_z3) for arg in expr.args]
            return args[0] + sum(args[1:], args[0] * 0)
        if expr.is_Mul:
            res = None
            for arg in expr.args:
                z = self._expr_to_z3(arg, var_map_z3)
                res = z if res is None else res * z
            return res
        if expr.is_Pow:
            # Only support power with small integer exponents
            base = self._expr_to_z3(expr.base, var_map_z3)
            exp = expr.exp
            if exp.is_Integer and 0 <= int(exp) <= 5:
                res = z3.IntVal(1) if (hasattr(base, "sort") and str(base.sort()) == "Int") else z3.RealVal(1.0)
                for _ in range(int(exp)):
                    res = res * base
                return res
            raise ValueError("Nonlinear exponent not supported in this simple translator")
        if expr.is_Negative:
            return -self._expr_to_z3(-expr, var_map_z3)
        # Fallback: try linearization via SymPy
        try:
            terms = expr.as_ordered_terms()
            z3_terms = [self._expr_to_z3(t, var_map_z3) for t in terms]
            if len(z3_terms) > 1:
                acc = z3_terms[0]
                for t in z3_terms[1:]:
                    acc = acc + t
                return acc
        except Exception:
            pass
        raise ValueError(f"Unsupported expression: {expr}")