import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class EmailSender:
    def __init__(self, sender_email: str, sender_password: str, smtp_server: str, smtp_port: int):
        print(f"EmailSender: Initializing with sender_email={sender_email}, smtp_server={smtp_server}, smtp_port={smtp_port}")
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port

    def send_email(self, recipient_email: str, subject: str, html_content: str):
        print(f"EmailSender: Attempting to send email to {recipient_email} with subject: {subject}")
        if not all([self.sender_email, self.sender_password, self.smtp_server, self.smtp_port]):
            print("EmailSender Error: Email sender configuration is incomplete. Cannot send email.")
            return False

        msg = MIMEMultipart('alternative')
        msg['From'] = self.sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject

        # Attach HTML content
        msg.attach(MIMEText(html_content, 'html'))

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                print("EmailSender: Starting TLS...")
                server.starttls()  # Secure the connection
                print("EmailSender: Logging in to SMTP server...")
                server.login(self.sender_email, self.sender_password)
                print("EmailSender: Sending message...")
                server.send_message(msg)
            print(f"EmailSender: Email sent successfully to {recipient_email}")
            return True
        except Exception as e:
            print(f"EmailSender Error: Failed to send email to {recipient_email}: {e}")
            return False

if __name__ == '__main__':
    """
    This block is for example usage and testing purposes only.
    It is commented out to prevent accidental execution and IndentationErrors.
    To run the application, use `python -m calmind.main`.
    """
    # Example usage (uncomment and modify if you want to test this specific file directly):
    # from calmind.config import Config
    # config = Config()
    # email_config = config.get_email_sender_config()

    # if all([email_config['email'], email_config['password'], email_config['smtp_server'], email_config['smtp_port']]):
    #     sender = EmailSender(
    #         sender_email=email_config['email'],
    #         sender_password=email_config['password'],
    #         smtp_server=email_config['smtp_server'],
    #         smtp_port=email_config['smtp_port']
    #     )

    #     test_recipient = "test@example.com" # Replace with a real recipient email for testing
    #     test_subject = "CalMind Test Report"
    #     test_html_content = "<h1>Hello from CalMind!</h1><p>This is a test email with <b>HTML</b> content.</p>"

    #     print(f"Attempting to send test email to {test_recipient}...")
    #     sender.send_email(test_recipient, test_subject, test_html_content)
    # else:
    #     print("Email sender configuration incomplete. Cannot run email sender example.")
