import base64
import os
from datetime import timedelta

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth import (
    create_access_token,
    get_current_user,
    get_password_hash,
    oauth2_scheme,
    verify_password,
)
from app.database import get_db
from app.models import Bank, BankRegistrationDocument

router = APIRouter()

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")


def get_admin(token: str = Depends(oauth2_scheme)):
    admin = get_current_user(token)
    if not admin or admin != ADMIN_USERNAME:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid bank"
        )
    return admin


@router.post("/register")
async def register(
    id: str = Form(...),
    name: str = Form(...),
    password: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    existing_bank_id = db.query(Bank).filter(Bank.id == id).first()
    existing_bank_name = db.query(Bank).filter(Bank.name == name).first()
    if existing_bank_id or existing_bank_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bank with the given id or name already exists.",
        )
    hashed_password = get_password_hash(password)
    new_bank = Bank(id=id, name=name, hashed_password=hashed_password)
    db.add(new_bank)
    db.commit()
    db.refresh(new_bank)
    file_content = await file.read()
    new_document = BankRegistrationDocument(
        filename=file.filename, file_content=file_content, bank_id=new_bank.id
    )
    db.add(new_document)
    db.commit()
    db.refresh(new_document)
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


@router.get("/banks")
async def get_all_banks(admin: str = Depends(get_admin), db: Session = Depends(get_db)):
    banks = db.query(Bank).all()
    return banks


@router.get("/bank/{bank_id}")
async def get_bank(
    bank_id: str,
    admin: str = Depends(get_admin),
    db: Session = Depends(get_db),
):
    bank = db.query(Bank).filter(Bank.id == bank_id).first()
    if not bank:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No bank with id {bank_id} found",
        )
    bank_data = {
        "id": bank.id,
        "name": bank.name,
        "active": bank.active,
    }
    proof_doc = bank.proof_doc
    proof_doc_data = None
    if proof_doc:
        proof_doc_data = base64.b64encode(proof_doc.file_content).decode("utf-8")
    return {"bank":bank_data,"proof_doc": proof_doc_data}


@router.put("/bank/{bank_id}")
async def update_bank(
    bank_id: str,
    active: bool,
    admin: str = Depends(get_admin),
    db: Session = Depends(get_db),
):
    bank = db.query(Bank).filter(Bank.id == bank_id).first()
    if not bank:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No bank with id {bank_id} found",
        )
    bank.active = active
    db.commit()
    db.refresh(bank)
    return {"message": "Bank activated successfully", "bank_id": bank_id}


@router.post("/logout")
async def logout():
    response = JSONResponse(
        content={"message": "Logged out"},
        status_code=status.HTTP_200_OK,
    )
    response.headers["Location"] = "/login"
    return response
