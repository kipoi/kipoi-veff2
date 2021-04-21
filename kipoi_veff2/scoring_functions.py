from typing import Any, List
import warnings

import numpy as np

AVAILABLE_SCORING_FUNCTIONS = [
    "diff",
    "logit",
    "logitalt",
    "logitref",
    "deepsea_effect",
]


def diff(ref_pred: Any, alt_pred: Any) -> List:
    # For DeepBind - TODO: Cleaner code
    if alt_pred.size == 1 and ref_pred.size == 1:
        return [alt_pred - ref_pred]
    else:
        return list(alt_pred - ref_pred)


def logit(ref_pred: Any, alt_pred: Any) -> List:
    preds = {"ref": ref_pred, "alt": alt_pred}
    if np.any([(preds[k].min() < 0 or preds[k].max() > 1) for k in preds]):
        warnings.warn(
            "Using log_odds on model outputs that are not bound [0,1]"
        )
    diffs = np.log(preds["alt"] / (1 - preds["alt"])) - np.log(
        preds["ref"] / (1 - preds["ref"])
    )
    if diffs.size == 1:
        diffs = [diffs]
    return diffs


def logitalt(ref_pred: Any, alt_pred: Any) -> List:
    preds = {"ref": ref_pred, "alt": alt_pred}
    # TODO: Should it be checking only alt_pred?
    if np.any([(preds[k].min() < 0 or preds[k].max() > 1) for k in preds]):
        warnings.warn(
            "Using log_odds on model outputs that are not bound [0,1]"
        )
    logits = np.log(preds["alt"] / (1 - preds["alt"]))

    if logits.size == 1:
        logits = [logits]
    return logits


def logitref(ref_pred: Any, alt_pred: Any) -> List:
    preds = {"ref": ref_pred, "alt": alt_pred}
    # TODO: Should it be checking only ref_pred?
    if np.any([(preds[k].min() < 0 or preds[k].max() > 1) for k in preds]):
        warnings.warn(
            "Using log_odds on model outputs that are not bound [0,1]"
        )
    logits = np.log(preds["ref"] / (1 - preds["ref"]))

    if logits.size == 1:
        logits = [logits]
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
    if scores.size == 1:
        scores = [scores]
    return scores
