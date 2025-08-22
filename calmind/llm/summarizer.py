from typing import List
import logging
import os
from calmind.calendars.base import CalendarEvent
from calmind.llm.client import LLMClient

logger = logging.getLogger(__name__)

class LLMSummarizer:
    def __init__(self, llm_client: LLMClient, context_file: str = 'calmind/llm/email_summary_context.md'):
        logger.info("Initializing LLM summarizer.")
        self.llm_client = llm_client
        self.context_file = context_file
        self.context_content = self._load_context_file()

    def _load_context_file(self) -> str:
        if not os.path.exists(self.context_file):
            logger.warning(f"Context file not found at {self.context_file}. LLM will operate without additional context.")
            return ""
        try:
            with open(self.context_file, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.info(f"Context file {self.context_file} loaded successfully.")
            return content
        except Exception as e:
            logger.error(f"Error loading context file {self.context_file}: {e}")
            return ""

    def summarize_events(self, events: List[CalendarEvent], user_name: str) -> str:
        logger.info(f"Starting event summarization for {user_name} with {len(events)} events.")
        if not events:
            logger.info("No events provided for summarization.")
            return "No events to summarize."

        prompt_parts = []
        if self.context_content:
            prompt_parts.append(self.context_content)
            prompt_parts.append("\n---\n") # Separator for context and main prompt

        prompt_parts.append(
            f"Hello {user_name}, please summarize the following calendar events. "
            "Provide a concise overview, highlight key meetings or tasks, "
            "and suggest any useful information or potential conflicts that might be relevant to the user. "
            "Also, add any useful info that might be relevant and useful to the enduser."
            "\n\nCalendar Events:"
        )

        for event in events:
            prompt_parts.append(str(event)) # Using the __str__ method of CalendarEvent

        prompt = "\n".join(prompt_parts)
        logger.info("Sending prompt to LLM for summarization...")
        summary = self.llm_client.generate_content(prompt)
        logger.info("Summarization complete.")
        return summary


if __name__ == '__main__':
    """
    This block is for example usage and testing purposes only.
    It is commented out to prevent accidental execution and IndentationErrors.
    To run the application, use `python -m calmind.main`.
    """
    # Example usage (uncomment and modify if you want to test this specific file directly):
    # from calmind.config import Config
    # config = Config()
    # api_key = config.get_llm_api_key()

    # if api_key and api_key != "YOUR_GEMINI_API_KEY":
    #     llm_client = LLMClient(api_key)
    #     summarizer = LLMSummarizer(llm_client)

    #     from datetime import datetime, timedelta
    #     sample_events = [
    #         CalendarEvent(
    #             summary="Team Standup",
    #             start=datetime.now() + timedelta(hours=1),
    #             end=datetime.now() + timedelta(hours=1, minutes=30),
    #             location="Zoom",
    #             description="Daily team sync"
    #         ),
    #         CalendarEvent(
    #             summary="Project Deadline",
    #             start=datetime.now() + timedelta(days=5),
    #             end=datetime.now() + timedelta(days=5, hours=1),
    #             description="Final submission for Project X"
    #         )
    #     ]

    #     summary_text = summarizer.summarize_events(sample_events, "Test User")
    #     logger.info("\nGenerated Summary:")
    #     logger.info(summary_text)
    # else:
    #     logger.warning("LLM API key not configured or is default. Cannot run summarizer example.")

