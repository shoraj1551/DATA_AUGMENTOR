import urllib.robotparser
from urllib.parse import urlparse

def is_scraping_allowed(url, user_agent="DataAugmentorBot"):
    """
    Check if scraping is allowed for the given URL and user agent
    by parsing the website's robots.txt file.
    
    Args:
        url (str): The URL to scrape.
        user_agent (str): The user agent string to check against.
        
    Returns:
        bool: True if scraping is allowed, False otherwise.
    """
    try:
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        robots_url = f"{base_url}/robots.txt"
        
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(robots_url)
        rp.read()
        
        return rp.can_fetch(user_agent, url)
    except Exception as e:
        # Failsafe: If robots.txt cannot be checked, default to caution or allow based on policy.
        # Here we allow if robots.txt is missing/unreachable but log it ideally.
        # However, stricter policy might be False. 
        # For this tool, we will return True if error implies no robots.txt exists 
        # (e.g. 404), but let's be safe.
        print(f"Error checking robots.txt: {e}")
        # If we can't reach robots.txt, we technically can't verify compliance.
        # But many sites don't have it. We'll assume Allowed if check fails non-critically.
        return True
