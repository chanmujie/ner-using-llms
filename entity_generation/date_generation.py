from generate_entities import generate_entities

prompt_date = """Generate 80 distinct dates in varied formats as JSON array with:

1. **Date Rules**:
   - Range: 2000-01-01 to 2023-12-31
   - Must be valid dates:
     * Proper day/month combinations
     * Handle leap years correctly
     * Exclude impossible dates (e.g., 31-04-2020)
   - Do **not** prioritise special/recognisable dates (e.g. holidays like 25 December, 31 October, 14 February)
   - Avoid clustering around the same month/year
   - Must include a mix of leap and non-leap years, weekdays and weekends
   - - **Each date must be unique**.

2. **Variations for 'text'**:
    Each `text` must follow one of the following **date formats** (apply **one per date**):
    - `DD-MM-YYYY`
    - `MM/DD/YYYY`
    - `YYYY.MM.DD`
    - `Month DD, YYYY`
    - `DD Month YYYY`
    - `Abbreviated month` (e.g. `Apr 3, 2021`, `3 Apr 2021`)
    - `Compact` (e.g. `20030715`)
    - `ISO-like` (e.g. `2020-12-25`)
    - `With/without leading zeros`

**Apply only one format per date**—do not generate multiple formats for the same date.

3. **Output Fields**:
```json
{
  "text": "{formatted_date}",
  "label": "date",
  "clean": "{ISO_format_date}",
  "batch": "1"
}"""

result = generate_entities(prompt_date)

with open("date.jsonl", "w", encoding="utf-8") as f:
    for line in result:
        f.write(line + "\n")

