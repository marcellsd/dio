from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List
from models.database import TransactionType


# User schemas
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


# Account schemas
class AccountCreate(BaseModel):
    account_number: str = Field(..., min_length=5, max_length=20)


class AccountResponse(BaseModel):
    id: int
    user_id: int
    account_number: str
    balance: float
    created_at: datetime

    class Config:
        from_attributes = True


# Transaction schemas
class TransactionCreate(BaseModel):
    account_id: int
    transaction_type: TransactionType
    amount: float = Field(..., gt=0, description="Amount must be greater than 0")
    description: Optional[str] = None


class TransactionResponse(BaseModel):
    id: int
    account_id: int
    transaction_type: TransactionType
    amount: float
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Statement schemas
class StatementResponse(BaseModel):
    account: AccountResponse
    transactions: List[TransactionResponse]
    total_transactions: int


# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str

