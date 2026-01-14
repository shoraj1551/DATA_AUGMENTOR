"""
Risk Assessment Engine
Calculates risk scores based on company profile data
"""
from typing import List
from ..models.company_profile import CompanyProfile, RiskAssessment

class RiskEngine:
    """Assess company risk"""
    
    def assess_risk(self, profile: CompanyProfile) -> RiskAssessment:
        """
        Calculate risk score and identify alerts
        
        Risk Score: 0 (Critical) to 100 (Safe)
        """
        score = 100
        alerts = []
        risk_level = "Low"
        
        # 1. Verification Check
        if not profile.verification.is_verified:
            score -= 40
            alerts.append("Unverified: Company not found in official registry")
        elif "dissolved" in profile.verification.status.lower() or "inactive" in profile.verification.status.lower():
            score -= 80
            alerts.append(f"Critical: Company status is '{profile.verification.status}'")
            
        # 2. Digital Presence Check
        if not profile.digital_presence.website:
            score -= 20
            alerts.append("No official website detected")
        
        if not profile.digital_presence.linkedin_url:
            score -= 10
            alerts.append("No LinkedIn presence found")
            
        # 3. Determine Risk Level
        if score >= 80:
            risk_level = "Low"
        elif score >= 50:
            risk_level = "Medium"
        elif score >= 30:
            risk_level = "High"
        else:
            risk_level = "Critical"
            
        return RiskAssessment(
            score=score,
            alerts=alerts,
            risk_level=risk_level
        )
