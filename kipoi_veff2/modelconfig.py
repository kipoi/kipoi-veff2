from typing import Any, List

import kipoi
from kipoiseq.transforms import ReorderedOneHot


class ModelConfig:
    def __init__(
        self,
        model: str,
        scoring_fn: Any,
        required_sequence_length=None,
        transform=None,
    ) -> None:
        self.model = model
        self.model_description = kipoi.get_model_descr(self.model)
        self.scoring_fn = scoring_fn
        self.required_sequence_length = required_sequence_length
        self.transform = transform

    def get_model(self) -> str:
        return self.model

    def get_transform(self) -> Any:
        if self.transform is None:
            dataloader = self.model_description.default_dataloader
            if dataloader.defined_as == "kipoiseq.dataloaders.SeqIntervalDl":
                dataloader_args = dataloader.default_args
                self.transform = ReorderedOneHot(
                    alphabet="ACGT",
                    dtype=dataloader_args["dtype"],
                    alphabet_axis=dataloader_args["alphabet_axis"],
                    dummy_axis=dataloader_args["dummy_axis"],
                )
        if self.transform is None:
            raise ValueError("Cannot proceed without a transform")
        else:
            return self.transform

    def get_required_sequence_length(self) -> Any:
        if self.required_sequence_length is None:
            self.required_sequence_length = (
                self.model_description.default_dataloader.default_args.get(
                    "auto_resize_len", None
                )
            )
        if self.required_sequence_length is None:
            raise ValueError("Cannot proceed without required sequence length")
        else:
            return self.required_sequence_length

    def get_column_labels(self) -> List:
        targets = self.model_description.schema.targets
        column_labels = targets.column_labels
        target_shape = targets.shape[0]
        if column_labels:
            if len(column_labels) == target_shape:
                return [f"{self.model}/{c}" for c in column_labels]
            else:
                raise IOError(
                    "Something wrong with the model description - \
                    length of column names does not match target shape"
                )
        else:
            return [f"{self.model}/{num+1}" for num in range(target_shape)]
