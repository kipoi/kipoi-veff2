import click

import kipoi
from kipoi_veff2 import variant_centered


def validate_model(ctx, param, model):
    """[This is a callback for validation of requested model w.r.t AVAILABLE_MODELS]

    Args:
        ctx ([click.Context]): [Current context]
        param ([click.Parameter]): [The parameters to register with this command - Options in this case]
        model ([Tuple]): [Model of interest]

    Raises:
        click.BadParameter: [An exception that formats out a standardized error message for a bad parameter
        if there are no model to score variants with]

    Returns:
        [str]: [Name of the model to score variant with]
    """
    model = model[0]
    if model not in variant_centered.MODELS.keys():
        print(
            f"Removing {model} as it is not supported. \
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
@click.argument("output_vcf", required=True)
@click.option(
    "-m",
    "--model",
    required=True,
    type=str,
    multiple=True,
    callback=validate_model,
    help="Run variant effect prediction using this model. \
        Example: python kipoi_veff2/cli.py in.vcf in.fa out.vcf -m 'Basenji' ",
)
def score_variants(input_vcf, input_fasta, output_vcf, model):
    """Perform variant effect prediction with the INPUT_VCF and INPUT_FASTA files using the MODELS and write them to OUTPUT_VCF"""
    click.echo(
        f"input_vcf = {input_vcf}, input_fasta = {input_fasta}, output_vcf = {output_vcf}, model={model}"
    )
    model_config = variant_centered.MODELS[model]
    scores = variant_centered.score_variants(
        model_config, input_vcf, input_fasta, output_vcf
    )
    click.echo(f"scores = {scores[0].size}")


if __name__ == "__main__":
    score_variants()
