from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
import os

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client["Cluster"]

usuarios_collection = db["usuarios"]
materias_collection = db["materias"]
notas_collection = db["notas"]

def serialize_doc(doc):
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            doc[key] = str(value)
        elif hasattr(value, 'isoformat'):
            doc[key] = value.isoformat()
    return doc