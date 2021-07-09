import click

from kipoi_veff2 import interval_based
from kipoi_veff2 import variant_centered

from typing import List


def validate_model_groups(
    ctx: click.Context, param: click.Parameter, model_group: str
) -> List[str]:
    """[This is a callback for validation of requested model group w.r.t
        variant_centered.MODEL_GROUPS and interval_based.MODEL_GROUPS]
    Raises:
        click.BadParameter: [An exception that formats
        out a standardized error message for a bad parameter
        if there are no model to score variants with]
    """
    model_groups = list(model_group)
    available_model_groups = []
    for mg in model_groups:
        # To distinguish DeepBind/Human/AHR and Basset for example
        main_model_group = mg.split("/")[0]
        if (
            main_model_group in variant_centered.MODEL_GROUPS
            or main_model_group in interval_based.MODEL_GROUPS
        ):
            available_model_groups.append(mg)
        else:
            print(f"Not adding {mg} as it is not supported yet")
    if list(model_group) and not available_model_groups:
        raise click.BadParameter(
            "Please select atleast one supported model group."
        )
    else:
        return available_model_groups


@click.command()
@click.option(
    "-mg",
    "--model-groups",
    required=True,
    multiple=True,
    type=str,
    callback=validate_model_groups,
    help="Enter your model group of choice \
    Example: kipoi_veff2_generate_workflow -mg Basset -mg DeepSEA",
)
def generate_snakefiles(model_groups: str) -> None:
    click.echo(f"working model groups are = {model_groups}")


if __name__ == "__main__":
    generate_snakefiles()
