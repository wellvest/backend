import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.services.investment_service import InvestmentService

logger = logging.getLogger(__name__)

def process_monthly_interest():
    """
    Process monthly interest payments for all active investments.
    This job runs daily but will only process interest for investments
    that are due for their monthly interest payment.
    """
    logger.info(f"Running monthly interest processing job at {datetime.now()}...")
    db = SessionLocal()
    try:
        payments_processed = InvestmentService.process_monthly_interest_payments(db)
        logger.info(f"Processed interest payments for {payments_processed} investments")
    except Exception as e:
        logger.error(f"Error processing monthly interest payments: {str(e)}")
    finally:
        db.close()

def check_investment_completion():
    """
    Check for investments that have reached their end date and mark them as completed.
    """
    logger.info(f"Running investment completion check job at {datetime.now()}...")
    db = SessionLocal()
    try:
        completed = InvestmentService.check_investment_completion(db)
        logger.info(f"Marked {completed} investments as completed")
    except Exception as e:
        logger.error(f"Error checking investment completion: {str(e)}")
    finally:
        db.close()

def setup_scheduler():
    """
    Set up the scheduler with all required jobs.
    """
    scheduler = BackgroundScheduler()
    
    # Process monthly interest payments - runs daily at 1:00 AM
    scheduler.add_job(
        process_monthly_interest,
        trigger=CronTrigger(hour=1, minute=0),
        id="process_monthly_interest",
        name="Process monthly interest payments",
        replace_existing=True
    )
    
    # Check for completed investments - runs daily at 2:00 AM
    scheduler.add_job(
        check_investment_completion,
        trigger=CronTrigger(hour=2, minute=0),
        id="check_investment_completion",
        name="Check investment completion",
        replace_existing=True
    )
    
    return scheduler