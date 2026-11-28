"""The tests of the jumpless truncated lognormal, the law shock-laws.md calls JumplessTruncatedLogNormal: its numbers
against HARK's, its closed forms against quadrature of the density it states, and the rules of its written form.

    uv run --project core --with pytest pytest -q core/tests

HARK's numbers are those of HARK.distributions.LogNormalTruncatedJumplessMeanOne.from_sd_log(sd_log, bot) at the tag
pin-buffer-stock-continuous-2026-11-25 of llorracc/HARK (aca90ba8), printed with repr and copied here, so that the
core's tests need no HARK.
"""

from __future__ import annotations

import math

import pytest
from scipy import integrate
from scipy.stats import norm

from wg1core.laws import FLOOR_LINEAR, LAWS, filled, law_from_mapping

TOLERANCE = 1e-13

# (sd_log, bot): HARK's sigma and mu, the infimum of its support, and its moment(k)
HARK = {
    (0.1, -3.0): (0.10112525005925814, -0.00582995231649257, 0.7340297627424461,
                  {2.0: 1.0100994156589491, -1.0: 1.0100492491448236, -2.0: 1.0303893059810971,
                   0.5: 0.9987475562895811, -4.0: 1.1044214351051067, 3.0: 1.0306467365170675}),
    (0.2, -2.0): (0.21876346531232807, -0.04121550527303182, 0.6195620410848565,
                  {2.0: 1.0429289342410593, -1.0: 1.0407818188451126, -2.0: 1.1247113086766811,
                   0.5: 0.9948794671086928, -4.0: 1.454455436642706, 3.0: 1.1363154890026825}),
    (0.05, -1.0): (0.06662219702163302, -0.0322275597216057, 0.9058787999809832,
                   {2.0: 1.0025749656947645, -1.0: 1.0025031831504703, -2.0: 1.007456894029768,
                    0.5: 0.9996830820822377, -4.0: 1.0245928631772148, 3.0: 1.0078174792151124}),
}


def jumpless(sd_log, bot=None):
    params = {"sd_log": sd_log} if bot is None else {"sd_log": sd_log, "bot": bot}
    return law_from_mapping({"JumplessTruncatedLogNormal": params})


def close(a, b, tolerance=TOLERANCE):
    return abs(a - b) <= tolerance * max(1.0, abs(a), abs(b))


@pytest.mark.parametrize("sd_log, bot", sorted(HARK))
def test_the_law_is_hark_s(sd_log, bot):
    sigma, mu, infimum, moments = HARK[(sd_log, bot)]
    law = jumpless(sd_log, bot)
    assert law.check() == []
    assert close(law.normal.scale, sigma) and close(law.normal.location, mu)
    assert close(law.infimum, infimum) and law.supremum == math.inf and law.mass_at_infimum == 0.0
    assert close(law.moment(1.0), 1.0)
    for k, value in moments.items():
        assert close(law.moment(k), value), k
        assert close(law.log_moment(k), math.log(value)), k


@pytest.mark.parametrize("sd_log, bot", [(0.1, -3.0), (0.2, -2.0), (0.05, -1.0), (0.3, -0.25)])
def test_the_closed_forms_are_the_density_s(sd_log, bot):
    """Every expectation the regularity conditions read, against quadrature of the density the law states: the
    standard normal density less its reflection in the bound."""
    law = jumpless(sd_log, bot)
    n = law.normal

    def expect(f):
        g = lambda z: f(n.location + n.scale * z) * (norm.pdf(z) - norm.pdf(2 * bot - z)) / n.mass
        near = integrate.quad(g, bot, bot + 1, epsabs=1e-16, epsrel=1e-13, limit=200)[0]
        return near + integrate.quad(g, bot + 1, 40.0, epsabs=1e-16, epsrel=1e-13, limit=200)[0]

    mean_log, second = expect(lambda y: y), expect(lambda y: y * y)
    assert close(expect(lambda y: 1.0), 1.0, 1e-12)
    assert close(math.sqrt(second - mean_log ** 2), sd_log, 1e-12)  # sd_log is the standard deviation of ln X
    assert close(mean_log, law.mean_log, 1e-12)
    assert close(expect(lambda y: math.exp(y) * y), law.mean_x_log_x, 1e-12)
    for k in (-3.0, -1.0, 0.5, 1.0, 2.0, 4.0):
        assert close(expect(lambda y: math.exp(k * y)), law.moment(k), 1e-12), k


def test_the_written_form():
    assert "JumplessTruncatedLogNormal" in LAWS
    assert filled({"JumplessTruncatedLogNormal": {"sd_log": 0.1}}) == {
        "JumplessTruncatedLogNormal": {"bot": -3.0, "sd_log": 0.1}}
    assert jumpless(0.1).moment(2.0) == jumpless(0.1, -3.0).moment(2.0)
    with_null = law_from_mapping({"JumplessTruncatedLogNormal": {"sd_log": 0.1, "bot": None}})
    assert with_null.check() == ["the bound may not be null: a lognormal with no bound is LogNormal"]
    assert jumpless(0.1, 0.0).check() == ["bot must be finite and below zero, the center of the normal"]
    assert jumpless(0.1, 0.5).check() == ["bot must be finite and below zero, the center of the normal"]
    assert jumpless(0.0).check() == ["sd_log must be positive"]
    with_top = law_from_mapping({"JumplessTruncatedLogNormal": {"sd_log": 0.1, "top": None}})
    assert with_top.check() == ["the law has no upper bound: top is not one of its fields"]


def test_the_floor_and_bellman():
    law = jumpless(0.1)
    assert law.floor_kind == FLOOR_LINEAR
    assert law.bellman() is None  # Bellman-SYM has no family for it
