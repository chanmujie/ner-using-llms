from generate_entities import generate_entities

prompt_organisation_sg = (
    """Generate 80 realistic and varied Singaporean organisation names in JSON lines format with:

    1. **Organisation Types**:
    - Private companies (tech, F&B, finance)
    - Government agencies
    - Educational institutions
    - Religious/NPOs
    - SMEs/family businesses

    2. **Industry Classification**:
    - Technology, Finance, Education, Healthcare, Government
    - Retail, F&B, Legal, Construction, Transportation

    3. **Naming Rules**:
    - Follow Singaporean naming conventions:
        * Common suffixes: "Pte Ltd", "Ltd", "Sdn Bhd"
        * Romanised multilingual names (English/Chinese/Malay/Tamil)
    Avoid obviously synthetic names.
    
    **Casing for each full name must be ***consistently*** one of the following:**
    - Capitalisation
    - ALL CAPS
    - lowercase

    4. **Output Fields**:
    ```json
    {
    "text": "{noisy_name}",
    "label": "organisation",
    "clean": "{properly_formatted_name}",
    "industry": "{industry}",
    "batch": "1"
    }
    Where:
    - `text` is a generated version of the name
    - `clean` is the properly formatted version using Capitalisation.
    - `label` is always "name"
    - `batch` is always "1" """
)

result = generate_entities(prompt_organisation_sg)

with open("organisation_sg.jsonl", "w", encoding="utf-8") as f:
    for line in result:
        f.write(line + "\n")