# routers/instruments.py
from fastapi import APIRouter
from connectors.tingo import list_instruments

router = APIRouter(prefix="/instruments", tags=["instruments"])

@router.get("")
def instruments():
    return {"items": list_instruments()}

