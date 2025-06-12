from pydantic import BaseModel
from typing import List

class NameItem(BaseModel):
    text: str
    label: str
    clean: str
    alias: str
    gender: str
    batch: str="1"

class NameList(BaseModel):
    names: List[NameItem]

class EmailItem(BaseModel):
    text: str
    label: str
    clean: str
    batch: str
    type: str
    name_source: str
    organisation_source: str

class RelationshipItem(BaseModel):
    text: str
    label: str
    clean: str
    gender: str
    batch: str="1"

class RelationshipList(BaseModel):
    names: List[RelationshipItem]

class DateItem(BaseModel):
    text: str
    label: str
    clean: str
    batch: str="1"

class DateList(BaseModel):
    names: List[DateItem]

class OrganisationItem(BaseModel):
    text: str
    label: str
    clean: str
    industry: str
    batch: str="1"

class OrganisationList(BaseModel):
    names: List[OrganisationItem]

