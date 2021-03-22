import os
import pytest
import subprocess


@pytest.mark.parametrize(
    "model",
    [
        "Basenji",
        "Basset",
        "CleTimer/customBP",
        "DeepBind/Homo_sapiens/RBP/D00084.001_RNAcompete_A1CF",
        "DeepMEL/DeepMEL",
        "DeepSEA/predict",
        "MaxEntScan/5prime",
    ],
)
def test_models(model):
    if (
        "CONDA_DEFAULT_ENV" in os.environ
        and os.environ["CONDA_DEFAULT_ENV"] == "kipoi-veff2"
    ):
        from kipoi_conda import get_kipoi_bin

        args = [
            get_kipoi_bin("kipoi-veff2"),
            "test",
            "--source=kipoi",
            model,
        ]
        if model == "Basenji":
            args.append("--batch_size=2")
        returncode = subprocess.call(args=args)
        assert returncode == 0
    else:
        import docker

        if model == "Basenji":
            test_cmd = f"kipoi test {model} --source=kipoi --batch_size=2"
        else:
            test_cmd = f"kipoi test {model} --source=kipoi"
        client = docker.from_env()
        image_name = "kipoi-veff2-docker:latest"
        try:
            client.images.build(
                path=".", dockerfile="Dockerfile", tag=image_name
            )
        except RuntimeError as e:
            raise (e)
        try:
            client.containers.run(image=image_name, command=test_cmd)
        except docker.errors.ImageNotFound:
            raise (f"Image {image_name} is not found")
        except docker.errors.ContainerError as e:
            raise (e)
        except docker.errors.APIError as e:
            raise (e)
        client.volumes.prune()
        client.containers.prune()
