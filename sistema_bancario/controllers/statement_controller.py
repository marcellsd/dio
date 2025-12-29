from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.database import Account, Transaction, User, get_db
from models.schemas import StatementResponse, AccountResponse, TransactionResponse
from services.auth import get_current_user

router = APIRouter(prefix="/statements", tags=["Statements"])


@router.get("/account/{account_id}", response_model=StatementResponse)
async def get_account_statement(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the complete statement for an account, including all transactions.
    
    - **account_id**: The ID of the account
    
    Returns:
    - Account information (number, balance, etc.)
    - List of all transactions (ordered by date, newest first)
    - Total number of transactions
    
    Only the account owner can view their statement.
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
            detail="Not authorized to view statement for this account"
        )
    
    # Get all transactions for this account
    result = await db.execute(
        select(Transaction)
        .where(Transaction.account_id == account_id)
        .order_by(Transaction.created_at.desc())
    )
    transactions = result.scalars().all()
    
    return StatementResponse(
        account=AccountResponse.model_validate(account),
        transactions=[TransactionResponse.model_validate(t) for t in transactions],
        total_transactions=len(transactions)
    )

