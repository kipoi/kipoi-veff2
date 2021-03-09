import click

from kipoi_veff2.kipoi_veff2 import KipoiVeff


def validate_model(ctx, param, value):
    model_groups = list(value)
    for model_group in model_groups:
        if model_group.split("/")[0] not in KipoiVeff.available_models.keys():
            print(
                f"Removing {model_group} as it is not supported. \
                Please consult the documentation"
            )
            model_groups.remove(model_group)
    if not model_groups:
        raise click.BadParameter(
            f"Please select atleast one supported model group."
        )
    else:
        return model_groups


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
    help="Run variant effect prediction using this list of models",
)
def cli(input_vcf, output_vcf, models):
    """Perform variant effect prediction with the INPUT_VCF
    file using the MODELS and write them to OUTPUT_VCF
    """
    kv = KipoiVeff(input_vcf=input_vcf, output_vcf=output_vcf, models=models)
    click.echo(kv.predict_variant_effect())


if __name__ == "__main__":
    cli()
