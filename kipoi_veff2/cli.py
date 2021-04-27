import click
import importlib
from typing import Any, Callable, Dict, List

from kipoi_veff2 import scores
from kipoi_veff2 import variant_centered

ScoringFunction = Callable[[Any, Any], List]


def validate_model(
    ctx: click.Context, param: click.Parameter, model: str
) -> str:
    """[This is a callback for validation of requested model w.r.t
        variant_centered.MODEL_GROUPS]
    Raises:
        click.BadParameter: [An exception that formats
        out a standardized error message for a bad parameter
        if there are no model to score variants with]
    """
    model_group = model.split("/")[0]
    if model_group not in variant_centered.MODEL_GROUPS:
        print(
            f"Removing {model_group} as it is not supported. \
            Please consult the documentation"
        )
        raise click.BadParameter(
            f"Please select atleast one supported model group."
        )
    else:
        return model


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

    if not scoring_functions:
        raise click.BadParameter(
            f"Please select atleast one available scoring function."
        )
    return scoring_functions


@click.command()
@click.argument(
    "input_vcf", required=True, type=click.Path(exists=True, readable=True)
)
@click.argument(
    "input_fasta", required=True, type=click.Path(exists=True, readable=True)
)
@click.argument("output_tsv", required=True)
@click.option(
    "-m",
    "--model",
    required=True,
    type=str,
    callback=validate_model,
    help="Run variant effect prediction using this model. \
        Example: python kipoi_veff2/cli.py in.vcf in.fa \
                 out.tsv -m Basset -s diff",
)
@click.option(
    "-s",
    "--scoring_function",
    required=True,
    multiple=True,
    type=str,
    callback=validate_scoring_function,
    help="Use this function to score \
        Example: python kipoi_veff2/cli.py \
                 in.vcf in.fa out.tsv -m Basset \
                 -s diff -s logit",
)
def score_variants(
    input_vcf: click.Path,
    input_fasta: click.Path,
    output_tsv: str,
    model: str,
    scoring_function: List[Dict[str, ScoringFunction]],
) -> None:
    """Perform variant effect prediction with the INPUT_VCF and INPUT_FASTA
    files using the MODELS and write them to OUTPUT_TSV"""
    model_config = variant_centered.get_model_config(model_name=model)
    variant_centered.score_variants(
        model_config, input_vcf, input_fasta, output_tsv, scoring_function
    )


if __name__ == "__main__":
    score_variants()
