from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Bank, LoanPackage
from app.routers.customer import get_current_bank

router = APIRouter()


class LoanPackageBase(BaseModel):
    loan_name: str
    loan_amount: float
    min_income: float
    min_assets: float
    min_credit_score: float
    loan_term: int
    interest_rate: float


@router.get("/loan_packages")
async def get_packages(
    bank: Bank = Depends(get_current_bank), db: Session = Depends(get_db)
):
    loan_packages = db.query(LoanPackage).filter(LoanPackage.bank_id == bank.id).all()
    return {"packages": loan_packages}


@router.post("/loan_package")
async def add_package(
    package: LoanPackageBase,
    bank: Bank = Depends(get_current_bank),
    db: Session = Depends(get_db),
):
    new_package = LoanPackage(
        loan_name=package.loan_name,
        loan_amount=package.loan_amount,
        min_income=package.min_income,
        min_assets=package.min_assets,
        min_credit_score=package.min_credit_score,
        interest_rate=package.interest_rate,
        loan_term=package.loan_term,
        bank_id=bank.id,
    )
    db.add(new_package)
    db.commit()
    db.refresh(new_package)
    return {"message": "Package added successfully", "package_id": new_package.id}


@router.get("/loan_package/{package_id}")
async def get_package(
    package_id: int,
    bank: Bank = Depends(get_current_bank),
    db: Session = Depends(get_db),
):
    package = (
        db.query(LoanPackage)
        .filter(LoanPackage.id == package_id, LoanPackage.bank_id == bank.id)
        .first()
    )
    if not package:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No package with id {package_id} found",
        )
    return {"package": package}


@router.put("/loan_package/{package_id}")
async def update_package(
    package_id: int,
    package: LoanPackageBase,
    bank: Bank = Depends(get_current_bank),
    db: Session = Depends(get_db),
):
    existing_package = (
        db.query(LoanPackage)
        .filter(LoanPackage.id == package_id, LoanPackage.bank_id == bank.id)
        .first()
    )
    if not existing_package:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No package with id {package_id} found",
        )
    existing_package.loan_name = package.loan_name
    existing_package.loan_amount = package.loan_amount
    existing_package.min_income = package.min_income
    existing_package.min_assets = package.min_assets
    existing_package.min_credit_score = package.min_credit_score
    existing_package.interest_rate = package.interest_rate
    existing_package.loan_term = package.loan_term
    db.commit()
    db.refresh(existing_package)
    return {"message": "Package updated successfully", "package_id": package_id}


@router.delete("/loan_package/{package_id}")
async def delete_customer(
    package_id: int,
    bank: Bank = Depends(get_current_bank),
    db: Session = Depends(get_db),
):
    existing_package = (
        db.query(LoanPackage)
        .filter(LoanPackage.id == package_id, LoanPackage.bank_id == bank.id)
        .first()
    )
    if not existing_package:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No package with id {package_id} found",
        )
    db.delete(existing_package)
    db.commit()
    return {"message": "Package deleted successfully", "customer_id": package_id}
