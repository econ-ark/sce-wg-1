"""The shock laws of shock-laws.md: their rules, and their moments in closed form.

Every law is a positive random variable with mean one. A law object answers `moment(k)`, the expectation of the k-th
power for any real k; `mean_log`, the expectation of the log; `mean_x_log_x`, the expectation of the variable times its
log; `infimum` and `supremum` of the support; and `mass_at_infimum`. These are what the regularity conditions of a family
read. `check` returns the problems the validator cannot express, as a list of sentences; an empty list means the law is
well formed. `bellman` returns the law's Bellman-SYM call, the converter's output, or None where Bellman-SYM has no
family for it.

A truncation bound left out of a parameter file is three standard deviations; null is no bound. `filled` writes the
defaults in, and the hash is taken over the filled form, so a law written with its defaults and without them hash alike.
Each law is a chart of a subfamily of mean one in the ontology of probability distributions, whose identifier the law's
class names; the conversions to Bellman-SYM's charts are the ontology's.
"""

from __future__ import annotations

import math
from fractions import Fraction

from scipy.special import log_ndtr, logsumexp, ndtr

TOLERANCE = 1e-12
INF = math.inf
DEFAULT_BOUND = 3.0  # an omitted truncation bound, in standard deviations of the normal before truncation


def _bound(params: dict, key: str) -> float:
    """A truncation bound: three standard deviations when left out, none when null."""
    if key not in params:
        return -DEFAULT_BOUND if key == "bot" else DEFAULT_BOUND
    value = params[key]
    if value is None:
        return -INF if key == "bot" else INF
    return float(value)


def _num(x: float) -> str:
    """A number as Bellman-SYM reads it: the shortest decimal that reads back to the same double, or inf."""
    x = float(x)
    if math.isinf(x):
        return "inf" if x > 0 else "-inf"
    return repr(x)


def _phi(z: float) -> float:
    """The standard normal density, zero at an infinite argument."""
    if math.isinf(z):
        return 0.0
    return math.exp(-0.5 * z * z) / math.sqrt(2.0 * math.pi)


def _Phi(z: float) -> float:
    return float(ndtr(z))


def _log_mass_between(lo: float, hi: float) -> float:
    """log(Phi(hi) - Phi(lo)), computed in whichever tail keeps the difference from cancelling."""
    if lo > 0:
        a, b = float(log_ndtr(-lo)), float(log_ndtr(-hi))
    else:
        a, b = float(log_ndtr(hi)), float(log_ndtr(lo))
    return a + math.log1p(-math.exp(b - a)) if b > -INF else a


def _log_power_integral(q0: float, q1: float, k: float) -> float:
    """log of the integral of q^k from q0 to q1, for 0 < q0 < q1."""
    if k == -1:
        return math.log(math.log(q1 / q0))
    if k + 1 > 0:
        return (k + 1) * math.log(q1) + math.log1p(-((q0 / q1) ** (k + 1))) - math.log(k + 1)
    return (k + 1) * math.log(q0) + math.log1p(-((q1 / q0) ** (k + 1))) - math.log(-(k + 1))


class _TruncatedNormalInLogs:
    """ln X = location + scale * Z, with Z standard normal conditioned on bot <= Z <= top.

    `sd_log` and `mean_log` are the standard deviation and the mean of ln X after truncation; `scale` and `location`
    are those of the normal before it. An infinite bound is no bound.
    """

    def __init__(self, sd_log: float, bot: float, top: float):
        self.bot, self.top = bot, top
        self.mass = _Phi(top) - _Phi(bot)
        ez = (_phi(bot) - _phi(top)) / self.mass
        # z * phi(z) vanishes at an infinite bound; written out so that -inf * 0 does not become NaN.
        bot_term = 0.0 if math.isinf(bot) else bot * _phi(bot)
        top_term = 0.0 if math.isinf(top) else top * _phi(top)
        var = 1.0 + (bot_term - top_term) / self.mass - ez * ez
        self.ez = ez
        self.scale = sd_log / math.sqrt(var)
        self.location = 0.0

    def log_mgf_at_location_zero(self, k: float) -> float:
        """log E[exp(k * scale * Z)] under the truncation, stable for any k."""
        s = self.scale
        return 0.5 * k * k * s * s + _log_mass_between(self.bot - k * s, self.top - k * s) - math.log(self.mass)

    def log_mgf(self, k: float) -> float:
        return k * self.location + self.log_mgf_at_location_zero(k)

    def mgf(self, k: float) -> float:
        return math.exp(self.log_mgf(k))

    def mgf_derivative(self, k: float) -> float:
        """d/dk E[exp(k (location + scale Z))]."""
        s = self.scale
        tail = math.exp(k * self.location + 0.5 * k * k * s * s) / self.mass
        return self.mgf(k) * (self.location + k * s * s) + tail * s * (_phi(self.bot - k * s) - _phi(self.top - k * s))

    def mean(self) -> float:
        return self.location + self.scale * self.ez

    def lower(self) -> float:
        return -INF if math.isinf(self.bot) else self.location + self.scale * self.bot

    def upper(self) -> float:
        return INF if math.isinf(self.top) else self.location + self.scale * self.top


