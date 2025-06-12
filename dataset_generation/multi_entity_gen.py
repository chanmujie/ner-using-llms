import json
import random
import string
import re
from typing import List, Dict, Any, Tuple
from email_generation import EmailEntityGenerator

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
    entities = [e for e in load_entities(entity_type) if e.get("batch") == batch]
    return random.sample(entities, min(count, len(entities)))


def concatenate(text):
    return re.sub(r'\s+', '', text)

def junk(entity: str) -> str:
    noise = ''.join(random.choices(string.ascii_letters + string.digits + "!@#$%^&*", k=random.randint(3, 8)))
    insert_positions = sorted(random.sample(range(len(text)), k=min(2, len(text))))
    for pos in insert_positions:
        text = text[:pos] + (noise) + text[pos:]
    return text  

def noise_structure(batch: str, valid_entities: List[str]) -> Tuple[str, List[str]]:
    num_entities = random.randint(2, 7)
    sampled_entities = random.sample(valid_entities, k=min(num_entities, len(valid_entities)))

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

############################################################
def generate_specified_entities_text(
    entity_types: List[str],
    sampling_batch: str, 
    noise_batch: str,
) -> Dict:
    all_entities = []
    name_entity, org_entity, salutation_entity = None, None, None

    # Pre-sample name if needed
    if "name" in entity_types or "email" in entity_types or "salutation" in entity_types:
        name_candidates = sample_entities("name", count=1, batch=sampling_batch)
        name_entity = name_candidates[0] if name_candidates else None

    # Pre-sample org if needed
    if "organisation" in entity_types or "email" in entity_types:
        org_candidates = sample_entities("organisation", count=1, batch=sampling_batch)
        org_entity = org_candidates[0] if org_candidates else None

    # If salutation is required, match to the name's gender
    if "salutation" in entity_types and name_entity:
        name_gender = name_entity.get("gender", "U")
        salutation_candidates = sample_entities("salutation", count=5, batch=sampling_batch)
        matching_salutations = [
            s for s in salutation_candidates
            if s.get("gender", "U") == name_gender or s.get("gender") == "U"
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
        try:
            email_entity = email_gen.generate(batch=noise_batch, email_type=email_type)   
        except ValueError as e:
            raise ValueError(f"Email generation failed: {e}")
        
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
        else:
            sample = sample_entities(ent_type, count=1, batch=sampling_batch)
            all_entities.extend(sample)

    # Extract clean entity text for the noise structure
    valid_texts = [e["text"] for e in all_entities]

    noisy_text, noise_types = noise_structure(noise_batch, valid_texts)

    annotations = []
    for entity in all_entities:
        annotated = entity.copy()
        annotated.update({
            "sampling_batch": sampling_batch,
            "noise_batch": noise_batch
        })
        annotated.pop("batch", None)
        annotations.append(annotated)

    return {
        "text": noisy_text,
        "sampling_batch": sampling_batch,
        "noise_batch": noise_batch,
        "annotations": annotations,
        "noise_types": noise_types
    }

def run_specified_batch(
    entity_types: List[str],
    sampling_batch: str, 
    noise_batch: str,
    num_samples: int,
    output_file: str
):
    with open(output_file, 'w', encoding='utf-8') as out_f:
        for _ in range(num_samples):
            try:
                result = generate_specified_entities_text(entity_types, sampling_batch, noise_batch)
                out_f.write(json.dumps(result) + '\n')
            except ValueError as e:
                print(f"Skipped: {e}")

run_specified_batch(
    entity_types=["organisation", "phone", "email", "name", "salutation"],
    sampling_batch="1",
    noise_batch="1",
    num_samples=10,
    output_file="output/sample_b1.jsonl"
)
