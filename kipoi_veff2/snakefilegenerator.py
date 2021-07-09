import click
from math import ceil
from typing import List

from kipoi import list_models
from kipoi_veff2 import interval_based
from kipoi_veff2 import variant_centered


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


def validate_number_of_shards(
    ctx: click.Context, param: click.Parameter, number_of_shards: int
) -> int:
    if number_of_shards <= 0:
        raise click.BadParameter("Please enter a positive number of shards.")
    else:
        return number_of_shards


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
@click.option(
    "-n",
    "--number-of-shards",
    required=True,
    type=int,
    callback=validate_number_of_shards,
    help="Enter the number of groups to divide all the models in \
    Example: kipoi_veff2_generate_workflow -mg Basset -mg DeepSEA \
    -mg DeepBind/Homo_sapiens -n 10",
)
def generate_snakefiles(
    model_groups: List[str], number_of_shards: int
) -> None:
    click.echo(f"working model groups are = {model_groups}")
    all_models = list_models().model
    list_of_models_veff = []
    for mg in model_groups:
        list_of_models_veff.extend(
            list(all_models[all_models.str.contains(mg)])
        )
    number_of_models_veff = len(list_of_models_veff)
    if number_of_shards > number_of_models_veff:
        raise click.BadParameter(
            f"Please adjust the number of shards. The number of models are \
            {number_of_models_veff} and number of shards is {number_of_shards}"
        )
    chunk_size = ceil(number_of_models_veff / number_of_shards)
    list_of_shards = [
        list_of_models_veff[i : i + chunk_size]
        for i in range(0, number_of_models_veff, chunk_size)
    ]
    click.echo(len(list_of_shards[0]))


if __name__ == "__main__":
    generate_snakefiles()
