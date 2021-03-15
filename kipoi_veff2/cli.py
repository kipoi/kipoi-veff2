import click
from path import Path

AVAILABLE_MODELS = {
    "Basenji": ["diff"],
    "Basset": ["diff"],
    "CleTimer": ["diff"],
    "DeepBind": ["diff"],
    "DeepMEL": ["diff"],
    "DeepSEA": ["diff"],
}


def validate_model(ctx, param, models):
    """[This is a callback for validation of requested model groups w.r.t AVAILABLE_MODELS]

    Args:
        ctx ([click.Context]): [Current context]
        param ([click.Parameter]): [The parameters to register with this command - Options in this case]
        models ([Tuple]): [Models of interest]

    Raises:
        click.BadParameter: [An exception that formats out a standardized error message for a bad parameter
        if there are no models to score variants with]

    Returns:
        [list]: [List of models which are available for variant scoing]
    """
    models = list(models)
    for model in models:
        if model.split("/")[0] not in AVAILABLE_MODELS.keys():
            print(
                f"Removing {model} as it is not supported. \
                Please consult the documentation"
            )
            models.remove(model)
    if not models:
        raise click.BadParameter(
            f"Please select atleast one supported model group."
        )
    else:
        return models


@click.command()
@click.argument("input_vcf", required=True, type=click.Path(exists=True))
@click.argument("output_vcf", required=True)
@click.option(
    "-m",
    "--models",
    required=True,
    type=str,
    multiple=True,
    callback=validate_model,
    help="Run variant effect prediction using this list of models. \
        Example: python kipoi_veff2/cli.py in.vcf out.vcf -m 'Basenji' -m 'Basset' ",
)
def score_variants(input_vcf, output_vcf, models):
    """Perform variant effect prediction with the INPUT_VCF
    file using the MODELS and write them to OUTPUT_VCF
    """
    input_vcf = Path(input_vcf)
    output_vcf = Path(output_vcf)
    click.echo(
        f"input_vcf = {input_vcf}, output_vcf = {output_vcf},models={models}"
    )


if __name__ == "__main__":
    score_variants()
