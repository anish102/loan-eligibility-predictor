import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.database import engine
from app.models import Base
from app.routers import admin, bank, customer, package

app = FastAPI()

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
app.include_router(package.router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def read_home():
    home_path = os.path.join("app", "static", "index.html")
    if os.path.exists(home_path):
        with open(home_path, "r") as file:
            content = file.read()
        return HTMLResponse(content=content)
    else:
        return HTMLResponse(content="Home page not found", status_code=404)
