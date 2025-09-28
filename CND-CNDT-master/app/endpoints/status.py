from fastapi import APIRouter
from app.models import StatusResponse

router = APIRouter()

@router.get("/status", response_model=StatusResponse, tags=["Status"])
async def get_status():
    """Verifica se a API está online."""
    return {"status": "ok"}