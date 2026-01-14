"""
Company Registry Service
Integrates with OpenCorporates and other registries to verify company existence
"""
import requests
import urllib.parse
from typing import Optional, Dict, List
import logging
from ..models.company_profile import VerificationStatus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RegistryService:
    """Service to interact with company registries"""
    
    OPENCORPORATES_BASE_URL = "https://api.opencorporates.com/v0.4/companies/search"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
    
    def verify_company(self, name: str, country: str = "") -> VerificationStatus:
        """
        Verify if a company exists in official registries
        
        Args:
            name: Company name
            country: Jurisdiction/Country (e.g., 'us', 'gb', 'in')
            
        Returns:
            VerificationStatus object
        """
        # normalize country code if possible (simplified)
        country_code = self._normalize_country_code(country)
        
        try:
            # Construct query params
            params = {
                'q': name,
                'current_status': 'Active', # Prefer active companies
                'per_page': 5
            }
            
            if country_code:
                params['jurisdiction_code'] = country_code
                
            if self.api_key:
                params['api_token'] = self.api_key
                
            # Call OpenCorporates API
            # Note: Without API key, this might hit rate limits quickly.
            # We'll stick to a short timeout.
            response = requests.get(
                self.OPENCORPORATES_BASE_URL, 
                params=params, 
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', {}).get('companies', [])
                
                if results:
                    # Find best match
                    best_match = results[0]['company']
                    
                    return VerificationStatus(
                        is_verified=True,
                        status=best_match.get('current_status', 'Active'),
                        source="OpenCorporates",
                        registration_number=best_match.get('company_number'),
                        incorporation_date=best_match.get('incorporation_date'),
                        registered_address=best_match.get('registered_address_in_full'),
                        jurisdiction=best_match.get('jurisdiction_code'),
                        confidence_score=0.9 # High confidence if found in registry
                    )
            elif response.status_code == 403 or response.status_code == 429:
                logger.warning("OpenCorporates rate limit or auth error. Falling back to unverified.")
                
        except Exception as e:
            logger.error(f"Registry lookup failed: {str(e)}")
            
        # Fallback / Not Found
        return VerificationStatus(
            is_verified=False, 
            status="Not Found", 
            source="Registry Search"
        )

    def _normalize_country_code(self, country: str) -> str:
        """Helper to map common country names to 2-letter codes"""
        if not country:
            return ""
            
        country = country.lower().strip()
        mapping = {
            'united states': 'us',
            'usa': 'us',
            'us': 'us',
            'india': 'in',
            'uk': 'gb',
            'united kingdom': 'gb',
            'great britain': 'gb',
            'canada': 'ca',
            'australia': 'au',
            'germany': 'de',
            'france': 'fr'
        }
        return mapping.get(country, "")
