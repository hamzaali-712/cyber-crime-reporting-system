import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

def send_case_update_email(recipient_email, tracking_id, status, notes):
    """
    Sends a professional case update email.
    Returns: (bool, str) - (Success Status, Error Message or Success Message)
    """
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = os.getenv('SMTP_PORT')
    smtp_user = os.getenv('SMTP_USERNAME')
    smtp_pass = os.getenv('SMTP_PASSWORD')

    # Basic configuration check
    if not all([smtp_server, smtp_port, smtp_user, smtp_pass]):
        err = "SMTP configuration missing in environment/secrets."
        logger.error(err)
        return False, err

    try:
        smtp_port = int(smtp_port)
        msg = MIMEMultipart()
        msg['From'] = f"NCIA Cyber Portal <{smtp_user}>"
        msg['To'] = recipient_email
        msg['Subject'] = f"OFFICIAL CASE UPDATE: {tracking_id}"

        # Content styling
        color = "#3b82f6" if status.lower() == "approved" else "#10b981" if status.lower() == "solved" else "#ef4444"
        
        # We assume 'notes' now contains the full AI-generated detailed content
        html = f"""
        <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 650px; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; background-color: #ffffff; color: #1a202c;">
            <div style="background: #1e3a8a; color: white; padding: 25px; text-align: center;">
                <h1 style="margin: 0; font-size: 24px; letter-spacing: 1px;">NCIA CYBERCRIME WING</h1>
                <p style="margin: 5px 0 0 0; opacity: 0.9; font-size: 14px;">Government of Pakistan</p>
            </div>
            <div style="padding: 40px;">
                <p style="font-size: 16px; line-height: 1.6;">Hello,</p>
                <p style="font-size: 16px; line-height: 1.6;">Your reported case <b style="color: #1e3a8a;">{tracking_id}</b> has been processed by our analysis department.</p>
                
                <div style="background: #f7fafc; padding: 20px; border-left: 6px solid {color}; margin: 25px 0; border-radius: 4px;">
                    <p style="margin: 0; font-weight: bold; font-size: 18px;">Case Status: <span style="color: {color};">{status.upper()}</span></p>
                </div>
                
                <div style="white-space: pre-line; font-size: 15px; line-height: 1.8; color: #2d3748;">
                    {notes}
                </div>
                
                <div style="margin-top: 40px; border-top: 1px solid #edf2f7; padding-top: 20px;">
                    <p style="font-size: 14px; color: #718096;">For further tracking, please visit the official portal using your Tracking ID.</p>
                </div>
            </div>
            <div style="background: #edf2f7; padding: 20px; text-align: center; font-size: 11px; color: #a0aec0; letter-spacing: 0.5px;">
                This is a secure, automated notification. Do not reply to this email.
                <br>&copy; {2026} National Cybercrime Investigation Agency.
            </div>
        </div>
        """
        
        msg.attach(MIMEText(html, 'html'))

        # Secure connection
        with smtplib.SMTP(smtp_server, smtp_port, timeout=15) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        
        return True, "Dispatch successful."

    except Exception as e:
        err_msg = str(e)
        logger.error(f"SMTP Error: {err_msg}")
        return False, err_msg
