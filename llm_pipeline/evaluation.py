from collections import defaultdict
from typing import List, Dict, Tuple, Any, Union
import pandas as pd

class Evaluator:

    def __init__(self, dataset, labels_to_consider: List[str] = None):
        self.dataset = dataset
        self.labels_to_consider = set(labels_to_consider) if labels_to_consider else None

    def _extract_label_text(self, e: Union[Dict[str, Any], Any]) -> Tuple[str, str]:
        label = e["label"] if isinstance(e, dict) else e.label
        if isinstance(e, dict):
            text = e.get("raw_text") or e.get("text") or e.get("clean_text", "")
        else:
            text = getattr(e, "raw_text", None) or getattr(e, "text", None) or getattr(e, "clean_text", "")
        return label, text

    def _compute_partial_overlap(self, gold_text: str, pred_text: str) -> float:
        set_gold = set(gold_text) if gold_text else set()
        set_pred = set(pred_text) if pred_text else set()
        if not set_gold:
            return 0.0
        intersection = len(set_gold.intersection(set_pred))
        return intersection / len(set_gold)

    def _compute_exact_metrics(
        self,
        gold_entities: List[Dict[str, Any]],
        pred_entities: List[Dict[str, Any]]
    ) -> Tuple[float, float, float]:
        gold_set = {(self._extract_label_text(e)) for e in gold_entities}
        pred_set = {(self._extract_label_text(e)) for e in pred_entities}
        tp = len(gold_set & pred_set)
        fp = len(pred_set - gold_set)
        fn = len(gold_set - pred_set)
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        return precision, recall, f1

    def _compute_partial_metrics(
        self,
        gold_entities: List[Dict[str, Any]],
        pred_entities: List[Dict[str, Any]]
    ) -> Tuple[float, float, float]:

        gold_set = {(self._extract_label_text(e)) for e in gold_entities}
        pred_set = {(self._extract_label_text(e)) for e in pred_entities}

        precision_scores = []
        for p_label, p_text in pred_set:
            best_overlap = 0.0
            for g_label, g_text in gold_set:
                if g_label == p_label:
                    overlap = self._compute_partial_overlap(g_text, p_text)
                    if overlap > best_overlap:
                        best_overlap = overlap
            precision_scores.append(best_overlap)
        precision = sum(precision_scores) / len(precision_scores) if precision_scores else 0.0

        recall_scores = []
        for g_label, g_text in gold_set:
            best_overlap = 0.0
            for p_label, p_text in pred_set:
                if p_label == g_label:
                    overlap = self._compute_partial_overlap(g_text, p_text)
                    if overlap > best_overlap:
                        best_overlap = overlap
            recall_scores.append(best_overlap)
        recall = sum(recall_scores) / len(recall_scores) if recall_scores else 0.0

        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        return precision, recall, f1

    def evaluate(
        self,
        predictions: Dict[Union[str, int], List[Dict[str, Any]]],
    ) -> Dict[str, Any]:

        micro_tp = 0
        micro_fp = 0
        micro_fn = 0
        per_label_counts = defaultdict(lambda: {
            "tp": 0, "fp": 0, "fn": 0,
            "partial_tp": 0.0, "partial_fp": 0.0, "partial_fn": 0.0
        })
        per_instance_results = []

        precision_bucket_counts = {"0-29": 0, "30-69": 0, "70-99": 0, "100": 0}
        recall_bucket_counts = {"0-29": 0, "30-69": 0, "70-99": 0, "100": 0}

        for instance in self.dataset.instances:
            gold_entities = instance.entities
            pred_entities = predictions.get(str(instance.text_id), predictions.get(instance.text_id, []))

            if self.labels_to_consider:
                gold_entities = [e for e in gold_entities if self._extract_label_text(e)[0] in self.labels_to_consider]
                pred_entities = [e for e in pred_entities if self._extract_label_text(e)[0] in self.labels_to_consider]

            # Exact metrics for micro counts
            exact_precision, exact_recall, exact_f1 = self._compute_exact_metrics(gold_entities, pred_entities)

            # Partial metrics for reporting
            partial_precision, partial_recall, partial_f1 = self._compute_partial_metrics(gold_entities, pred_entities)

            # Update micro counts with exact matching only
            gold_set = {(self._extract_label_text(e)) for e in gold_entities}
            pred_set = {(self._extract_label_text(e)) for e in pred_entities}

            tp = len(gold_set & pred_set)
            fp = len(pred_set - gold_set)
            fn = len(gold_set - pred_set)

            micro_tp += tp
            micro_fp += fp
            micro_fn += fn

            # Calculate per-label exact and partial TP/FP/FN
            all_labels = {label for label, _ in gold_set.union(pred_set)}
            for label in all_labels:
                gold_label_entities = [(l, t) for (l, t) in gold_set if l == label]
                pred_label_entities = [(l, t) for (l, t) in pred_set if l == label]

                # Exact TP/FP/FN
                gold_label_set = set(t for _, t in gold_label_entities)
                pred_label_set = set(t for _, t in pred_label_entities)
                label_tp = len(gold_label_set & pred_label_set)
                label_fp = len(pred_label_set - gold_label_set)
                label_fn = len(gold_label_set - pred_label_set)

                # Partial TP: sum of best partial overlaps per predicted entity
                partial_tp_sum = 0.0
                for p_label, p_text in pred_label_entities:
                    best_overlap = 0.0
                    for g_label, g_text in gold_label_entities:
                        overlap = self._compute_partial_overlap(g_text, p_text)
                        if overlap > best_overlap:
                            best_overlap = overlap
                    partial_tp_sum += best_overlap

                # Partial FP: predicted entities that have zero overlap
                partial_fp_sum = 0.0
                for p_label, p_text in pred_label_entities:
                    best_overlap = 0.0
                    for g_label, g_text in gold_label_entities:
                        overlap = self._compute_partial_overlap(g_text, p_text)
                        if overlap > best_overlap:
                            best_overlap = overlap
                    if best_overlap == 0.0:
                        partial_fp_sum += 1.0  # fully wrong prediction counts as FP

                # Partial FN: gold entities that were not well matched by any predicted entity
                partial_fn_sum = 0.0
                for g_label, g_text in gold_label_entities:
                    best_overlap = 0.0
                    for p_label, p_text in pred_label_entities:
                        overlap = self._compute_partial_overlap(g_text, p_text)
                        if overlap > best_overlap:
                            best_overlap = overlap
                    if best_overlap == 0.0:
                        partial_fn_sum += 1.0  # fully missed gold entity counts as FN

                per_label_counts[label]["tp"] += label_tp
                per_label_counts[label]["fp"] += label_fp
                per_label_counts[label]["fn"] += label_fn
                per_label_counts[label]["partial_tp"] += partial_tp_sum
                per_label_counts[label]["partial_fp"] += partial_fp_sum
                per_label_counts[label]["partial_fn"] += partial_fn_sum

            # Buckets based on exact precision/recall
            if exact_precision == 1.0:
                precision_bucket_counts["100"] += 1
            elif exact_precision >= 0.7:
                precision_bucket_counts["70-99"] += 1
            elif exact_precision >= 0.3:
                precision_bucket_counts["30-69"] += 1
            else:
                precision_bucket_counts["0-29"] += 1

            if exact_recall == 1.0:
                recall_bucket_counts["100"] += 1
            elif exact_recall >= 0.7:
                recall_bucket_counts["70-99"] += 1
            elif exact_recall >= 0.3:
                recall_bucket_counts["30-69"] += 1
            else:
                recall_bucket_counts["0-29"] += 1

            per_instance_results.append({
                "text_id": instance.text_id,
                "precision": exact_precision,
                "recall": exact_recall,
                "f1": exact_f1,
                "partial_precision": partial_precision,
                "partial_recall": partial_recall,
                "partial_f1": partial_f1
            })

        # Micro metrics from exact counts only
        micro_precision = micro_tp / (micro_tp + micro_fp) if (micro_tp + micro_fp) > 0 else 0.0
        micro_recall = micro_tp / (micro_tp + micro_fn) if (micro_tp + micro_fn) > 0 else 0.0
        micro_f1 = (2 * micro_precision * micro_recall) / (micro_precision + micro_recall) if (micro_precision + micro_recall) > 0 else 0.0

        per_label_results = []
        for label, counts in per_label_counts.items():
            tp = counts["tp"]
            fp = counts["fp"]
            fn = counts["fn"]
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

            partial_tp = counts["partial_tp"]
            partial_fp = counts["partial_fp"]
            partial_fn = counts["partial_fn"]
            partial_precision = partial_tp / (partial_tp + partial_fp) if (partial_tp + partial_fp) > 0 else 0.0
            partial_recall = partial_tp / (partial_tp + partial_fn) if (partial_tp + partial_fn) > 0 else 0.0
            partial_f1 = (2 * partial_precision * partial_recall) / (partial_precision + partial_recall) if (partial_precision + partial_recall) > 0 else 0.0

            per_label_results.append({
                "label": label,
                "precision": precision,
                "recall": recall,
                "f1": f1,
                "partial_precision": partial_precision,
                "partial_recall": partial_recall,
                "partial_f1": partial_f1,
                "tp": tp,
                "fp": fp,
                "fn": fn
            })

        return {
            "micro_precision": micro_precision,
            "micro_recall": micro_recall,
            "micro_f1": micro_f1,
            "per_instance": per_instance_results,
            "per_label": per_label_results,
            "per_instance_precision_buckets": precision_bucket_counts,
            "per_instance_recall_buckets": recall_bucket_counts
        }

    def results_to_dataframe(self, results: Dict[str, Any]):
        df_instance = pd.DataFrame(results["per_instance"])
        df_label = pd.DataFrame(results["per_label"])
        return df_instance, df_label
