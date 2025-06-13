# Named entity recognition
## Description of contents
### dataset_generation
- **multi_entity_gen** contains the code for joining, concatenating and noising samples of different entity types.
- **single_entity_gen** contains the code for joining, concatenating and noising samples of the same entity type.

### entity_generation
- Set-up:
  + generate_entities.py
  + entity_definition.py
  
- Prompt-based generation:
  + alias_generation.py
  + car_n_id.py
  + name_generation.py
  + organisation.py
  + relationship_generation.py
    
- Code-based generation:
  + email_generation.py
  + phone_w_code.py
  + phone_wo_code.py

### multi_entity_dataset
- **output_b1.jsonl** is the clean dataset. It contains batch 1 clean entities and all samples are evenly spaced out.
- **output_b1_concat.jsonl** is the concatenated dataset. It contains batch 1 clean entities and all samples are concatenated. Its purpose is to possibly evaluate the effects of concatenation only on the NER model.
- **output_b2.jsonl** is batch 2 dataset. It contains batch 2 (noisy) entities concatenated.
- **output_b3.jsonl** is batch 3 dataset. It contains batch 3 (very noisy) entities concatenated and with junk added.

### single_entity_dataset
Each entity type has the following batches:
  +  **{entity type}_b1.jsonl** is the clean dataset. It contains batch 1 clean entities and all samples are evenly spaced out.
  +  **{entity type}_b1_concat.jsonl** is the concatenated dataset. It contains batch 1 clean entities and all samples are concatenated.
  +  **{entity type}_b2.jsonl** is batch 2 dataset. It contains batch 2 (noisy) entities concatenated.
  +  **{entity type}_b3.jsonl** is batch 3 dataset. It contains batch 3 (very noisy) entities concatenated and with junk added.
