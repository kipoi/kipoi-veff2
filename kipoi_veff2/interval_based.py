import csv
from pathlib import Path
from typing import Any, Dict, Union, List

from dataclasses import dataclass
import kipoi

MODEL_GROUPS = ["MMSplice"]


@dataclass
class ModelConfig:
    model: str

    def __post_init__(self):
        self.model_description = kipoi.get_model_descr(self.model)
        self.kipoi_model_with_dataloader = kipoi.get_model(
            self.model, source="kipoi", with_dataloader=True
        )

    def get_model(self) -> str:
        return self.model

    def get_column_labels(self) -> List:
        targets = self.model_description.schema.targets
        column_labels = targets.column_labels
        target_shape = targets.shape[0]
        variant_column_labels = ["#CHROM", "POS", "ID", "REF", "ALT"]
        if column_labels:
            if len(column_labels) == target_shape:
                return variant_column_labels + [
                    f"{self.model}/{c}" for c in column_labels
                ]
            else:
                raise IOError(
                    "Something wrong with the model description - \
                        length of column names does not match target shape"
                )
        else:
            return variant_column_labels + [
                f"{self.model}/{num+1}" for num in range(target_shape)
            ]

    # TODO: Should Any be Callable?
    def get_dataloader(self, params: Dict[str, str]) -> Any:
        dataloader_args = list(
            self.kipoi_model_with_dataloader.default_dataloader.args.keys()
        )
        # TODO: This most likely will vary across model groups which we can
        # control through get_model_config or dataloader_args
        necessary_file_types = ["gtf", "fasta", "vcf"]
        if not all(item in params.keys() for item in necessary_file_types):
            raise IOError(
                "Please provide a dictionary with atleast gtf,\
                fasta and vcf file locations"
            )
        for file_type in necessary_file_types:
            matching_dl_param = [
                param for param in dataloader_args if file_type in param
            ]
            if not matching_dl_param:
                raise IOError(
                    f"Cannot find a matching parameter for {file_type}"
                )
            if len(matching_dl_param) > 1:
                raise IOError(
                    f"Found too many matching parameters for \
                        {file_type} in {matching_dl_param}"
                )
            params[matching_dl_param[0]] = params.pop(file_type)
        return self.kipoi_model_with_dataloader.default_dataloader(**params)


def get_model_config(model_name: str) -> ModelConfig:
    return ModelConfig(model=model_name)


def score_variants(
    model_config: ModelConfig,
    vcf_file: Union[str, Path],
    fasta_file: Union[str, Path],
    gtf_file: Union[str, Path],
    output_file: Union[str, Path],
) -> None:
    # TODO: This will download the model weights - any way around it?
    dataloader = model_config.get_dataloader(
        {
            "fasta": fasta_file,
            "gtf": gtf_file,
            "vcf": vcf_file,
        }
    )
    with open(output_file, "w") as output_tsv:
        tsv_writer = csv.writer(output_tsv, delimiter="\t")
        tsv_writer.writerow(model_config.get_column_labels())
        for batch in dataloader.batch_iter():
            # TODO: Should we check if inputs, metadata, exon_id
            #  are present in batch?
            predictions = (
                model_config.kipoi_model_with_dataloader.predict_on_batch(
                    batch["inputs"]
                )
            )
            variant = batch["metadata"]["variant"]
            exon_id = batch["metadata"]["exon"]["exon_id"]
            for index, pred in enumerate(predictions):
                if pred.size == 1:
                    pred = [pred]
                else:
                    pred = list(pred)
                tsv_writer.writerow(
                    [
                        variant["chrom"][index],
                        variant["pos"][index],
                        # TODO: is this correct?
                        f'{variant["annotation"][index]}:{exon_id[index]}',
                        variant["ref"][index],
                        variant["alt"][index],
                    ]
                    + pred
                )
