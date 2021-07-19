import click
import importlib
from typing import Any, Callable, Dict, List, Optional

from kipoi_veff2 import interval_based
from kipoi_veff2 import scores
from kipoi_veff2 import variant_centered

ScoringFunction = Callable[[Any, Any], List]


def validate_model(
    ctx: click.Context, param: click.Parameter, model: str
) -> str:
    """[This is a callback for validation of requested model w.r.t
        variant_centered.MODEL_GROUPS and interval_based.MODEL_GROUPS]
    Raises:
        click.BadParameter: [An exception that formats
        out a standardized error message for a bad parameter
        if there are no model to score variants with]
    """
    model_group = model.split("/")[0]
    if (
        model_group in variant_centered.MODEL_GROUPS
        or model_group in interval_based.MODEL_GROUPS
    ):
        return model
    else:
        print(
            f"Removing {model_group} as it is not supported. \
            Please consult the documentation"
        )
        raise click.BadParameter(
            "Please select atleast one supported model group."
        )


def validate_scoring_function(
    ctx: click.Context, param: click.Parameter, scoring_function: tuple
) -> List[Dict[str, ScoringFunction]]:
    """[This is a callback for validation of scoring functions w.r.t
        scores.AVAILABLE_SCORING_FUNCTIONS]
    Raises:
        click.BadParameter: [An exception that formats
        out a standardized error message for a bad parameter
        if there are no scoring function]"""
    scoring_functions = []
    for scoring_function_name in list(scoring_function):
        if scoring_function_name not in scores.AVAILABLE_SCORING_FUNCTIONS:
            print(
                f"Removing {scoring_function_name} as it is not supported. \
                  Please consult the documentation"
            )
        else:
            func_def = f"kipoi_veff2.scores.{scoring_function_name}"
            mod_name, func_name = func_def.rsplit(".", 1)
            mod = importlib.import_module(mod_name)
            func = getattr(mod, func_name)
            scoring_functions.append(
                {"name": scoring_function_name, "func": func}
            )

    if (
        list(scoring_function) and not scoring_functions
    ):  # For variant centered models
        raise click.BadParameter(
            "Please select atleast one available scoring function."
        )
    return scoring_functions


@click.command()
@click.argument(
    "input_vcf", required=True, type=click.Path(exists=True, readable=True)
)
@click.argument(
    "input_fasta", required=True, type=click.Path(exists=True, readable=True)
)
@click.option(
    "-g", "--gtf", "input_gtf", type=click.Path(exists=True, readable=True)
)
@click.option(
    "-l", "--seq-length", "sequence_length", default=None, type=int
)  # TODO: A validation function for checking if it is a positive int?
@click.argument("output_tsv", required=True)
@click.option(
    "-m",
    "--model",
    required=True,
    type=str,
    callback=validate_model,
    help="Run variant effect prediction using this model. \
        Example (Variant centered): python kipoi_veff2/cli.py in.vcf in.fa \
                 out.tsv -m Basset -s diff\
        Example (Interval based): python kipoi_veff2/cli.py in.vcf in.fa\
                -g in.gtf -m 'MMSplice/modularPredictions' out.tsv",
)
@click.option(
    "-s",
    "--scoring_function",
    required=False,
    multiple=True,
    type=str,
    callback=validate_scoring_function,
    help="Use this function to score \
        Example (variant centered only): python kipoi_veff2/cli.py \
                 in.vcf in.fa out.tsv -m Basset \
                 -s diff -s logit. \
        For interval based models scoring functions are redundant as\
        the model perform the scoring as part of prediction",
)
def score_variants(
    input_vcf: click.Path,
    input_fasta: click.Path,
    input_gtf: Optional[click.Path],
    sequence_length: Optional[int],
    output_tsv: str,
    model: str,
    scoring_function: List[Dict[str, ScoringFunction]],
) -> None:
    """Perform variant effect prediction with the INPUT_VCF and INPUT_FASTA
    files using the MODELS and write them to OUTPUT_TSV"""
    model_group = model.split("/")[0]
    if model_group in variant_centered.MODEL_GROUPS:
        model_group_config_dict = (
            variant_centered.VARIANT_CENTERED_MODEL_GROUP_CONFIGS.get(
                model_group, {}
            )
        )
        if sequence_length is not None:
            # None is to match the value we use in
            # get_required_sequence_length
            model_group_config_dict[
                "required_sequence_length"
            ] = sequence_length
        model_config = variant_centered.get_model_config(
            model_name=model, **model_group_config_dict
        )
        if sequence_length is not None:
            assert (
                getattr(model_config, "required_sequence_length")
                == sequence_length
            )  # TODO: write a meaningful test
        click.echo(model_config)
        variant_centered.score_variants(
            model_config, input_vcf, input_fasta, output_tsv, scoring_function
        )
    elif model_group in interval_based.MODEL_GROUPS:
        model_config = interval_based.INTERVAL_BASED_MODEL_CONFIGS[
            model
        ]  # TODO; Use .get here?
        interval_based.score_variants(
            model_config, input_vcf, input_fasta, input_gtf, output_tsv
        )


if __name__ == "__main__":
    score_variants()