# How a law behaves at the lowest value of its support, which the lower tail of the stationary distribution inherits:
# "atom", a point mass there; "density", a positive finite density there; "thin", a density that vanishes faster than any
# power (a lognormal at zero).
FLOOR_ATOM, FLOOR_DENSITY, FLOOR_THIN = "atom", "density", "thin"


class Degenerate:
    name = "Degenerate"
    ontology = "PD_0000025"  # the point mass at one, chart degenerate

    def __init__(self, params: dict):
        self.params = params

    def check(self):
        return [] if self.params == {} else ["Degenerate takes no parameters"]

    def moment(self, k):
        return 1.0

    def log_moment(self, k):
        return 0.0

    mean_log = 0.0
    mean_x_log_x = 0.0
    infimum = 1.0
    supremum = 1.0
    mass_at_infimum = 1.0
    floor_kind = FLOOR_ATOM

    def bellman(self):
        return "LogNormal(0, 0)"


class TruncatedLogNormal:
    """Also serves LogNormal, with no bound on either side."""

    name = "TruncatedLogNormal"
    ontology = "PD_0000032"  # the truncated lognormal with mean one, chart sd-log-standardized-bounds

    def __init__(self, params: dict, require_bound: bool = True):
        self.params = params
        self.require_bound = require_bound
        sd_log = params["sd_log"]
        self.bot = _bound(params, "bot")
        self.top = _bound(params, "top")
        if sd_log > 0 and self.bot < self.top:
            self.normal = _TruncatedNormalInLogs(sd_log, self.bot, self.top)
            self.normal.location = -self.normal.log_mgf_at_location_zero(1.0)

    def check(self):
        problems = []
        if self.params["sd_log"] <= 0:
            problems.append("sd_log must be positive")
        if self.require_bound and math.isinf(self.bot) and math.isinf(self.top):
            problems.append("a lognormal with no bound on either side is LogNormal")
        if not self.bot < self.top:
            problems.append("bot must be below top")
        return problems

    def moment(self, k):
        return self.normal.mgf(k)

    def log_moment(self, k):
        return self.normal.log_mgf(k)

    @property
    def mean_log(self):
        return self.normal.mean()

    @property
    def mean_x_log_x(self):
        return self.normal.mgf_derivative(1.0)

    @property
    def infimum(self):
        low = self.normal.lower()
        return 0.0 if math.isinf(low) else math.exp(low)

    @property
    def supremum(self):
        high = self.normal.upper()
        return INF if math.isinf(high) else math.exp(high)

    mass_at_infimum = 0.0

    @property
    def floor_kind(self):
        return FLOOR_THIN if math.isinf(self.bot) else FLOOR_DENSITY

    def bellman(self):
        """TruncatedLogNormal(μ, σ, l, u): the normal's location and scale in logs, and the bounds in the draw's units."""
        n = self.normal
        return f"TruncatedLogNormal({_num(n.location)}, {_num(n.scale)}, {_num(self.infimum)}, {_num(self.supremum)})"


class LogNormal(TruncatedLogNormal):
    name = "LogNormal"
    ontology = "PD_0000019"  # the lognormal with mean one, chart sd-log

    def __init__(self, params: dict):
        super().__init__({"sd_log": params["sd_log"], "bot": None, "top": None}, require_bound=False)
        self.params = params

    def bellman(self):
        sd = self.params["sd_log"]
        return f"LogNormal({_num(-sd * sd / 2)}, {_num(sd)})"


