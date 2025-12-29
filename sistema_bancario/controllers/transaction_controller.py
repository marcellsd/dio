from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.database import Transaction, Account, User, TransactionType, get_db
from models.schemas import TransactionCreate, TransactionResponse
from services.auth import get_current_user

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction_data: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new transaction (deposit or withdrawal).
    
    - **account_id**: ID of the account for the transaction
    - **transaction_type**: Either "deposit" or "withdrawal"
    - **amount**: Transaction amount (must be greater than 0)
    - **description**: Optional description for the transaction
    
    **Validation Rules:**
    - Amount must be positive
    - Account must belong to the authenticated user
    - For withdrawals, account must have sufficient balance
    """
    # Validate amount is positive (already validated by Pydantic, but double-check)
    if transaction_data.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transaction amount must be greater than 0"
        )
    
    # Get the account
    result = await db.execute(select(Account).where(Account.id == transaction_data.account_id))
    account = result.scalar_one_or_none()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    # Verify that the account belongs to the current user
    if account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform transactions on this account"
        )
    
    # Validate withdrawal balance
    if transaction_data.transaction_type == TransactionType.WITHDRAWAL:
        if account.balance < transaction_data.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient balance. Current balance: {account.balance}"
            )
        # Update account balance (subtract)
        account.balance -= transaction_data.amount
    else:  # DEPOSIT
        # Update account balance (add)
        account.balance += transaction_data.amount
    
    # Create transaction
    new_transaction = Transaction(
        account_id=transaction_data.account_id,
        transaction_type=transaction_data.transaction_type,
        amount=transaction_data.amount,
        description=transaction_data.description
    )
    
    db.add(new_transaction)
    await db.commit()
    await db.refresh(new_transaction)
    
    return new_transaction


@router.get("/account/{account_id}", response_model=list[TransactionResponse])
async def get_account_transactions(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all transactions for a specific account.
    
    - **account_id**: The ID of the account
    
    Only the account owner can view their transactions.
    """
    # Verify account exists and belongs to user
    result = await db.execute(select(Account).where(Account.id == account_id))
    account = result.scalar_one_or_none()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    if account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view transactions for this account"
        )
    
    # Get all transactions for this account
    result = await db.execute(
        select(Transaction)
        .where(Transaction.account_id == account_id)
        .order_by(Transaction.created_at.desc())
    )
    transactions = result.scalars().all()
    
    return list(transactions)

