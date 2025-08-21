from typing import List
from calmind.calendars.base import CalendarEvent
from calmind.llm.client import LLMClient

class LLMSummarizer:
    def __init__(self, llm_client: LLMClient):
        print("LLMSummarizer: Initializing LLM summarizer.")
        self.llm_client = llm_client

    def summarize_events(self, events: List[CalendarEvent], user_name: str) -> str:
        print(f"LLMSummarizer: Starting event summarization for {user_name} with {len(events)} events.")
        if not events:
            print("LLMSummarizer: No events provided for summarization.")
            return "No events to summarize."

        prompt_parts = [
            f"Hello {user_name}, please summarize the following calendar events. "
            "Provide a concise overview, highlight key meetings or tasks, "
            "and suggest any useful information or potential conflicts that might be relevant to the user. "
            "Also, add any useful info that might be relevant and useful to the enduser."
            "\n\nCalendar Events:"
        ]

        for event in events:
            prompt_parts.append(str(event)) # Using the __str__ method of CalendarEvent

        prompt = "\n".join(prompt_parts)
        print("LLMSummarizer: Sending prompt to LLM for summarization...")
        summary = self.llm_client.generate_content(prompt)
        print("LLMSummarizer: Summarization complete.")
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
    #     print("\nGenerated Summary:")
    #     print(summary_text)
    # else:
    #     print("LLM API key not configured or is default. Cannot run summarizer example.")
