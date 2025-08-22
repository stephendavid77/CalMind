import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from calmind.config import EmailConfig

logger = logging.getLogger(__name__)

class EmailSender:
    def __init__(self, config: EmailConfig):
        logger.info(f"Initializing with sender_email={config.email}, password_provided={'Yes' if config.password else 'No'}, smtp_server={config.smtp_server}, smtp_port={config.smtp_port}")
        self.sender_email = config.email
        self.sender_password = config.password
        self.smtp_server = config.smtp_server
        self.smtp_port = config.smtp_port

    def send_email(self, recipient_email: str, subject: str, html_content: str):
        logger.info(f"Attempting to send email to {recipient_email} with subject: {subject}")
        if not all([self.sender_email, self.sender_password, self.smtp_server, self.smtp_port]):
            logger.error("Email sender configuration is incomplete. Cannot send email.")
            return False

        msg = MIMEMultipart('alternative')
        msg['From'] = self.sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject

        # Attach HTML content
        msg.attach(MIMEText(html_content, 'html'))

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                logger.info("Starting TLS...")
                server.starttls()  # Secure the connection
                logger.info("Logging in to SMTP server...")
                server.login(self.sender_email, self.sender_password)
                logger.info("Sending message...")
                server.send_message(msg)
            logger.info(f"Email sent successfully to {recipient_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {recipient_email}: {e}")
            return False

if __name__ == '__main__':
    """
    This block is for example usage and testing purposes only.
    It is commented out to prevent accidental execution and IndentationErrors.
    To run the application, use `python -m calmind.main`.
    """
    # Example usage (uncomment and modify if you want to test this specific file directly):
    # from calmind.config import Config
    # config_obj = Config()
    # email_config = config_obj.get_email_sender_config()

    # if email_config:
    #     sender = EmailSender(
    #         config=email_config
    #     )

    #     test_recipient = "test@example.com" # Replace with a real recipient email for testing
    #     test_subject = "CalMind Test Report"
    #     test_html_content = "<h1>Hello from CalMind!</h1><p>This is a test email with <b>HTML</b> content.</p>"

    #     logger.info(f"Attempting to send test email to {test_recipient}...")
    #     sender.send_email(test_recipient, test_subject, test_html_content)
    # else:
    #     logger.warning("Email sender configuration incomplete. Cannot run email sender example.")
