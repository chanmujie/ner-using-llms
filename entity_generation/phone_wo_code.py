import phonenumbers
from phonenumbers import example_number_for_type, format_number, PhoneNumberFormat, PhoneNumberType, national_significant_number, PhoneMetadata
import re
import random
from faker import Faker
import json

faker = Faker()

# Extract digit group lengths from national number format
def get_digit_groups(national_format: str):
    return [len(part) for part in re.findall(r'\d+', national_format)]

# Split number string by group lengths
def split_number_by_grouping(number_str: str, group_lengths: list):
    parts = []
    i = 0
    for length in group_lengths:
        parts.append(number_str[i:i+length])
        i += length
    return parts

# Generate noisy formats for any country
def generate_noisy_formats(number_str: str, digit_groups: list):
    parts = split_number_by_grouping(number_str, digit_groups)
    variants = {
        "compact": number_str,
        "space_separated": ' '.join(parts),
        "hyphenated": '-'.join(parts)
    }
    return variants

def generate_phone_entry(country_code: str, valid_prefixes: list[str], batch: str = "1"):
    try:
        sample_number_obj = example_number_for_type(country_code, PhoneNumberType.MOBILE)
        sample_nsn = national_significant_number(sample_number_obj)

        prefix = random.choice(valid_prefixes)
        total_len = len(sample_nsn)
        remaining_len = total_len - len(prefix)
        random_tail = str(faker.random_number(digits=remaining_len)).zfill(remaining_len)

        random_nsn = prefix + random_tail
        number_obj = phonenumbers.parse(random_nsn, country_code)
        national_format = format_number(sample_number_obj, PhoneNumberFormat.NATIONAL)
        digit_groups = get_digit_groups(national_format)

        clean_number = format_number(number_obj, PhoneNumberFormat.E164).replace('+', '')
        noisy_variants = generate_noisy_formats(random_nsn, digit_groups)

        return {
            "text": noisy_variants[random.choice(list(noisy_variants.keys()))],
            "label": "phone_number",
            "clean": clean_number,
            "batch": batch,
            "country": country_code
        }

    except Exception as e:
        return {"error": f"{country_code}: {str(e)}"}

def generate_multiple_phone_entries(country_code: str, valid_prefixes: list[str], count: int = 10, batch: str = "1"):
    return [generate_phone_entry(country_code, valid_prefixes, batch) for _ in range(count)]

if __name__ == "__main__":
    results = generate_multiple_phone_entries("SG", ["6", "8", "9"], 80)
    with open("phone_numbers_wo_code.jsonl", "w", encoding="utf-8") as f:
        for entry in results:
            json.dump(entry, f, ensure_ascii=False)
            f.write("\n")


