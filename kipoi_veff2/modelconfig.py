from typing import Any

import kipoi


class ModelConfig:
    def __init__(
        self,
        model: str,
        scoring_fn: Any,
        required_sequence_length: int,
        transform=None,
    ) -> None:
        self.model = model
        self.scoring_fn = scoring_fn
        self.required_sequence_length = required_sequence_length
        self.transform = transform

    def get_model(self) -> str:
        return self.model

    def get_transform(self) -> Any:
        if self.transform is None:
            # Infer from the model. raise an error if you cannot find them
            pass
        return self.transform
