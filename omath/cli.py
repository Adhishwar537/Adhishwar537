import json
import sys
import click
from omath.core.problem import Problem
from omath.solvers.sympy_solver import SympySolver
from omath.solvers.z3_solver import Z3Solver


@click.group()
def cli():
    pass


@cli.command()
@click.argument("expression", type=str)
@click.option("--vars", "vars_", multiple=True, help="Variables, e.g., --vars x --vars y")
def equation(expression: str, vars_: tuple):
    solver = SympySolver()
    problem = Problem.create(expression, kind="equation", variables=list(vars_))
    result = solver.solve(problem)
    _print_result(result)


@cli.command()
@click.argument("expression", type=str)
@click.option("--var", "var_", default="x", help="Integration variable")
def integral(expression: str, var_: str):
    solver = SympySolver()
    problem = Problem.create(expression, kind="integral", variables=[var_])
    result = solver.solve(problem)
    _print_result(result)


@cli.command()
@click.argument("expression", type=str)
def simplify(expression: str):
    solver = SympySolver()
    problem = Problem.create(expression, kind="simplify")
    result = solver.solve(problem)
    _print_result(result)


@cli.command()
@click.argument("n", type=str)
def prime(n: str):
    solver = SympySolver()
    problem = Problem.create(n, kind="prime")
    result = solver.solve(problem)
    _print_result(result)


@cli.command()
@click.argument("constraints", type=str)
@click.option("--dom", type=click.Choice(["int", "real"], case_sensitive=False), default="int")
@click.option("--vars", "vars_", multiple=True, help="Variables override, e.g., --vars x --vars y")
def logic(constraints: str, dom: str, vars_: tuple):
    solver = Z3Solver()
    problem = Problem.create(constraints, kind="logic", variables=list(vars_), domain=dom)
    result = solver.solve(problem)
    _print_result(result)


def _print_result(result):
    status = "ok" if result.success else "error"
    payload = {"status": status, "summary": result.summary, "data": result.data}
    click.echo(json.dumps(payload, default=str))


if __name__ == "__main__":
    cli()