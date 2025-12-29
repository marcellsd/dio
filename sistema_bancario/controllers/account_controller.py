from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.database import Account, User, get_db
from models.schemas import AccountCreate, AccountResponse
from services.auth import get_current_user

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.post("", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    account_data: AccountCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new bank account for the authenticated user.
    
    - **account_number**: Unique account number (5-20 characters)
    
    The account will be linked to the authenticated user and start with a balance of 0.0.
    """
    # Check if account number already exists
    result = await db.execute(select(Account).where(Account.account_number == account_data.account_number))
    existing_account = result.scalar_one_or_none()
    if existing_account:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account number already exists"
        )
    
    # Create new account
    new_account = Account(
        user_id=current_user.id,
        account_number=account_data.account_number,
        balance=0.0
    )
    db.add(new_account)
    await db.commit()
    await db.refresh(new_account)
    
    return new_account


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get account details by account ID.
    
    - **account_id**: The ID of the account to retrieve
    
    Only the account owner can access their account information.
    """
    result = await db.execute(select(Account).where(Account.id == account_id))
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
            detail="Not authorized to access this account"
        )
    
    return account


@router.get("", response_model=list[AccountResponse])
async def get_user_accounts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all accounts belonging to the authenticated user.
    
    Returns a list of all accounts associated with the current user.
    """
    result = await db.execute(select(Account).where(Account.user_id == current_user.id))
    accounts = result.scalars().all()
    return list(accounts)

