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
    return alt_pred - ref_pred


def ref(ref_pred: Any, alt_pred: Any) -> List:
    return ref_pred


def alt(ref_pred: Any, alt_pred: Any) -> List:
    return alt_pred


def logit(ref_pred: Any, alt_pred: Any) -> List:
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
    preds = {"ref": ref_pred, "alt": alt_pred}
    # TODO: Should it be checking only alt_pred?
    if np.any([(preds[k].min() < 0 or preds[k].max() > 1) for k in preds]):
        warnings.warn(
            "Using log_odds on model outputs that are not bound [0,1]"
        )
    logits = np.log(preds["alt"] / (1 - preds["alt"]))
    return logits


def logit_ref(ref_pred: Any, alt_pred: Any) -> List:
    preds = {"ref": ref_pred, "alt": alt_pred}
    # TODO: Should it be checking only ref_pred?
    if np.any([(preds[k].min() < 0 or preds[k].max() > 1) for k in preds]):
        warnings.warn(
            "Using log_odds on model outputs that are not bound [0,1]"
        )
    logits = np.log(preds["ref"] / (1 - preds["ref"]))
    return logits


def deepsea_effect(ref_pred: Any, alt_pred: Any) -> List:
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


def basenji_effect(ref_pred: Any, alt_pred: Any) -> List:
    return (alt_pred - ref_pred).mean(axis=0)
