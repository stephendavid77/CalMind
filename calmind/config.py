
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

class TrelloConfig(BaseModel):
    type: str = "trello"
    name: str
    api_key: str
    api_token: str
    board_id: str

class UserSourceConfig(RootModel[Union[GoogleCalendarConfig, AppleCalendarConfig, TrelloConfig]]):
    pass

class UserConfig(BaseModel):
    name: str
    report_to_email: EmailStr
    days_to_fetch: int = 30
    sources: List[UserSourceConfig] = []

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
