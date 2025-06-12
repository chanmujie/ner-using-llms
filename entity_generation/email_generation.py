import json
import re
import random
from typing import List, Dict, Any, Optional

with open("entity_list/personal_domains.json", "r", encoding="utf-8") as f:
    PERSONAL_DOMAINS = json.load(f)
with open("entity_list/throwaway_domain.json", "r", encoding="utf-8") as f:
    THROWAWAY_DOMAINS = json.load(f)
ORG_SHARED_HANDLES = [
    "support","help","service","care","contact",
    "sales","info","enquiries","business","partnerships",
    "orders","logistics","shipping","warehouse",
    "billing","accounts","admin","payroll","marketing",
    "press","media","events","team","hr","it","office"
]

def load_jsonl(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return [json.loads(line.strip()) for line in f if line.strip()]

def normalise_org_name(name):
    name = re.sub(r"\b(pte\s*ltd|ltd|inc|corp|co|limited|gmbh|plc|llc)\b", "", name, flags=re.IGNORECASE)
    name = re.sub(r"[^a-zA-Z0-9]", "", name)
    return name.lower()

def generate_personal_email(name, batch: str):
    name_parts = name.lower().split()
    first, last = name_parts[0], name_parts[-1]

    first_initial = first[0] if first else ""
    last_initial = last[0] if last else ""

    # Generate varied patterns
    patterns = []
    patterns.extend([
        f"{first}{last}",
        f"{first}.{last}",
        f"{first}_{last}",
        f"{first_initial}{last}",
        f"{first}{last_initial}",
        f"{last}{first}",
        f"{last}.{first}",
        f"{last}_{first}",
        f"{first_initial}.{last}",
        f"{first}-{last}",
    ])
    patterns.extend([
        f"{first}{random.randint(10,99)}",
        f"{first}_{random.randint(100,999)}",
        f"{first}{last}{random.randint(1,9)}",
        f"{last}{random.randint(1,99)}"
    ])

    # Deduplicate patterns (in case of overlaps)
    patterns = list(set(patterns))

    pattern = random.choice(patterns)
    domain = random.choice(PERSONAL_DOMAINS)
    clean_email = f"{pattern}@{domain}"
    if batch != '1':
        noisy_email, is_invalid = apply_email_noise(clean_email, batch)
    else:
        noisy_email = clean_email
        is_invalid = False

    return {
        "text": noisy_email,
        "label": "email",
        "clean": clean_email,
        "batch": batch,
        "type": "personal",
        "name_source": name,
        "organisation_source": None,
        "invalid": is_invalid
    }

def generate_throwaway_emails(name, batch: str):
    name_parts = name.lower().split()
    first, last = name_parts[0], name_parts[-1]

    first_initial = first[0] if first else ""
    last_initial = last[0] if last else ""

    # Generate varied patterns
    patterns = []
    patterns.extend([
        f"{first}{last}",
        f"{first}.{last}",
        f"{first}_{last}",
        f"{first_initial}{last}",
        f"{first}{last_initial}",
        f"{last}{first}",
        f"{last}.{first}",
        f"{last}_{first}",
        f"{first_initial}.{last}",
        f"{first}-{last}",
    ])
    patterns.extend([
        f"{first}{random.randint(10,99)}",
        f"{first}_{random.randint(100,999)}",
        f"{first}{last}{random.randint(1,9)}",
        f"{last}{random.randint(1,99)}"
    ])

    # Deduplicate patterns (in case of overlaps)
    patterns = list(set(patterns))

    pattern = random.choice(patterns)
    domain = random.choice(THROWAWAY_DOMAINS)
    clean_email = f"{pattern}@{domain}"
    if batch != '1':
        noisy_email, is_invalid = apply_email_noise(clean_email, batch)
    else:
        noisy_email = clean_email
        is_invalid = False

    return {
        "text": noisy_email,
        "label": "email",
        "clean": clean_email,
        "batch": batch,
        "type": "throwaway",
        "name_source": name,
        "organisation_source": None,
        "invalid": is_invalid
    }

def generate_organisational_personal_emails(name, org, batch: str):
    name_parts = name.lower().split()
    domain = normalise_org_name(org) + ".com"
    first, last = name_parts[0], name_parts[-1]

    first_initial = first[0] if first else ""
    last_initial = last[0] if last else ""

    # Generate varied patterns
    patterns = []
    patterns.extend([
        f"{first}{last}",
        f"{first}.{last}",
        f"{first}_{last}",
        f"{first_initial}{last}",
        f"{first}{last_initial}",
        f"{last}{first}",
        f"{last}.{first}",
        f"{last}_{first}",
        f"{first_initial}.{last}",
        f"{first}-{last}",
    ])

    pattern = random.choice(patterns)
    clean_email = f"{pattern}@{domain}"
    if batch != '1':
        noisy_email, is_invalid = apply_email_noise(clean_email, batch)
    else:
        noisy_email = clean_email
        is_invalid = False

    return {
        "text": noisy_email,
        "label": "email",
        "clean": clean_email,
        "batch": batch,
        "type": "org_personal",
        "name_source": name,
        "organisation_source": org,
        "invalid": is_invalid
    }

def generate_organisational_shared_emails(org, batch: str):
    domain = normalise_org_name(org) + ".com"
    handle = random.choice(ORG_SHARED_HANDLES)
    clean_email = f"{handle}@{domain}"
    if batch != '1':
        noisy_email, is_invalid = apply_email_noise(clean_email, batch)
    else:
        noisy_email = clean_email
        is_invalid = False

    return {
        "text": noisy_email,
        "label": "email",
        "clean": clean_email,
        "batch": batch,
        "type": "personal",
        "name_source": None,
        "organisation_source": None,
        "invalid": is_invalid
    }

# Noise Functions
def mixed_case_noise(email):
    return ''.join(
        char.upper() if random.random() < 0.5 else char.lower()
        for char in email
    )

def slash_noise(email):
    at_replacements = ["//", "/", "-", "(at)", "|"]
    chosen_at = random.choice(at_replacements)
    email = email.replace("@", chosen_at)
    return email

def malformed_domain(email):
    domain_match = re.search(r"@([\w.-]+\.\w+)", email)
    if not domain_match:
        return email
    domain = domain_match.group(1)
    dot_replacement = random.choice(['/', ',', '..', '-', ''])  
    malformed = domain.replace('.', dot_replacement)
    return email.replace(domain, malformed)

def domain_extension(email): 
    return re.sub(r"\.\w+$", ".c0m", email)

def missing_at_symbol(email):  # jontanorg.com
    return email.replace("@", "", 1)

def truncate_email(email: str) -> str:
    max_len = random.randint(8, len(email) - 1)
    return email[:max_len]
 
# Apply noise functions to email based on batch
def apply_email_noise(email: str, batch: str) :
    noise_levels = {
        "2": [mixed_case_noise, domain_extension],
        "3": [mixed_case_noise, slash_noise, malformed_domain, domain_extension, truncate_email, missing_at_symbol]
    }

    num_noises = {
        "2": random.randint(1, 2),
        "3": random.randint(1, 3)
    }

    selected_funcs = random.sample(noise_levels.get(batch, []), num_noises.get(batch, 0))
    invalid = False
    for fn in selected_funcs:
        email = fn(email)
        if "@" not in email or "." not in email.split("@")[-1]:
            invalid = True
    return email, invalid

class EmailEntityGenerator:
    def __init__(self, names: List[Dict], orgs: List[Dict]):
        self.names = names
        self.orgs = orgs

    def generate(self, batch: str, email_type: str) -> Dict:
        name = random.choice(self.names)["clean"] if self.names else None
        org = random.choice(self.orgs)["clean"] if self.orgs else None

        if email_type == "personal":
            return self._generate_personal_email(name, batch)
        elif email_type == "throwaway":
            return self._generate_throwaway_email(name, batch)
        elif email_type == "org_personal":
            if not name or not org:
                raise ValueError("org_personal email requires both name and organisation")
            return self._generate_org_personal_email(name, org, batch)
        elif email_type == "org_shared":
            if not org:
                raise ValueError("org_shared email requires organisation")
            return self._generate_org_shared_email(org, batch)
        else:
            raise ValueError(f"Unknown email type: {email_type}")

    def _generate_personal_email(self, name: str, batch: str) -> Dict:
        from email_generation import generate_personal_email
        return generate_personal_email(name, batch)

    def _generate_throwaway_email(self, name: str, batch: str) -> Dict:
        from email_generation import generate_throwaway_emails
        return generate_throwaway_emails(name, batch)

    def _generate_org_personal_email(self, name: str, org: str, batch: str) -> Dict:
        from email_generation import generate_organisational_personal_emails
        return generate_organisational_personal_emails(name, org, batch)

    def _generate_org_shared_email(self, org: str, batch: str) -> Dict:
        from email_generation import generate_organisational_shared_emails
        return generate_organisational_shared_emails(org, batch)

name_filepath = [
    "entity_data/name_sg_c_b1.jsonl",
    "entity_data/name_sg_m_b1.jsonl",
    "entity_data/name_sg_i_b1.jsonl",
    "entity_data/name_sg_e_b1.jsonl"
]
def load_multiple_jsonl(filepaths: List[str]) -> List[Dict]:
    all_data = []
    for path in filepaths:
        all_data.extend(load_jsonl(path))
    return all_data

# Usage
names = load_multiple_jsonl(name_filepath)
orgs = load_jsonl("entity_data/org_sg_b1.jsonl")
email_gen = EmailEntityGenerator(names, orgs)
batches = ["3"]
email_types = ["personal", "throwaway", "org_personal", "org_shared"]

def generate_email_dataset(
    generator: EmailEntityGenerator,
    batches: List[str],
    types: List[str],
    samples_per_combo: int = 100
) -> List[Dict]:
    dataset = []
    for batch in batches:
        for email_type in types:
            for _ in range(samples_per_combo):
                try:
                    sample = generator.generate(batch=batch, email_type=email_type)
                    dataset.append(sample)
                except Exception as e:
                    print(f"Skipping {email_type} in batch {batch} due to error: {e}")
    return dataset

def save_jsonl(data: List[Dict], path: str):
    with open(path, "w", encoding="utf-8") as f:
        for entry in data:
            f.write(json.dumps(entry) + "\n")

# Generate dataset
dataset = generate_email_dataset(email_gen, batches, email_types, samples_per_combo=100)
save_jsonl(dataset, "emails_b3.jsonl")
