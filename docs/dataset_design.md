# Dataset Design Record
This document outlines the rationale and design principles behind the construction of the synthetic datasets used for Named Entity Recognition (NER) evaluation.

## Dataset Overview
Datasets are structured into:

- Single-entity datasets: Contain only one entity type per file (e.g., only names, only phone numbers).
- Multi-entity datasets: Contain mixed entity types per sample (e.g., names + emails + dates).

Each dataset is divided into three noise-level batches:

- Batch 1 (B1): Clean, well-formatted examples.
- Batch 2 (B2): Moderately noisy (e.g., typos, casing inconsistencies).
- Batch 3 (B3): Very noisy (e.g., concatenated entities, corrupted tokens, hallucinated junk).

## Design Philosophy
Due to practical limits on dataset size, entity strings were manually selected to maximise coverage of edge cases rather than relying on random sampling. The goal was to stress-test LLM performance across controlled variations.

### Batch 1 – Clean dataset
#### Cases covered:
- Casing diversity:
  - All lowercase (e.g., johntanbrother)
  - All uppercase (e.g., JOHNTANBROTHER)
  - All title case (e.g., JohnTanBrother)
  - Mixed casing (e.g., JohnTanBROTHER)

- Length diversity:
  - Short samples: ~3 entities per string
  - Long samples: 7–8 entities per string
  
### Batch 2 – Medium noise dataset
#### Cases covered:
- Typographic errors (e.g., Jhon Tann)
- Partial entity corruption (e.g., john@gmal.com)
- Irregular casing
- Format inconsistencies (e.g., 31=Jan-2000, 31|01/2000)
- Entity structure noise (e.g., random separator symbols)
- Duplication
- Length diversity:
  - Short samples: ~3 entities per string
  - Long samples: 7–8 entities per string

### Batch 3 – High Noise Dataset Design
#### Cases covered:
- Typographic errors (e.g., Jhon Tann)
- Partial entity corruption (e.g., john@gmal.com)
- Irregular casing
- Format inconsistencies (e.g., 31=Jan-2000, 31|01/2000)
- Entity structure noise (e.g., random separator symbols)
- Duplication
- Length diversity:
  - Short samples: ~3 entities per string
  - Long samples: 7–8 entities per string
- Junk text
- Invalid, unrecoverable entities
- Recognisable, recoverable entities


## Notes on Sampling
For all entities, samples for B2 and B3 included invalid and malformed entries.
For phones, variations covered with/without country code.
Relationship, organisation, and salutation entries included context ambiguity (e.g., "Director", "Mr", "partner").
