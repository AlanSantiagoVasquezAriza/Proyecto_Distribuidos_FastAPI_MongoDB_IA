from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth.routes import router as auth_router
from routes.users import router as users_router
from routes.subjects import router as subjects_router
from routes.notes import router as notes_router


app = FastAPI(
    title="Asistente Inteligente de Estudio",
    description="Una API para gestionar usuarios y materias, facilitando el estudio mediante la organización de notas y tareas.",
    version="1.0.0",
)

# Habilitar CORS para cualquier origen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(subjects_router)
app.include_router(notes_router)