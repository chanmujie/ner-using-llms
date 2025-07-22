import json
import random
import string
import re
from typing import List, Dict, Any, Tuple

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
    "salutation": ["entity_data/salutation.jsonl"],
    "email": ["entity_data/email_b1.jsonl", "entity_data/email_b2.jsonl", "entity_data/email_b3.jsonl"],
    "plate": ["entity_data/car_plate_sg.jsonl"],
    "id": ["entity_data/id_num_sg.jsonl"]
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
    entities = [e for e in load_entities(entity_type) if e.get("batch") == batch]
    return random.sample(entities, min(count, len(entities)))

# Noise functions
def concatenate(text):
    return re.sub(r'\s+', '', text)

def junk(text):
    junk = ['PASSWD', 'INFO', 'ABCD', 'NULL', 'NA']
    if random.random() < 0.5:
        text = random.choice(junk) + ' ' + text
    elif random.random() > 0.5:
        text = text + ' ' + random.choice(junk)
    return text

def duplicate(text):
    if not text.strip():
        return text
    return text + ' ' + text

def noise_structure(batch: str, entities: List[str]) -> Tuple[str, List[str]]:
    noise_types = []

    if batch == "1":
        # Clean: evenly spaced valid entities
        text = " ".join(entities)
        return text, noise_types

    elif batch == "2":
        # Moderate noise: entity-level noising followed by concatenation
        noised_entities = []
        for entity in entities:
            noised_entities.append(entity)

            # if random.random() < 0.5:
            #     noised_entities.append(duplicate(entity))
            #     noise_types.append("duplicate")
            # else:
            #     noised_entities.append(entity)
        text = concatenate("".join(noised_entities))
        noise_types.append("concatenate")
        return text, list(set(noise_types))

    elif batch == "3":
        # Heavy noise
        noised_entities = []
        for entity in entities:
            if random.random() < 0.3:
                noised_entities.append(junk(entity))
                noise_types.append("junk")
            else:
                noised_entities.append(duplicate(entity))
                noise_types.append("duplicate")
        text = concatenate("".join(noised_entities))
        noise_types.append("concatenate")

        if random.random() < 0.5:
            text = junk(text)
            noise_types.append("junk")
        text = concatenate(text)
        return text, list(set(noise_types))

    else:
        raise ValueError(f"Unsupported batch: {batch}")

def generate_single_entity_text(entity_type: str, sampling_batch: str, noise_batch: str) -> Dict:
    try:
        sampled_entities = sample_entities(entity_type, count=7, batch=sampling_batch)  # max 7
    except ValueError as e:
        raise ValueError(f"Sampling failed: {e}")

    if not sampled_entities or len(sampled_entities) < 2:
        raise ValueError("Not enough valid entity samples.")

    # Pick a random subset to actually use
    use_count = random.randint(2, min(7, len(sampled_entities)))
    used_entities = random.sample(sampled_entities, use_count)
    valid_texts = [e["text"] for e in used_entities]

    # Generate the noisy string and record noise types
    noisy_text, noise_types = noise_structure(noise_batch, valid_texts)

    annotations = []
    for entity in used_entities:
        annotated = entity.copy()
        annotated.pop("batch", None)
        if noise_batch in {"2", "3"}:
            annotated["text"] = re.sub(r"\s+", "", annotated["text"])
        annotations.append(annotated)

    return {
        "text": noisy_text,
        "sampling_batch": sampling_batch,
        "noise_batch": noise_batch,
        "annotations": annotations,
        "noise_types": noise_types
    }

def run_single_entity_batch(
    entity_type: str,
    sampling_batch: str,
    noise_batch: str,
    num_samples: int,
    output_file: str
):
    with open(output_file, 'a', encoding='utf-8') as out_f:
        for _ in range(num_samples):
            try:
                result = generate_single_entity_text(entity_type, sampling_batch, noise_batch)
                out_f.write(json.dumps(result) + '\n')
            except ValueError as e:
                print(f"Skipped: {e}")


run_single_entity_batch(
    entity_type="plate",
    sampling_batch="1",
    noise_batch="1",
    num_samples=30,
    output_file="datasets/single_entity_dataset/plate_b1.jsonl"
)
