import csv
from typing import List, Dict

def load_leads(csv_path: str) -> List[Dict]:
    """Load leads from CSV file."""
    leads = []
    try:
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                leads.append(row)
    except FileNotFoundError:
        print(f"Error: CSV file not found at {csv_path}")
        return []
    return leads

def parse_lead_data(leads: List[Dict]) -> List[Dict]:
    """Parse and validate lead data."""
    parsed_leads = []
    for lead in leads:
        # Ensure required fields exist
        parsed_lead = {
            'name': lead.get('name', ''),
            'email': lead.get('email', ''),
            'company': lead.get('company', ''),
            'company_size': lead.get('company_size', ''),
            'industry': lead.get('industry', ''),
            'budget': lead.get('budget', '0'),
            'phone': lead.get('phone', ''),
            'website': lead.get('website', '')
        }
        parsed_leads.append(parsed_lead)
    return parsed_leads
