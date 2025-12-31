from typing import Dict

def score_lead(lead: Dict) -> int:
    """Score a lead based on various criteria.
    
    Scoring logic:
    - Enterprise company size: +40 points
    - Budget > $50,000: +30 points
    - Target industries (construction, logistics, equipment): +20 points
    - Valid email: +10 points
    
    Max score: 100 points
    """
    score = 0
    
    # Company size scoring
    company_size = lead.get("company_size", "").lower()
    if company_size == "enterprise":
        score += 40
    elif company_size == "medium":
        score += 25
    elif company_size == "small":
        score += 10
    
    # Budget scoring
    budget_str = lead.get("budget", "0").replace("$", "").replace(",", "").strip()
    if budget_str.isdigit() and int(budget_str) > 50000:
        score += 30
    elif budget_str.isdigit() and int(budget_str) > 25000:
        score += 15
    
    # Industry scoring
    industry = lead.get("industry", "").lower()
    if industry in ["construction", "logistics", "equipment"]:
        score += 20
    elif industry in ["manufacturing", "transportation", "retail"]:
        score += 10
    
    # Email validation
    if lead.get("email") and "@" in lead.get("email", ""):
        score += 10
    
    return min(score, 100)  # Cap at 100

def get_lead_priority(score: int) -> str:
    """Get lead priority level based on score."""
    if score >= 70:
        return "HIGH"
    elif score >= 40:
        return "MEDIUM"
    else:
        return "LOW"
