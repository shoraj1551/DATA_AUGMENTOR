import requests

def fetch_content(url):
    """
    Fetch the HTML content of the given URL.
    
    Args:
        url (str): The URL to fetch.
        
    Returns:
        str: The HTML content of the page.
        
    Raises:
        requests.exceptions.RequestException: If the request fails.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch {url}: {str(e)}")
