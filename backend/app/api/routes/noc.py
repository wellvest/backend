from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import json
from fastapi.responses import HTMLResponse
import os

from app.core.auth import get_current_active_user
from app.db.database import get_db
from app.models.user import User, Profile
from app.models.wallet import IncomeWallet, ShoppingWallet
from app.schemas.noc import NOCResponse
import logging
logger=logging.getLogger(__name__)

router = APIRouter()

import logging

logger = logging.getLogger(__name__)

from fastapi.responses import JSONResponse

@router.get("/noc/document")
async def get_noc_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get NOC document data for the current user."""
    logger.info(f"NOC data requested for user: {current_user.id}")
    print(f"NOC data requested for user: {current_user.id}")
    
    try:
        # Get user data
        try:
            profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
            logger.debug(f"Profile found: {profile is not None}")
        except Exception as e:
            logger.error(f"Error querying profile: {str(e)}", exc_info=True)
            raise
            
        try:
            income_wallet = db.query(IncomeWallet).filter(IncomeWallet.user_id == current_user.id).first()
            logger.debug(f"Income wallet found: {income_wallet is not None}")
        except Exception as e:
            logger.error(f"Error querying income wallet: {str(e)}", exc_info=True)
            raise
            
        try:
            shopping_wallet = db.query(ShoppingWallet).filter(ShoppingWallet.user_id == current_user.id).first()
            logger.debug(f"Shopping wallet found: {shopping_wallet is not None}")
        except Exception as e:
            logger.error(f"Error querying shopping wallet: {str(e)}", exc_info=True)
            raise
        
        income_balance = income_wallet.balance if income_wallet else 0
        shopping_balance = shopping_wallet.balance if shopping_wallet else 0
        plan_amount = profile.plan_amount if profile else 0
        
        logger.debug(f"Income balance: {income_balance}, Shopping balance: {shopping_balance}, Plan amount: {plan_amount}")
        
        # Check eligibility for NOC
        if plan_amount <= 0 and income_balance <= 0 and shopping_balance <= 0:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You must have an active plan or positive balance to access NOC document"
            )
        
        # Calculate values for NOC with proper validation
        try:
            plan_amount = float(plan_amount) if plan_amount else 0.0
            amount_paid = plan_amount * 0.5  # Example calculation, adjust as needed
            total_amount_paid = float(amount_paid)
            incentive_amount = plan_amount * 0.1  # Example calculation
            foreclosure_charges = 0.0
            final_payable_amount = plan_amount - amount_paid
            due_date = datetime.now() + timedelta(days=60)  # Example due date
        except (ValueError, TypeError):
            # Fallback values if calculations fail
            plan_amount = 0.0
            amount_paid = 0.0
            total_amount_paid = 0.0
            incentive_amount = 0.0
            foreclosure_charges = 0.0
            final_payable_amount = 0.0
            due_date = datetime.now() + timedelta(days=60)
        
        # Ensure member_id and name have default values if they're None or empty
        member_id = current_user.member_id if current_user.member_id else "N/A"
        name = current_user.name if current_user.name else "User"
        company_name = "WellVest Financial Services Pvt. Ltd."
        
        # Create response data directly as a dictionary
        response_data = {
            "user_id": str(current_user.id),
            "member_id": member_id,
            "name": name,
            "plan_amount": plan_amount,
            "amount_paid": amount_paid,
            "total_amount_paid": total_amount_paid,
            "incentive_amount": incentive_amount,
            "foreclosure_charges": foreclosure_charges,
            "final_payable_amount": final_payable_amount,
            "due_date": due_date.isoformat(),
            "company_name": company_name,
            "generated_at": datetime.now().isoformat()
        }
        
        # Log the response data
        print(f"NOC response data: {response_data}")
        logger.info(f"NOC response data: {response_data}")
        
        return response_data
        
    except Exception as e:
        error_msg = f"Error in NOC data generation: {str(e)}"
        print(error_msg)
        logger.error(error_msg, exc_info=True)  # Include full exception details in logs
        
        # Return a more user-friendly error with technical details in logs
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating NOC document. Please try again later or contact support."
        )

@router.get("/noc/download", response_class=HTMLResponse)
async def download_noc_html(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Generate NOC document as HTML for client-side PDF generation."""
    # Get NOC data
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    income_wallet = db.query(IncomeWallet).filter(IncomeWallet.user_id == current_user.id).first()
    shopping_wallet = db.query(ShoppingWallet).filter(ShoppingWallet.user_id == current_user.id).first()
    
    income_balance = income_wallet.balance if income_wallet else 0
    shopping_balance = shopping_wallet.balance if shopping_wallet else 0
    plan_amount = profile.plan_amount if profile else 0
    
    # Check eligibility for NOC
    if plan_amount <= 0 and income_balance <= 0 and shopping_balance <= 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must have an active plan or positive balance to access NOC document"
        )
    
    # Calculate values for NOC
    amount_paid = plan_amount * 0.5  # Example calculation, adjust as needed
    total_amount_paid = amount_paid
    incentive_amount = plan_amount * 0.1  # Example calculation
    foreclosure_charges = 0.0
    final_payable_amount = plan_amount - amount_paid
    due_date = datetime.now() + timedelta(days=60)  # Example due date
    
    # Ensure member_id and name have default values if they're None or empty
    member_id = current_user.member_id if current_user.member_id else "N/A"
    name = current_user.name if current_user.name else "User"
    company_name = "WellVest Financial Services Pvt. Ltd."
    
    # Generate HTML content for client-side PDF generation
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>NOC Certificate - {member_id}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                border: 1px solid #ddd;
            }}
            .header {{
                text-align: center;
                border-bottom: 2px solid #f0f0f0;
                padding-bottom: 20px;
                margin-bottom: 20px;
            }}
            .title {{
                font-size: 24px;
                font-weight: bold;
                color: #333;
                margin-bottom: 5px;
            }}
            .date {{
                text-align: right;
                margin-bottom: 20px;
            }}
            .subject {{
                font-weight: bold;
                margin-bottom: 20px;
            }}
            .section {{
                margin-bottom: 20px;
            }}
            .financial-summary {{
                margin: 20px 0;
            }}
            .financial-summary table {{
                width: 100%;
                border-collapse: collapse;
            }}
            .financial-summary td {{
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
            }}
            .financial-summary td:first-child {{
                width: 70%;
            }}
            .financial-summary td:last-child {{
                text-align: right;
                font-weight: bold;
            }}
            .highlight {{
                background-color: #f9f9f9;
            }}
            .footer {{
                margin-top: 40px;
                border-top: 1px solid #f0f0f0;
                padding-top: 20px;
            }}
            @media print {{
                body {{
                    border: none;
                }}
                .no-print {{
                    display: none;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="title">ACKNOWLEDGMENT CERTIFICATE CUM NO DUES (NOC) CERTIFICATE</div>
        </div>
        
        <div class="date">Date: {datetime.now().strftime('%d-%m-%Y')}</div>
        
        <div class="subject">
            Subject: Final Settlement and Closure (NOC) of Financing Agreement (Financer ID: {member_id})
        </div>
        
        <p>Dear {name},</p>
        
        <p>
            We, <strong>{company_name}</strong>, hereby acknowledge and confirm the following in respect of
            the financing arrangement entered into with you under Financer ID: <strong>{member_id}</strong>:
        </p>
        
        <div class="section">
            <h3>1. Financial Summary:</h3>
            <div class="financial-summary">
                <table>
                    <tr>
                        <td>Total Principal Amount Financed: INR</td>
                        <td>₹{plan_amount:.2f}/-</td>
                    </tr>
                    <tr>
                        <td>Amount Paid to Patron Till Date: INR</td>
                        <td>₹{amount_paid:.2f}/-</td>
                    </tr>
                    <tr>
                        <td>Total Amount Paid to Patron: INR</td>
                        <td>₹{total_amount_paid:.2f}/-</td>
                    </tr>
                    <tr>
                        <td colspan="2">Principal Adjustment: From the initial principal amount, the amount already paid to the patron as of the termination date shall be deducted.</td>
                    </tr>
                    <tr>
                        <td>Total Incentive Amount Paid (if any): INR</td>
                        <td>₹{incentive_amount:.2f}/-</td>
                    </tr>
                    <tr class="highlight">
                        <td colspan="2">This Incentive amount is not being deducted by the company</td>
                    </tr>
                    <tr>
                        <td>Foreclosure Charges</td>
                        <td>₹{foreclosure_charges:.2f}/-</td>
                    </tr>
                    <tr>
                        <td>Final Payable Amount (if any): INR</td>
                        <td>₹{final_payable_amount:.2f}/-</td>
                    </tr>
                    <tr>
                        <td>The due date for final payment is:</td>
                        <td>{due_date.strftime('%Y-%m-%d')}</td>
                    </tr>
                </table>
            </div>
            
            <p>
                In case the amount already paid to the patron exceeds the principal amount originally financed, such excess shall remain with the patron/financier, and {company_name} shall make no claim over the same.
            </p>
        </div>
        
        <div class="section">
            <h3>3. Termination of Agreement:</h3>
            <p>
                Upon execution of this certificate and form, once the payment is credited to your bank account,
                all the original financing agreements under this financer ID shall be considered closed, and all
                obligations between the parties shall cease to exist with no further liability or dues remaining.
            </p>
            
            <p>
                We request you to kindly authenticate this NOC form by entering one time password to be
                received on your phone as your confirmation and acceptance of the above.
            </p>
            
            <p>Thank you for your cooperation and association.</p>
        </div>
        
        <div class="footer">
            <p>Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}</p>
            <p>This is a system-generated document and does not require a physical signature.</p>
        </div>
        
        <div class="no-print">
            <script>
                // Auto-print when the page loads
                window.onload = function() {{
                    // You can uncomment this to auto-print
                    // window.print();
                }};
            </script>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)
