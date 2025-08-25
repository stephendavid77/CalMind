
from calmind.llm.client import LLMClient
from calmind.trello.trello_client import TrelloCard

class TrelloSummarizer:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def summarize_cards(self, cards: list[TrelloCard]) -> str:
        """Summarizes a list of Trello cards using the LLM."""
        if not cards:
            return "No Trello cards to summarize."

        # Create a single string with all card details
        cards_text = "\n".join([str(card) for card in cards])

        # Load the summarization context/prompt
        # (Assuming a trello_summary_context.md file exists)
        with open("calmind/llm/trello_summary_context.md", "r") as f:
            prompt = f.read()

        # Combine the prompt and the card data
        full_prompt = f"{prompt}\n\nHere are the Trello cards:\n\n{cards_text}"

        # Get the summary from the LLM
        summary = self.llm_client.generate_text(full_prompt)
        return summary
