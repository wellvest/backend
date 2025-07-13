from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.core.auth import get_current_active_user, get_current_active_superuser
from app.schemas.payment import PaymentResponse, PaymentCreate, PaymentUpdate, PaymentApproval, PaymentRejection, PaymentWithUpiRef
from app.services.payment_service import PaymentService

router = APIRouter()

@router.get("/", response_model=List[PaymentResponse])
def get_payments(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_active_superuser),
):
    """
    Retrieve all payments (admin only).
    """
    payments = PaymentService.get_payments(db, skip=skip, limit=limit)
    return payments

@router.get("/pending", response_model=List[PaymentResponse])
def get_pending_payments(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_active_superuser),
):
    """
    Retrieve all pending payments (admin only).
    """
    payments = PaymentService.get_pending_payments(db, skip=skip, limit=limit)
    return payments

@router.get("/user", response_model=List[PaymentResponse])
def get_user_payments(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_active_user),
):
    """
    Retrieve all payments for the current user.
    """
    payments = PaymentService.get_user_payments(db, user_id=current_user.id, skip=skip, limit=limit)
    return payments

@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    """
    Get a specific payment by id.
    """
    payment = PaymentService.get_payment_by_id(db, payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )
    
    # Only allow admins or the payment owner to access the payment
    if payment.user_id != current_user.id and not deps.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this payment",
        )
    
    return payment

@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(
    *,
    db: Session = Depends(get_db),
    payment_in: PaymentCreate,
    current_user = Depends(get_current_active_user),
):
    """
    Create a new payment.
    """
    # Ensure the user can only create payments for themselves
    if payment_in.user_id != current_user.id and not deps.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to create payment for another user",
        )
    
    payment = PaymentService.create_payment(db, payment_in)
    return payment

@router.patch("/{payment_id}/upi-ref", response_model=PaymentResponse)
def update_payment_upi_ref(
    *,
    db: Session = Depends(get_db),
    payment_id: str,
    upi_ref_data: PaymentWithUpiRef,
    current_user = Depends(get_current_active_user),
):
    """
    Update a payment's UPI reference ID.
    """
    payment = PaymentService.get_payment_by_id(db, payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )
    
    # Only allow the payment owner to update the UPI reference ID
    if payment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this payment",
        )
    
    payment_update = PaymentUpdate(upi_ref_id=upi_ref_data.upi_ref_id)
    updated_payment = PaymentService.update_payment(db, payment_id, payment_update)
    return updated_payment

@router.patch("/{payment_id}/approve", response_model=PaymentResponse)
def approve_payment(
    *,
    db: Session = Depends(get_db),
    payment_id: str,
    approval_data: PaymentApproval,
    current_user = Depends(get_current_active_superuser),
):
    """
    Approve a payment (admin only).
    """
    approved_payment = PaymentService.approve_payment(db, payment_id, approval_data.admin_notes)
    if not approved_payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found or already processed",
        )
    return approved_payment

@router.patch("/{payment_id}/reject", response_model=PaymentResponse)
def reject_payment(
    *,
    db: Session = Depends(get_db),
    payment_id: str,
    rejection_data: PaymentRejection,
    current_user = Depends(get_current_active_superuser),
):
    """
    Reject a payment (admin only).
    """
    rejected_payment = PaymentService.reject_payment(db, payment_id, rejection_data.admin_notes)
    if not rejected_payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found or already processed",
        )
    return rejected_payment
