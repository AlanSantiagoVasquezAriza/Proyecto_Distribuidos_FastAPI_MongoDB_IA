from bson import ObjectId
from database.db import usuarios_collection, serialize_doc
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from models.users import UserModel
from pydantic import BaseModel, Field
from typing import Optional
from auth.dependencies import get_current_user
from fastapi import Depends

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[str] = Field(None, min_length=5, max_length=100)
    password_hash: Optional[str] = Field(None, min_length=8)

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/")
async def get_users(current_user: dict = Depends(get_current_user)):
    users = []
    for user in usuarios_collection.find():
        users.append(serialize_doc(user))
    return JSONResponse(content=users)

@router.get("/me")
async def get_user(current_user: dict = Depends(get_current_user)):
    return current_user


from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.put("/me", response_model=UserModel)
async def update_user(user: UserUpdate, current_user: dict = Depends(get_current_user)):
    update_data = {k: v for k, v in user.dict(exclude_unset=True).items() if v is not None}
    if "password_hash" in update_data:
        update_data["password_hash"] = pwd_context.hash(update_data["password_hash"])
    if not update_data:
        raise HTTPException(status_code=400, detail="No se proporcionaron campos para actualizar")
    result = usuarios_collection.update_one({"_id": ObjectId(current_user["id"])}, {"$set": update_data})
    if result.matched_count == 1:
        updated_user = usuarios_collection.find_one({"_id": ObjectId(current_user["id"])})
        return serialize_doc(updated_user)
    raise HTTPException(status_code=404, detail="Usuario no encontrado")