class Uniform:
    name = "Uniform"
    ontology = "PD_0000037"  # the uniform with mean one, chart half-width

    def __init__(self, params: dict):
        self.params = params
        self.w = params["half_width"]

    def check(self):
        return [] if 0 < self.w < 1 else ["half_width must lie strictly between 0 and 1"]

    def log_moment(self, k):
        a, b, w = 1 - self.w, 1 + self.w, self.w
        return _log_power_integral(a, b, k) - math.log(2 * w)

    def moment(self, k):
        return math.exp(self.log_moment(k))

    @property
    def mean_log(self):
        a, b, w = 1 - self.w, 1 + self.w, self.w
        return (b * math.log(b) - a * math.log(a) - 2 * w) / (2 * w)

    @property
    def mean_x_log_x(self):
        a, b, w = 1 - self.w, 1 + self.w, self.w
        F = lambda x: x * x / 2 * math.log(x) - x * x / 4
        return (F(b) - F(a)) / (2 * w)

    @property
    def infimum(self):
        return 1 - self.w

    @property
    def supremum(self):
        return 1 + self.w

    mass_at_infimum = 0.0
    floor_kind = FLOOR_DENSITY

    def bellman(self):
        return f"Uniform({_num(1 - self.w)}, {_num(1 + self.w)})"


class Discrete:
    name = "Discrete"
    ontology = "PD_0000045"  # the finite discrete law with mean one, chart values-probabilities

    def __init__(self, params: dict):
        self.params = params
        self.values = list(params["values"])
        self.probs = list(params["probs"])

    def check(self):
        problems = []
        if len(self.values) != len(self.probs):
            problems.append("values and probs must have the same length")
            return problems
        if len(self.values) < 2:
            problems.append("at least two values; one value is Degenerate")
        if any(v <= 0 for v in self.values):
            problems.append("values must be positive")
        if any(b <= a for a, b in zip(self.values, self.values[1:])):
            problems.append("values must be strictly increasing")
        if any(p <= 0 for p in self.probs):
            problems.append("probs must be positive")
        if abs(sum(self.probs) - 1) > TOLERANCE:
            problems.append(f"probs sum to {sum(self.probs)!r}, not 1")
        mean = sum(p * v for p, v in zip(self.probs, self.values))
        if abs(mean - 1) > TOLERANCE:
            problems.append(f"the mean is {mean!r}, not 1")
        return problems

    def log_moment(self, k):
        return float(logsumexp([math.log(p) + k * math.log(v) for p, v in zip(self.probs, self.values)]))

    def moment(self, k):
        return sum(p * v ** k for p, v in zip(self.probs, self.values))

    @property
    def mean_log(self):
        return sum(p * math.log(v) for p, v in zip(self.probs, self.values))

    @property
    def mean_x_log_x(self):
        return sum(p * v * math.log(v) for p, v in zip(self.probs, self.values))

    @property
    def infimum(self):
        return self.values[0]

    @property
    def supremum(self):
        return self.values[-1]

    @property
    def mass_at_infimum(self):
        return self.probs[0]

    floor_kind = FLOOR_ATOM

    def bellman(self):
        """A Mixture of numbers, each a point mass."""
        return "Mixture(" + ", ".join(f"({_num(p)}, {_num(v)})" for p, v in zip(self.probs, self.values)) + ")"


