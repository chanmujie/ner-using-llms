import json
import random
import string
import re
from typing import List, Dict, Any, Tuple

ENTITY_FILE_MAP = {
    "name": ["entity_data/name_sg_c_b1.jsonl", "entity_data/name_sg_c_b2.jsonl", "entity_data/name_sg_c_b3.jsonl", 
             "entity_data/name_sg_m_b1.jsonl", "entity_data/name_sg_m_b2.jsonl", "entity_data/name_sg_m_b3.jsonl", 
              "entity_data/name_sg_i_b1.jsonl", "entity_data/name_sg_i_b2.jsonl", "entity_data/name_sg_i_b2.jsonl", 
              "entity_data/name_sg_e_b1.jsonl", "entity_data/name_sg_e_b2.jsonl", "entity_data/name_sg_e_b3.jsonl"],
    "phone": ["entity_data/phone_wo_code_sg_b1.jsonl", "entity_data/phone_wo_code_sg_b2.jsonl", "entity_data/phone_wo_code_sg_b2.jsonl",
              "entity_data/phone_code_sg_b1.jsonl", "entity_data/phone_code_sg_b2.jsonl", "entity_data/phone_code_sg_b3.jsonl"],
    "relationship": ["entity_data/relationship_b1.jsonl", "entity_data/relationship_b2.jsonl", "entity_data/relationship_b3.jsonl"],
    "date": ["entity_data/date_b1.jsonl", "entity_data/date_b2.jsonl", "entity_data/date_b3.jsonl"],
    "organisation": ["entity_data/org_sg_b1.jsonl","entity_data/org_sg_b2.jsonl","entity_data/org_sg_b3.jsonl"],
    "country": ["entity_data/country_entity.jsonl"],
    "airport_code": ["entity_data/airport_codes.jsonl"],
    "random_entity": ["entity_data/car_plate_sg.jsonl", "entity_data/id_num_sg.jsonl"],
    "salutation": ["entity_data/salutation.jsonl"],
    "email": ["entity_data/email_b1.jsonl", "entity_data/email_b2.jsonl", "entity_data/email_b2.jsonl"]
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

def junk(entity: str) -> str:
    noise = ''.join(random.choices(string.ascii_letters + string.digits + "!@#$%^&*", k=random.randint(3, 8)))
    return entity + noise

def noise_structure(batch: str, valid_entities: List[str]) -> Tuple[str, List[str]]:
    num_entities = random.randint(2, 7)
    sampled_entities = random.sample(valid_entities, k=min(num_entities, len(valid_entities)))

    if batch == "1":
        # Clean: evenly spaced valid entities
        text = " ".join(sampled_entities)
        return text, []

    elif batch == "2":
        # Moderate noise: concatenation with some junk
        text = ''.join(sampled_entities)
        pipeline = [concatenate]
        applied_functions = []
        for fn in random.sample(pipeline, k=random.randint(1, len(pipeline))):
            old = text
            text = fn(text)
            if text != old:
                applied_functions.append(fn.__name__)
        return text, applied_functions

    elif batch == "3":
        # Heavy noise: concatenated and more junk
        text = ''.join(sampled_entities)
        pipeline = [concatenate, junk]
        applied_functions = []
        for fn in random.sample(pipeline, k=random.randint(2, len(pipeline))):
            old = text
            text = fn(text)
            if text != old:
                applied_functions.append(fn.__name__)
        return text, applied_functions

    else:
        raise ValueError(f"Unsupported batch: {batch}")

def generate_single_entity_text(entity_type: str, sampling_batch: str, noise_batch: str) -> Dict:
    try:
        sampled_entities = sample_entities(entity_type, count=random.randint(2, 7), batch=sampling_batch)
    except ValueError as e:
        raise ValueError(f"Sampling failed: {e}")

    if not sampled_entities or len(sampled_entities) < 2:
        raise ValueError("Not enough valid entity samples.")

    valid_texts = [e["text"] for e in sampled_entities]

    noisy_text, noise_types = noise_structure(entity_type, noise_batch, valid_texts)

    annotations = []
    for entity in sampled_entities:
        annotated = entity.copy()
        annotated.pop("start", None)
        annotated.pop("end", None)
        annotations.append(annotated)

    return {
        "text": noisy_text,
        "sampling_batch": sampling_batch,
        "batch": noise_batch,  
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
    with open(output_file, 'w', encoding='utf-8') as out_f:
        for _ in range(num_samples):
            try:
                result = generate_single_entity_text(entity_type, sampling_batch, noise_batch)
                out_f.write(json.dumps(result) + '\n')
            except ValueError as e:
                print(f"Skipped: {e}")



run_single_entity_batch(
    entity_type="country",
    sampling_batch="1",
    noise_batch="3",
    num_samples=50,
    output_file="output/country_b3.jsonl"
)
