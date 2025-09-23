from bson import ObjectId
from database.db import notas_collection, usuarios_collection, materias_collection, serialize_doc
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from openai import OpenAI
import os
from models.notes import NoteModel, NoteUpdate
from auth.dependencies import get_current_user
from fastapi import Depends
from datetime import datetime

router = APIRouter(prefix="/notes", tags=["Notes"])

@router.get("/")
async def get_notes(current_user: dict = Depends(get_current_user)):
    notes = []
    for note in notas_collection.find({"user_id": ObjectId(current_user["id"])}):
        notes.append(serialize_doc(note))
    return JSONResponse(content=notes)

@router.get("/{note_id}")
async def get_note(note_id: str, current_user: dict = Depends(get_current_user)):
    note = notas_collection.find_one({"_id": ObjectId(note_id), "user_id": ObjectId(current_user["id"])})
    if not note:
        raise HTTPException(status_code=404, detail="Nota no encontrada")

    note_data = serialize_doc(note)
    content = note_data.get("content", "")
    subject_id = note_data.get("subject_id")
    subject = None
    if subject_id:
        subject = materias_collection.find_one({"_id": ObjectId(subject_id)})
    subject_name = subject["name"] if subject and "name" in subject else "la materia"

    # Preparar prompt para IA
    prompt = f"""
    Dada la siguiente nota de la materia '{subject_name}':
    """
    prompt += content + "\n\n"
    prompt += "1. Dame un resumen claro y breve de lo anotado.\n"
    prompt += "2. Dame 5 preguntas de opción múltiple sobre el contenido, cada una con 4 opciones y la respuesta correcta marcada.\n"

    # Llamada a OpenRouter
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY", "")
    )
    completion = client.chat.completions.create(
        model="nvidia/nemotron-nano-9b-v2:free",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    ai_response = completion.choices[0].message.content

    # Intentar separar resumen y preguntas
    resumen = ""
    preguntas = []
    if ai_response:
        partes = ai_response.split("2.")
        if len(partes) == 2:
            resumen = partes[0].replace("1.", "").strip()
            preguntas = partes[1].strip()
        else:
            resumen = ai_response.strip()

    return {
        "nota": note_data,
        "resumen": resumen,
        "preguntas": preguntas
    }

@router.get("/by-subject/{subject_id}")
async def get_notes_by_subject(subject_id: str, current_user: dict = Depends(get_current_user)):
    notes = []
    query = {
        "$and": [
            {"user_id": {"$in": [ObjectId(current_user["id"]), str(current_user["id"]) ]}},
            {"subject_id": {"$in": [ObjectId(subject_id), str(subject_id)] }}
        ]
    }
    for note in notas_collection.find(query):
        notes.append(serialize_doc(note))
    return JSONResponse(content=notes)

@router.post("/", response_model=NoteModel)
async def create_note(note: NoteModel, current_user: dict = Depends(get_current_user)):
    # Verificar que el subject_id existe
    subject_id = note.subject_id
    if isinstance(subject_id, str):
        try:
            subject_id_obj = ObjectId(subject_id)
        except Exception:
            raise HTTPException(status_code=400, detail="subject_id no es un ObjectId válido")
    else:
        subject_id_obj = subject_id
    subject = materias_collection.find_one({"_id": subject_id_obj})
    if not subject:
        raise HTTPException(status_code=404, detail="Materia no encontrada para subject_id")
    note_dict = note.dict()
    note_dict["user_id"] = ObjectId(current_user["id"])
    note_dict["created_at"] = datetime.utcnow()
    result = notas_collection.insert_one(note_dict)
    new_note = notas_collection.find_one({"_id": result.inserted_id})
    return serialize_doc(new_note)

@router.put("/{note_id}", response_model=NoteModel)
async def update_note(note_id: str, note: NoteUpdate, current_user: dict = Depends(get_current_user)):
    update_data = {k: v for k, v in note.dict(exclude_unset=True).items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No se proporcionaron campos para actualizar")
    result = notas_collection.update_one({"_id": ObjectId(note_id), "user_id": ObjectId(current_user["id"])} , {"$set": update_data})
    if result.matched_count == 1:
        updated_note = notas_collection.find_one({"_id": ObjectId(note_id)})
        return serialize_doc(updated_note)
    raise HTTPException(status_code=404, detail="Nota no encontrada")

@router.delete("/{note_id}")
async def delete_note(note_id: str, current_user: dict = Depends(get_current_user)):
    result = notas_collection.delete_one({"_id": ObjectId(note_id), "user_id": ObjectId(current_user["id"])} )
    if result.deleted_count == 1:
        return JSONResponse(content={"message": "Nota eliminada"})
    raise HTTPException(status_code=404, detail="Nota no encontrada")
