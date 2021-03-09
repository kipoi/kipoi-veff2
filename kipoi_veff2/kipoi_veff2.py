import json
from pathlib import Path


class KipoiVeff:
    with open(
        str(Path(__file__).resolve().parent.parent / "config" / "models.json")
    ) as model_config:
        available_models = json.load(model_config)

    def __init__(self, input_vcf, output_vcf, models):
        self.input = Path(input_vcf)
        self.output = Path(output_vcf)
        self.models = models

    def predict_variant_effect(self):
        print(
            f"input_vcf = {self.input}, output_vcf = {self.output},\
            models={self.models}"
        )
