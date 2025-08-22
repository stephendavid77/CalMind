import os
import shutil
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO, # Reverted to INFO
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
# Get the root logger and set its level to INFO as well
logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger(__name__)

from calmind.config import Config, UserConfig
from calmind.calendars.google_calendar import GoogleCalendar
from calmind.calendars.apple_calendar import AppleCalendar
from calmind.llm.client import LLMClient
from calmind.llm.summarizer import LLMSummarizer
from calmind.reporting.generator import ReportGenerator
from calmind.emailing.sender import EmailSender

class CalMindApp:
    def __init__(self, config_path='config.yaml'):
        logger.info(f"Initializing application with config path: {config_path}")
        self.config = Config(config_path)
        self.llm_client = None
        self.llm_summarizer = None
        self.report_generator = ReportGenerator()
        self.email_sender = None
        logger.info("Application components initialized.")

    def _initialize_llm(self):
        logger.info("Initializing LLM components...")
        llm_config = self.config.get_llm_config()
        if not llm_config or not llm_config.api_key or llm_config.api_key == "YOUR_GEMINI_API_KEY":
            logger.warning("LLM API key not configured or is default. LLM summarization will not work.")
            return False
        try:
            self.llm_client = LLMClient(llm_config.api_key)
            self.llm_summarizer = LLMSummarizer(self.llm_client, context_file='calmind/llm/email_summary_context.md')
            logger.info("LLM components initialized successfully.")
            return True
        except Exception as e:
            logger.error(f"Error initializing LLM: {e}")
            return False

    def _initialize_email_sender(self):
        logger.info("Initializing email sender...")
        email_config = self.config.get_email_sender_config()
        
        if not email_config or not all([email_config.email, email_config.password, email_config.smtp_server, email_config.smtp_port]):
            logger.warning("Email sender configuration incomplete. Email reports will not be sent.")
            return False
        try:
            self.email_sender = EmailSender(config=email_config)
            logger.info("Email sender initialized successfully.")
            return True
        except Exception as e:
            logger.error(f"Error initializing email sender: {e}")
            return False

    def run_for_user(self, user_config: UserConfig):
        user_name = user_config.name
        report_to_email = user_config.report_to_email
        days_to_fetch = user_config.days_to_fetch

        logger.info(f"--- Processing for user: {user_name} ---")
        logger.info(f"Report will be sent to: {report_to_email}")
        logger.info(f"Fetching events for {days_to_fetch} days.")

        all_events = []
        start_date = datetime.now()
        end_date = start_date + timedelta(days=days_to_fetch)
        logger.info(f"Event fetch period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}.")

        calendars_to_process = user_config.calendars
        if not calendars_to_process:
            logger.warning(f"No calendars configured for user {user_name}. Skipping event fetch.")
            return

        for cal_union_config in calendars_to_process:
            cal_config = cal_union_config.root 
            cal_type = cal_config.type.lower()
            cal_name = cal_config.name
            logger.info(f"Attempting to access {cal_type} calendar: {cal_name}")

            calendar_instance = None
            if cal_type == 'google':
                logger.info(f"Initializing GoogleCalendar for {cal_name}...")
                calendar_instance = GoogleCalendar(cal_name, cal_config)
            elif cal_type == 'apple':
                username = cal_config.username
                password = cal_config.password
                url = cal_config.url
                logger.info(f"Initializing AppleCalendar for {cal_name} with username: {username}...")
                if not username or not password:
                    logger.error(f"Apple Calendar credentials (username/password) not found for {cal_name}. Skipping.")
                    continue
                calendar_instance = AppleCalendar(name=cal_name, config=cal_config)
            else:
                logger.warning(f"Unsupported calendar type: {cal_type}. Skipping calendar {cal_name}.")
                continue

            if calendar_instance:
                logger.info(f"Authenticating with {cal_name}...")
                if calendar_instance.authenticate():
                    logger.info(f"Authenticated with {cal_name}. Fetching events...")
                    events = calendar_instance.get_events(start_date, end_date)
                    all_events.extend(events)
                    logger.info(f"Fetched {len(events)} events from {cal_name}.")
                else:
                    logger.error(f"Authentication failed for {cal_name}. Skipping event fetch.")
            else:
                logger.error(f"Calendar instance not created for {cal_name}.")

        if not all_events:
            logger.info(f"No events found for {user_name} in the specified period. Skipping summarization and reporting.")
            return

        logger.info(f"Total events fetched for {user_name}: {len(all_events)}.")

        # Summarize events
        summary_content = "No summary generated due to LLM issues."
        if self.llm_summarizer:
            logger.info("Summarizing events with LLM...")
            summary_content = self.llm_summarizer.summarize_events(all_events, user_name)
            logger.info("Summary generated by LLM.")
        else:
            logger.warning("LLM summarizer not initialized. Skipping summarization and falling back to raw events.")
            # Fallback: just list events if LLM is not available
            summary_content = "## Raw Events (LLM not available)\n\n"
            for event in all_events:
                summary_content += f"- {event.summary} ({event.start} - {event.end})\n"

        # Generate reports
        logger.info("Generating reports...")
        html_report_path = self.report_generator.generate_html_report(user_name, summary_content)
        md_report_path = self.report_generator.generate_md_report(user_name, summary_content)
        logger.info(f"Reports generated: HTML at {html_report_path}, Markdown at {md_report_path}.")

        # Send email
        if report_to_email and self.email_sender:
            logger.info(f"Sending email report to {report_to_email}...")
            try:
                with open(html_report_path, 'r', encoding='utf-8') as f:
                    html_report_content = f.read()
                subject = f"CalMind: Your Calendar Summary for {user_name}"
                self.email_sender.send_email(report_to_email, subject, html_report_content)
                logger.info(f"Email report sent to {report_to_email}.")
            except Exception as e:
                logger.error(f"Failed to send email report to {report_to_email}: {e}")
        else:
            logger.info("Email not sent (recipient not specified or email sender not initialized).")

    def run(self):
        logger.info("Starting CalMind application...")
        reports_dir = "reports"
        if os.path.exists(reports_dir):
            logger.info(f"Clearing existing reports in {reports_dir}...")
            shutil.rmtree(reports_dir)
        os.makedirs(reports_dir, exist_ok=True)
        logger.info(f"Ensured {reports_dir} directory is clean.")
        
        # Initialize LLM and Email Sender based on new config structure
        if not self.config.get_llm_config() or not self._initialize_llm():
            logger.warning("LLM will not be available for summarization.")
        if not self.config.get_email_sender_config() or not self._initialize_email_sender():
            logger.warning("Email sending will not be available.")

        users_config = self.config.get_users_config()
        if not users_config:
            logger.error("No users configured in config.yaml. Exiting.")
            return

        logger.info(f"Found {len(users_config)} user(s) in configuration.")
        for user_config in users_config:
            self.run_for_user(user_config)

        logger.info("Application finished.")

if __name__ == '__main__':
    logger.info("Application started from main entry point.")
    app = CalMindApp()
    app.run()
    logger.info("Application execution finished.")