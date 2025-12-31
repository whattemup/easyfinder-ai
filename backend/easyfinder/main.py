#!/usr/bin/env python3
"""
EasyFinder AI - Lead Management and Outreach Automation

CLI tool for processing leads from CSV files.
"""

import sys
from pathlib import Path
from easyfinder.ingestion import load_leads, parse_lead_data
from easyfinder.scoring import score_lead, get_lead_priority
from easyfinder.outreach import send_nda_email
from easyfinder.logging import log_event

EMAIL_THRESHOLD = 70

def run(csv_path: str = "/app/backend/data/leads.csv"):
    """Main execution function.
    
    Args:
        csv_path: Path to CSV file containing leads
    """
    print(f"\n=== EasyFinder AI - Lead Processing ===")
    print(f"Loading leads from: {csv_path}\n")
    
    # Load and parse leads
    raw_leads = load_leads(csv_path)
    if not raw_leads:
        print("No leads found. Please check the CSV file.")
        return
    
    leads = parse_lead_data(raw_leads)
    print(f"Loaded {len(leads)} leads\n")
    
    # Process each lead
    high_priority_count = 0
    emails_sent = 0
    
    print("Processing leads...\n")
    print("-" * 80)
    
    for lead in leads:
        # Score the lead
        score = score_lead(lead)
        priority = get_lead_priority(score)
        
        # Log scoring event
        log_event("LEAD_SCORED", {
            "name": lead.get("name"),
            "email": lead.get("email"),
            "company": lead.get("company"),
            "score": score,
            "priority": priority
        })
        
        # Print lead info
        print(f"Lead: {lead.get('name')} ({lead.get('company')})")
        print(f"  Email: {lead.get('email')}")
        print(f"  Score: {score}/100 | Priority: {priority}")
        
        # Send email if score meets threshold
        if score >= EMAIL_THRESHOLD:
            high_priority_count += 1
            if lead.get('email'):
                success = send_nda_email(
                    to_email=lead['email'],
                    lead_name=lead.get('name', 'there'),
                    company=lead.get('company', 'your company')
                )
                if success:
                    emails_sent += 1
                    print(f"  ✓ NDA email sent")
                else:
                    print(f"  ✗ Failed to send email")
            else:
                print(f"  ⚠ No email address available")
        
        print("-" * 80)
    
    # Summary
    print(f"\n=== Processing Complete ===")
    print(f"Total leads processed: {len(leads)}")
    print(f"High-priority leads (score >= {EMAIL_THRESHOLD}): {high_priority_count}")
    print(f"Emails sent: {emails_sent}")
    print(f"\nLogs saved to: /app/backend/data/logs.json\n")

if __name__ == "__main__":
    csv_file = sys.argv[1] if len(sys.argv) > 1 else "/app/backend/data/leads.csv"
    run(csv_file)
