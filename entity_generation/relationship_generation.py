from generate_entities import generate_entities

prompt_relationship =""" Generate 50 distinct and realistic relationship terms used for identifying people associated with phone contacts. Output should be in JSON array format.

---

### 1. Categories to Cover:
Select terms from a diverse range of human relationships:
- **Family**: Include nuclear (e.g., "father", "aunt") and extended (e.g., "cousin", "grandmother") terms, plus generational variations.
- **Social**: Friends, roommates, neighbours, mentors, and community ties.
- **Workplace**: Clients, bosses, interns, colleagues, subordinates.
- **Services**: Doctors, tutors, therapists, landlords, lawyers, school teachers.

Each relationship should be unique.
---

### 2. Casing Rules:
The `"text"` field should have **varied casing styles**, mixed across the outputs:
- **UPPERCASE**: e.g., `"MOTHER"`
- **lowercase**: e.g., `"cousin"`
- **Capitalised**: e.g., `"Uncle"`

Each item must randomly use one of the three casing types.

The `"clean"` field must always be in **Title Case** (capitalised first letters of each word).

---

### 3. Output Format:
Return a JSON array with the following structure:
```json

  {
    "text": "{raw_term}",        // Casing: upper/lower/capitalised
    "label": "relationship",
    "clean": "{Title_Case_Term}", 
    "batch": "1",
    "gender": {gender}
  },
  ...

  where gender is M for male, F for female and U for unisex terms.
"""

result = generate_entities(prompt_relationship)

with open("relastionship.jsonl", "w", encoding="utf-8") as f:
    for line in result:
        f.write(line + "\n")