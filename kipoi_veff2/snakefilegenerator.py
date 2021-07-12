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
@click.argument(
    "input_vcf", required=True, type=click.Path(exists=True, readable=True)
)
@click.argument(
    "input_fasta", required=True, type=click.Path(exists=True, readable=True)
)
@click.argument(
    "output_dir", required=True, type=click.Path(exists=True, writable=True)
)
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
    input_vcf: click.Path,
    input_fasta: click.Path,
    output_dir: click.Path,
    model_groups: List[str],
    number_of_shards: int,
) -> None:
    all_models = list_models().model
    list_of_models_veff = []
    for mg in model_groups:
        list_of_models_veff.extend(
            list(all_models[all_models.str.contains(mg)])
        )
    number_of_models_veff = len(list_of_models_veff)
    if number_of_shards > number_of_models_veff:
        raise click.BadParameter(
            f"Number of shards must be <= the number of models. The number of \
            models are {number_of_models_veff} and number of shards is {number_of_shards}"
        )
    chunk_size = ceil(number_of_models_veff / number_of_shards)
    list_of_shards = [
        list_of_models_veff[i : i + chunk_size]
        for i in range(0, number_of_models_veff, chunk_size)
    ]
    for shard_id, shard in enumerate(list_of_shards):
        snakefile_content = f'''def get_args(wildcards):
    """Function returning appropriate parameters with the flag
    for the corresponding model
    """
    return "-s diff"

models = {shard}

rule all:
    input: 
        expand("{output_dir}/{{model}}.tsv", model=models)

rule run_vep:
    output:
        "{output_dir}/{{model}}.tsv"
    params: 
        model_args = get_args
    shell: 
        "kipoi_veff2_predict {input_vcf} {input_fasta} {{params.model_args}} {{output}} -m {{wildcards.model}}" 
        '''

        with open(f"{output_dir}/Snakefile.{shard_id}", "w") as out:
            out.write(snakefile_content)


if __name__ == "__main__":
    generate_snakefiles()
