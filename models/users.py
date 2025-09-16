from pydantic import BaseModel, Field, constr
from typing import Optional
from bson import ObjectId
from datetime import datetime

class UserModel(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Nombre de usuario")
    email: str = Field(..., min_length=5, max_length=100, description="Correo electrónico")
    password_hash: str = Field(..., min_length=8, description="Hash de la contraseña")
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow, description="Fecha de creación")