from bson import ObjectId
from fastapi.params import Depends
from database.db import materias_collection, usuarios_collection, serialize_doc
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from models.subjects import SubjectModel, SubjectUpdate
from auth.dependencies import get_current_user
from fastapi import Depends
from datetime import datetime


router = APIRouter(prefix="/subjects", tags=["Subjects"])


@router.get("/")
async def get_subjects(current_user: dict = Depends(get_current_user)):
    subjects = []
    for subject in materias_collection.find({"user_id": ObjectId(current_user["id"])}):
        subjects.append(serialize_doc(subject))
    return JSONResponse(content=subjects)

@router.get("/{subject_id}")
async def get_subject(subject_id: str, current_user: dict = Depends(get_current_user)):
    subject = materias_collection.find_one({"_id": ObjectId(subject_id), "user_id": ObjectId(current_user["id"])})
    if subject:
        return serialize_doc(subject)
    raise HTTPException(status_code=404, detail="Materia no encontrada")

@router.post("/", response_model=SubjectModel)
async def create_subject(subject: SubjectModel, current_user: dict = Depends(get_current_user)):
    subject_dict = subject.dict()
    subject_dict["user_id"] = ObjectId(current_user["id"])
    subject_dict["created_at"] = datetime.utcnow()
    result = materias_collection.insert_one(subject_dict)
    new_subject = materias_collection.find_one({"_id": result.inserted_id})
    return serialize_doc(new_subject)

@router.put("/{subject_id}", response_model=SubjectModel)
async def update_subject(subject_id: str, subject: SubjectUpdate, current_user: dict = Depends(get_current_user)):
    update_data = {k: v for k, v in subject.dict(exclude_unset=True).items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No se proporcionaron campos para actualizar")
    result = materias_collection.update_one({"_id": ObjectId(subject_id)}, {"$set": update_data})
    if result.matched_count == 1:
        updated_subject = materias_collection.find_one({"_id": ObjectId(subject_id)})
        return serialize_doc(updated_subject)
    raise HTTPException(status_code=404, detail="Materia no encontrada")

@router.delete("/{subject_id}")
async def delete_subject(subject_id: str, current_user: dict = Depends(get_current_user)):
    result = materias_collection.delete_one({"_id": ObjectId(subject_id)})
    if result.deleted_count == 1:
        return JSONResponse(content={"message": "Materia eliminada"})
    raise HTTPException(status_code=404, detail="Materia no encontrada")
