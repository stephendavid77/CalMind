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
from calmind.trello.trello_client import TrelloService
from calmind.llm.client import LLMClient
from calmind.llm.summarizer import LLMSummarizer
from calmind.trello.trello_summarizer import TrelloSummarizer
from calmind.reporting.generator import ReportGenerator
from calmind.emailing.sender import EmailSender

class CalMindApp:
    def __init__(self, config_path='config.yaml'):
        logger.info(f"Initializing application with config path: {config_path}")
        self.config = Config(config_path)
        self.llm_client = None
        self.llm_summarizer = None
        self.trello_summarizer = None
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
            self.trello_summarizer = TrelloSummarizer(self.llm_client)
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

    def run_for_user(self, user_config: UserConfig, source_name: str = None):
        user_name = user_config.name
        report_to_email = user_config.report_to_email
        days_to_fetch = user_config.days_to_fetch

        logger.info(f"--- Processing for user: {user_name} ---")
        if source_name:
            logger.info(f"Processing for source: {source_name}")

        all_events = []
        all_cards = []
        start_date = datetime.now()
        end_date = start_date + timedelta(days=days_to_fetch)

        sources_to_process = user_config.sources
        if source_name:
            sources_to_process = [s for s in sources_to_process if s.root.name == source_name]

        if not sources_to_process:
            logger.warning(f"No sources found for user {user_name} with name {source_name}. Skipping.")
            return "No sources found."

        for source_union_config in sources_to_process:
            source_config = source_union_config.root 
            source_type = source_config.type.lower()
            current_source_name = source_config.name
            logger.info(f"Attempting to access {source_type} source: {current_source_name}")

            if source_type == 'google':
                calendar_instance = GoogleCalendar(current_source_name, source_config)
                if calendar_instance.authenticate():
                    events = calendar_instance.get_events(start_date, end_date)
                    all_events.extend(events)
            elif source_type == 'apple':
                calendar_instance = AppleCalendar(name=current_source_name, config=source_config)
                if calendar_instance.authenticate():
                    events = calendar_instance.get_events(start_date, end_date)
                    all_events.extend(events)
            elif source_type == 'trello':
                trello_service = TrelloService(api_key=source_config.api_key, api_token=source_config.api_token, board_id=source_config.board_id)
                cards = trello_service.get_cards()
                all_cards.extend(cards)
            else:
                logger.warning(f"Unsupported source type: {source_type}. Skipping source {current_source_name}.")
                continue

        summary_content = ""
        if all_events:
            if self.llm_summarizer:
                summary_content += self.llm_summarizer.summarize_events(all_events, user_name)
        
        if all_cards:
            if self.trello_summarizer:
                summary_content += self.trello_summarizer.summarize_cards(all_cards)

        if not summary_content:
            return "No events or cards found to summarize."

        html_report_path = self.report_generator.generate_html_report(user_name, summary_content)
        self.report_generator.generate_md_report(user_name, summary_content)

        with open(html_report_path, 'r', encoding='utf-8') as f:
            html_report_content = f.read()

        if report_to_email and self.email_sender:
            subject = f"CalMind: Your Summary for {user_name}"
            self.email_sender.send_email(report_to_email, subject, html_report_content)

        return html_report_content

    def run(self):
        logger.info("Starting CalMind application...")
        reports_dir = "reports"
        if os.path.exists(reports_dir):
            shutil.rmtree(reports_dir)
        os.makedirs(reports_dir, exist_ok=True)
        
        if not self.config.get_llm_config() or not self._initialize_llm():
            logger.warning("LLM will not be available for summarization.")
        if not self.config.get_email_sender_config() or not self._initialize_email_sender():
            logger.warning("Email sending will not be available.")

        users_config = self.config.get_users_config()
        if not users_config:
            logger.error("No users configured in config.yaml. Exiting.")
            return

        for user_config in users_config:
            self.run_for_user(user_config)

        logger.info("Application finished.")

if __name__ == '__main__':
    logger.info("Application started from main entry point.")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, '..', 'config.yaml')
    app = CalMindApp(config_path=config_path)
    app.run()
    logger.info("Application execution finished.")