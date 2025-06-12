import json
import random
import re

### Noise functions ###
def random_casing(text):
    return ''.join(
        c.upper() if random.random() < 0.5 else c.lower()
        for c in text
    )

def swap_char(text: str, num_swaps: int = 1) -> str:
    if len(text) < 2:
        return text
    text_list = list(text)
    for _ in range(num_swaps):
        i, j = random.sample(range(len(text_list)), 2)
        text_list[i], text_list[j] = text_list[j], text_list[i]
    return ''.join(text_list)

def punctuation(text):
    text = text.replace('/', '').replace('-', '=')
    if random.random() < 0.3:
        text = re.sub(r'(?<=\w)(?=\w)', '.', text, count=1)
    return text

def typo(text):
    typo_map = {'e': '3', 'a': '@', 'o': '0', 'i': '1', 's': '$'}
    chars = list(text)
    for i in range(len(chars)):
        if chars[i].lower() in typo_map and random.random() < 0.2:
            chars[i] = typo_map[chars[i].lower()]
    return ''.join(chars)

def truncation(text):
    if len(text) > 5:
        cut_point = random.randint(len(text) // 2, len(text) - 1)
        return text[:cut_point]
    return text

def duplicate(text):
    if not text.strip():
        return text
    return text + ' ' + text

def random_char(text):
    junk = ['#', '%', '^', '*', '~', '|', '`']
    insert_positions = sorted(random.sample(range(len(text)), k=min(2, len(text))))
    for pos in insert_positions:
        text = text[:pos] + random.choice(junk) + text[pos:]
    return text  

def junk(text):
    junk = ['PASSWD', 'INFO', 'ABCD', 'NULL', 'NA']
    if random.random() < 0.5:
        text = random.choice(junk) + ' ' + text
    if random.random() < 0.5:
        text = text + ' ' + random.choice(junk)
    return text

### Apply noise functions by batch ###
# Batch 2 (B2)
def apply_noise_b2(text):
    pipeline = [typo, truncation]
    # Name, Name+ALias, Relationship, Organisation: random_casing, typo, truncation, swap_char
    # Date: punctuation, typo, truncation
    # Phone number: typo, truncation
    # Email: random_casing, punctuation, typo, truncation

    max_tries = 5
    for _ in range(max_tries):
        text_copy = text
        random.shuffle(pipeline)
        num_to_apply = random.randint(1, 4)
        applied_functions = []

        for fn in pipeline[:num_to_apply]:
            old_text = text_copy
            text_copy = fn(text_copy)
            if text_copy != old_text:
                applied_functions.append(fn.__name__)

        if applied_functions:
            return text_copy, applied_functions

    # Apply one noise forcibly if none applied
    fn = random.choice(pipeline)
    return fn(text), [fn.__name__]

    

# Batch 3 (B3)
def apply_noise_b3(text):
    pipeline = [typo, truncation, duplicate, junk]
    # Name, Name+ALias, Relationship, Organisation: random_casing, typo, truncation, duplicate, junk, swap_char
    # Date: punctuation, typo, truncation, duplicate
    # Phone number: typo, truncation, duplicate, junk, random_char
    # Email: random_casing, punctuation, typo, truncation, duplicate

    max_tries = 7
    for _ in range(max_tries):
        text_copy = text
        random.shuffle(pipeline)
        num_to_apply = random.randint(1, 4)
        applied_functions = []

        for fn in pipeline[:num_to_apply]:
            old_text = text_copy
            text_copy = fn(text_copy)
            if text_copy != old_text:
                applied_functions.append(fn.__name__)

        if applied_functions:
            return text_copy, applied_functions

    # apply one noise forcibly if still none applied
    fn = random.choice(pipeline)
    return fn(text), [fn.__name__]

    

def process_jsonl_lines_b2(input_lines):
    noised_lines = []
    for line in input_lines:
        data = json.loads(line)
        clean_text = data["clean"]

        noised_text, applied_noises = apply_noise_b2(clean_text)

        data["text"] = noised_text
        data["batch"] = "2"
        if applied_noises:
            data["noise"] = applied_noises
            data["is_valid"] = "truncation" not in applied_noises

        noised_lines.append(json.dumps(data, ensure_ascii=False))
    return noised_lines

# for number, email, date, name
def process_jsonl_num_b2(input_lines):
    noised_lines = []
    for line in input_lines:
        data = json.loads(line)

        original_text = data.get("text", "")
        clean_text = data.get("clean", "")

        noised_text, applied_noises = apply_noise_b2(original_text)

        data["text"] = noised_text
        data["clean"] = clean_text  
        data["batch"] = "2"
        if applied_noises:
            data["noise"] = applied_noises
            # phone number, email, date, name/alias become invalid when truncation applied
            data["is_valid"] = "truncation" not in applied_noises

        noised_lines.append(json.dumps(data, ensure_ascii=False))
    return noised_lines

def process_jsonl_lines_b3(input_lines):
    noised_lines = []
    for line in input_lines:
        data = json.loads(line)
        clean_text = data["clean"]

        noised_text, applied_noises = apply_noise_b3(clean_text)

        data["text"] = noised_text
        data["batch"] = "3"
        if applied_noises:
            data["noise"] = applied_noises
            data["is_valid"] = "truncation" not in applied_noises

        noised_lines.append(json.dumps(data, ensure_ascii=False))
    return noised_lines

# For phone number, email, date, names/alias
def process_jsonl_num_b3(input_lines):
    noised_lines = []
    for line in input_lines:
        data = json.loads(line)

        original_text = data.get("text", "")
        clean_text = data.get("clean", "")

        noised_text, applied_noises = apply_noise_b3(original_text)

        data["text"] = noised_text
        data["clean"] = clean_text  
        data["batch"] = "3"
        if applied_noises:
            data["noise"] = applied_noises
            # phome number, email, date, name/alias become invalid when truncation applied
            data["is_valid"] = not any(n in applied_noises for n in ["truncation", "random_char"])

        noised_lines.append(json.dumps(data, ensure_ascii=False))
    return noised_lines


if __name__ == "__main__":
    input_file = "{entity_b1}.jsonl"
    output_file = "{entity_b2}.jsonl"

    with open(input_file, "r", encoding="utf-8") as f:
        input_lines = [line.strip() for line in f if line.strip()]
    noisy_output = process_jsonl_num_b2(input_lines)
    
    with open(output_file, "w", encoding="utf-8") as f:
        for line in noisy_output:
            f.write(line + "\n")
    