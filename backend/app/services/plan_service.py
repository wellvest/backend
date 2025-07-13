from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.plan import Plan
from app.schemas.plan import PlanCreate, PlanUpdate

class PlanService:
    @staticmethod
    def get_plans(db: Session, skip: int = 0, limit: int = 100) -> List[Plan]:
        """
        Retrieve all plans with pagination.
        """
        return db.query(Plan).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_plan_by_id(db: Session, plan_id: str) -> Optional[Plan]:
        """
        Get a specific plan by ID.
        """
        return db.query(Plan).filter(Plan.id == plan_id).first()
    
    @staticmethod
    def create_plan(db: Session, plan_data: PlanCreate) -> Plan:
        """
        Create a new plan.
        """
        db_plan = Plan(
            name=plan_data.name,
            min_amount=plan_data.min_amount,
            max_amount=plan_data.max_amount,
            returns_percentage=plan_data.returns_percentage,
            duration_months=plan_data.duration_months,
        )
        db.add(db_plan)
        db.commit()
        db.refresh(db_plan)
        return db_plan
    
    @staticmethod
    def update_plan(db: Session, plan_id: str, plan_data: PlanUpdate) -> Optional[Plan]:
        """
        Update an existing plan.
        """
        db_plan = PlanService.get_plan_by_id(db, plan_id)
        if not db_plan:
            return None
        
        update_data = plan_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_plan, field, value)
        
        db.add(db_plan)
        db.commit()
        db.refresh(db_plan)
        return db_plan
    
    @staticmethod
    def delete_plan(db: Session, plan_id: str) -> bool:
        """
        Delete a plan by ID.
        """
        db_plan = PlanService.get_plan_by_id(db, plan_id)
        if not db_plan:
            return False
        
        db.delete(db_plan)
        db.commit()
        return True
