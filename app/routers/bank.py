from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import create_access_token, get_password_hash, verify_password
from app.database import get_db
from app.models import Bank

router = APIRouter()


class BankBase(BaseModel):
    id: str
    name: str


class BankPass(BankBase):
    password: str


@router.post("/register")
async def register(bank: BankPass, db: Session = Depends(get_db)):
    existing_bank_id = db.query(Bank).filter(Bank.id == bank.id).first()
    existing_bank_name = db.query(Bank).filter(Bank.name == bank.name).first()
    if existing_bank_id or existing_bank_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bank with the given id or name already exists.",
        )
    hashed_password = get_password_hash(bank.password)
    new_bank = Bank(id=bank.id, name=bank.name, hashed_password=hashed_password)
    db.add(new_bank)
    db.commit()
    db.refresh(new_bank)
    return {"message": "Bank registered successfully", "name": new_bank.name}


@router.post("/login")
async def login(
    bank: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    bank_record = db.query(Bank).filter(Bank.id == bank.username).first()
    if not bank_record or not verify_password(
        bank.password, bank_record.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": bank_record.id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout():
    response = JSONResponse(
        content={"message": "Logged out"},
        status_code=status.HTTP_200_OK,
    )
    response.headers["Location"] = "/login"
    return response
