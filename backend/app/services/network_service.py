from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.models.network import Network
from app.models.investment import Investment, TeamInvestment
from app.models.user import User
from app.services.notification_service import NotificationService

class NetworkService:
    @staticmethod
    def get_upline_members(db: Session, user_id: str, max_levels: int = 5) -> List[dict]:
        """
        Get a user's upline members (referrers) up to max_levels
        Returns a list of dicts with user_id and level
        """
        upline_members = []
        current_user_id = user_id
        current_level = 1
        
        while current_level <= max_levels:
            # Get the network record for the current user
            network = db.query(Network).filter(Network.user_id == current_user_id).first()
            if not network or not network.referred_by:
                break
                
            # Add the referrer to the upline list
            upline_members.append({
                "user_id": network.referred_by,
                "level": current_level
            })
            
            # Move up to the next level
            current_user_id = network.referred_by
            current_level += 1
        
        return upline_members
    
    @staticmethod
    def process_team_investment(db: Session, investment_id: str) -> List[TeamInvestment]:
        """
        Process team investments for a new investment
        Creates team investment records for upline members
        """
        # Get the investment
        investment = db.query(Investment).filter(Investment.id == investment_id).first()
        if not investment:
            raise ValueError(f"Investment with ID {investment_id} not found")
        
        # Get the investor
        user = db.query(User).filter(User.id == investment.user_id).first()
        if not user:
            raise ValueError(f"User with ID {investment.user_id} not found")
        
        # Get upline members (up to 5 levels)
        upline_members = NetworkService.get_upline_members(db, user.id, max_levels=5)
        
        # Calculate commission percentages for each level
        level_percentages = {
            1: 0.10,  # 10% for level 1
            2: 0.05,  # 5% for level 2
            3: 0.03,  # 3% for level 3
            4: 0.02,  # 2% for level 4
            5: 0.01,  # 1% for level 5
        }
        
        team_investments = []
        
        # Create team investment records for each upline member
        for member in upline_members:
            level = member["level"]
            user_id = member["user_id"]
            
            # Calculate commission amount based on level
            percentage = level_percentages.get(level, 0)
            amount = investment.amount * percentage
            
            # Create team investment record
            team_investment = TeamInvestment(
                investment_id=investment.id,
                team_member_id=user_id,
                amount=amount,
                level=level
            )
            db.add(team_investment)
            team_investments.append(team_investment)
            
            # Create notification for the team member
            try:
                NotificationService.create_team_investment_notification(
                    db=db,
                    user_id=user_id,
                    amount=amount,
                    level=level,
                    team_member_name=user.name
                )
            except Exception as e:
                # Log the error but continue processing
                print(f"Error creating team investment notification: {str(e)}")
        
        # Commit all team investments
        db.flush()
        
        return team_investments
