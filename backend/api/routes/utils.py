from fastapi import APIRouter

from api.storage import storage

router = APIRouter()


@router.get("/ping")
async def pong():
    return {"message": "pong"}


@router.get("/config")
async def info():
    return {"NAUTILUS_STORAGE_URL": storage.public_url}
