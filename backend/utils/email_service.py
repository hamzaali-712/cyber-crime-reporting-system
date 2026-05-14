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
    Sends a professional case update email to the user.
    """
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    smtp_user = os.getenv('SMTP_USERNAME')
    smtp_pass = os.getenv('SMTP_PASSWORD')

    if not all([smtp_server, smtp_user, smtp_pass]):
        logger.warning("SMTP settings not fully configured. Email not sent.")
        return False

    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = f"Cyber Crime Reporting System <{smtp_user}>"
        msg['To'] = recipient_email
        msg['Subject'] = f"Case Update: {tracking_id} - {status.upper()}"

        # Status color and icon
        status_colors = {
            "approved": "#10b981",
            "solved": "#3b82f6",
            "rejected": "#ef4444"
        }
        color = status_colors.get(status.lower(), "#64748b")

        # HTML Body
        html = f"""
        <html>
        <body style="font-family: 'Inter', sans-serif; background-color: #f8fafc; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); border: 1px solid #e2e8f0;">
                <div style="background: linear-gradient(135deg, #1e3a8a, #3b82f6); color: white; padding: 30px; text-align: center;">
                    <h1 style="margin: 0; font-size: 24px;">Cyber Crime Reporting System</h1>
                    <p style="margin: 10px 0 0; opacity: 0.9;">Official Case Status Update</p>
                </div>
                <div style="padding: 40px; color: #1e293b;">
                    <h2 style="margin-top: 0; color: #0f172a;">Case Update Notification</h2>
                    <p>Dear Citizen,</p>
                    <p>We are writing to inform you of an update regarding your complaint submitted to the Cyber Crime Reporting System.</p>
                    
                    <div style="background-color: #f1f5f9; padding: 20px; border-radius: 8px; margin: 25px 0;">
                        <p style="margin: 0;"><strong>Tracking ID:</strong> <span style="font-family: monospace;">{tracking_id}</span></p>
                        <p style="margin: 10px 0 0;"><strong>Current Status:</strong> <span style="color: {color}; font-weight: bold; text-transform: uppercase;">{status}</span></p>
                    </div>

                    <h3 style="color: #0f172a; border-bottom: 2px solid #f1f5f9; padding-bottom: 10px;">Officer Remarks:</h3>
                    <p style="font-style: italic; color: #475569;">"{notes}"</p>

                    <p style="margin-top: 30px;">You can track further progress by visiting our portal and entering your Tracking ID.</p>
                    
                    <div style="text-align: center; margin-top: 40px;">
                        <a href="https://cyber-crime-reporting-system.streamlit.app" style="background-color: #1e40af; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: 600;">Visit Portal</a>
                    </div>
                </div>
                <div style="background-color: #f8fafc; color: #64748b; padding: 20px; text-align: center; font-size: 12px; border-top: 1px solid #e2e8f0;">
                    <p style="margin: 0;">&copy; 2026 Cyber Crime Reporting System - Pakistan. All rights reserved.</p>
                    <p style="margin: 5px 0 0;">This is an automated notification. Please do not reply directly to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """

        msg.attach(MIMEText(html, 'html'))

        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)

        logger.info(f"Update email sent to {recipient_email} for case {tracking_id}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
        return False
