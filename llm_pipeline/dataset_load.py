from dataclasses import dataclass
from dataclass import GoldEntity, Entity
from typing import List, Dict, Tuple
import pandas as pd
from pathlib import Path
import json
from random import shuffle

@dataclass
class GoldInstance:
    text_id: int
    text: str
    entities: List[GoldEntity]

    def to_records(self):
        """Return a list of records (one per entity) to be converted to DataFrame."""
        return [
            {
                "text_id": self.text_id,
                "text": self.text,
                "entity_label": e.label,
                "gold_text": e.raw_text,
                "gold_clean": e.clean_text,
                "model_prediction": e.model_prediction,
                "correct": e.correct,
                "gold_fields": e.extra_fields,
            }
            for e in self.entities
        ]

    def get_sentence(self):
        return self.text

def load_ner_gold(file_path):
    instances = []
    
    with open(file_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            record = json.loads(line)
            text = record["text"]
            annotations = record.get("annotations", [])
            
            entities = []
            for ann in annotations:
                # Skip entity if marked as invalid
                if ann.get("is_valid", True) is False:
                    continue

                label = ann["label"]
                gold_text = ann["text"]
                gold_clean = ann.get("clean", gold_text)
                
                # Capture extra fields
                extra_fields = {k: v for k, v in ann.items() if k not in ["label", "text", "clean"]}
                
                entity = GoldEntity(
                    label=label,
                    raw_text=gold_text,
                    clean_text=gold_clean,
                    extra_fields=extra_fields,
                    model_prediction=None,
                    correct=None
                )
                entities.append(entity)
            
            instance = GoldInstance(
                text_id=i,
                text=text,
                entities=entities
            )
            instances.append(instance)
    
    return instances

class Dataset:
    def __init__(self, jsonl_path: Path):
        self.jsonl_path = jsonl_path
        self.instances: List[GoldInstance] = []

    def load(self):
        self.instances = load_ner_gold(self.jsonl_path)

    def get_instances(self) -> List[GoldInstance]:
        shuffle(self.instances)
        return self.instances

    def __len__(self):
        return len(self.instances)

    def __getitem__(self, idx):
        return self.instances[idx]
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert entire dataset to a flat DataFrame."""
        all_records = []
        for instance in self.instances:
            all_records.extend(instance.to_records())
        return pd.DataFrame(all_records)
    
    def save_csv(self, out_path: Path):
        """Save the dataset as a CSV file."""
        df = self.to_dataframe()
        df.to_csv(out_path, index=False)
        print(f"Saved CSV to {out_path}")

    def save_jsonl(self, out_path: Path, mode: str = "flat"):
        """
        Save dataset to JSONL with format options:
        
        Args:
            out_path: Output file path
            mode: "flat" (default) for evaluation-ready format,
                  "nested" for original structure preservation
        """
        with open(out_path, 'w', encoding='utf-8') as f:
            for instance in self.instances:
                if mode == "flat":
                    # Evaluation-ready format (matches your to_records() structure)
                    for record in instance.to_records():
                        f.write(json.dumps(record, ensure_ascii=False) + '\n')
                else:
                    # Original nested structure
                    f.write(json.dumps({
                        "text_id": instance.text_id,
                        "text": instance.text,
                        "entities": [
                            {
                                "label": e.label,
                                "text": e.raw_text,
                                "clean": e.clean_text,
                                **e.extra_fields,
                                "model_prediction": e.model_prediction,
                                "correct": e.correct
                            }
                            for e in instance.entities
                        ]
                    }, ensure_ascii=False) + '\n')
        
        print(f"Saved {mode} JSONL to {out_path}")
    
    def update_prediction(self, predictions: Dict[int, List[Entity]]):
        """
        Update each gold entity with model predictions.

        Args:
            predictions: Dict[int, List[Entity]] — text_id → list of predicted Entity objects
        """
        for instance in self.instances:
            pred_entities = predictions.get(instance.text_id, [])
            
            # Create a set of unmatched predictions so we can mark which predictions have been "used"
            unmatched_preds = {(p.label, p.clean_text.lower()): p for p in pred_entities}
            
            for gold_entity in instance.entities:
                match_key = (gold_entity.label, gold_entity.clean_text.lower())
                
                if match_key in unmatched_preds:
                    # Matching prediction found
                    pred_entity = unmatched_preds.pop(match_key)
                    
                    # Record prediction into gold entity
                    gold_entity.model_prediction = pred_entity.clean_text
                    gold_entity.correct = True  # Exact match
                else:
                    # No match found
                    gold_entity.model_prediction = None
                    gold_entity.correct = False
