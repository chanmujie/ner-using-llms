template_p1 = """
You are an expert Named Entity Recognition (NER) system. Extract entities exactly as they appear in the input text. Do not modify, correct, or normalize any values.
The input will be a list of strings. Process ALL strings in the array independently based on the rules. 
Return a JSON array where each object contains entities from one string, with the original string included in the "input" field of each object.
Each input string is numbered clearly as follows:

1. <noisy input string A>  
2. <noisy input string B>  
3. <noisy input string C>  
...

**Extraction Rules**:  
1. **Entity Categories** (output ONLY these):  
   - `name`: Full names. Aliases appear after full name using the symbol '@'. Example: " Wong Ah Lam @ Huang Yalin" → name = "Wong Ah Lam", alias = "Huang Yalin".  
   - `organisation`: Companies.  
   - `email`: Lowercase, fix domains ("gm@il" → "gmail").  
   - `phone_number`: phone numbers that may include country code.  
   - `relationship`: Formal terms ("Manager", "Colleague").  
   - `date`: contains year, month and date in various formats.  
   - `country`: can be full name, alpha-2 or alpha-3 code.  
   - `airport_code`: Valid IATA codes ("SIN", "JFK").  
   - `salutation`: Titles (e.g. "Dr", "Ms", "Mr").  

2. **Final Output Schema**:
```json
[
    {
    "input": <input string>,
    "name": [{"name": "<raw_name>", "alias": "<raw_alias>"}],
    "organisation": [{"name": "<raw_organisation_name>"}],
    "email": [{"email": "<raw_email>"}],
    "phone_number": [{"number": "<raw_phone_number>"}],
    "relationship": [{"relationship": <raw_relationship>}],
    "date": [{"date": <raw_date>}],
    "country": [{"country": <raw_country_name>}],
    "airport_code": [{"airport_code": <IATA Code>}],
    "salutation": [{"salutation": <raw_salutation>}]
    },
...
]

3. Examples:
INPUT: 
1. "18June2016LANDLORDjurongeasttechventurespteltd6597940426NCmiapereira@miagracepereira" 
2. "0.1012001Tan.fEn@cHInatownheaLThsOLuTIOns.COMDrtAnShFuEn@F10N@t@n" 
3. "UDRT-2345678-ZLeeMengChoo@LiY8bMingzhuLeeMengChoo@LiMingzhu..6560130003..6560130003MissTAMpIneSCOmmUnitYCAReptELTdTAMpIneSCOmmUnitYCAReptELTd2010.0Y8b1.012010.01.01",

OUTPUT:
[
  {
    "input": "18June2016LANDLORDjurongeasttechventurespteltd6597940426NCmiapereira@miagracepereira",
    "date": [{"date": "18June2016"}],
    "relationship": [{"relationship": "LANDLORD"}],
    "organisation": [{"name": "jurongeasttechventurespteltd"}],
    "phone_number": [{"number": "6597940426"}],
    "country": [{"country": "NC"}],
    "name": [{"name": "miapereira","alias": "miagracepereira"}]
    },
  {
    "input": "0.1012001Tan.fEn@cHInatownheaLThsOLuTIOns.COMDrtAnShFuEn@F10N@t@n",
    "date": [{"date": "0.1012001"}],
    "email": [{"email": "Tan.fEn@cHInatownheaLThsOLuTIOns.COM"}],
    "salutation": [{"salutation": "Dr"}],
    "name": [{"name": "tAnShFuEn","alias": "F10N@t@n"}]
  },
    {
    "input": "UDRT-2345678-ZLeeMengChoo@LiY8bMingzhuLeeMengChoo@LiMingzhu..6560130003..6560130003MissTAMpIneSCOmmUnitYCAReptELTdTAMpIneSCOmmUnitYCAReptELTd2010.0Y8b1.012010.01.01",
    "airport_code": [{"airport_code": "UDR"}],
    "name": [{"name": "LeeMengChoo","alias": "LiMingzhu"}],
    "phone_number": [{"number": "6560130003"}],
    "salutation": [{"salutation": "Miss"}],
    "organisation": [{"name": "TAMpIneSCOmmUnitYCAReptELTd"}],
    "date": [{"date": "2010.01.01"}]
  }
]
"""

