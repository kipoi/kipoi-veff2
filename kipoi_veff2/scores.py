from typing import Any, List
import warnings

import numpy as np

AVAILABLE_SCORING_FUNCTIONS = [
    "diff",
    "alt",
    "ref",
    "logit",
    "logit_alt",
    "logit_ref",
    "deepsea_effect",
]


def diff(ref_pred: Any, alt_pred: Any) -> List:
    """Returns the difference between alternative and
    reference prediction. This is the default scoring
    function of all variant centered model groups except
    Basenji"""
    return alt_pred - ref_pred


def ref(ref_pred: Any, alt_pred: Any) -> List:
    """Returns reference predictions"""
    return ref_pred


def alt(ref_pred: Any, alt_pred: Any) -> List:
    """Returns altenrative predictions"""
    return alt_pred


def logit(ref_pred: Any, alt_pred: Any) -> List:
    """Returns ln(A/(1 - A)) - ln(R/(1 - R)"""
    preds = {"ref": ref_pred, "alt": alt_pred}
    if np.any([(preds[k].min() < 0 or preds[k].max() > 1) for k in preds]):
        warnings.warn(
            "Using log_odds on model outputs that are not bound [0,1]"
        )
    diffs = np.log(preds["alt"] / (1 - preds["alt"])) - np.log(
        preds["ref"] / (1 - preds["ref"])
    )
    return diffs


def logit_alt(ref_pred: Any, alt_pred: Any) -> List:
    """Returns ln(A/(1- A))"""
    preds = {"ref": ref_pred, "alt": alt_pred}
    # TODO: Should it be checking only alt_pred?
    if np.any([(preds[k].min() < 0 or preds[k].max() > 1) for k in preds]):
        warnings.warn(
            "Using log_odds on model outputs that are not bound [0,1]"
        )
    logits = np.log(preds["alt"] / (1 - preds["alt"]))
    return logits


def logit_ref(ref_pred: Any, alt_pred: Any) -> List:
    """Returns ln(R/(1- R))"""
    preds = {"ref": ref_pred, "alt": alt_pred}
    # TODO: Should it be checking only ref_pred?
    if np.any([(preds[k].min() < 0 or preds[k].max() > 1) for k in preds]):
        warnings.warn(
            "Using log_odds on model outputs that are not bound [0,1]"
        )
    logits = np.log(preds["ref"] / (1 - preds["ref"]))
    return logits


def deepsea_effect(ref_pred: Any, alt_pred: Any) -> List:
    """Returns the score used by DeepSEA in order to calculate the e-value:
    `abs(logit_diff) * abs(diff)`"""
    preds = {"ref": ref_pred, "alt": alt_pred}
    if np.any([(preds[k].min() < 0 or preds[k].max() > 1) for k in preds]):
        warnings.warn(
            "Using log_odds on model outputs that are not bound [0,1]"
        )
    logit_diffs = np.log(preds["alt"] / (1 - preds["alt"])) - np.log(
        preds["ref"] / (1 - preds["ref"])
    )
    diffs = preds["alt"] - preds["ref"]
    scores = np.abs(logit_diffs) * np.abs(diffs)
    return scores
