from dataclasses import dataclass
from typing import Dict

@dataclass
class Entity:
    label: str
    clean_text: str
    extra_fields: Dict

@dataclass
class GoldEntity:
    label: str
    raw_text: str
    clean_text: str
    extra_fields: Dict
    model_prediction: str = None
    correct: bool = None

@dataclass
class Category:
    name: str
    description: str