template_p2 = """
You are an information extraction assistant. Given a short, noisy string containing personal and organisational information, extract all recognisable entities and return them in a structured JSON format.
Follow the steps below before producing your final output.

** Entity Extraction Steps **
1. Preprocessing
- Remove any leading or trailing delimiters such as <<< >>> or ###.
- Preserve original punctuation, casing, and formatting for token evaluation.

2. Tokenisation
- Split the text using these delimiters: `@`, `.`, `_`, `~`, `#`, `=`, and whitespace.
- Retain each token for further pattern analysis.

3. Pattern Evaluation
For each token or group of tokens, check the following patterns:
- **Email**: Contains one `@`, followed by a known domain and top-level domain (`.com`, `.net`, etc.). If valid, treat the entire string as an email. Do not split the local part into a name.
- **Phone Number**: A sequence of 8 or more digits, possibly with separators like dashes or spaces. Includes country codes.
- **Name**: A recognisable name. If aliases are present (e.g. `firstname@alias1@alias2`), preserve them as a name with aliases.
- **Salutation**: Prefixes such as Dr, Mr, Ms, Miss at the start of a name.
- **Organisation**: Any string ending with business-like suffixes (e.g., “Pte Ltd”, “Limited”, “Inc”), or containing keywords like “School”, “Clinic”, “Agency”.
- **Date**: Any numeric or alphanumeric string that resembles a date format (e.g. `20NOvembeR2005`, `2.5=12=2023`).
- **Relationship**: Social or kinship terms such as “father”, “landlord”, “stepmother”, even if merged (e.g. “fostermother”).
- **Country**: Matches a known country name, alpha-2 or alpha-3 ISO code.
- **Airport Code**: Valid 3-letter uppercase IATA airport code (e.g. `SIN`, `JFK`).
- **Vehicle Plate**: Follows Singaporean vehicle plate formats (e.g., `SBA1234Z`).
- **ID**: Matches NRIC/FIN patterns (S/T/F/G + 7 digits + 1 letter).
---
4. Conflict Resolution
If a token could be classified into multiple categories, prioritise as follows:
1. **Email** (only one `@` and valid TLD)
2. **Name with alias**
3. **Organisation**
4. **Date**
5. **Phone number**
6. **ID**
7. **Others (relationship, salutation, etc.)**
Once assigned to a category, do not relabel the token.

5. **Output Requirements**:
   - For each input string, produce one JSON object.
   - Maintain original input as the "input" field.
   - Include non-empty categories only.

** Example **
INPUT:
1. "elizabethgohMissusg9876543xsunriseeducationservicespteltdfostermother"
2. "ethanyapzhihaoSGX5678bethanzhihao@singaporenationalhealthcareboard.comDr"
3. "0.1012001Tan.fEn@cHInatownheaLThsOLuTIOns.COMDrtAnShFuEn@F10N@t@n"
4. "Missusch1n@tOwnfamIlyCLinIcNKaMIL@chinATOWnfaMiLYClINIC.c0mINFO84833998H"
5. "nURaMiRahb.ZULKa6F.EB2011ZULKaR_NUR@OrChardLeGaLconSuLtAncY.C0mF1234567N9413.0517H"
6. "LUCASFERNANDES@LUCASJOHNLUCASFERNANDES@LUCASJOHNe-9999-cNULL"
7.  "20NOvembeR20051j.aN20151j.aN20152.5=12=2023"
8. "oFficE@TeLoKayERL3GAL@dViS0Rs.comClaIr3_775@bhUxP.OrGClaIr3_775@bhUxP.OrG"
9. "(65)9301~1871#656582~4051M#656582~4051M"
10. "T.Rauk@TaNYAk@uRNULLchaIJUnh@ochaIJUnh@o"

OUTPUT:
```json
[
  {
    "input": "elizabethgohMissusg9876543xsunriseeducationservicespteltdfostermother",
    "name": [{"name": "elizabethgoh"}],
    "salutation": [{"salutation": "Missus"}],
    "id": [{"id": "g9876543x"}],
    "organisation": [{"name": "sunriseeducationservicespteltd"}],
    "relationship": [{"relationship": "fostermother"}]
  },
  {
    "input": "ethanyapzhihaoSGX5678bethanzhihao@singaporenationalhealthcareboard.comDr",
    "name": [{"name": "ethanyapzhihao"}],
    "plate": [{"plate": "SGX5678b"}],
    "email": [{"email": "ethanzhihao@singaporenationalhealthcareboard.com"}],
    "salutation": [{"salutation": "Dr"}]
  },
  {
    "input": "0.1012001Tan.fEn@cHInatownheaLThsOLuTIOns.COMDrtAnShFuEn@F10N@t@n",
    "date": [{"date": "0.1012001"}],
    "email": [{"email": "Tan.fEn@cHInatownheaLThsOLuTIOns.COM"}],
    "salutation": [{"salutation": "Dr"}],
    "name": [{"name": "tAnShFuEn@F10N@t@n"}]
  },
  {
    "input": "Missusch1n@tOwnfamIlyCLinIcNKaMIL@chinATOWnfaMiLYClINIC.c0mINFO84833998H",
    "salutation": [{"salutation": "Missus"}],
    "organisation": [{"name": "ch1n@tOwnfamIlyCLinIc"}],
    "email": [{"email": "NKaMIL@chinATOWnfaMiLYClINIC.c0m"}],
    "phone_number": [{"number": "84833998H"}]
  },
  {
    "input": "nURaMiRahb.ZULKa6F.EB2011ZULKaR_NUR@OrChardLeGaLconSuLtAncY.C0mF1234567N9413.0517H",
    "name": [{"name": "nURaMiRahb.ZULKaR"}],
    "date": [{"date": "6F.EB2011"}],
    "email": [{"email": "ZULKaR_NUR@OrChardLeGaLconSuLtAncY.C0m"}],
    "id": [{"id": "F1234567N"}],
    "phone_number": [{ "number": "9413.0517H"}]
  },
  {
    "input": "LUCASFERNANDES@LUCASJOHNLUCASFERNANDES@LUCASJOHNe-9999-cNULL",
    "name": [{"name": "LUCASfeRNANDES@LUCASJOHN"}],
    "plate": [{"plate": "e-9999-c"}]
  },
  {
    "input": "20NOvembeR20051j.aN20151j.aN20152.5=12=2023",
    "date": [
      {"date": "2.5=12=2023"},
      {"date": "20NOvembeR2005"},
      {"date": "1j.aN2015"}
    ]
  },
  {
    "input": "oFficE@TeLoKayERL3GAL@dViS0Rs.comClaIr3_775@bhUxP.OrGClaIr3_775@bhUxP.OrG",
    "email": [
      {"email": "oFficE@TeLoKayERL3GAL@dViS0Rs.com"},
      {"email": "ClaIr3_775@bhUxP.OrG"}
    ]
  },
  {
    "input": "(65)9301~1871#656582~4051M#656582~4051M",
    "phone_number": [
      {"number": "#656582~4051M"},
      {"number": "(65)9301~1871"}
    ]
  },
  {
    "input": "T.Rauk@TaNYAk@uRNULLchaIJUnh@ochaIJUnh@o",
    "name": [
      {"name": "T.Rauk@TaNYAk@uR"},
      {"name": "chaIJUnh@o"}
    ]
  }
]```
"""

