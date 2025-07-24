import argparse
import keyring
import json
import time
from pathlib import Path
from typing import List, Dict, Any

# Imports
from models import Llama, Phi, Extractor
from evaluation import Evaluator
from dataset_load import Dataset
from dataclass import Entity
from prompt_template import prompt_map

class Main:
    def __init__(self, args=None):
        if args is None:
            self.args = self.parse_args()  # from CLI
        else:
            self.args = self.parse_args(args)  # from script

    def parse_args(self, args=None):
        parser = argparse.ArgumentParser(description="NER Pipeline with Llama/Phi")

        parser.add_argument("--model", type=str, required=True)
        parser.add_argument("--dataset_path", type=str, required=True)
        parser.add_argument("--output_dir", type=str, default="./outputs")
        parser.add_argument("--prompt_tag", type=str, default="p1", help="Prompt version tag (e.g. p1, p2, p3, p4, p5)")
        parser.add_argument("--run_tag", type=str, default="run1", help="Run tag to allow repeated runs")

        return parser.parse_args(args)

    def create_model_client(self):
        model_name = self.args.model.lower()
        if "phi" in model_name:
            print(f"Creating Phi client for model: {model_name}")
            return Phi(
                endpoint=keyring.get_password("azureml", "phi_endpoint"),
                api_key=keyring.get_password("azureml", "phi_api_key"),
                model_name=model_name
            )
        else:
            print(f"Creating Llama client for model: {model_name}")
            return Llama(
                endpoint=keyring.get_password("azureml", "llama_endpoint"),
                api_key=keyring.get_password("azureml", "llama_api_key")
            )

    def run(self):
        # Setup output directory
        output_path = Path(self.args.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Subdirectory for raw LLM responses
        debug_dir = output_path / "api_responses"
        debug_dir.mkdir(exist_ok=True)

        # Load dataset
        dataset = Dataset(jsonl_path=Path(self.args.dataset_path))
        dataset.load()
        print(f"\nLoaded dataset with {len(dataset.instances)} instances.")

        # Model + extractor
        llm_client = self.create_model_client()
        prompt_tag = self.args.prompt_tag.lower()
        if prompt_tag in prompt_map:
            system_prompt = prompt_map[prompt_tag]
        else:
            print(f"[Warning] Prompt tag '{prompt_tag}' not found, using default prompt.")
            system_prompt = prompt_map["default"]

        extractor = Extractor()

        all_predictions = {}
        latencies = []
        batch_size = 5 

        for i in range(0, len(dataset.instances), batch_size):
            batch = dataset.instances[i:i + batch_size]
            input_texts = [inst.text for inst in batch]
            text_ids = [inst.text_id for inst in batch]

            try:
                user_prompt = "\n".join(f"{j+1}. {t}" for j, t in enumerate(input_texts))

                response_str, latency = llm_client.generate_completion(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt
                )
                latencies.append(latency)

                with open(debug_dir / f"response_batch_{i}.json", "w") as f:
                    json.dump({
                        "text_ids": text_ids,
                        "texts": input_texts,
                        "response": response_str.decode('utf-8') if isinstance(response_str, bytes) else response_str,
                        "latency": latency,
                        "timestamp": time.time()
                    }, f, indent=2)

                parsed = extractor.parse_response(response_str)
                entity_map = extractor.parse_entities_from_extracted(parsed)

                entity_items = list(entity_map.items())
                if len(entity_items) != len(batch):
                    print(f"[Warning] Mismatch: {len(entity_items)} outputs vs {len(batch)} inputs")

                for inst, (pred_input, entities) in zip(batch, entity_items):
                    all_predictions[inst.text_id] = entities

            except Exception as e:
                print(f"[Error] Batch starting at {i} failed: {e}")
                for inst in batch:
                    all_predictions[inst.text_id] = []

        # Save predictions
        with open(output_path / "raw_predictions.json", "w") as f:
            json.dump(all_predictions, f, indent=2)

        # Evaluate
        evaluator = Evaluator(
            dataset,
            labels_to_consider=[
                "name", "email", "date", "phone_number",
                "organisation", "salutation", "relationship",
                "country", "airport_code", "id", "plate"
            ]
        )
        results = evaluator.evaluate(all_predictions)
        df_instance, df_label = evaluator.results_to_dataframe(results)

        df_instance.to_csv(output_path / "per_instance.csv", index=False)
        df_label.to_csv(output_path / "per_label.csv", index=False)

        with open(output_path / "metrics.json", "w", encoding="utf-8") as f:
            json.dump({
                "micro_precision": results["micro_precision"],
                "micro_recall": results["micro_recall"],
                "micro_f1": results["micro_f1"],
                "avg_latency_sec": sum(latencies) / len(dataset.instances) if latencies else 0.0,
                "per_instance_precision_buckets": results["per_instance_precision_buckets"],
                "per_instance_recall_buckets": results["per_instance_recall_buckets"]
            }, f, indent=2)

        print("\n---- RESULTS ----")
        print(f"Prompt Tag: {self.args.prompt_tag} | Run Tag: {self.args.run_tag}")
        print("Micro F1:", results["micro_f1"])
        print(f"Saved outputs to: {output_path}")
        print(f"Raw responses: {debug_dir}")


if __name__ == "__main__":
    Main().run()
