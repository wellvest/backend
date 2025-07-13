from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api import deps
from app.models.plan import Plan
from app.schemas.plan import Plan as PlanSchema, PlanCreate, PlanUpdate

router = APIRouter()

@router.get("/", response_model=List[PlanSchema])
def get_plans(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
):
    """
    Retrieve all plans.
    """
    plans = db.query(Plan).offset(skip).limit(limit).all()
    return plans

@router.get("/{plan_id}", response_model=PlanSchema)
def get_plan(
    plan_id: str,
    db: Session = Depends(deps.get_db),
):
    """
    Get a specific plan by id.
    """
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found",
        )
    return plan

@router.post("/", response_model=PlanSchema, status_code=status.HTTP_201_CREATED)
def create_plan(
    *,
    db: Session = Depends(deps.get_db),
    plan_in: PlanCreate,
    current_user = Depends(deps.get_current_active_superuser),
):
    """
    Create new plan (admin only).
    """
    plan = Plan(
        name=plan_in.name,
        min_amount=plan_in.min_amount,
        max_amount=plan_in.max_amount,
        returns_percentage=plan_in.returns_percentage,
        duration_months=plan_in.duration_months,
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan

@router.put("/{plan_id}", response_model=PlanSchema)
def update_plan(
    *,
    db: Session = Depends(deps.get_db),
    plan_id: str,
    plan_in: PlanUpdate,
    current_user = Depends(deps.get_current_active_superuser),
):
    """
    Update a plan (admin only).
    """
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found",
        )
    
    update_data = plan_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(plan, field, value)
    
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan

@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plan(
    *,
    db: Session = Depends(deps.get_db),
    plan_id: str,
    current_user = Depends(deps.get_current_active_superuser),
):
    """
    Delete a plan (admin only).
    """
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found",
        )
    
    db.delete(plan)
    db.commit()
    return None
