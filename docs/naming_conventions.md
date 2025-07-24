# Naming Conventions for Entity Data

This document outlines the naming structure used for all synthetic entity data files in the project.

---

## General Format
```css
{entity_type}{region?}{ethnicity?}_{variant?}_b{batch}.jsonl
```

Components marked with `?` are optional, depending on the entity type.

---

## Components

| Component       | Meaning                                                                 |
|----------------|-------------------------------------------------------------------------|
| `entity_type`   | Type of entity (e.g., `name`, `alias`, `email`, `org`)                 |
| `region`        | Optional. Region or country code, e.g. `sg` for Singapore              |
| `ethnicity`     | Optional. Ethnic group when relevant (used for names/aliases):         |
|                 | - `c` = Chinese                                                         |
|                 | - `i` = Indian                                                          |
|                 | - `m` = Malay                                                           |
|                 | - `e` = Eurasian                                                        |
| `variant`       | Optional. For specialised formats, e.g., `wo_code` (without country code) |
| `b{batch}`      | Optional. Indicates noise level (if used):                             |
|                 | - `b1` = Clean                                                          |
|                 | - `b2` = Moderate noise                                                 |
|                 | - `b3` = High noise                                       |

---

## File Index

| Filename                                | Description                                                  |
|-----------------------------------------|--------------------------------------------------------------|
| `alias_sg_[c/i/e/m]_b[1/2/3].jsonl`     | Singaporean aliases with ethnicity and batch variants       |
| `name_sg_[c/i/e/m]_b[1/2/3].jsonl`      | Singaporean names (no aliases) by ethnicity and batch        |
| `org_sg_b[1/2/3].jsonl`                 | Singaporean organisation names, clean to noisy               |
| `email_b[1/2/3].jsonl`                  | Email addresses (generic), across batch noise levels         |
| `date_b[1/2/3].jsonl`                   | Dates in various formats and noise levels                    |
| `relationship_b[1/2/3].jsonl`           | Relationship terms (e.g., spouse, friend) with noise levels  |
| `phone_code_sg_b[1/2/3].jsonl`          | Singaporean phone numbers *with* country code                |
| `phone_wo_code_sg_b[1/2/3].jsonl`       | Singaporean phone numbers *without* country code             |
| `car_plate_sg.jsonl`                    | Singaporean car plate numbers (no batches)                   |
| `id_num_sg.jsonl`                       | Singaporean ID numbers (no batches)                          |
| `airport_code.jsonl`                    | Airport IATA codes (global)                                  |
| `country_entity.jsonl`                  | Country names and ISO codes                                  |
| `salutation.jsonl`                      | Honorifics (e.g., Mr, Ms, Dr)                                |

---

## Notes

- Files without batch suffixes (`b1`, `b2`, `b3`) are clean or universal.
- The `_sg_` tag denotes Singapore-specific data.
- Ethnicity markers apply only where culturally relevant (e.g., `name`, `alias`).

---

