from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
)
from sqlalchemy.orm import relationship

from app.database import Base


class Bank(Base):
    __tablename__ = "bank"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    active = Column(Boolean)
    hashed_password = Column(String)
    customers = relationship("Customer", back_populates="bank")
    loan_package = relationship("LoanPackage", back_populates="bank")
    proof_doc = relationship(
        "BankRegistrationDocument", back_populates="bank", uselist=False
    )


class Customer(Base):
    __tablename__ = "customer"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )
    name = Column(String, index=True)
    is_employed = Column(Boolean)
    income = Column(Float)
    is_graduated = Column(Boolean)
    residential_assets = Column(Float)
    commercial_assets = Column(Float)
    luxury_assets = Column(Float)
    bank_assets = Column(Float)
    credit_score = Column(Integer)
    loan_amount = Column(Float)
    loan_term = Column(Integer)
    approval_status = Column(Boolean)
    bank_id = Column(String, ForeignKey("bank.id"))
    bank = relationship("Bank", back_populates="customers")


class LoanPackage(Base):
    __tablename__ = "loan_package"

    id = Column(Integer, primary_key=True, index=True)
    loan_amount = Column(Float)
    interest_rate = Column(Float)
    loan_term = Column(Integer)
    loan_type = Column(String, index=True)
    bank_id = Column(String, ForeignKey("bank.id"))
    bank = relationship("Bank", back_populates="loan_package")


class BankRegistrationDocument(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    file_content = Column(LargeBinary)
    bank_id = Column(String, ForeignKey("bank.id"))
    bank = relationship("Bank", back_populates="proof_doc")
