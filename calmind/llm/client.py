import google.generativeai as genai

class LLMClient:
    def __init__(self, api_key: str):
        print("LLMClient: Initializing LLM client.")
        if not api_key:
            print("LLMClient Error: Gemini API Key is required.")
            raise ValueError("Gemini API Key is required.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro-latest')
        print("LLMClient: LLM client initialized successfully.")

    def generate_content(self, prompt: str) -> str:
        print("LLMClient: Sending prompt to LLM...")
        print(f"LLMClient: Prompt sent to LLM:\n---\n{prompt}\n---") # Print full prompt
        try:
            response = self.model.generate_content(prompt)
            print("LLMClient: Received response from LLM.")
            print(f"LLMClient: Raw LLM Response:\n---\n{response.text}\n---") # Print raw response
            return response.text
        except Exception as e:
            print(f"LLMClient Error: Error generating content from LLM: {e}")
            return ""

    def list_available_models(self):
        print("LLMClient: Listing available models...")
        try:
            for m in genai.list_models():
                print(f"  Model: {m.name}, Supported methods: {m.supported_generation_methods}")
        except Exception as e:
            print(f"LLMClient Error: Could not list models: {e}")

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
        print("\n--- Available Models --- ")
        client.list_available_models()
        print("\n--- End Available Models ---")

        # Example of generating content (uncomment to test)
        # prompt = "Tell me a short story about a robot who loves to read."
        # print("\nGenerated Content:")
        # print(client.generate_content(prompt))
    else:
        print("LLM API key not configured or is default. Cannot run LLM client example.")

