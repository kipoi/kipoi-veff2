import numpy as np
from scipy.special import logit

from kipoi_veff2 import scores


def test_diff():
    ref_pred = np.linspace(0.5, 1, 5)
    alt_pred = np.linspace(0.1, 0.5, 5)
    assert np.all(scores.diff(ref_pred, alt_pred) == (alt_pred - ref_pred))


def test_ref():
    ref_pred = np.linspace(0.5, 1, 5)
    alt_pred = np.linspace(0.1, 0.5, 5)
    assert np.all(scores.ref(ref_pred, alt_pred) == ref_pred)


def test_alt():
    ref_pred = np.linspace(0.5, 1, 5)
    alt_pred = np.linspace(0.1, 0.5, 5)
    assert np.all(scores.alt(ref_pred, alt_pred) == alt_pred)


def test_logit():
    ref_pred = np.array([0.1, 0.2, 0.3])
    alt_pred = np.array([0.2, 0.25, 0.5])
    assert np.all(
        (scores.logit(ref_pred, alt_pred) == logit(alt_pred) - logit(ref_pred))
    )


def test_logit_alt():
    ref_pred = np.array([0.1, 0.2, 0.3])
    alt_pred = np.array([0.2, 0.25, 0.5])
    assert np.all((scores.logit_alt(ref_pred, alt_pred) == logit(alt_pred)))


def test_logit_ref():
    ref_pred = np.array([0.1, 0.2, 0.3])
    alt_pred = np.array([0.2, 0.25, 0.5])
    assert np.all((scores.logit_ref(ref_pred, alt_pred) == logit(ref_pred)))


def test_deepseaeffect():
    ref_pred = np.array([0.1, 0.2, 0.3])
    alt_pred = np.array([0.2, 0.25, 0.5])
    assert np.all(
        (
            scores.deepsea_effect(ref_pred, alt_pred)
            == np.abs(logit(alt_pred) - logit(ref_pred))
            * np.abs(alt_pred - ref_pred)
        )
    )


def test_diff_single():
    ref_pred = np.array(0.5)
    alt_pred = np.array(0.8)
    assert np.all(scores.diff(ref_pred, alt_pred) == (alt_pred - ref_pred))


def test_logit_single():
    ref_pred = np.array(0.8)
    alt_pred = np.array(0.4)
    assert np.all(
        scores.logit(ref_pred, alt_pred) == logit(alt_pred) - logit(ref_pred)
    )


def test_logit_alt_single():
    ref_pred = np.array(0.8)
    alt_pred = np.array(0.4)
    assert np.all((scores.logit_alt(ref_pred, alt_pred) == logit(alt_pred)))


def test_logit_ref_single():
    ref_pred = np.array(0.8)
    alt_pred = np.array(0.4)
    assert np.all((scores.logit_ref(ref_pred, alt_pred) == logit(ref_pred)))


def test_deepseaeffect_single():
    ref_pred = np.array(0.8)
    alt_pred = np.array(0.4)
    assert np.all(
        (
            scores.deepsea_effect(ref_pred, alt_pred)
            == np.abs(logit(alt_pred) - logit(ref_pred))
            * np.abs(alt_pred - ref_pred)
        )
    )
