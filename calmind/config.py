import yaml
import os

class Config:
    def __init__(self, config_path='config.yaml'):
        print(f"Config: Initializing with config path: {config_path}")
        self.config = self._load_config(config_path)
        if self.config:
            print("Config: Configuration loaded successfully.")
        else:
            print("Config: Failed to load configuration.")

    def _load_config(self, config_path):
        try:
            print(f"Config: Attempting to load config from {config_path}")
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Config Error: Config file not found at {config_path}")
            exit(1)
        except yaml.YAMLError as e:
            print(f"Config Error: Error parsing config file: {e}")
            exit(1)

    def get_email_sender_config(self):
        sender_config = self.config.get('email_sender', {})
        email = sender_config.get('email') or os.getenv('EMAIL_SENDER_EMAIL')
        password = sender_config.get('password') or os.getenv('EMAIL_SENDER_PASSWORD')
        smtp_server = sender_config.get('smtp_server') or os.getenv('EMAIL_SMTP_SERVER')
        smtp_port = sender_config.get('smtp_port') or os.getenv('EMAIL_SMTP_PORT')
        return {
            'email': email,
            'password': password,
            'smtp_server': smtp_server,
            'smtp_port': int(smtp_port) if smtp_port else None
        }

    def get_llm_api_key(self):
        return self.config.get('llm', {}).get('api_key')

    def get_users_config(self):
        return self.config.get('users', [])

if __name__ == '__main__':
    # Example usage:
    config = Config()
    print("Email Sender Config:", config.get_email_sender_config())
    print("LLM API Key:", config.get_llm_api_key())
    print("Users Config:")
    for user in config.get_users_config():
        print(f"  - Name: {user.get('name')}")
        print(f"    Report To: {user.get('report_to_email')}")
        print(f"    Days To Fetch: {user.get('days_to_fetch', 30)}")
        print(f"    Calendars:")
        for calendar in user.get('calendars', []):
            print(f"      - Type: {calendar.get('type')}, Name: {calendar.get('name')}")
