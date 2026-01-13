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
    
    session = requests.Session()
    retry_strategy = requests.adapters.Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    adapter = requests.adapters.HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    try:
        response = session.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.text
    except requests.exceptions.SSLError:
        # Fallback for SSL verify failed (common in some corp/dev envs)
        print(f"SSL Error for {url}. Retrying with verify=False...")
        response = session.get(url, headers=headers, timeout=15, verify=False)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch {url}: {str(e)}")
