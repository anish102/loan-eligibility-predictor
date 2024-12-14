import os
from datetime import timedelta

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import get_password_hash, verify_password
from app.database import get_db
from app.models import Admin

router = APIRouter()

pwd = os.getenv("ADMIN_PASS")


class AdminBase(BaseModel):
    username: str
    password: str


def create_admin(db: Session):
    existing_admin = db.query(Admin).first()
    if not existing_admin:
        hashed_pwd = get_password_hash(pwd)
        admin = Admin(username="admin", hashed_password=hashed_pwd)
        db.add(admin)
        db.commit()
        db.refresh(admin)


@router.post("/admin")
async def login(
    admin: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    existing_admin = db.query(Admin).first()
    if not existing_admin or not verify_password(
        admin.password, existing_admin.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    return {"message": "Admin authorized!"}
