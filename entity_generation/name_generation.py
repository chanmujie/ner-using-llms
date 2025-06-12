from generate_entities import generate_entities

prompt_name_malay =(
    """Generate 50 realistic full names representing Singaporean Malay individuals.
    Each name must follow this structural pattern: [Given name(s)] [Patronymic noun] [Father’s given name]
    Each name should have 1 to 3 given names.
    The patronymic noun should be abbreviated to 'B.' 10 times.

    **Casing for each full name must be ***consistently*** one of the following:**
    - Capitalisation
    - ALL CAPS
    - lowercase
    Each casing type must be used at least 10 times.
    
    Return the names as JSON lines in the following format:
    {\"text\": \"{noisy_name1}\", \"label\": \"name\", \"clean\": \"{name1}\", \"gender\": \"{gender}\", \"batch\": \"1\"}

    Where:
    - `text` is a generated version of the name
    - `clean` is the properly formatted version using Capitalisation. If patronymic nouns are abbreviated in the generated version of the name, spell out correct patronymic noun in full.
    - `label` is always "name"
    - `gender` is M for male names or F for female names.
    - `batch` is always "1" """
)

prompt_name_indian =(
    """Generate 50 realistic full names representing Singaporean Indian individuals.
    Each name must follow one of the following structural patterns: 
    - [Given name] [Patronymic noun] [Father’s given name]
    - [Given name] [Father’s given name]
    - [Initial of Father’s given name] [Given name]
    - [Given name] [Singh/Kaur] [Patronymic noun] [Father’s given name] [Singh]
    - [Christian name] [Given name] [Father’s given name]

    **Casing for each full name must be ***consistently*** one of the following:**
    - Capitalisation
    - ALL CAPS
    - lowercase
    
     Return the names as JSON lines in the following format:
    {\"text\": \"{noisy_name1}\", \"label\": \"name\", \"clean\": \"{name1}\", \"gender\": \"{gender}\", \"batch\": \"1\"}

    Where:
    - `text` is a generated version of the name
    - `clean` is the properly formatted version using Capitalisation.
    - `label` is always "name"
    - `gender` is M for male names or F for female names.
    - `batch` is always "1" """
)


prompt_name_eurasian =(
    """Generate 40 realistic full names representing Singaporean Eurasian individuals.

    **Casing for each full name must be ***consistently*** one of the following:**
    - Capitalisation
    - ALL CAPS
    - lowercase
    Each casing type must be used at least 10 times.
    
     Return the names as JSON lines in the following format:
    {\"text\": \"{noisy_name1}\", \"label\": \"name\", \"clean\": \"{name1}\", \"gender\": \"{gender}\", \"batch\": \"1\"}

    Where:
    - `text` is a generated version of the name
    - `clean` is the properly formatted version using Capitalisation. 
    - `label` is always "name"
    - `gender` is M for male names or F for female names.
    - `batch` is always "1" """
)

prompt_name_chinese =(
    """Generate 50 realistic full names representing Singaporean Chinese individuals.
    Each name must belong to one of the following structural patterns:
    1. English given name + Chinese surname
    2. Chinese surname + HanYu PinYin given name
    3. English given name + Chinese surname + HanYu PinYin given name

    Vary the order and structure of the surnames and given names across examples to reflect naming diversity in Singapore.
    Use common Singaporean Chinese surnames.
    Chinese names should reflect diverse Chinese backgrounds and dialects (Hokkien, Teochew, Cantonese, Hakka, Hainan).
    English given names should be common in Singapore.

    **Casing for each full name must be ***consistently*** one of the following:**
    - Capitalisation
    - ALL CAPS
    - lowercase
    
     Return the names as JSON lines in the following format:
    {\"text\": \"{noisy_name1}\", \"label\": \"name\", \"clean\": \"{name1}\", \"gender\": \"{gender}\", \"batch\": \"1\"}

    Where:
    - `text` is a generated version of the name
    - `clean` is the properly formatted version using Capitalisation.
    - `label` is always "name"
    - `gender` is M for male names or F for female names.
    - `batch` is always "1" """
)

result = generate_entities(prompt_name_indian)

with open("name_sg_indian.jsonl", "a", encoding="utf-8") as f:
    for line in result:
        f.write(line + "\n")



