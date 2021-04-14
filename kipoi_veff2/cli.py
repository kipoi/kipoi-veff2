import click

from kipoi_veff2 import variant_centered


def validate_model(
    ctx: click.Context, param: click.Parameter, model: str
) -> str:
    """[This is a callback for validation of requested model w.r.t
        AVAILABLE_MODELS]
    Raises:
        click.BadParameter: [An exception that formats
        out a standardized error message for a bad parameter
        if there are no model to score variants with]
    """
    model_group = model.split("/")[0]
    if model_group not in variant_centered.MODELGROUPS:
        print(
            f"Removing {model_group} as it is not supported. \
            Please consult the documentation"
        )
        raise click.BadParameter(
            f"Please select atleast one supported model group."
        )
    else:
        return model


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
        Example: python kipoi_veff2/cli.py in.vcf in.fa out.tsv -m Basenji ",
)
def score_variants(
    input_vcf: click.Path, input_fasta: click.Path, output_tsv: str, model: str
) -> None:
    """Perform variant effect prediction with the INPUT_VCF and INPUT_FASTA
    files using the MODELS and write them to OUTPUT_TSV"""
    model_config = variant_centered.get_model_config(model_name=model)
    variant_centered.score_variants(
        model_config, input_vcf, input_fasta, output_tsv
    )


if __name__ == "__main__":
    score_variants()
