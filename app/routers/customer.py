from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import get_current_user, oauth2_scheme
from app.database import get_db
from app.load_model import predict_approval_status
from app.loan_package_recommendation import loan_package_recommender
from app.models import Bank, Customer, LoanPackage

router = APIRouter()


class CustomerBase(BaseModel):
    name: str
    is_employed: bool
    income: float
    is_graduated: bool
    residential_assets: float = 0
    commercial_assets: float = 0
    luxury_assets: float = 0
    bank_assets: float = 0
    credit_score: int
    loan_amount: float
    loan_term: int
    approval_status: bool | None = None


class CustomerLoan(CustomerBase):
    loan_package: int | None = None


def get_current_bank(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    bank_id = get_current_user(token)
    bank = db.query(Bank).filter(Bank.id == bank_id).first()
    if not bank:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid bank"
        )
    return bank


@router.get("/customers")
async def get_customers(
    bank: Bank = Depends(get_current_bank), db: Session = Depends(get_db)
):
    customers = db.query(Customer).filter(Customer.bank_id == bank.id).all()
    return {"customers": customers}


@router.post("/customer")
async def add_customer(
    customer: CustomerBase,
    bank: Bank = Depends(get_current_bank),
    db: Session = Depends(get_db),
):
    new_customer = Customer(
        name=customer.name,
        is_employed=customer.is_employed,
        income=customer.income,
        is_graduated=customer.is_graduated,
        residential_assets=customer.residential_assets,
        commercial_assets=customer.commercial_assets,
        luxury_assets=customer.luxury_assets,
        bank_assets=customer.bank_assets,
        credit_score=customer.credit_score,
        loan_amount=customer.loan_amount,
        loan_term=customer.loan_term,
        approval_status=customer.approval_status,
        bank_id=bank.id,
    )
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return {"message": "Customer added successfully", "customer_id": new_customer.id}


@router.get("/customer/{customer_id}")
async def get_customer(
    customer_id: int,
    bank: Bank = Depends(get_current_bank),
    db: Session = Depends(get_db),
):
    customer = (
        db.query(Customer)
        .filter(Customer.id == customer_id, Customer.bank_id == bank.id)
        .first()
    )
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No customer with id {customer_id} found",
        )
    return {"customer": customer}


@router.put("/customer/{customer_id}")
async def update_customer(
    customer_id: int,
    customer: CustomerBase,
    bank: Bank = Depends(get_current_bank),
    db: Session = Depends(get_db),
):
    existing_customer = (
        db.query(Customer)
        .filter(Customer.id == customer_id, Customer.bank_id == bank.id)
        .first()
    )
    if not existing_customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No customer with id {customer_id} found",
        )
    existing_customer.name = customer.name
    existing_customer.is_employed = customer.is_employed
    existing_customer.income = customer.income
    existing_customer.is_graduated = customer.is_graduated
    existing_customer.residential_assets = customer.residential_assets
    existing_customer.commercial_assets = customer.commercial_assets
    existing_customer.luxury_assets = customer.luxury_assets
    existing_customer.bank_assets = customer.bank_assets
    existing_customer.credit_score = customer.credit_score
    existing_customer.loan_amount = customer.loan_amount
    existing_customer.loan_term = customer.loan_term
    existing_customer.approval_status = customer.approval_status
    db.commit()
    db.refresh(existing_customer)
    return {"message": "Customer updated successfully", "customer_id": customer_id}


@router.put("/check_approval_status/{customer_id}")
async def check_approval_status(
    customer_id: int,
    customer: CustomerBase,
):
    approval_status = predict_approval_status(customer.model_dump())
    if approval_status:
        message = f"Customer {customer.name} is eligible for getting loan."
    else:
        message = f"Customer {customer.name} is not eligible for getting loan."
    return {"approval_status": approval_status, "message": message}


@router.put("/recommend_loan_package/{customer_id}")
async def recommend_loan_package(
    customer_id: int,
    customer: CustomerLoan,
    bank: Bank = Depends(get_current_bank),
    db: Session = Depends(get_db),
):
    customer_data = customer.model_dump()
    if not customer_data["approval_status"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Customer with id {customer_id} is not eligible for getting loan!",
        )
    packages = db.query(LoanPackage).filter(LoanPackage.bank_id == bank.id).all()
    package_ids = loan_package_recommender(packages, customer_data)
    return {"message": "Packages retrieved successfully", "packages": package_ids}


@router.delete("/customer/{customer_id}")
async def delete_customer(
    customer_id: int,
    bank: Bank = Depends(get_current_bank),
    db: Session = Depends(get_db),
):
    existing_customer = (
        db.query(Customer)
        .filter(Customer.id == customer_id, Customer.bank_id == bank.id)
        .first()
    )
    if not existing_customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No customer with id {customer_id} found",
        )
    db.delete(existing_customer)
    db.commit()
    return {"message": "Customer deleted successfully", "customer_id": customer_id}
