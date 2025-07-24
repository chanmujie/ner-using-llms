# Open-Source LLM Prompt Engineering for Noisy NER

This project investigates the suitability of open-source large language models (LLMs) for Named Entity Recognition (NER) under varying levels of input noise. 
It includes synthetic dataset generation, prompt engineering, batched evaluation across entity types and noise settings. LLaMA 3.5 8B Instruct and Phi-4 Reasoning were tested. 

---
## Table of Contents

- [Overview](#-llm-based-prompt-engineering-for-noisy-ner)
- [Repository Structure](#-repository-structure)
- [Workflow Overview](#-workflow-overview)
  - [1. Generate Entity Samples](#-1-generate-entity-samples)
  - [2. Generate Datasets](#-2-generate-datasets)
  - [3. Run Evaluation Experiments](#-3-run-evaluation-experiments)
- [Prompt Variants](#-prompt-variants)
- [Dataset Types & Batches](#-dataset-types--batches)
- [Results Format](#-results-format)


## Repository Structure

| Folder | Description |
|--------|-------------|
| `entity_generation/` | Scripts to generate raw samples for each entity type (e.g. names, phones, orgs). |
| `entity_data/` | JSONL files containing sampled entity examples used in datasets. |
| `dataset_generation/` | Code to generate single-entity and multi-entity datasets across noise levels. |
| `datasets/` | Final test datasets: split into `multi_entity/` and `single_entity/`, with three noise levels: `b1c` (clean), `b2` (moderate), `b3` (noisy). |
| `llm_pipeline/` | Core pipeline for loading datasets, applying prompt templates, querying LLMs, and evaluating results. |
| `experiment_outputs/` | Evaluation results, organised by dataset type, batch, prompt version, and run. |
| `docs/` | (Optional) Additional documentation: design notes, diagrams, evaluation results. |

---

## Workflow Overview
This project is run programmatically. Each phase is controlled through configurable Python scripts that can be edited directly.

### 1. Generate Entity Samples
Raw synthetic entities (e.g., names, phone numbers, emails) are generated using Python scripts in `entity_generation/`.
Entities are generated either by prompting OpenAI's GPT-4o or programmatically (phone numbers, emails).
Entities are then noised programmatically with `entity_generation/noise.py`.

### 2. Generate Datasets
Raw entity samples are combined into synthetic datasets using batch-specific noise. Code lives in `dataset_generation/`.

There are two generation scripts:
- multi_entity_gen.py (generates strings with multiple types of entities)
- single_entity_gen.py (generates strings with one type of entity)

### 3. Run Prompt Evaluation Experiments
The evaluation pipeline is controlled through:

```bash
llm_pipeline/run_experiments.py
```
This file loops through dataset types, batches, prompt variants, and repeat runs.

Each run produces predictions and metrics, structured as:

``` css
experiment_outputs/
└── [multi|single]/
    └── [b1c|b2|b3]/
        └── [p1–p5]/
            └── run[1–n]/
                ├── metrics.json
                ├── per_instance.csv
                ├── per_label.csv
                ├── raw_prediction.json
                └── api_responses/
                    └── response_batch_[0-m].json
```
## Prompt Variants
Prompt variants are defined in `llm_pipeline/prompt_template.py`

## Dataset Types & Batches
#### Types
- multi_entity_dataset: multiple entity types per line.
- single_entity_dataset: one entity type per line.

#### Batches
- b1/b1c: clean, concatenated
- b2: moderately noisy, still recognisable
- b3: heavily noisy + junk









