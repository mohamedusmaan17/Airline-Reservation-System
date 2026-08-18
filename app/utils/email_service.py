import os
import smtplib
from email.message import EmailMessage

# Note: For this to work in production, you must set these environment variables
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "465"))
SMTP_USERNAME = os.environ.get("SMTP_USERNAME", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")

def send_ticket_email(to_email: str, passenger_name: str, pnr: str, pdf_data: bytes):
    """
    Sends an email with the attached PDF ticket to the passenger.
    """
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        print(f"\n[Mock Email Service] Would have sent ticket to {to_email}")
        print(f"Subject: ✈️ Your SkyBooker E-Ticket - PNR: {pnr}")
        print("Body: Dear passenger, your ticket is attached.")
        print("To actually send emails, please configure SMTP_USERNAME and SMTP_PASSWORD environment variables.\n")
        return

    try:
        msg = EmailMessage()
        msg['Subject'] = f"✈️ Your SkyBooker E-Ticket - PNR: {pnr}"
        msg['From'] = f"SkyBooker <{SMTP_USERNAME}>"
        msg['To'] = to_email

        body = f"""
        Dear {passenger_name},

        Thank you for booking with SkyBooker!
        Your flight is confirmed. PNR: {pnr}

        Please find your official E-Ticket and Boarding Pass attached to this email.

        Have a safe flight!
        - The SkyBooker Team
        """
        msg.set_content(body)

        # Attach the PDF
        msg.add_attachment(
            pdf_data, 
            maintype='application', 
            subtype='pdf', 
            filename=f"SkyBooker_Ticket_{pnr}.pdf"
        )

        # Send the email via SMTP SSL
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
            
        print(f"Successfully sent ticket email to {to_email}")

    except Exception as e:
        print(f"Failed to send email to {to_email}. Error: {e}")