class _MixtureInLogs:
    """ln X = c + Y, Y drawn from component j with probability weight_j: a normal in logs, truncated or not, stated by
    its mean and standard deviation after truncation, with one common shift c making the mean one."""

    truncated = False

    def __init__(self, params: dict):
        self.params = params
        self.components = params["components"]
        self.bounds = [(_bound(c, "bot"), _bound(c, "top")) if self.truncated else (-INF, INF) for c in self.components]
        self.normals = []
        for c, (bot, top) in zip(self.components, self.bounds):
            if c["sd_log"] > 0 and bot < top:
                n = _TruncatedNormalInLogs(c["sd_log"], bot, top)
                n.location = c["mean_log"] - n.scale * n.ez
                self.normals.append(n)
        self.weights = [c["weight"] for c in self.components]
        if len(self.normals) == len(self.components):
            self.shift = -math.log(sum(w * n.mgf(1.0) for w, n in zip(self.weights, self.normals)))

    def _order_key(self, c, bounds):
        return (c["mean_log"], c["sd_log"])

    def check(self):
        problems = []
        if len(self.components) < 2:
            problems.append("at least two components; one component is LogNormal or TruncatedLogNormal")
        for i, (c, (bot, top)) in enumerate(zip(self.components, self.bounds)):
            if c["sd_log"] <= 0:
                problems.append(f"component {i}: sd_log must be positive")
            if not bot < top:
                problems.append(f"component {i}: bot must be below top")
            if c["weight"] <= 0:
                problems.append(f"component {i}: weight must be positive")
        if abs(sum(self.weights) - 1) > TOLERANCE:
            problems.append(f"weights sum to {sum(self.weights)!r}, not 1")
        centered = sum(c["weight"] * c["mean_log"] for c in self.components)
        if abs(centered) > TOLERANCE:
            problems.append(f"the weighted mean of mean_log is {centered!r}, not 0")
        keys = [self._order_key(c, b) for c, b in zip(self.components, self.bounds)]
        if any(b <= a for a, b in zip(keys, keys[1:])):
            problems.append(self.order_rule)
        return problems

    def log_moment(self, k):
        return k * self.shift + float(logsumexp([math.log(w) + n.log_mgf(k) for w, n in zip(self.weights, self.normals)]))

    def moment(self, k):
        return math.exp(self.log_moment(k))

    @property
    def mean_log(self):
        return self.shift + sum(w * n.mean() for w, n in zip(self.weights, self.normals))

    @property
    def mean_x_log_x(self):
        inner = sum(w * n.mgf(1.0) for w, n in zip(self.weights, self.normals))
        inner_derivative = sum(w * n.mgf_derivative(1.0) for w, n in zip(self.weights, self.normals))
        return math.exp(self.shift) * (self.shift * inner + inner_derivative)

    @property
    def infimum(self):
        low = min(n.lower() for n in self.normals)
        return 0.0 if math.isinf(low) else math.exp(self.shift + low)

    @property
    def supremum(self):
        high = max(n.upper() for n in self.normals)
        return INF if math.isinf(high) else math.exp(self.shift + high)

    mass_at_infimum = 0.0

    @property
    def floor_kind(self):
        return FLOOR_THIN if any(math.isinf(n.lower()) for n in self.normals) else FLOOR_DENSITY

    def bellman(self):
        """A Mixture of each component's law: LogNormal(μ, σ), or TruncatedLogNormal(μ, σ, l, u) for a component with a
        bound, μ including the common shift."""
        parts = []
        for w, n, (bot, top) in zip(self.weights, self.normals, self.bounds):
            mu, sigma = self.shift + n.location, n.scale
            if math.isinf(bot) and math.isinf(top):
                law = f"LogNormal({_num(mu)}, {_num(sigma)})"
            else:
                low = 0.0 if math.isinf(bot) else math.exp(mu + sigma * bot)
                high = INF if math.isinf(top) else math.exp(mu + sigma * top)
                law = f"TruncatedLogNormal({_num(mu)}, {_num(sigma)}, {_num(low)}, {_num(high)})"
            parts.append(f"({_num(w)}, {law})")
        return "Mixture(" + ", ".join(parts) + ")"


class LogNormalMixture(_MixtureInLogs):
    name = "LogNormalMixture"
    ontology = "PD_0000054"  # the lognormal mixture with mean one, chart relative-means
    order_rule = "components must be in increasing order of mean_log, then sd_log, with no repeat"


class TruncatedLogNormalMixture(_MixtureInLogs):
    name = "TruncatedLogNormalMixture"
    ontology = "PD_0000058"  # the truncated lognormal mixture with mean one, chart relative-means-standardized-bounds
    truncated = True
    order_rule = "components must be in increasing order of mean_log, then sd_log, bot and top, with no repeat"

    def _order_key(self, c, bounds):
        return (c["mean_log"], c["sd_log"], *bounds)

    def check(self):
        problems = super().check()
        if all(math.isinf(bot) and math.isinf(top) for bot, top in self.bounds):
            problems.append("no component has a bound: the law is LogNormalMixture")
        return problems


