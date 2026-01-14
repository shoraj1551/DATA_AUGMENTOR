"""
Data models for Company Intelligence
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class VerificationStatus(BaseModel):
    """Company verification status from official registries"""
    is_verified: bool = Field(False, description="Whether the company was found in official registries")
    status: str = Field("Unknown", description="Current status (Active, Dissolved, etc.)")
    source: str = Field(..., description="Source of verification (e.g., OpenCorporates, MCA)")
    registration_number: Optional[str] = Field(None, description="CIN, CRN, or other registration ID")
    incorporation_date: Optional[str] = Field(None, description="Date of incorporation")
    registered_address: Optional[str] = Field(None, description="Registered office address")
    jurisdiction: Optional[str] = Field(None, description="Country/State of registration")
    confidence_score: float = Field(0.0, description="Confidence in the match (0-1.0)")

class FinancialInfo(BaseModel):
    """Financial information (optional/estimated)"""
    revenue_range: Optional[str] = None
    funding_total: Optional[str] = None
    currency: str = "USD"
    last_funding_date: Optional[str] = None
    investors: List[str] = Field(default_factory=list)

class DigitalPresence(BaseModel):
    """Online footprint"""
    website: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_url: Optional[str] = None
    facebook_url: Optional[str] = None
    description: Optional[str] = Field(None, description="Extracted description from website")
    tech_stack: List[str] = Field(default_factory=list, description="Detected technologies")

class RiskAssessment(BaseModel):
    """Risk indicators"""
    risk_level: str = Field("Unknown", description="Low, Medium, High, Critical")
    alerts: List[str] = Field(default_factory=list, description="List of risk factors found")
    score: int = Field(100, description="Risk score (0-100, where 100 is likely safe, 0 is critical risk)")

class CompanyProfile(BaseModel):
    """Comprehensive Company Intelligence Profile"""
    name: str
    domain: Optional[str] = None
    industry: Optional[str] = None
    employees_range: Optional[str] = None
    
    # Components
    verification: VerificationStatus = Field(default_factory=lambda: VerificationStatus(source="System"))
    financials: FinancialInfo = Field(default_factory=FinancialInfo)
    digital_presence: DigitalPresence = Field(default_factory=DigitalPresence)
    risk_assessment: RiskAssessment = Field(default_factory=RiskAssessment)
    
    # Metadata
    last_updated: datetime = Field(default_factory=datetime.now)
    query_country: Optional[str] = None
