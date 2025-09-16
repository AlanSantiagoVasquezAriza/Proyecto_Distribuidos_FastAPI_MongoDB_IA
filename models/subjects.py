from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class SubjectModel(BaseModel):
	name: str = Field(..., description="Nombre de la materia")

class SubjectUpdate(BaseModel):
	name: Optional[str] = Field(None, description="Nombre de la materia")