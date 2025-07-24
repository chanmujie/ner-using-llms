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

# generate summary.csv and averages.csv
def generate_summary_and_averages(base_dir="./experiment_outputs"):
    base_path = Path(base_dir)
    all_results = []

    for metrics_file in base_path.rglob("*/run*/metrics.json"):
        parts = metrics_file.parts
        try:
            entity_type = parts[-5]
            batch = parts[-4]
            prompt = parts[-3]
            run = parts[-2]
        except IndexError:
            print(f"[Warning] Could not parse path: {metrics_file}")
            continue

        with open(metrics_file, "r") as f:
            metrics = json.load(f)

        all_results.append({
            "entity_type": entity_type,
            "batch": batch,
            "prompt": prompt,
            "run": run,
            "micro_f1": metrics.get("micro_f1", 0.0),
            "micro_precison": metrics.get("micro_precision", 0.0),
            "micro_recall": metrics.get("micro_recall", 0.0),
            "avg_latency_sec": metrics.get("avg_latency_sec", 0.0),
            "precision_100": metrics["precision_buckets"].get("100", 0),
            "precision_70_99": metrics["precision_buckets"].get("70-99", 0),
            "precision_30_69": metrics["precision_buckets"].get("30-69", 0),
            "precision_0_29": metrics["precision_buckets"].get("0-29", 0),
            "recall_100": metrics["recall_buckets"].get("100", 0),
            "recall_70_99": metrics["recall_buckets"].get("70-99", 0),
            "recall_30_69": metrics["recall_buckets"].get("30-69", 0),
            "recall_0_29": metrics["recall_buckets"].get("0-29", 0)
        })

    if not all_results:
        print("No metrics found for summary.")
        return

    summary_df = pd.DataFrame(all_results)
    summary_df.to_csv(base_path / "summary.csv", index=False)

    avg_df = summary_df.groupby(["entity_type", "batch", "prompt"]).agg({
        "micro_f1": "mean",
        "micro_precision": "mean",
        "micro_recall": "mean",
        "avg_latency_sec": "mean",
        "precision_100": "mean",
        "precision_70_99": "mean",
        "precision_30_69": "mean",
        "precision_0_29": "mean",
        "recall_100": "mean",
        "recall_70_99": "mean",
        "recall_30_69": "mean",
        "recall_0_29": "mean"
    }).reset_index()
    avg_df.to_csv(base_path / "averages.csv", index=False)

    print(f"\nSummary and averages written to {base_path}/")

# Call after all runs complete
generate_summary_and_averages()
