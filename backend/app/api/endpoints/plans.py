from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api import deps
from app.schemas.plan import Plan as PlanSchema, PlanCreate, PlanUpdate
from app.services.plan_service import PlanService

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
    plans = PlanService.get_plans(db, skip=skip, limit=limit)
    return plans

@router.get("/{plan_id}", response_model=PlanSchema)
def get_plan(
    plan_id: str,
    db: Session = Depends(deps.get_db),
):
    """
    Get a specific plan by id.
    """
    plan = PlanService.get_plan_by_id(db, plan_id)
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
    plan = PlanService.create_plan(db, plan_in)
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
    plan = PlanService.update_plan(db, plan_id, plan_in)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found",
        )
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
    success = PlanService.delete_plan(db, plan_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found",
        )
    return None
