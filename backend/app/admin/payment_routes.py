from fastapi import APIRouter, Depends, HTTPException, status, Form, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.services.payment_service import PaymentService
from app.models.payment import PaymentStatus

router = APIRouter(prefix="/admin/payment")

@router.get("/approve/{payment_id}")
async def approve_payment_form(
    request: Request,
    payment_id: str,
    db: Session = Depends(get_db),
):
    """Admin form for approving a payment"""
    payment = PaymentService.get_payment_by_id(db, payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )
    
    if payment.status != PaymentStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment is not in pending status",
        )
    
    # Return a simple HTML form for approval
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Approve Payment</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {{ padding: 20px; }}
            .container {{ max-width: 800px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Approve Payment</h2>
            <div class="card mb-4">
                <div class="card-body">
                    <h5 class="card-title">Payment Details</h5>
                    <p><strong>ID:</strong> {payment.id}</p>
                    <p><strong>User ID:</strong> {payment.user_id}</p>
                    <p><strong>Plan ID:</strong> {payment.plan_id}</p>
                    <p><strong>Amount:</strong> ₹{payment.amount}</p>
                    <p><strong>UPI Reference:</strong> {payment.upi_ref_id or 'N/A'}</p>
                    <p><strong>Created At:</strong> {payment.created_at}</p>
                </div>
            </div>
            
            <form action="/admin/payment/approve/{payment_id}/submit" method="post">
                <div class="mb-3">
                    <label for="admin_notes" class="form-label">Admin Notes</label>
                    <textarea class="form-control" id="admin_notes" name="admin_notes" rows="3"></textarea>
                </div>
                <button type="submit" class="btn btn-success">Approve Payment</button>
                <a href="/admin/payment" class="btn btn-secondary">Cancel</a>
            </form>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

@router.post("/approve/{payment_id}/submit")
async def approve_payment_submit(
    payment_id: str,
    admin_notes: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    """Process payment approval"""
    try:
        approved_payment = PaymentService.approve_payment(db, payment_id, admin_notes)
        if not approved_payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found or already processed",
            )
        
        # Redirect back to the payment list
        return RedirectResponse(url="/admin/payment", status_code=303)
    except Exception as e:
        # Log the error
        print(f"Error approving payment: {str(e)}")
        # Return an error message
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body {{ padding: 20px; }}
                .container {{ max-width: 800px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="alert alert-danger">
                    <h4>Error approving payment</h4>
                    <p>{str(e)}</p>
                </div>
                <a href="/admin/payment" class="btn btn-primary">Back to Payments</a>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content, status_code=500)

@router.get("/reject/{payment_id}")
async def reject_payment_form(
    request: Request,
    payment_id: str,
    db: Session = Depends(get_db),
):
    """Admin form for rejecting a payment"""
    payment = PaymentService.get_payment_by_id(db, payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )
    
    if payment.status != PaymentStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment is not in pending status",
        )
    
    # Return a simple HTML form for rejection
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Reject Payment</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {{ padding: 20px; }}
            .container {{ max-width: 800px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Reject Payment</h2>
            <div class="card mb-4">
                <div class="card-body">
                    <h5 class="card-title">Payment Details</h5>
                    <p><strong>ID:</strong> {payment.id}</p>
                    <p><strong>User ID:</strong> {payment.user_id}</p>
                    <p><strong>Plan ID:</strong> {payment.plan_id}</p>
                    <p><strong>Amount:</strong> ₹{payment.amount}</p>
                    <p><strong>UPI Reference:</strong> {payment.upi_ref_id or 'N/A'}</p>
                    <p><strong>Created At:</strong> {payment.created_at}</p>
                </div>
            </div>
            
            <form action="/admin/payment/reject/{payment_id}/submit" method="post">
                <div class="mb-3">
                    <label for="admin_notes" class="form-label">Rejection Reason</label>
                    <textarea class="form-control" id="admin_notes" name="admin_notes" rows="3" required></textarea>
                </div>
                <button type="submit" class="btn btn-danger">Reject Payment</button>
                <a href="/admin/payment" class="btn btn-secondary">Cancel</a>
            </form>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

@router.post("/reject/{payment_id}/submit")
async def reject_payment_submit(
    payment_id: str,
    admin_notes: str = Form(...),
    db: Session = Depends(get_db),
):
    """Process payment rejection"""
    try:
        rejected_payment = PaymentService.reject_payment(db, payment_id, admin_notes)
        if not rejected_payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found or already processed",
            )
        
        # Redirect back to the payment list
        return RedirectResponse(url="/admin/payment", status_code=303)
    except Exception as e:
        # Log the error
        print(f"Error rejecting payment: {str(e)}")
        # Return an error message
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body {{ padding: 20px; }}
                .container {{ max-width: 800px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="alert alert-danger">
                    <h4>Error rejecting payment</h4>
                    <p>{str(e)}</p>
                </div>
                <a href="/admin/payment" class="btn btn-primary">Back to Payments</a>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content, status_code=500)
