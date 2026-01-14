"""
Website Scraper Service
Extracts basic intelligence from company websites
"""
import requests
from bs4 import BeautifulSoup
import re
from typing import Optional, Dict, List
import logging
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)

class WebsiteScraper:
    """Service to scrape and analyze company websites"""
    
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    def scrape_basic_info(self, url: str) -> Dict:
        """
        Scrape basic info from a website
        Returns:
            Dict containing description, social_links, contact_info
        """
        if not url:
            return {}
            
        if not url.startswith('http'):
            url = 'https://' + url
            
        try:
            response = requests.get(url, headers=self.HEADERS, timeout=10)
            if response.status_code != 200:
                logger.warning(f"Failed to fetch {url}: {response.status_code}")
                return {}
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 1. Extract Description
            description = self._extract_description(soup)
            
            # 2. Extract Social Links
            social_links = self._extract_social_links(soup, url)
            
            # 3. Extract Tech Stack (Basic inference from meta tags/scripts)
            tech_stack = self._detect_technologies(soup)
            
            return {
                'description': description,
                'social_links': social_links,
                'tech_stack': tech_stack,
                'title': soup.title.string if soup.title else ""
            }
            
        except Exception as e:
            logger.error(f"Scraping failed for {url}: {str(e)}")
            return {}
    
    def _extract_description(self, soup) -> str:
        """Extract description from meta tags or content"""
        # Try meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'}) or \
                   soup.find('meta', attrs={'property': 'og:description'})
                   
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content']
            
        return ""
        
    def _extract_social_links(self, soup, base_url) -> Dict:
        """Find social media links"""
        links = {
            'linkedin': None,
            'twitter': None,
            'facebook': None,
            'instagram': None
        }
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            # Resolve relative URLs
            full_url = urljoin(base_url, href).lower()
            
            if 'linkedin.com/company' in full_url:
                links['linkedin'] = full_url
            elif 'twitter.com' in full_url or 'x.com' in full_url:
                links['twitter'] = full_url
            elif 'facebook.com' in full_url:
                links['facebook'] = full_url
                
        return links
        
    def _detect_technologies(self, soup) -> List[str]:
        """Detect basic technologies from HTML"""
        technologies = []
        html_str = str(soup).lower()
        
        checks = {
            'WordPress': 'wp-content',
            'React': 'react',
            'Next.js': '__next',
            'Shopify': 'shopify',
            'Google Analytics': 'google-analytics',
            'HubSpot': 'hs-script-loader',
            'Tailwind CSS': 'tailwind',
            'Bootstrap': 'bootstrap'
        }
        
        for tech, key in checks.items():
            if key in html_str:
                technologies.append(tech)
                
        return technologies
