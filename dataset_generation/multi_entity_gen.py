import json
import random
import string
import re
from typing import List, Dict, Any, Tuple
from email_generation import EmailEntityGenerator
import numpy as np

ENTITY_FILE_MAP = {
    "name": ["entity_data/name_sg_c_b1.jsonl", "entity_data/name_sg_c_b2.jsonl", "entity_data/name_sg_c_b3.jsonl", 
             "entity_data/name_sg_m_b1.jsonl", "entity_data/name_sg_m_b2.jsonl", "entity_data/name_sg_m_b3.jsonl", 
              "entity_data/name_sg_i_b1.jsonl", "entity_data/name_sg_i_b2.jsonl", "entity_data/name_sg_i_b2.jsonl", 
              "entity_data/name_sg_e_b1.jsonl", "entity_data/name_sg_e_b2.jsonl", "entity_data/name_sg_e_b3.jsonl",
              "entity_data/alias_sg_c_b1.jsonl", "entity_data/alias_sg_c_b2.jsonl", "entity_data/alias_sg_c_b3.jsonl", 
             "entity_data/alias_sg_m_b1.jsonl", "entity_data/alias_sg_m_b2.jsonl", "entity_data/alias_sg_m_b3.jsonl", 
              "entity_data/alias_sg_i_b1.jsonl", "entity_data/alias_sg_i_b2.jsonl", "entity_data/alias_sg_i_b2.jsonl", 
              "entity_data/alias_sg_e_b1.jsonl", "entity_data/alias_sg_e_b2.jsonl", "entity_data/alias_sg_e_b3.jsonl"],
    "phone": ["entity_data/phone_wo_code_sg_b1.jsonl", "entity_data/phone_wo_code_sg_b2.jsonl", "entity_data/phone_wo_code_sg_b2.jsonl",
              "entity_data/phone_code_sg_b1.jsonl", "entity_data/phone_code_sg_b2.jsonl", "entity_data/phone_code_sg_b3.jsonl"],
    "relationship": ["entity_data/relationship_b1.jsonl", "entity_data/relationship_b2.jsonl", "entity_data/relationship_b3.jsonl"],
    "date": ["entity_data/date_b1.jsonl", "entity_data/date_b2.jsonl", "entity_data/date_b3.jsonl"],
    "organisation": ["entity_data/org_sg_b1.jsonl","entity_data/org_sg_b2.jsonl","entity_data/org_sg_b3.jsonl"],
    "country": ["entity_data/country_entity.jsonl"],
    "airport_code": ["entity_data/airport_codes.jsonl"],
    "random_entity": ["entity_data/car_plate_sg.jsonl", "entity_data/id_num_sg.jsonl"],
    "salutation": ["entity_data/salutation.jsonl"]
    }


def load_entities(entity_type: str, files: List[str] = None) -> List[Dict[str, Any]]:
    file_list = files or ENTITY_FILE_MAP.get(entity_type)
    if not file_list:
        raise ValueError(f"No file mapping defined for entity type '{entity_type}'")

    all_entities = []
    for file_name in file_list:
        with open(file_name, 'r', encoding='utf-8') as f:
            all_entities.extend(json.loads(line) for line in f)
    return all_entities

def sample_entities(entity_type: str, count: int, batch: str) -> List[Dict[str, Any]]:
    all_data = load_entities(entity_type)
    all_batches = {e.get("batch", "1") for e in all_data}

    if all_batches == {"1"}:
        # Only batch 1 exists across all files (eg. salutations, random_entity)
        return random.sample(all_data, min(count, len(all_data)))

    # Sample from specified batch
    batch_filtered = [e for e in all_data if e.get("batch") == batch]
    if len(batch_filtered) >= count:
        return random.sample(batch_filtered, count)

    # Fallback to batch 1 if sampling batch is not sufficient
    fallback_batch_1 = [e for e in all_data if e.get("batch") == "1"]
    if len(fallback_batch_1) >= count:
        return random.sample(fallback_batch_1, count)

    # Fallback to sampling from all available data
    return random.sample(all_data, min(count, len(all_data)))


### Noise functions ###
def concatenate(text):
    return re.sub(r'\s+', '', text)

def junk(text):
    noise = ''.join(random.choices(string.ascii_letters + string.digits + "!@#$%^&*", k=random.randint(3, 8)))
    insert_positions = sorted(random.sample(range(len(text)), k=min(2, len(text))))
    for pos in insert_positions:
        text = text[:pos] + (noise) + text[pos:]
    return text  

def noise_structure(batch: str, valid_entities: List[str]) -> Tuple[str, List[str]]:
    sampled_entities = valid_entities

    if batch == "1":
        # Clean: evenly spaced valid entities
        text = " ".join(sampled_entities)
        return text, []

    elif batch == "2":
        # Moderate noise: concatenation
        text = ''.join(sampled_entities)
        text = concatenate(text)
        return text, ["concatenate"]

    elif batch == "3":
        # Heavy noise: concatenated and junk
        text = ''.join(sampled_entities)
        text = concatenate(text)
        text = junk(text)
        return text, ["concatenate", "junk"]

    else:
        raise ValueError(f"Unsupported batch: {batch}")

