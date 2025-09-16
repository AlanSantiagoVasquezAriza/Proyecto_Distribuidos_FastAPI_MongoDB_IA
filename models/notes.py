from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class NoteModel(BaseModel):
    subject_id: str = Field(..., description="Referencia a la materia")
    type: str = Field(..., description='"text" o "image"')
    content: str = Field(..., description="Contenido de la nota")
    image_url: Optional[str] = Field(default=None, description="URL de la imagen si aplica")

class NoteUpdate(BaseModel):
    subject_id: Optional[str] = None
    type: Optional[str] = None
    content: Optional[str] = None
    image_url: Optional[str] = None