import secrets
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from src.configs.db import create_api_key

router = APIRouter()

class GenerateKeyRequest(BaseModel):
    name: str = "Admin Key"

@router.post("/admin/generate-key")
async def create_api_key_for_auth(payload: GenerateKeyRequest = None):
    """
    Generate a secure API key, register it in the SQLite database, and return it.
    """
    name = "Admin Key"
    if payload and payload.name:
        name = payload.name.strip()
    
    key_val = f"notes_{secrets.token_hex(16)}"
    new_key = await create_api_key(name, key_val)
    return new_key