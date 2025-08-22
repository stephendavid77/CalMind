import google.generativeai as genai
import logging

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self, api_key: str):
        logger.info("Initializing LLM client.")
        if api_key:
            logger.info(f"API Key provided (first 5 chars: {api_key[:5]}...{api_key[-5:]}).")
        else:
            logger.error("Gemini API Key is required.")
            raise ValueError("Gemini API Key is required.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro-latest')
        logger.info("LLM client initialized successfully.")

    def generate_content(self, prompt: str) -> str:
        logger.info("Sending prompt to LLM...")
        logger.debug(f"Prompt sent to LLM:\n---\n{prompt}\n---") # Print full prompt
        try:
            response = self.model.generate_content(prompt)
            logger.info("Received response from LLM.")
            logger.debug(f"Raw LLM Response:\n---\n{response.text}\n---") # Print raw response
            return response.text
        except Exception as e:
            logger.error(f"Error generating content from LLM: {e}")
            return ""

    def list_available_models(self):
        logger.info("Listing available models...")
        try:
            for m in genai.list_models():
                logger.info(f"  Model: {m.name}, Supported methods: {m.supported_generation_methods}")
        except Exception as e:
            logger.error(f"Could not list models: {e}")

if __name__ == '__main__':
    """
    This block is for example usage and testing purposes only.
    It is commented out to prevent accidental execution and IndentationErrors.
    To run the application, use `python -m calmind.main`.
    """
    # Example usage (uncomment and modify if you want to test this specific file directly):
    from calmind.config import Config
    config = Config()
    api_key = config.get_llm_api_key()

    if api_key and api_key != "YOUR_GEMINI_API_KEY":
        client = LLMClient(api_key)
        logger.info("\n--- Available Models --- ")
        client.list_available_models()
        logger.info("\n--- End Available Models ---")

        # Example of generating content (uncomment to test)
        # prompt = "Tell me a short story about a robot who loves to read."
        # logger.info("\nGenerated Content:")
        # logger.info(client.generate_content(prompt))
    else:
        logger.warning("LLM API key not configured or is default. Cannot run LLM client example.")

