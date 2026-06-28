from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class PanneBase(BaseModel):
    machine_id: int
    titre: str
    description: Optional[str] = None
    causes_possibles: Optional[List[str]] = []
    cause_reelle: Optional[str] = None
    solution: Optional[str] = None
    criticite: Optional[int] = 3
    temps_moyen_reparation: Optional[int] = None
    photos: Optional[List[str]] = []


class PanneCreate(PanneBase):
    pass


class PanneUpdate(BaseModel):
    titre: Optional[str] = None
    description: Optional[str] = None
    causes_possibles: Optional[List[str]] = None
    cause_reelle: Optional[str] = None
    solution: Optional[str] = None
    criticite: Optional[int] = None
    temps_moyen_reparation: Optional[int] = None
    photos: Optional[List[str]] = None


class PanneOut(PanneBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
