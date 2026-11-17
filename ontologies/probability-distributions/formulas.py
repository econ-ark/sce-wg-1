"""The formula syntax of the ontology's source, and an evaluator for it.

A formula is an arithmetic expression in Python's syntax over the coordinates of a chart: numbers, names, + - * / **,
unary minus, comparisons, `and`/`or`, and calls to the functions in FUNCTIONS. A coordinate's meaning may also be given
as an expectation, E(g(X)), the expected value under the law of a formula in the draw X. A coordinate may be a vector or
a matrix: arithmetic and comparisons on vectors are elementwise, x[j] is entry j counted from one, [a, b] is a vector,
and the functions include sums and the like. Nothing else parses, so a formula can be read by any consumer and evaluated
without running code from the source. The generator rejects a formula
outside this syntax, or one naming anything but the coordinates its place allows.

The evaluator serves the generator's checks and the tests. The ontology provides no routines for the distributions
themselves.
"""

from __future__ import annotations

import ast
import math

try:  # numpy, where present, lets a formula be evaluated at many points at once, as an expectation is
    import numpy as _np
except ImportError:  # the generator needs none
    _np = None

def _array(x) -> bool:
    return _np is not None and isinstance(x, _np.ndarray)


def _sqrt(x):
    return _np.sqrt(x) if _array(x) else math.sqrt(x)


def _exp(x):
    return _np.exp(x) if _array(x) else math.exp(x)


def _log(x):
    if _array(x):
        with _np.errstate(divide="ignore"):
            return _np.log(x)
    return -math.inf if x == 0 else math.log(x)


def _Phi(x):
    if _array(x):
        return _np.vectorize(lambda t: 0.5 * math.erfc(-t / math.sqrt(2.0)))(x)
    return 0.5 * math.erfc(-x / math.sqrt(2.0))


def _phi(x):
    return _exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def _xphi(x):
    if _array(x):
        return _np.where(_np.isinf(x), 0.0, x * _phi(_np.where(_np.isinf(x), 0.0, x)))
    return 0.0 if math.isinf(x) else x * _phi(x)


def _increasing(x) -> bool:
    return all(a < b for a, b in zip(list(x)[:-1], list(x)[1:]))


def _lex_increasing(*vectors) -> bool:
    rows = list(zip(*[list(v) for v in vectors]))
    return all(a < b for a, b in zip(rows[:-1], rows[1:]))


FUNCTIONS = {
    "sqrt": _sqrt,
    "exp": _exp,
    "log": _log,  # log(0) = -inf
    "Phi": _Phi,  # the standard normal distribution function
    "phi": _phi,  # its density
    "xphi": _xphi,  # x times phi(x), zero at an infinite x
    # vectors and matrices
    "sum": lambda x: _np.sum(x) if _np is not None else sum(x),
    "min": lambda x: _np.min(x) if _np is not None else min(x),
    "max": lambda x: _np.max(x) if _np is not None else max(x),
    "count": len,  # the number of entries; of a matrix, its rows
    "first": lambda x: x[0],
    "last": lambda x: x[-1],
    "index": lambda x: _np.arange(1, len(x) + 1) if _np is not None else list(range(1, len(x) + 1)),  # 1, 2, ..., n
    "increasing": _increasing,  # strictly
    "row": lambda m, i: m[int(i) - 1],  # row i of a matrix, counted from one
    "any": lambda x: bool(_np.any(x)) if _np is not None else any(x),
    "all": lambda x: bool(_np.all(x)) if _np is not None else all(x),
    "lex_increasing": _lex_increasing,  # the vectors' entries, read as tuples, strictly increase
    "diff": lambda x: x[1:] - x[:-1],  # successive differences
    "heads": lambda x: x[:-1],  # all entries but the last
    "tails": lambda x: x[1:],  # all entries but the first
    "interp": lambda x, xs, ys: _np.interp(x, xs, ys),  # the piecewise-linear function through the points (xs, ys)
}
CONSTANTS = {"inf": math.inf, "pi": math.pi, "euler_gamma": 0.5772156649015329}  # Euler's constant γ
EXPECTATION = "E"  # E(g(X)): the expectation of g of the draw X, allowed in a coordinate's as_expectation only
TRANSCENDENTAL = {"sqrt", "exp", "log", "Phi", "phi", "xphi"}

_BINARY = {
    ast.Add: lambda a, b: a + b,
    ast.Sub: lambda a, b: a - b,
    ast.Mult: lambda a, b: a * b,
    ast.Div: lambda a, b: a / b,
    ast.Pow: lambda a, b: a**b,
}
_COMPARE = {
    ast.Lt: lambda a, b: a < b,
    ast.LtE: lambda a, b: a <= b,
    ast.Gt: lambda a, b: a > b,
    ast.GtE: lambda a, b: a >= b,
    ast.Eq: lambda a, b: a == b,
    ast.NotEq: lambda a, b: a != b,
}


class FormulaError(ValueError):
    pass


