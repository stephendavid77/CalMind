from abc import ABC, abstractmethod
from datetime import datetime

class Calendar(ABC):
    def __init__(self, name: str, config: dict):
        self.name = name
        self.config = config

    @abstractmethod
    def get_events(self, start_date: datetime, end_date: datetime) -> list:
        """Abstract method to fetch calendar events within a date range."""
        pass

    @abstractmethod
    def authenticate(self):
        """Abstract method to handle calendar authentication."""
        pass

class CalendarEvent:
    def __init__(self, summary: str, start: datetime, end: datetime, location: str = None, description: str = None):
        self.summary = summary
        self.start = start
        self.end = end
        self.location = location
        self.description = description

    def __str__(self):
        start_time = self.start.strftime('%Y-%m-%d %H:%M')
        end_time = self.end.strftime('%Y-%m-%d %H:%M')
        return f"Summary: {self.summary}\nStart: {start_time}\nEnd: {end_time}\nLocation: {self.location or 'N/A'}\nDescription: {self.description or 'N/A'}\n---"

    def to_dict(self):
        return {
            "summary": self.summary,
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),
            "location": self.location,
            "description": self.description
        }