### Short text generation ###
def specified_entities_text(
    entity_types: List[str],
    sampling_batch: str, 
    noise_batch: str,
) -> Dict:
    all_entities = []
    name_entity, org_entity, salutation_entity = None, None, None
    gender = "U"

    # Pre-sample name if needed
    if any(e in entity_types for e in ["name", "email", "salutation", "relationship"]):
        name_candidates = sample_entities("name", count=1, batch=sampling_batch)
        if name_candidates:
            name_entity = name_candidates[0]
            gender = name_entity.get("gender", "U")

    # Pre-sample organisation if needed
    if "organisation" in entity_types or "email" in entity_types:
        org_candidates = sample_entities("organisation", count=1, batch=sampling_batch)
        org_entity = org_candidates[0] if org_candidates else None

    # Match salutation to name's gender
    if "salutation" in entity_types and name_entity:
        salutation_candidates = sample_entities("salutation", count=5, batch=sampling_batch)
        matching_salutations = [
            s for s in salutation_candidates
            if s.get("gender", "U") == gender or s.get("gender") == "U"
        ]
        if matching_salutations:
            salutation_entity = random.choice(matching_salutations)

    # Handle email generation based on available entities
    if "email" in entity_types:
        if name_entity and org_entity:
            email_type = "org_personal"
        elif name_entity:
            email_type = "personal"
        elif org_entity:
            email_type = "org_shared"
        else:
            email_type = "throwaway"
        name_entities = [name_entity] if name_entity else []
        org_entities = [org_entity] if org_entity else []
        email_gen = EmailEntityGenerator(names=name_entities, orgs=org_entities)
        if sampling_batch != noise_batch:
            email_entity = email_gen.generate(batch=sampling_batch, email_type=email_type)  
        else:
            email_entity = email_gen.generate(batch=noise_batch, email_type=email_type)  

    for ent_type in entity_types:
        if ent_type == "email":
            all_entities.append(email_entity)
        elif ent_type == "name":
            if name_entity:
                all_entities.append(name_entity)
        elif ent_type == "organisation":
            if org_entity:
                all_entities.append(org_entity)
        elif ent_type == "salutation":
            if salutation_entity:
                all_entities.append(salutation_entity)
        elif ent_type == "relationship":
            relationship_candidates = sample_entities("relationship", count=5, batch=sampling_batch)
            matching_relationships = [
                r for r in relationship_candidates
                if r.get("gender", "U") == gender or r.get("gender") == "U"
            ]
            if matching_relationships:
                relationship_entity = random.choice(matching_relationships)
                all_entities.append(relationship_entity)
        else:
            sample = sample_entities(ent_type, count=1, batch=sampling_batch)
            all_entities.extend(sample)

    # Combine and noise the text
    valid_texts = [e["text"] for e in all_entities]
    noisy_text, noise_types = noise_structure(noise_batch, valid_texts)

    annotations = []
    for entity in all_entities:
        annotated = entity.copy()
        annotated.pop("batch", None)
        annotations.append(annotated)

    return {
        "text": noisy_text,
        "sampling_batch": sampling_batch,
        "noise_batch": noise_batch,
        "annotations": annotations,
        "noise_types": noise_types
    }


### Dataset generation per batch ###
entity_types = [
    "salutation", "name", "organisation", "phone", "email",
    "relationship", "date", "country", "airport_code", "random_entity"
]

def entity_type_combinations(
    num_samples: int,
    all_entity_types: List[str],
    priority_weights: dict 
) -> List[Tuple[str, ...]]:
    
    min_len, max_len = 3, 7
    combos_set = set()
    combos_list = []

    weights = np.array([priority_weights.get(ent, 1) for ent in all_entity_types], dtype=float)
    weights /= weights.sum() 

    while len(combos_set) < num_samples:
        r = random.randint(min_len, max_len)
        sampled = list(np.random.choice(all_entity_types, size=r, replace=False, p=weights))
        key = tuple(sorted(sampled))  # for uniqueness check

        if key not in combos_set:
            combos_set.add(key)
            random.shuffle(sampled)  # shuffle after uniqueness check
            combos_list.append(tuple(sampled))

    return combos_list

def generate_batch_with_combinations(
    noise_batch: str,
    combos_with_counts: List[Tuple[Tuple[str, ...], int]],
    output_file: str,
    sampling_batch: str
):
    # combos_with_counts: List of (entity_types_tuple, num_samples_to_generate)
    with open(output_file, 'w', encoding='utf-8') as out_f:
        for entity_combo, samples_count in combos_with_counts:
            for _ in range(samples_count):
                try:
                    result = specified_entities_text(
                        list(entity_combo),
                        sampling_batch,
                        noise_batch
                    )
                    out_f.write(json.dumps(result) + '\n')
                except ValueError as e:
                    print(f"Skipped: {e}")

# Generate combos randomly and get unique combos
priority = {"name": 3, "email": 2, "phone": 2, "organisation": 2}  # Higher = more likely to appear
combos = entity_type_combinations(num_samples=40,
                                        all_entity_types=entity_types,
                                        priority_weights=priority)

# Define how many samples per combo
combo_sample_counts = [(combo, 10) for combo in combos]

generate_batch_with_combinations(
    sampling_batch="3",
    noise_batch="3",
    combos_with_counts=combo_sample_counts,
    output_file="multi_entity_dataset/output_b3.jsonl"
)