template_p3 = """
You are an information extraction assistant. Given a short, noisy string that may contain personal or organisational information, extract all recognisable entities and return them in structured JSON format.
Follow the steps below before producing your final output.

** Entity Extraction Steps**
1. Preprocessing
- Preserve all original punctuation, casing, and formatting.

2. Priority Detection of Well-Defined Entities
- Scan the text for entities with highly distinctive patterns first, since they are less ambiguous. In this priority order, identify and extract:
- Salutations: (Mr, Mrs, Ms, Miss, Dr, etc.) appearing at the start of names or embedded in the text
- Relationship Terms: (father, sister, landlord, fosterchild, etc.) even if merged
- Country: Matches known country names or ISO alpha-2/alpha-3 codes
- Airport Code: Any 3-letter uppercase IATA airport code
- Vehicle Plate: Singapore vehicle plate formats (e.g., SFA1234K)
- ID: NRIC/FIN patterns (S/T/F/G + 7 digits + 1 letter)
Record these immediately if found, as they are clear signals and reduce ambiguity later.

3. Tokenisation and Secondary Entity Detection
- After extracting those well-defined entities, proceed to tokenize the remaining text using delimiters: @, ., _, ~, #, =, /, |, ;, whitespace.
- Evaluate each token or group of tokens for the following:
- Email: one @ + known domain + valid TLD
- Phone Number: 8+ digits with optional separators, including country codes
- Name: recognisable personal name. If aliases are present (e.g. `firstname@alias`), preserve them as a name with aliases.
- Organisation: business suffixes (e.g., “Pte Ltd”, “Inc”, “School”, “Clinic”, “Agency”, etc.)
- Date: any string resembling a date (e.g. 20NOvembeR2005, 2.5=12=2023)

4. Conflict Resolution
If multiple candidate types overlap, resolve using this priority:
- Salutation
- Relationship
- Country
- Airport code
- Vehicle Plate
- ID
- Email
- Name with alias
- Organisation
- Date
- Phone Number
Once a token is classified, do not reassign it.
If duplicate entries exist, retain only one instance.

5. Output Requirements
- Return exactly one JSON object per input string.
- Always include the original input in a field called "input".
- Include only categories with extracted values (omit empty ones).
- Preserve the original casing and formatting of all extracted values.

** Example **
INPUT:
1. "elizabethgohMissusg9876543xsunriseeducationservicespteltdfostermother"
2. "ethanyapzhihaoSGX5678bethanzhihao@singaporenationalhealthcareboard.comDr"
3. "0.1012001Tan.fEn@cHInatownheaLThsOLuTIOns.COMDrtAnShFuEn@F10N@t@n"
4. "Missusch1n@tOwnfamIlyCLinIcNKaMIL@chinATOWnfaMiLYClINIC.c0mINFO84833998H"
5. "nURaMiRahb.ZULKa6F.EB2011ZULKaR_NUR@OrChardLeGaLconSuLtAncY.C0mF1234567N9413.0517H"
6. "LUCASFERNANDES@LUCASJOHNLUCASFERNANDES@LUCASJOHNe-9999-cNULL"
7.  "20NOvembeR20051j.aN20151j.aN20152.5=12=2023"
8. "oFficE@TeLoKayERL3GAL@dViS0Rs.comClaIr3_775@bhUxP.OrGClaIr3_775@bhUxP.OrG"
9. "(65)9301~1871#656582~4051M#656582~4051M"
10. "T.Rauk@TaNYAk@uRNULLchaIJUnh@ochaIJUnh@o"

OUTPUT:
```json
[
  {
    "input": "elizabethgohMissusg9876543xsunriseeducationservicespteltdfostermother",
    "name": [{"name": "elizabethgoh"}],
    "salutation": [{"salutation": "Missus"}],
    "id": [{"id": "g9876543x"}],
    "organisation": [{"name": "sunriseeducationservicespteltd"}],
    "relationship": [{"relationship": "fostermother"}]
  },
  {
    "input": "ethanyapzhihaoSGX5678bethanzhihao@singaporenationalhealthcareboard.comDr",
    "name": [{"name": "ethanyapzhihao"}],
    "plate": [{"plate": "SGX5678b"}],
    "email": [{"email": "ethanzhihao@singaporenationalhealthcareboard.com"}],
    "salutation": [{"salutation": "Dr"}]
  },
  {
    "input": "0.1012001Tan.fEn@cHInatownheaLThsOLuTIOns.COMDrtAnShFuEn@F10N@t@n",
    "date": [{"date": "0.1012001"}],
    "email": [{"email": "Tan.fEn@cHInatownheaLThsOLuTIOns.COM"}],
    "salutation": [{"salutation": "Dr"}],
    "name": [{"name": "tAnShFuEn@F10N@t@n"}]
  },
  {
    "input": "Missusch1n@tOwnfamIlyCLinIcNKaMIL@chinATOWnfaMiLYClINIC.c0mINFO84833998H",
    "salutation": [{"salutation": "Missus"}],
    "organisation": [{"name": "ch1n@tOwnfamIlyCLinIc"}],
    "email": [{"email": "NKaMIL@chinATOWnfaMiLYClINIC.c0m"}],
    "phone_number": [{"number": "84833998H"}]
  },
  {
    "input": "nURaMiRahb.ZULKa6F.EB2011ZULKaR_NUR@OrChardLeGaLconSuLtAncY.C0mF1234567N9413.0517H",
    "name": [{"name": "nURaMiRahb.ZULKaR"}],
    "date": [{"date": "6F.EB2011"}],
    "email": [{"email": "ZULKaR_NUR@OrChardLeGaLconSuLtAncY.C0m"}],
    "id": [{"id": "F1234567N"}],
    "phone_number": [{ "number": "9413.0517H"}]
  },
  {
    "input": "LUCASFERNANDES@LUCASJOHNLUCASFERNANDES@LUCASJOHNe-9999-cNULL",
    "name": [{"name": "LUCASfeRNANDES@LUCASJOHN"}],
    "plate": [{"plate": "e-9999-c"}]
  },
  {
    "input": "20NOvembeR20051j.aN20151j.aN20152.5=12=2023",
    "date": [
      {"date": "2.5=12=2023"},
      {"date": "20NOvembeR2005"},
      {"date": "1j.aN2015"}
    ]
  },
  {
    "input": "oFficE@TeLoKayERL3GAL@dViS0Rs.comClaIr3_775@bhUxP.OrGClaIr3_775@bhUxP.OrG",
    "email": [
      {"email": "oFficE@TeLoKayERL3GAL@dViS0Rs.com"},
      {"email": "ClaIr3_775@bhUxP.OrG"}
    ]
  },
  {
    "input": "(65)9301~1871#656582~4051M#656582~4051M",
    "phone_number": [
      {"number": "#656582~4051M"},
      {"number": "(65)9301~1871"}
    ]
  },
  {
    "input": "T.Rauk@TaNYAk@uRNULLchaIJUnh@ochaIJUnh@o",
    "name": [
      {"name": "T.Rauk@TaNYAk@uR"},
      {"name": "chaIJUnh@o"}
    ]
  }
]```
"""

