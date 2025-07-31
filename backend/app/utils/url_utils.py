"""
Utility functions for handling URLs in the API
"""
from urllib.parse import urlparse

def ensure_relative_url(url: str) -> str:
    """
    Ensures that a URL is relative by removing any domain information.
    This is particularly useful for avatar and upload URLs that should be served
    relative to the backend server rather than with absolute URLs.
    
    Args:
        url: The URL to process
        
    Returns:
        A relative URL path
    """
    if not url:
        return ""
        
    # If it's already a relative URL, return it as is
    if not url.startswith('http'):
        return url
        
    # Parse the URL and extract just the path component
    parsed_url = urlparse(url)
    return parsed_url.path
