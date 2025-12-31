from typing import Optional
import datetime
from easyfinder.config import SENDGRID_API_KEY, FROM_EMAIL, MOCK_EMAIL_MODE
from easyfinder.logging import log_event

def send_email(to_email: str, subject: str, html_body: str) -> bool:
    """Send email using SendGrid API or mock mode.
    
    Args:
        to_email: Recipient email address
        subject: Email subject line
        html_body: HTML content of email
        
    Returns:
        bool: True if email sent successfully
    """
    if MOCK_EMAIL_MODE:
        # Mock mode - simulate email sending
        print(f"\n[MOCK EMAIL] Sending email to: {to_email}")
        print(f"Subject: {subject}")
        print(f"From: {FROM_EMAIL}")
        print(f"Body preview: {html_body[:100]}...")
        
        log_event("EMAIL_SENT", {
            "to": to_email,
            "subject": subject,
            "status": "mock_success",
            "timestamp": datetime.datetime.utcnow().isoformat()
        })
        return True
    else:
        # Real SendGrid integration
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail
            
            message = Mail(
                from_email=FROM_EMAIL,
                to_emails=to_email,
                subject=subject,
                html_content=html_body
            )
            sg = SendGridAPIClient(SENDGRID_API_KEY)
            response = sg.send(message)
            
            log_event("EMAIL_SENT", {
                "to": to_email,
                "subject": subject,
                "status": "success",
                "status_code": response.status_code
            })
            return True
        except Exception as e:
            log_event("EMAIL_FAILED", {
                "to": to_email,
                "subject": subject,
                "error": str(e)
            })
            print(f"Error sending email: {e}")
            return False

def send_nda_email(to_email: str, lead_name: str, company: str) -> bool:
    """Send NDA and demo invitation email."""
    subject = "Private Demo & NDA – EasyFinder AI"
    
    # Read template
    try:
        with open("/app/backend/templates/nda_email.html", "r", encoding="utf-8") as f:
            html = f.read()
            # Replace placeholders
            html = html.replace("{{name}}", lead_name)
            html = html.replace("{{company}}", company)
    except FileNotFoundError:
        # Fallback template
        html = f"""
        <html>
            <body>
                <h2>Hello {lead_name},</h2>
                <p>Thank you for your interest in EasyFinder AI.</p>
                <p>We'd like to invite you to a private demo of our enterprise-grade AI system.</p>
                <p>Best regards,<br>The EasyFinder AI Team</p>
            </body>
        </html>
        """
    
    return send_email(to_email, subject, html)
