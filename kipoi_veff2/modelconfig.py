import kipoi


class ModelConfig:
    def __init__(
        self, model, scoring_fn, required_sequence_length, transform=None
    ):
        self.model = model
        self.scoring_fn = scoring_fn
        self.required_sequence_length = required_sequence_length
        self.transform = transform

    def get_model(self):
        return self.model

    def get_transform(self):
        if self.transform is None:
            # Infer from the model. raise an error if you cannot find them
            pass
        return self.transform
