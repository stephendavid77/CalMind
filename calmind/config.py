import yaml
import os
import logging
from pydantic import BaseModel, Field, EmailStr, HttpUrl, RootModel
from pydantic_settings import SettingsConfigDict
from typing import List, Optional, Union

logger = logging.getLogger(__name__)

class EmailConfig(BaseModel):
    model_config = SettingsConfigDict(env_prefix='EMAIL_', extra='ignore')

    email: Optional[EmailStr] = None
    password: Optional[str] = None
    smtp_server: Optional[str] = None
    smtp_port: Optional[int] = None

class LLMConfig(BaseModel):
    api_key: str

class GoogleCalendarConfig(BaseModel):
    type: str = "google"
    name: str
    credentials_path: Optional[str] = "credentials.json"
    calendar_ids: List[str] = ["primary"]

class AppleCalendarConfig(BaseModel):
    type: str = "apple"
    name: str
    username: EmailStr
    password: str
    url: Optional[HttpUrl] = None
    calendar_name: Optional[str] = None

class UserCalendarConfig(RootModel[Union[GoogleCalendarConfig, AppleCalendarConfig]]):
    pass

class UserConfig(BaseModel):
    name: str
    report_to_email: EmailStr
    days_to_fetch: int = 30
    calendars: List[UserCalendarConfig] = []

class AppConfig(BaseModel):
    email_sender: EmailConfig = Field(default_factory=EmailConfig)
    llm: Optional[LLMConfig] = None
    users: List[UserConfig] = []

class Config:
    def __init__(self, config_path: str = 'config.yaml'):
        logger.info(f"Initializing Config with path: {config_path}")
        self.config_path = config_path
        self._app_config: Optional[AppConfig] = None
        self._load_config()

    def _load_config(self):
        logger.info(f"Attempting to load config from {self.config_path}")
        try:
            with open(self.config_path, 'r') as f:
                raw_config = yaml.safe_load(f)
            self._app_config = AppConfig(**raw_config)
            logger.info("Configuration loaded and validated successfully.")
        except FileNotFoundError:
            logger.critical(f"Config file not found at {self.config_path}. Please ensure it exists.")
            raise
        except yaml.YAMLError as e:
            logger.critical(f"Error parsing config file {self.config_path}: {e}")
            raise
        except Exception as e:
            logger.critical(f"Error validating config file {self.config_path} with Pydantic: {e}")
            raise

    def get_email_sender_config(self) -> Optional[EmailConfig]:
        return self._app_config.email_sender

    def get_llm_config(self) -> Optional[LLMConfig]:
        return self._app_config.llm

    def get_users_config(self) -> List[UserConfig]:
        return self._app_config.users

if __name__ == '__main__':
    # Example usage:
    try:
        config = Config()
        email_config = config.get_email_sender_config()
        if email_config:
            logger.info(f"Email Sender Config: Email={email_config.email}, SMTP={email_config.smtp_server}:{email_config.smtp_port}")
        else:
            logger.info("Email Sender Config: Not configured.")

        llm_config = config.get_llm_config()
        if llm_config:
            logger.info(f"LLM API Key: {llm_config.api_key[:5]}...{llm_config.api_key[-5:]}")
        else:
            logger.info("LLM API Key: Not configured.")

        logger.info("Users Config:")
        for user in config.get_users_config():
            logger.info(f"  - Name: {user.name}")
            logger.info(f"    Report To: {user.report_to_email}")
            logger.info(f"    Days To Fetch: {user.days_to_fetch}")
            logger.info(f"    Calendars:")
            for calendar_union in user.calendars:
                calendar = calendar_union.root # Access the actual model from the Union
                if isinstance(calendar, GoogleCalendarConfig):
                    logger.info(f"      - Type: {calendar.type}, Name: {calendar.name}, Credentials Path: {calendar.credentials_path}")
                elif isinstance(calendar, AppleCalendarConfig):
                    logger.info(f"      - Type: {calendar.type}, Name: {calendar.name}, Username: {calendar.username}, Password (provided): {'Yes' if calendar.password else 'No'}, URL: {calendar.url}")
    except Exception as e:
        logger.error(f"Error during example usage: {e}")