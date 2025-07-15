"""
Utility functions for phone number validation and normalization
"""
import re

def normalize_phone_number(phone: str) -> str:
    """
    Normalize phone number by removing country code prefixes like +91 or 91
    and ensuring it's a valid 10-digit Indian phone number.
    
    Args:
        phone: The phone number to normalize
        
    Returns:
        Normalized 10-digit phone number
        
    Raises:
        ValueError: If the phone number is invalid
    """
    if not phone:
        raise ValueError("Phone number is required")
    
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    
    # Check if it starts with country code (91 or +91)
    if digits_only.startswith('91') and len(digits_only) > 10:
        digits_only = digits_only[2:]
    
    # Validate that we have exactly 10 digits for Indian phone numbers
    if len(digits_only) != 10:
        raise ValueError("Invalid phone number. Must be 10 digits after removing country code")
    
    # Validate that the phone number starts with a valid prefix (6-9)
    if not digits_only[0] in "6789":
        raise ValueError("Invalid phone number. Must start with 6, 7, 8, or 9")
    
    return digits_only

def is_valid_phone_number(phone: str) -> bool:
    """
    Check if a phone number is valid
    
    Args:
        phone: The phone number to check
        
    Returns:
        True if valid, False otherwise
    """
    try:
        normalize_phone_number(phone)
        return True
    except ValueError:
        return False
