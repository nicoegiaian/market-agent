from fastapi import FastAPI
from routers import prices, instruments
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()
origins = os.getenv("CORS_ORIGINS","*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(prices.router)
app.include_router(instruments.router)

@app.get("/health")
def health():
    return {"ok": True}

