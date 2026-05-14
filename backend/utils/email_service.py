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
    Logs errors explicitly for debugging.
    """
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = os.getenv('SMTP_PORT')
    smtp_user = os.getenv('SMTP_USERNAME')
    smtp_pass = os.getenv('SMTP_PASSWORD')

    # Basic configuration check
    if not all([smtp_server, smtp_port, smtp_user, smtp_pass]):
        logger.error(f"SMTP Configuration Missing. Server: {bool(smtp_server)}, User: {bool(smtp_user)}")
        return False

    try:
        smtp_port = int(smtp_port)
        msg = MIMEMultipart()
        msg['From'] = f"Cyber Portal PK <{smtp_user}>"
        msg['To'] = recipient_email
        msg['Subject'] = f"CASE UPDATE: {tracking_id} [{status.upper()}]"

        # Content styling
        color = "#3b82f6" if status.lower() == "approved" else "#10b981" if status.lower() == "solved" else "#ef4444"
        
        html = f"""
        <div style="font-family: sans-serif; max-width: 600px; border: 1px solid #e2e8f0; border-radius: 10px; overflow: hidden;">
            <div style="background: #1e3a8a; color: white; padding: 20px; text-align: center;">
                <h2>Cyber Crime Reporting System</h2>
            </div>
            <div style="padding: 30px;">
                <p>Hello,</p>
                <p>Your case <b>{tracking_id}</b> has been updated.</p>
                <div style="background: #f8fafc; padding: 15px; border-left: 5px solid {color}; margin: 20px 0;">
                    <p style="margin: 0;"><b>New Status:</b> <span style="color: {color};">{status.upper()}</span></p>
                </div>
                <p><b>Officer Remarks:</b></p>
                <p style="color: #475569; font-style: italic;">"{notes}"</p>
                <p style="margin-top: 30px;">Visit the portal and use your tracking ID for more details.</p>
            </div>
            <div style="background: #f1f5f9; padding: 15px; text-align: center; font-size: 12px; color: #64748b;">
                This is an automated notification from the NCIA Cyber Portal.
            </div>
        </div>
        """
        
        msg.attach(MIMEText(html, 'html'))

        # Secure connection
        with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        
        logger.info(f"Email sent successfully to {recipient_email}")
        return True

    except Exception as e:
        logger.error(f"SMTP ERROR for {recipient_email}: {str(e)}")
        # If it's a connection error, it might be due to a blocked port or wrong server
        return False
