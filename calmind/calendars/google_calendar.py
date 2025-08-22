import os
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from calmind.calendars.base import Calendar, CalendarEvent
from calmind.config import GoogleCalendarConfig

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

class GoogleCalendar(Calendar):
    def __init__(self, name: str, config: GoogleCalendarConfig):
        super().__init__(name, config)
        self.credentials = None
        self.service = None
        self.token_path = 'token.json' # Path to store user's access and refresh tokens
        self.credentials_path = config.credentials_path # Access directly from Pydantic model
        self.calendar_ids = config.calendar_ids # Access directly from Pydantic model
        logger.info(f"Initialized for {self.name} with credentials_path={self.credentials_path}")

    def authenticate(self):
        """Shows user how to authenticate with Google Calendar API."""
        logger.info(f"Attempting to authenticate for {self.name}...")
        creds = None
        if os.path.exists(self.token_path):
            logger.info(f"Found existing token file at {self.token_path}")
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
        
        if not creds or not creds.valid:
            logger.info("No valid credentials found or token expired.")
            if creds and creds.expired and creds.refresh_token:
                logger.info("Refreshing expired token...")
                creds.refresh(Request())
            else:
                logger.info("Initiating new authentication flow.")
                if not os.path.exists(self.credentials_path):
                    logger.error(f"Google Calendar credentials file not found at {self.credentials_path}")
                    logger.error("Please download 'credentials.json' from Google Cloud Console and place it in the project root or specify its path in config.yaml.")
                    logger.error("Refer to Google Calendar API Quickstart for details: https://developers.google.com/calendar/api/quickstart/python")
                    return False
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                logger.info("Opening browser for authentication...")
                creds = flow.run_local_server(port=0)
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
            logger.info(f"Token saved to {self.token_path}")
        
        self.credentials = creds
        try:
            self.service = build('calendar', 'v3', credentials=creds)
            logger.info(f"Authentication successful for {self.name}.")
            return True
        except HttpError as error:
            logger.error(f'An HTTP error occurred during authentication: {error}')
            return False
        except Exception as e:
            logger.error(f'An unexpected error occurred during authentication: {e}')
            return False

    def get_events(self, start_date: datetime, end_date: datetime) -> list:
        """Fetches events from the configured Google Calendars."""
        logger.info(f"Fetching events from {start_date} to {end_date} for {self.name}.")
        if not self.service:
            logger.error("Google Calendar service not authenticated. Please run authenticate() first.")
            return []

        events_list = []
        time_min = start_date.isoformat() + 'Z'  # 'Z' indicates UTC time
        time_max = end_date.isoformat() + 'Z'

        for calendar_id in self.calendar_ids:
            logger.info(f"Fetching events for calendar ID: {calendar_id}")
            try:
                events_result = self.service.events().list(
                    calendarId=calendar_id,
                    timeMin=time_min,
                    timeMax=time_max,
                    singleEvents=True,
                    orderBy='startTime'
                ).execute()
                events = events_result.get('items', [])

                if not events:
                    logger.info(f'No upcoming events found for {calendar_id}.')
                else:
                    logger.info(f'Found {len(events)} events for {calendar_id}.')
                for event in events:
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    end = event['end'].get('dateTime', event['end'].get('date'))

                    if 'T' not in start: # All-day event
                        start_dt = datetime.fromisoformat(start)
                        end_dt = datetime.fromisoformat(end) - timedelta(days=1) 
                    else:
                        start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                        end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))

                    events_list.append(CalendarEvent(
                        summary=event.get('summary', 'No Summary'),
                        start=start_dt,
                        end=end_dt,
                        location=event.get('location'),
                        description=event.get('description')
                    ))
            except HttpError as error:
                logger.error(f'An HTTP error occurred fetching events for {calendar_id}: {error}')
            except Exception as e:
                logger.error(f'An unexpected error occurred for {calendar_id}: {e}')
        logger.info(f"Finished fetching events. Total events: {len(events_list)}")
        return events_list

if __name__ == '__main__':
    """
    This block is for example usage and testing purposes only.
    It is commented out to prevent accidental execution and IndentationErrors.
    To run the application, use `python -m calmind.main`.
    """
    # Example usage (uncomment and modify if you want to test this specific file directly):
    from calmind.config import Config, GoogleCalendarConfig
    config_obj = Config()
    users_config = config_obj.get_users_config()

    if users_config:
        user = users_config[0]
        google_calendar_config: Optional[GoogleCalendarConfig] = None
        for cal_union in user.calendars:
            cal = cal_union.__root__
            if isinstance(cal, GoogleCalendarConfig):
                google_calendar_config = cal
                break

        if google_calendar_config:
            logger.info(f"Attempting to fetch events for {user.name}'s Google Calendar...")
            gcal = GoogleCalendar(
                name=google_calendar_config.name,
                config=google_calendar_config
            )
            if gcal.authenticate():
                now = datetime.now()
                future = now + timedelta(days=7)
                events = gcal.get_events(now, future)
                for event in events:
                    logger.info(event)
            else:
                logger.error("Google Calendar authentication failed.")
        else:
            logger.warning("No Google Calendar found in config for the first user.")
    else:
        logger.warning("No users configured in config.yaml.")

