from generate_entities import generate_entities
from entity_definition import NameList

prompt_car_id = """Generate 20 entries of car plate numbers and 20 entries of national ID numbers in JSON lines format. Follow these guidelines:

#### **1. Car Plate Numbers (Label: "plate")**  
- **Formats (Singapore-style):**  
  - `SBA 1234 A` (Standard)  
  - `SGX 5678 B` (Premium)  
  - `E 9999 C` (Early series)  
- **Noise Rules for `text`:**  
  - No spaces: `SBA1234A` → `"SBA 1234 A"`  
  - Lowercase: `"sba 1234 a"` → `clean`: `"SBA 1234 A"`  
- **Clean Format:**  
  - Uppercase, single space between groups (e.g., `"SBA 1234 A"`).  

#### **2. National ID Numbers (Label: "id")**  
- **Formats (Singapore NRIC/FIN):**  
  - `S1234567A` (NRIC). Must start with one of `S` or `T`.  
  - `G9876543X` (FIN). Must start with one of `F`, `G` or `M`.
- **Noise Rules for `text`:**   
  - Extra chars: `"S-123-4567-A"` → `clean`: `"S1234567A"`  
  - Lowercase: `"s1234567a"` → `clean`: `"S1234567A"`  
- **Clean Format:**  
  - No separators, uppercase (e.g., `"S1234567A"`).  

#### **Output Structure (JSON Lines):**  
```json
{"text": "sba1234a", "label": "plate", "clean": "SBA 1234 A", "batch": "1"}  
{"text": "G-987-6543-X", "label": "id", "clean": "G9876543X", "batch": "1"}  
"""


result = generate_entities(prompt_car_id)

with open("car_n_id_sg.jsonl", "w", encoding="utf-8") as f:
    for line in result:
        f.write(line + "\n")