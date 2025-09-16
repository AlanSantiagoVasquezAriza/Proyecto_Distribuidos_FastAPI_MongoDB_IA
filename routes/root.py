from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from auth.dependencies import get_current_user

router = APIRouter()

@router.get("/", tags=["Root"])
async def read_root(current_user: dict = Depends(get_current_user)):
    return JSONResponse(content={"message": "Bienvenido a la API de Asistente Inteligente de Estudio"})