class Tabulated:
    """A quantile function Q, linear in u between the listed points."""

    name = "Tabulated"
    ontology = "PD_0000063"  # the quantile table with mean one, chart points

    def __init__(self, params: dict):
        self.params = params
        self.points = [(float(u), float(q)) for u, q in params["points"]]

    def check(self):
        pts = self.points
        problems = []
        us = [u for u, _ in pts]
        qs = [q for _, q in pts]
        if us[0] != 0.0 or us[-1] != 1.0:
            problems.append("the first u must be 0 and the last 1")
        if len(pts) > 1 and (us[1] == 0.0 or us[-2] == 1.0):
            problems.append("u = 0 and u = 1 may not be repeated")
        if any(b < a for a, b in zip(us, us[1:])):
            problems.append("u must never fall")
        for i in range(1, len(us) - 1):
            if us[i] == us[i - 1] and i >= 2 and us[i] == us[i - 2]:
                problems.append(f"u = {us[i]!r} appears more than twice")
        if any(b < a for a, b in zip(qs, qs[1:])):
            problems.append("Q must never fall")
        if qs[0] <= 0:
            problems.append("the first Q must be positive")
        rising = [i for i in range(len(pts) - 1) if us[i + 1] > us[i] and qs[i + 1] > qs[i]]
        if not rising:
            problems.append("no stretch where both u and Q rise: a table of steps is Discrete")
        if len(pts) == 2:
            problems.append("a single rising stretch is Uniform")
        for i in range(1, len(pts) - 1):
            u0, q0 = pts[i - 1]
            u1, q1 = pts[i]
            u2, q2 = pts[i + 1]
            if u0 < u1 < u2:
                left = (Fraction(u1) - Fraction(u0)) * (Fraction(q2) - Fraction(q1))
                right = (Fraction(q1) - Fraction(q0)) * (Fraction(u2) - Fraction(u1))
                if left == right:
                    problems.append(f"point {i} lies exactly on the line through its neighbors")
        mean = sum((u1 - u0) * (q0 + q1) / 2 for (u0, q0), (u1, q1) in zip(pts, pts[1:]))
        if abs(mean - 1) > TOLERANCE:
            problems.append(f"the mean is {mean!r}, not 1")
        return problems

    def _expect(self, f_point, f_integral):
        """E[f(X)] from f at a point mass and the antiderivative F of f on a rising stretch."""
        total = 0.0
        for (u0, q0), (u1, q1) in zip(self.points, self.points[1:]):
            du = u1 - u0
            if du == 0:
                continue
            if q1 == q0:
                total += du * f_point(q0)
            else:
                total += du / (q1 - q0) * (f_integral(q1) - f_integral(q0))
        return total

    def log_moment(self, k):
        terms = []
        for (u0, q0), (u1, q1) in zip(self.points, self.points[1:]):
            du = u1 - u0
            if du == 0:
                continue
            if q1 == q0:
                terms.append(math.log(du) + k * math.log(q0))
            else:
                terms.append(math.log(du) - math.log(q1 - q0) + _log_power_integral(q0, q1, k))
        return float(logsumexp(terms))

    def moment(self, k):
        return math.exp(self.log_moment(k))

    @property
    def mean_log(self):
        return self._expect(math.log, lambda q: q * math.log(q) - q)

    @property
    def mean_x_log_x(self):
        return self._expect(lambda q: q * math.log(q), lambda q: q * q / 2 * math.log(q) - q * q / 4)

    @property
    def infimum(self):
        return self.points[0][1]

    @property
    def supremum(self):
        return self.points[-1][1]

    @property
    def mass_at_infimum(self):
        (u0, q0), (u1, q1) = self.points[0], self.points[1]
        return u1 - u0 if q1 == q0 else 0.0

    @property
    def floor_kind(self):
        return FLOOR_ATOM if self.mass_at_infimum > 0 else FLOOR_DENSITY

    def bellman(self):
        return None  # Bellman-SYM has no quantile table


LAWS = {cls.name: cls for cls in (Degenerate, LogNormal, TruncatedLogNormal, Uniform, Discrete, LogNormalMixture,
                                  TruncatedLogNormalMixture, Tabulated)}


def filled(value):
    """The value with every omitted truncation bound written in, wherever a law that takes bounds appears: the form the
    hash is taken over. A null bound stays null."""
    if isinstance(value, dict):
        if len(value) == 1 and next(iter(value)) in ("TruncatedLogNormal", "TruncatedLogNormalMixture"):
            (name, params), = value.items()
            if isinstance(params, dict):
                if name == "TruncatedLogNormal":
                    return {name: {"bot": -DEFAULT_BOUND, "top": DEFAULT_BOUND, **params}}
                if isinstance(params.get("components"), list):
                    return {name: {**params, "components": [
                        {"bot": -DEFAULT_BOUND, "top": DEFAULT_BOUND, **c} if isinstance(c, dict) else c
                        for c in params["components"]]}}
        return {key: filled(item) for key, item in value.items()}
    if isinstance(value, list):
        return [filled(item) for item in value]
    return value


def law_from_mapping(mapping: dict):
    """The law object for a single-key mapping such as {"LogNormal": {"sd_log": 0.1}}."""
    if not isinstance(mapping, dict) or len(mapping) != 1:
        raise ValueError("a law is a mapping with one key, the law's name")
    (name, params), = mapping.items()
    if name not in LAWS:
        raise ValueError(f"unknown or reserved law {name!r}")
    return LAWS[name](params)
