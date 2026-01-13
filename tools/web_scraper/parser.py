import pandas as pd
from bs4 import BeautifulSoup
import io

def extract_tables(html_content):
    """
    Extract all tables from HTML content using pandas.
    
    Args:
        html_content (str): The raw HTML string.
        
    Returns:
        list: A list of pandas DataFrames found in the HTML.
    """
    try:
        # Use StringIO to avoid deprecation warning for passing string directly
        dfs = pd.read_html(io.StringIO(html_content))
        return dfs
    except ValueError:
        # No tables found
        return []
    except Exception as e:
        raise Exception(f"Error parsing tables: {str(e)}")

def extract_metadata(html_content):
    """
    Extract basic metadata (title, description) from HTML.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    title = soup.title.string if soup.title else "No Title"
    
    description = ""
    meta_desc = soup.find('meta', attrs={'name': 'description'}) or \
                soup.find('meta', attrs={'property': 'og:description'})
    if meta_desc:
        description = meta_desc.get('content', '')
        
    return {
        "title": title.strip(),
        "description": description.strip()
    }
