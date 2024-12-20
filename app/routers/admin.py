import os
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from app.auth import create_access_token

router = APIRouter()

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASS")


@router.post("/admin")
async def login(admin: OAuth2PasswordRequestForm = Depends()):
    if admin.username != ADMIN_USERNAME or admin.password != ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": ADMIN_USERNAME}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout():
    response = JSONResponse(
        content={"message": "Logged out"},
        status_code=status.HTTP_200_OK,
    )
    response.headers["Location"] = "/admin"
    return response
