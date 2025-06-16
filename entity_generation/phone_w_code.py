import phonenumbers
from phonenumbers import example_number_for_type, format_number, PhoneNumberFormat, PhoneNumberType, national_significant_number
from phonenumbers.data import _COUNTRY_CODE_TO_REGION_CODE
import re
import random
from faker import Faker
import json

faker = Faker()

def get_digit_groups(national_format: str):
    return [len(part) for part in re.findall(r'\d+', national_format)]

def split_number_by_grouping(number_str: str, group_lengths: list):
    parts = []
    i = 0
    for length in group_lengths:
        parts.append(number_str[i:i+length])
        i += length
    return parts

def get_country_calling_code(country_iso_code: str) -> int:
    for code, regions in _COUNTRY_CODE_TO_REGION_CODE.items():
        if country_iso_code.upper() in regions:
            return code
    raise ValueError(f"No calling code found for country {country_iso_code}")

def generate_noisy_formats_with_country_code(country_code: str, national_number: str, digit_groups: list):
    parts = split_number_by_grouping(national_number, digit_groups)
    national_variants = {
        "compact": national_number,
        "space_separated": ' '.join(parts),
        "hyphenated": '-'.join(parts)
    }
    numeric_country_code = str(get_country_calling_code(country_code))

    country_code_variants = [
        f"+{numeric_country_code}",
        f"+({numeric_country_code})",
        f"{numeric_country_code}",
        f"({numeric_country_code})",
    ]

    combined_variants = []
    for cc_variant in country_code_variants:
        for nat_variant in national_variants.values():
            combined_variants.append(f"{cc_variant} {nat_variant}")

    return list(set(combined_variants))

def generate_phone_entry(
        country_code: str, 
        valid_prefixes: list[str], 
        include_phone_type: bool = False,
        batch: str = "1"
        ):
    try:
        sample_number_obj = example_number_for_type(country_code, PhoneNumberType.MOBILE)
        sample_nsn = national_significant_number(sample_number_obj)

        prefix = random.choice(valid_prefixes)
        total_len = len(sample_nsn)
        remaining_len = total_len - len(prefix)
        random_tail = str(faker.random_number(digits=remaining_len)).zfill(remaining_len)

        random_nsn = prefix + random_tail
        national_format = format_number(sample_number_obj, PhoneNumberFormat.NATIONAL)
        digit_groups = get_digit_groups(national_format)
        numeric_country_code = str(get_country_calling_code(country_code))
        noisy_variants = generate_noisy_formats_with_country_code(country_code, random_nsn, digit_groups)
        base_text = random.choice(noisy_variants)
        
        output = {
            "text": base_text,
            "label": "phone_number",
            "clean": f"{numeric_country_code}{random_nsn}",
            "batch": batch,
            "country": country_code
        }
        if include_phone_type:
            phone_type_code = random.choice(['H', 'O', 'M']) # H = home, M = mobile, O = office
            phone_type_label = {'H': 'home', 'O': 'office', 'M': 'mobile'}[phone_type_code]
            if random.choice([True, False]):
                output["text"] = f"{phone_type_code} {base_text}"
            else:
                output["text"] = f"{base_text} {phone_type_code}"
            output["phone_type"] = phone_type_label
        return output
    
    except Exception as e:
        return {"error": f"{country_code}: {str(e)}"}

def generate_multiple_phone_entries(country_code: str, valid_prefixes: list[str], count: int = 10, include_phone_type: bool = False, batch: str = "1"):
    return [generate_phone_entry(country_code, valid_prefixes, include_phone_type, batch) for _ in range(count)]

# Example usage
if __name__ == "__main__":
    results = generate_multiple_phone_entries("SG", ["6", "8", "9"], 40, True)
    with open("phone_numbers_w_code.jsonl", "a", encoding="utf-8") as f:
        for entry in results:
            json.dump(entry, f, ensure_ascii=False)
            f.write("\n")