def parse(text: str) -> ast.Expression:
    """Parse a formula, refusing anything outside the syntax."""
    try:
        tree = ast.parse(str(text).strip(), mode="eval")
    except SyntaxError as e:
        raise FormulaError(f"not a formula: {text!r} ({e.msg})") from None
    for node in ast.walk(tree):
        if isinstance(node, (ast.Expression, ast.Load, ast.UnaryOp, ast.USub, ast.UAdd, ast.BoolOp, ast.And, ast.Or,
                             ast.List)):
            continue
        if isinstance(node, ast.Subscript):
            index = node.slice
            if isinstance(node.value, ast.Name) and (isinstance(index, ast.Name) or (
                    isinstance(index, ast.Constant) and isinstance(index.value, int) and index.value >= 1)):
                continue
            raise FormulaError(f"{text!r}: an entry is written name[j] or name[k], k a whole number from 1")
        if isinstance(node, ast.BinOp) and type(node.op) in _BINARY:
            continue
        if isinstance(node, ast.Compare) and all(type(op) in _COMPARE for op in node.ops):
            continue
        if type(node) in _BINARY or type(node) in _COMPARE:
            continue
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            continue
        if isinstance(node, ast.Name):
            continue
        if isinstance(node, ast.Call):
            known = node.func.id in FUNCTIONS or (node.func.id == EXPECTATION and len(node.args) == 1) \
                if isinstance(node.func, ast.Name) else False
            if known and not node.keywords:
                continue
            raise FormulaError(f"{text!r}: only {', '.join(sorted(FUNCTIONS))} may be called, with positional arguments")
        raise FormulaError(f"{text!r}: {type(node).__name__} is outside the formula syntax")
    return tree


def names(text: str) -> set[str]:
    """The free names of a formula: the names it uses as values, other than the constants."""
    tree = parse(text)
    called = {id(n.func) for n in ast.walk(tree) if isinstance(n, ast.Call)}
    used = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name) and id(n) not in called}
    return used - set(CONSTANTS)


def uses_expectation(text: str) -> bool:
    return any(isinstance(n, ast.Call) and n.func.id == EXPECTATION for n in ast.walk(parse(text)))


def is_exact(text: str) -> bool:
    """True when the formula is rational in its names: no transcendental function and no fractional power."""
    tree = parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and node.func.id in TRANSCENDENTAL | {EXPECTATION}:
            return False
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Pow):
            exponent = node.right
            if isinstance(exponent, ast.UnaryOp) and isinstance(exponent.operand, ast.Constant):
                exponent = exponent.operand
            if not (isinstance(exponent, ast.Constant) and float(exponent.value).is_integer()):
                return False
    return True


def evaluate_all(definitions: dict, env: dict) -> dict:
    """Evaluate auxiliary definitions in order, each seeing the names before it; return env with them added."""
    env = dict(env)
    for name, text in definitions.items():
        env[name] = evaluate(text, env)
    return env


def evaluate(text: str, env: dict):
    """Evaluate a formula with the numbers in `env`."""
    tree = parse(text)

    def ev(node):
        if isinstance(node, ast.Expression):
            return ev(node.body)
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Name):
            if node.id in env:
                return env[node.id]
            if node.id in CONSTANTS:
                return CONSTANTS[node.id]
            raise FormulaError(f"{text!r}: no value for {node.id!r}")
        if isinstance(node, ast.UnaryOp):
            v = ev(node.operand)
            return -v if isinstance(node.op, ast.USub) else v
        if isinstance(node, ast.BinOp):
            return _BINARY[type(node.op)](ev(node.left), ev(node.right))
        if isinstance(node, ast.Compare):
            left, results = ev(node.left), []
            for op, right_node in zip(node.ops, node.comparators):
                right = ev(right_node)
                results.append(_COMPARE[type(op)](left, right))
                left = right
            if any(_array(r) for r in results):
                return _np.logical_and.reduce([_np.asarray(r) for r in results])
            return all(results)
        if isinstance(node, ast.BoolOp):
            values = [ev(v) for v in node.values]
            if any(_array(v) for v in values):
                combine = _np.logical_and if isinstance(node.op, ast.And) else _np.logical_or
                return combine.reduce([_np.asarray(v) for v in values])
            return all(values) if isinstance(node.op, ast.And) else any(values)
        if isinstance(node, ast.Subscript):
            return ev(node.value)[int(ev(node.slice)) - 1]
        if isinstance(node, ast.List):
            items = [ev(e) for e in node.elts]
            return _np.array(items, dtype=float) if _np is not None else items
        if isinstance(node, ast.Call) and node.func.id == EXPECTATION:
            if EXPECTATION not in env:
                raise FormulaError(f"{text!r}: an expectation needs a law to take it under")
            argument = node.args[0]
            return env[EXPECTATION](lambda x: evaluate_node(argument, {**env, "X": x}))
        if isinstance(node, ast.Call):
            return FUNCTIONS[node.func.id](*[ev(a) for a in node.args])
        raise FormulaError(f"{text!r}: cannot evaluate {type(node).__name__}")

    return ev(tree)


def evaluate_node(node: ast.AST, env: dict):
    """Evaluate a parsed subexpression, as an expectation's argument is evaluated at each point of the draw."""
    return evaluate(ast.unparse(node), env)
