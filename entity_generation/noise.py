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
    elif random.random() > 0.5:
        text = text + ' ' + random.choice(junk)
    return text

def phone_separators(text):
    text = text.replace('+', random.choice(['--', '#', '"']))
    text = re.sub(r'[-/]', lambda m: random.choice(['.', '~', '/']), text)
    return text

### Apply noise functions by batch ###  
def apply_noise(text, label, batch):
    pipelines = {
        "2": {
            "name":         [random_casing, typo, swap_char],
            "relationship": [random_casing, typo, truncation, swap_char],
            "organisation": [random_casing, typo, truncation, swap_char],
            "date":         [random_casing, punctuation, typo],
            "phone_number": [phone_separators, junk],
            "email":        [random_casing, typo],
        },
        "3": {
            "name":         [random_casing, typo, truncation, duplicate, junk, swap_char],
            "relationship": [random_casing, typo, truncation, duplicate, junk, swap_char],
            "organisation": [random_casing, typo, truncation, duplicate, junk, swap_char],
            "date":         [random_casing, punctuation, typo, truncation, duplicate],
            "phone_number": [truncation, duplicate, junk, random_char, phone_separators],
            "email":        [random_casing, typo, truncation, duplicate],
        }
    }
    pipeline = pipelines.get(str(batch), {}).get(label, [typo, random_casing])
    max_tries = 5 if batch == 2 else 7
    for _ in range(max_tries):
        text_copy = text
        random.shuffle(pipeline)
        num_to_apply = random.randint(1, min(len(pipeline), 3))
        applied_functions = []

        for fn in pipeline[:num_to_apply]:
            old_text = text_copy
            text_copy = fn(text_copy)
            if text_copy != old_text:
                applied_functions.append(fn.__name__)

        if applied_functions:
            return text_copy, applied_functions

    fn = random.choice(pipeline)
    return fn(text), [fn.__name__]

### Process entity samples ###
def process_jsonl(input_lines, batch):
    noised_lines = []
    for line in input_lines:
        data = json.loads(line)
        text = data.get("text", "")
        clean = data.get("clean", "")
        label = data.get("label", "")

        noised_text, applied_noises = apply_noise(text, label, batch)
        data["text"] = noised_text
        data["clean"] = clean
        data["batch"] = str(batch)

        if applied_noises:
            data["noise"] = applied_noises
            if batch == 2:
                invalid_noise = any(n in applied_noises for n in ["truncation", "swap_char"])
                data["is_valid"] = not invalid_noise
            elif batch == 3:
                invalid_noise = any(n in applied_noises for n in ["truncation", "swap_char"])
                data["is_valid"] = not invalid_noise

        noised_lines.append(json.dumps(data, ensure_ascii=False))
    return noised_lines

### Execution ###
if __name__ == "__main__":
    input_file = "entity_data/date_b1.jsonl"
    output_file = "entity_data/date_test_b3.jsonl"

    with open(input_file, "r", encoding="utf-8") as f:
        input_lines = [line.strip() for line in f if line.strip()]
    noisy_output = process_jsonl(input_lines, 3)
    
    with open(output_file, "w", encoding="utf-8") as f:
        for line in noisy_output:
            f.write(line + "\n")