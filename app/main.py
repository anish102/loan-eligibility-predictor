import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.database import engine, get_db
from app.models import Base
from app.routers import admin, bank, customer


@asynccontextmanager
async def life_span(app: FastAPI):
    db = next(get_db())
    try:
        admin.create_admin(db)
        yield
    finally:
        db.close()


app = FastAPI(lifespan=life_span)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(admin.router)
app.include_router(bank.router)
app.include_router(customer.router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def read_home():
    home_path = os.path.join("app", "static", "home.html")
    if os.path.exists(home_path):
        with open(home_path, "r") as file:
            content = file.read()
        return HTMLResponse(content=content)
    else:
        return HTMLResponse(content="Home page not found", status_code=404)
