import json
import subprocess
import sys
import importlib.util
import pytest


def run_cli(args):
    cmd = [sys.executable, "-m", "omath.cli"] + args
    out = subprocess.check_output(cmd, text=True)
    return json.loads(out.strip())


def test_equation_solver():
    res = run_cli(["equation", "x^2 - 4 = 0", "--vars", "x"])
    assert res["status"] == "ok"
    sols = set(str(s) for s in res["data"]["solutions"])  # sympy prints roots as -2, 2
    assert "-2" in sols and "2" in sols


def test_integral():
    res = run_cli(["integral", "sin(x)", "--var", "x"])
    assert res["status"] == "ok"
    assert "-cos(x)" in str(res["data"]["integral"]) or "cos(x)" in str(res["data"]["integral"])  # up to constant


def test_prime():
    res = run_cli(["prime", "97"])
    assert res["status"] == "ok"
    assert res["data"]["is_prime"] is True


_z3_available = importlib.util.find_spec("z3") is not None
@pytest.mark.skipif(not _z3_available, reason="z3-solver not available in this environment")
def test_logic_linear_int():
    res = run_cli(["logic", "x + y == 3; x - y == 1", "--dom", "int"])  # auto var infer
    assert res["status"] == "ok"
    assign = res["data"]["assignment"]
    assert int(assign["x"]) == 2
    assert int(assign["y"]) == 1