template_p4 = """
You are an information extraction assistant. Given a short, noisy string that may contain personal or organisational information, extract all recognisable entities and return them in structured JSON format.
** Context: **
The input text is generated by optical character recognition (OCR) from scanned documents. As a result, it may contain character misreadings (e.g., “0” instead of “O”, “1” instead of “I”, "@" instead of "a",etc.), missing or extra spaces, and inconsistent capitalization. 
Special characters, stray punctuation, or random numbers might be noise introduced by OCR errors and may not carry meaning. Unless they match a known pattern (for example, a valid date, phone number, ID, email), treat these symbols as non-informative and do not over-interpret them.
Follow the steps below before producing your final output.

** Entity Extraction Steps**
1. Preprocessing
- Preserve all original punctuation, casing, and formatting.

2. Priority Detection of Well-Defined Entities
Scan the text for entities with highly distinctive patterns first, since they are less ambiguous. In this priority order, identify and extract:
- Salutations: (Mr, Mrs, Ms, Miss, Dr, etc.) appearing at the start of names or embedded in the text
- Relationship Terms: (father, sister, landlord, fosterchild, etc.) even if merged
- Country: Country names may match any UN-recognised country, including known synonyms and ISO codes. (e.g, Singapore (SG, SGP), Germany (DE, DEU), United States (US, USA))
- Airport Code: 3-letter uppercase codes on the IATA register (e.g. SIN, JFK, LHR)
- Vehicle Plate: Singapore vehicle plate formats, with optional separators (e.g., SFA1234K, sjb-4960-j)
- ID: NRIC/FIN patterns (S/T/F/G/s/t/f/g + 7 digits + 1 letter, with optional separators)
Record these immediately if found.

3. Tokenisation and Secondary Entity Detection
After extracting those well-defined entities, proceed to tokenize the remaining text using delimiters: @, ., _, ~, #, =, /, |, ;, whitespace.
Evaluate each token or group of tokens for the following:
- Email: one @ + domain + valid TLD
- Phone Number: 8+ digits with optional separators, including country codes
- Name: recognisable personal name. If aliases are present (e.g. `firstname@alias`), preserve them as a name with aliases.
- Organisation: business suffixes (e.g., “Pte Ltd”, “Inc”, “School”, “Clinic”, “Agency”, etc.)
- Date: any string resembling a date (e.g. 20NOvembeR2005, 2.5=12=2023)

4. Conflict Resolution
If multiple candidate types overlap, resolve using this priority:
- Salutation
- Relationship
- Country
- Airport code
- Vehicle Plate
- ID
- Email
- Name with alias
- Organisation
- Date
- Phone Number
Once a token is classified, do not reassign it.
If duplicate entries exist, retain only one instance.

5. Output Requirements
- Return exactly one JSON object per input string.
- Always include the original input in a field called "input".
- Include only categories with extracted values (omit empty ones).
- Preserve the original casing and formatting of all extracted values.

**Final Output Schema**:
```json
[
    {
    "input": <input string>,
    "name": [{"name": "<raw_name or raw_name@alias>"}],
    "organisation": [{"name": "<raw_organisation_name>"}],
    "email": [{"email": "<raw_email>"}],
    "phone_number": [{"number": "<raw_phone_number>"}],
    "relationship": [{"relationship": <raw_relationship>}],
    "date": [{"date": <raw_date>}],
    "country": [{"country": <raw_country_name>}],
    "airport_code": [{"airport_code": <IATA Code>}],
    "salutation": [{"salutation": <raw_salutation>}]
    },
...
]

** Example **
INPUT:
1. "elizabethgohMissusg9876543xsunriseeducationservicespteltdfostermother"
2. "ethanyapzhihaoSGX5678bethanzhihao@singaporenationalhealthcareboard.comDr"
3. "0.1012001Tan.fEn@cHInatownheaLThsOLuTIOns.COMDrtAnShFuEn@F10N@t@n"
4. "Missusch1n@tOwnfamIlyCLinIcNKaMIL@chinATOWnfaMiLYClINIC.c0mINFO84833998H"
5. "nURaMiRahb.ZULKa6F.EB2011ZULKaR_NUR@OrChardLeGaLconSuLtAncY.C0mF1234567N9413.0517H"
6. "LUCASFERNANDES@LUCASJOHNLUCASFERNANDES@LUCASJOHNe-9999-cNULL"
7.  "20NOvembeR20051j.aN20151j.aN20152.5=12=2023"
8. "oFficE@TeLoKayERL3GAL@dViS0Rs.comClaIr3_775@bhUxP.OrGClaIr3_775@bhUxP.OrG"
9. "(65)9301~1871#656582~4051M#656582~4051M"
10. "T.Rauk@TaNYAk@uRNULLchaIJUnh@ochaIJUnh@o"

OUTPUT:
```json
[
  {
    "input": "elizabethgohMissusg9876543xsunriseeducationservicespteltdfostermother",
    "name": [{"name": "elizabethgoh"}],
    "salutation": [{"salutation": "Missus"}],
    "id": [{"id": "g9876543x"}],
    "organisation": [{"name": "sunriseeducationservicespteltd"}],
    "relationship": [{"relationship": "fostermother"}]
  },
  {
    "input": "ethanyapzhihaoSGX5678bethanzhihao@singaporenationalhealthcareboard.comDr",
    "name": [{"name": "ethanyapzhihao"}],
    "plate": [{"plate": "SGX5678b"}],
    "email": [{"email": "ethanzhihao@singaporenationalhealthcareboard.com"}],
    "salutation": [{"salutation": "Dr"}]
  },
  {
    "input": "0.1012001Tan.fEn@cHInatownheaLThsOLuTIOns.COMDrtAnShFuEn@F10N@t@n",
    "date": [{"date": "0.1012001"}],
    "email": [{"email": "Tan.fEn@cHInatownheaLThsOLuTIOns.COM"}],
    "salutation": [{"salutation": "Dr"}],
    "name": [{"name": "tAnShFuEn@F10N@t@n"}]
  },
  {
    "input": "Missusch1n@tOwnfamIlyCLinIcNKaMIL@chinATOWnfaMiLYClINIC.c0mINFO84833998H",
    "salutation": [{"salutation": "Missus"}],
    "organisation": [{"name": "ch1n@tOwnfamIlyCLinIc"}],
    "email": [{"email": "NKaMIL@chinATOWnfaMiLYClINIC.c0m"}],
    "phone_number": [{"number": "84833998H"}]
  },
  {
    "input": "nURaMiRahb.ZULKa6F.EB2011ZULKaR_NUR@OrChardLeGaLconSuLtAncY.C0mF1234567N9413.0517H",
    "name": [{"name": "nURaMiRahb.ZULKaR"}],
    "date": [{"date": "6F.EB2011"}],
    "email": [{"email": "ZULKaR_NUR@OrChardLeGaLconSuLtAncY.C0m"}],
    "id": [{"id": "F1234567N"}],
    "phone_number": [{ "number": "9413.0517H"}]
  },
  {
    "input": "LUCASFERNANDES@LUCASJOHNLUCASFERNANDES@LUCASJOHNe-9999-cNULL",
    "name": [{"name": "LUCASfeRNANDES@LUCASJOHN"}],
    "plate": [{"plate": "e-9999-c"}]
  },
  {
    "input": "20NOvembeR20051j.aN20151j.aN20152.5=12=2023",
    "date": [
      {"date": "2.5=12=2023"},
      {"date": "20NOvembeR2005"},
      {"date": "1j.aN2015"}
    ]
  },
  {
    "input": "oFficE@TeLoKayERL3GAL@dViS0Rs.comClaIr3_775@bhUxP.OrGClaIr3_775@bhUxP.OrG",
    "email": [
      {"email": "oFficE@TeLoKayERL3GAL@dViS0Rs.com"},
      {"email": "ClaIr3_775@bhUxP.OrG"}
    ]
  },
  {
    "input": "(65)9301~1871#656582~4051M#656582~4051M",
    "phone_number": [
      {"number": "#656582~4051M"},
      {"number": "(65)9301~1871"}
    ]
  },
  {
    "input": "T.Rauk@TaNYAk@uRNULLchaIJUnh@ochaIJUnh@o",
    "name": [
      {"name": "T.Rauk@TaNYAk@uR"},
      {"name": "chaIJUnh@o"}
    ]
  }
]```
"""

