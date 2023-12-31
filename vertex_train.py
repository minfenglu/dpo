import sys
import os
sys.path.append(f"{os.getcwd()}/python_packages/google-cloud-aiplatform-1.31.1")
#sys.path.append(f"{os.getcwd()}/python_packages/google-cloud-storage-2.10.0")
import argparse
from os import environ as env
from google.cloud import aiplatform

# Environment variables to be passed to training from local environment.
ENV_KEYS = ["WANDB_PROJECT", "WANDB_ENTITY", "WANDB_API_KEY"]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("project", type=str, help="GCP project name")
    parser.add_argument(
        "container_uri", type=str, help="GCS URI of the training container"
    )
    parser.add_argument(
        "staging_bucket",
        type=str,
        help="GCS URI of bucket where training outputs will be staged",
    )
    parser.add_argument(
        "-a",
        "--args",
        type=str,
        default="--model=pythia69,--datasets=[hh],--loss=sft,--exp_name=anthropic_dpo_pythia69,--gradient_accumulation_steps=2,--batch_size=64,--eval_batch_size=32,--trainer=FSDPTrainer,--sample_during_eval=false",
        help="Args to be passed to train.py",
    )
    parser.add_argument(
        "-n",
        "--name",
        type=str,
        default="default",
        help="Display name for this job",
    )
    parser.add_argument(
        "-d",
        "--description",
        type=str,
        help="Description for this job",
    )
    parser.add_argument(
        "--machine_type",
        type=str,
        default="n1-standard-4",
        help="Compute engine instance type to use",
    )
    parser.add_argument(
        "--accelerator_type",
        type=str,
        default="NVIDIA_TESLA_T4",
        help="Type of gpu accelerator to use. "
        "Full list at https://cloud.google.com/compute/docs/gpus",
    )
    parser.add_argument(
        "--accelerator_count",
        type=int,
        default=1,
        help="Number of accelerators to use",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    args.args = args.args.split(",")
    aiplatform.init(project=args.project, staging_bucket=args.staging_bucket)
    job = aiplatform.CustomContainerTrainingJob(
        display_name=args.name,
        container_uri=args.container_uri,
        requirements=["ipykernel", 
                      "tokenizers", 
                      "tqdm",
                      "transformers",
                      "datasets",
                      "beautifulsoup4",
                      "wandb",
                      "hydra-core",
                      "tensor-parallel",
                      ],
        command=["python3", "train.py", *args.args],
    )
    job.run(
        machine_type=args.machine_type,
        accelerator_type=args.accelerator_type,
        accelerator_count=args.accelerator_count,
        environment_variables={k: env[k] for k in ENV_KEYS},
    )


if __name__ == "__main__":
    main()

'''
python vertex_train.py mlu-dpo us-docker.pkg.dev/vertex-ai/training/pytorch-gpu.1-13.py310:latest vertex-ai-minfeng-dpo
'''