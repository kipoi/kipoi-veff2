import numpy as np
from scipy.special import logit

from kipoi_veff2 import scoring_functions


def test_diff():
    ref_pred = np.linspace(0.5, 1, 5)
    alt_pred = np.linspace(0.1, 0.5, 5)
    assert np.all(
        scoring_functions.diff(ref_pred, alt_pred) == (alt_pred - ref_pred)
    )


def test_logit():
    ref_pred = np.array([0.1, 0.2, 0.3])
    alt_pred = np.array([0.2, 0.25, 0.5])
    assert np.all(
        (
            scoring_functions.logit(ref_pred, alt_pred)
            == logit(alt_pred) - logit(ref_pred)
        )
    )


def test_logitalt():
    ref_pred = np.array([0.1, 0.2, 0.3])
    alt_pred = np.array([0.2, 0.25, 0.5])
    assert np.all(
        (scoring_functions.logitalt(ref_pred, alt_pred) == logit(alt_pred))
    )


def test_logitref():
    ref_pred = np.array([0.1, 0.2, 0.3])
    alt_pred = np.array([0.2, 0.25, 0.5])
    assert np.all(
        (scoring_functions.logitref(ref_pred, alt_pred) == logit(ref_pred))
    )


def test_deepseaeffect():
    ref_pred = np.array([0.1, 0.2, 0.3])
    alt_pred = np.array([0.2, 0.25, 0.5])
    assert np.all(
        (
            scoring_functions.deepsea_effect(ref_pred, alt_pred)
            == np.abs(logit(alt_pred) - logit(ref_pred))
            * np.abs(alt_pred - ref_pred)
        )
    )


def test_diff_single():
    ref_pred = np.array(0.5)
    alt_pred = np.array(0.8)
    assert np.all(
        scoring_functions.diff(ref_pred, alt_pred) == (alt_pred - ref_pred)
    )


def test_logit_single():
    ref_pred = np.array(0.8)
    alt_pred = np.array(0.4)
    assert np.all(
        scoring_functions.logit(ref_pred, alt_pred)
        == logit(alt_pred) - logit(ref_pred)
    )


def test_logitalt_single():
    ref_pred = np.array(0.8)
    alt_pred = np.array(0.4)
    assert np.all(
        (scoring_functions.logitalt(ref_pred, alt_pred) == logit(alt_pred))
    )


def test_logitref_single():
    ref_pred = np.array(0.8)
    alt_pred = np.array(0.4)
    assert np.all(
        (scoring_functions.logitref(ref_pred, alt_pred) == logit(ref_pred))
    )


def test_deepseaeffect_single():
    ref_pred = np.array(0.8)
    alt_pred = np.array(0.4)
    assert np.all(
        (
            scoring_functions.deepsea_effect(ref_pred, alt_pred)
            == np.abs(logit(alt_pred) - logit(ref_pred))
            * np.abs(alt_pred - ref_pred)
        )
    )