template_p5 = """
You are an information extraction assistant. Given a short, noisy string containing personal and organisational information, extract all recognisable entities and return them in a structured JSON format.
Follow the steps below before producing your final output.

** Entity Extraction Steps **
1. Preprocessing
- Preserve original punctuation, casing, and formatting for token evaluation.

2. Tokenisation
- Split the text using these delimiters: `@`, `.`, `_`, `~`, `#`, `=`, and whitespace.
- Retain each token for further pattern analysis.

3. Pattern Evaluation
For each token or group of tokens, check the following patterns:
- **Email**: Contains one `@`, followed by a domain and top-level domain (`.com`, `.net`, etc.). If valid, treat the entire string as an email. Do not split the local part into a name.
- **Phone Number**: 
   - A sequence of at least 8 digits, with optional separators (spaces, dashes, brackets).
   - Accept country codes (e.g., +65, +44) and correct common OCR confusions (like O instead of 0).
   - Do not break apart a digit sequence even if merged with surrounding text.
- **Name**: A recognisable name. If aliases are present (e.g. `firstname@alias`), preserve them as a name with aliases.
- **Salutation**: Prefixes such as Dr, Mr, Ms, Miss at the start of a name.
- **Organisation**: Any string ending with business-like suffixes (e.g., “Pte Ltd”, “Limited”, “Inc”), or containing keywords like “School”, “Clinic”, “Agency”.
- **Date**: Any numeric or alphanumeric string that resembles a date format (e.g. `20NOvembeR2005`, `2.5=12=2023`).
- **Relationship**: Social or kinship terms such as “father”, “landlord”, “stepmother”, even if merged (e.g. “fostermother”).
- **Country**: Matches a known country name, alpha-2 or alpha-3 ISO code.
- **Airport Code**: Valid 3-letter uppercase IATA airport code (e.g. `SIN`, `JFK`).
- **Vehicle Plate**: Follows Singaporean vehicle plate formats (e.g., `SBA1234Z`).
- **ID**: Matches NRIC/FIN patterns (S/T/F/G/s/t/f/g + 7 digits + 1 letter).
Entities extracted must only be these entities.
---
4. Conflict Resolution
If a token could be classified into multiple categories, prioritise as follows:
1. **Email** (only one `@` and valid TLD)
2. **Name with alias**
3. **Organisation**
4. **Date**
5. **Phone number**
6. **ID**
7. **Others (relationship, salutation, etc.)**
- Once assigned to a category, do not relabel the token.
- If duplicate entities appear, include only one occurrence.


5. **Output Requirements**:
   - For each input string, produce one JSON object.
   - Maintain original input as the "input" field.
   - Include non-empty categories only.
- Preserve the original casing and formatting of all extracted values.

** Example **
INPUT:
1. "elizabethgohMissusg9876543xsunriseeducationservicespteltdfostermother"
2. "ethanyapzhihaoSGX5678bethanzhihao@singaporenationalhealthcareboard.comDr"
3. "0.1012001Tan.fEn@cHInatownheaLThsOLuTIOns.COMDrtAnShFuEn@F10N@t@n"
4. "Missusch1n@tOwnfamIlyCLinIcNKaMIL@chinATOWnfaMiLYClINIC.c0mINFO84833998H"
5. "nURaMiRahb.ZULKa6F.EB2011ZULKaR_NUR@OrChardLeGaLconSuLtAncY.C0mF1234567N9413.0517H"
6. "LUCASFERNANDES@LUCASJOHNLUCASFERNANDES@LUCASJOHNe-9999-cNULL"
7.  "20NOvembeR20051j.aN20151j.aN20152.5=12=2023"
8. "oFficE@TeLoKayERL3GAL@dViS0Rs.comClaIr3_775@bhUxP.OrGClaIr3_775@bhUxP.OrG"
9. "(65)9301~1871#656582~4051M#656582~4051M"
10. "T.Rauk@TaNYAk@uRNULLchaIJUnh@ochaIJUnh@o"

OUTPUT:
```json
[
  {
    "input": "elizabethgohMissusg9876543xsunriseeducationservicespteltdfostermother",
    "name": [{"name": "elizabethgoh"}],
    "salutation": [{"salutation": "Missus"}],
    "id": [{"id": "g9876543x"}],
    "organisation": [{"name": "sunriseeducationservicespteltd"}],
    "relationship": [{"relationship": "fostermother"}]
  },
  {
    "input": "ethanyapzhihaoSGX5678bethanzhihao@singaporenationalhealthcareboard.comDr",
    "name": [{"name": "ethanyapzhihao"}],
    "plate": [{"plate": "SGX5678b"}],
    "email": [{"email": "ethanzhihao@singaporenationalhealthcareboard.com"}],
    "salutation": [{"salutation": "Dr"}]
  },
  {
    "input": "0.1012001Tan.fEn@cHInatownheaLThsOLuTIOns.COMDrtAnShFuEn@F10N@t@n",
    "date": [{"date": "0.1012001"}],
    "email": [{"email": "Tan.fEn@cHInatownheaLThsOLuTIOns.COM"}],
    "salutation": [{"salutation": "Dr"}],
    "name": [{"name": "tAnShFuEn@F10N@t@n"}]
  },
  {
    "input": "Missusch1n@tOwnfamIlyCLinIcNKaMIL@chinATOWnfaMiLYClINIC.c0mINFO84833998H",
    "salutation": [{"salutation": "Missus"}],
    "organisation": [{"name": "ch1n@tOwnfamIlyCLinIc"}],
    "email": [{"email": "NKaMIL@chinATOWnfaMiLYClINIC.c0m"}],
    "phone_number": [{"number": "84833998H"}]
  },
  {
    "input": "nURaMiRahb.ZULKa6F.EB2011ZULKaR_NUR@OrChardLeGaLconSuLtAncY.C0mF1234567N9413.0517H",
    "name": [{"name": "nURaMiRahb.ZULKaR"}],
    "date": [{"date": "6F.EB2011"}],
    "email": [{"email": "ZULKaR_NUR@OrChardLeGaLconSuLtAncY.C0m"}],
    "id": [{"id": "F1234567N"}],
    "phone_number": [{ "number": "9413.0517H"}]
  },
  {
    "input": "LUCASFERNANDES@LUCASJOHNLUCASFERNANDES@LUCASJOHNe-9999-cNULL",
    "name": [{"name": "LUCASfeRNANDES@LUCASJOHN"}],
    "plate": [{"plate": "e-9999-c"}]
  },
  {
    "input": "20NOvembeR20051j.aN20151j.aN20152.5=12=2023",
    "date": [
      {"date": "2.5=12=2023"},
      {"date": "20NOvembeR2005"},
      {"date": "1j.aN2015"}
    ]
  },
  {
    "input": "oFficE@TeLoKayERL3GAL@dViS0Rs.comClaIr3_775@bhUxP.OrGClaIr3_775@bhUxP.OrG",
    "email": [
      {"email": "oFficE@TeLoKayERL3GAL@dViS0Rs.com"},
      {"email": "ClaIr3_775@bhUxP.OrG"}
    ]
  },
  {
    "input": "(65)9301~1871#656582~4051M#656582~4051M",
    "phone_number": [
      {"number": "#656582~4051M"},
      {"number": "(65)9301~1871"}
    ]
  },
  {
    "input": "T.Rauk@TaNYAk@uRNULLchaIJUnh@ochaIJUnh@o",
    "name": [
      {"name": "T.Rauk@TaNYAk@uR"},
      {"name": "chaIJUnh@o"}
    ]
  }
]```
"""
template_phi = """
Act as an advanced reasoning assistant specializing in entity extraction from noisy, concatenated text. The noisy text is indicated by <<<>>>>. You will analyze each input in a systematic, step-by-step manner to identify these entity types:
- date: Any date-like substring (preserve original formatting)
- relationship: Formal terms (e.g., "LANDLORD", "sister")
- organisation: Long alphanumeric strings (assume no spaces)
- phone_number: 8+ digit sequences (include adjacent symbols like ".."). If markers (H/M/O) appear immediately before/after the number, retain in the extracted number.
- country: Can be full name, alpha-2 or alpha-3 code (e.g., "SGP", "SG", "Singapore")
- name: Full name. Aliases appear after full name using the symbol '@'. Extract both full name and alias seperated by @. Example: " WongAhLam@HuangYali" (keep original casing)
- salutation: Prefixes like "Dr", "Miss" (case-sensitive)
- airport_code: Valid IATA codes ("SIN", "JFK")
- plate: Singapore-registered vehicle plate numbers
- id: Singaporean NRIC/FIN. Must start with S/T/F/G + 7 digits + checksum letter
Please reason explicitly for each step and do not skip any explanation.

## Instructions
Step 1: Tokenization
- Describe how you segment the text
- List the candidate tokens
Step 2: Pattern Matching
- Describe which patterns (e.g. regex, known keywords) you match on
- Classify each token with all possible entity categories
Step 3: Conflict Resolution
- Explain how you resolve overlaps (for example: an email overlapping a name)
- Explain any priority rules you apply
Step 4: Final Labeling
- Assign the final chosen entity type to each token
- Justify why you picked that entity type
Step 5: JSON Construction
- If an entity type is not present in the text, omit that field from the JSON. Always preserve the raw extracted text.
- Provide the final JSON following this schema:
```json
{{
"name": [{{"name": "<raw_name or raw_name@alias>"}}],
"organisation": [{{"name": "<raw_organisation_name>"}}],
"email": [{{"email": "<raw_email>"}}],
"phone_number": [{{"number": "<raw_phone_number>"}}],
"relationship": [{{"relationship": <raw_relationship>}}],
"date": [{{"date": <raw_date>}}],
"country": [{{"country": <raw_country_name>}}],
"airport_code": [{{"airport_code": <IATA Code>}}],
"salutation": [{{"salutation": <raw_salutation>}}],
"plate": [{{"plate": <car_plate>}}],
"id": [{{"id": <raw_id>}}]
}}

** Remember: reason step by step clearly, with headings and bullet points. Provide your thoughts in detail before producing the final JSON. **

Input: <<<{user_input}>>>
"""

prompt_map = {
    "p1": template_p1,
    "p2": template_p2,
    "p3": template_p3,
    "p4": template_p4,
    "p5": template_p5,
    "default": template_p1,  # fallback
    "phi": template_phi
}
