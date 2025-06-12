import json
from generate_entities import generate_entities
from entity_definition import NameList, NameItem

prompt_alias_m = ("""Generate 50 realistic Singaporean Malay names with OFFICIAL ALIASES in JSON lines format:
1. **ALIAS REQUIREMENTS**:
   - Must be another *full legal name* the individual is known by
   - Aliases must be plausible legal alternatives

2. **Cultural Specifications**:
   - Consider double-barrelled race options

3. **Casing for each full name including alias must be ***consistently*** one of the following:**
    - Capitalisation
    - ALL CAPS
    - lowercase

4. **Output Format**:
Return the names as JSON lines in the following format:
{"text": "{display_name} @ {alias}", "label": "name", "clean": "{Primary_Name}", "alias": "{Official_Alternate_Name}", "gender": "M/F", "batch": "1"}
Where:
    - `text` is a generated version of the name and alias
    - `clean` is the properly formatted version using Capitalisation
    - `alias` is the properly formatted version using Capitalisation
    - `label` is always "name"
    - `batch` is always "1" 
    - `gender` is either M or F """
)

prompt_alias_i = ("""Generate 30 realistic Singaporean Indian names with OFFICIAL ALIASES in JSON lines format:
1. **PRIMARY NAME REQUIREMENTS**:
   - Each name must follow one of the following structural patterns: 
    - [Given name] [Patronymic noun] [Father’s given name]
    - [Given name] [Father’s given name]
    - [Initial of Father’s given name] [Given name]
    - [Given name] [Singh/Kaur] [Patronymic noun] [Father’s given name] [Singh]
    - [Christian name] [Given name] [Father’s given name]
                  
2. **ALIAS REQUIREMENTS**:
   - Must be another *full legal name* the individual is known by
   - Aliases must be plausible legal alternatives

3. **Alias Cultural Specifications**:
   - Consider double-barrelled race, business names and married names

4. **Casing for each full name including alias must be ***consistently*** one of the following:**
    - Capitalisation
    - ALL CAPS
    - lowercase

5. **Output Format**:
Return the names as JSON lines in the following format:
{"text": "{display_name} @ {alias}", "label": "name", "clean": "{Primary_Name}", "alias": "{Official_Alternate_Name}", "gender": "M/F", "batch": "1"}
Where:
    - `text` is a generated version of the name and alias
    - `clean` is the properly formatted version using Capitalisation
    - `alias` is the properly formatted version using Capitalisation
    - `label` is always "name"
    - `batch` is always "1" 
    - `gender` is either M or F """
)

prompt_alias_e = ("""Generate 50 realistic Singaporean Eurasian names with OFFICIAL ALIASES in JSON lines format:
1. **ALIAS REQUIREMENTS**:
   - Must be another *full legal name* the individual is known by
   - Aliases must be plausible legal alternatives

2. **Cultural Specifications**:
   - Consider double-barrelled race options

3. **Casing for each full name including alias must be ***consistently*** one of the following:**
    - Capitalisation
    - ALL CAPS
    - lowercase

4. **Output Format**:
Return the names as JSON lines in the following format:
{"text": "{display_name} @ {alias}", "label": "name", "clean": "{Primary_Name}", "alias": "{Official_Alternate_Name}", "gender": "M/F", "batch": "1"}
Where:
    - `text` is a generated version of the name and alias
    - `clean` is the properly formatted version using Capitalisation
    - `alias` is the properly formatted version using Capitalisation
    - `label` is always "name"
    - `batch` is always "1" 
    - `gender` is either M or F """
                 )

prompt_alias_c =("""Generate 60 Singaporean Chinese names with official aliases in JSON lines format, ensuring:

1. **Generational Diversity**:
   - Older generation (born 1940-1970):
     * Mostly dialect-based names (Hokkien, Teochew, Cantonese)
     * Formal aliases often use older romanization systems
     * Example: {"text": "Tan Ah Kow @ Chen Yagao", ...}
   
   - Middle generation (1970-1990):
     * Mix of dialect and pinyin names
     * English aliases become common but are formal
     * Example: {"text": "Goh Bee Leng @ Michelle Goh", ...}

   - Younger generation (1990-):
     * Standardized pinyin names
     * English name aliases (but include some without)
     * Example: {"text": "Lim Jia Hui @ Rachel Lim", ...}

2. **Dialect-Romanization Cases** (50% of output ):
   - Hokkien: "Ooi" -> "Huang", "Teo" -> "Zhang"
   - Cantonese: "Wong" -> "Huang", "Leong" -> "Liang",  "Lee" -> "Li"
   - Teochew: "Ng" -> "Wu", "Chua" -> "Cai"
   - Example: {"text": "Ooi Choon Seng @ Huang Chuncheng", ...}

3. **Married Name Cases** (15% of output):
   - Women with maiden name aliases
   - Example: {"text": "Tan Li Ling @ Lim Li Ling", ...}

4. **Casing for each full name including alias must be ***consistently*** one of the following:**
    - Capitalisation
    - ALL CAPS
    - lowercase

5. **Output Structure**:
Return the names as JSON lines in the following format:
{"text": "{display_name} @ {alias}", "label": "name", "clean": "{primary_name}", "alias": "{official_alternate}", "gender": "M/F", "batch": "1"}
""")


result = generate_entities(prompt_alias_e)

with open("alias_sg_e.jsonl", "w", encoding="utf-8") as f:
    for line in result:
        f.write(line + "\n")
