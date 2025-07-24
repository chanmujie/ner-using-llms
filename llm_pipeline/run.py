from main import Main
from pathlib import Path
import json
import pandas as pd

# CONFIG
dataset_base = Path("./datasets")

# 2 sets x 3 batches
dataset_configs = [
    ("multi", "b1c"), 
    ("multi", "b2"), 
    ("multi", "b3")
    ("single", "b1c"),
    ("single", "b2"),
    ("single", "b3")
]

prompt_tag = "p5"

# repeats per config
num_repeats = 3

# base model
model_name = "llama-3.5-8b-instruct"

# base output folder
output_base = Path("./experiment_outputs_salutation")
output_base.mkdir(parents=True, exist_ok=True)

# launch
for set_name, batch_name in dataset_configs:
    dataset_path = dataset_base / f"{set_name}_entity_dataset" / f"test_input_{batch_name}.jsonl"

    for repeat in range(1, num_repeats + 1):
        output_dir = output_base/f"{set_name}/{batch_name}/{prompt_tag}/run{repeat}"

        args = [
            "--model", model_name,
            "--dataset_path", str(dataset_path),
            "--output_dir", str(output_dir),
            "--prompt_tag", prompt_tag,
            "--run_tag", f"run{repeat}"
        ]

        print(f"\n=== Running: {set_name}-{batch_name} | prompt {prompt_tag} | run {repeat} ===\n")

        main = Main(args)
        main.run()
