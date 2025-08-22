import caldav
import logging
from caldav.elements import dav, cdav
from urllib.parse import quote
from datetime import datetime, timedelta
import pytz # For timezone handling
import icalendar # For parsing and creating iCalendar events
import uuid # For generating unique IDs for events

logger = logging.getLogger(__name__)

from .base import Calendar
from calmind.config import AppleCalendarConfig

class AppleCalendar(Calendar):
    def __init__(self, name: str, config: AppleCalendarConfig):
        super().__init__(name, config)
        self.username = config.username # Access directly from Pydantic model
        self.password = config.password # Access directly from Pydantic model
        self.calendar_url = config.url # Access directly from Pydantic model
        self.client = None
        self.principal = None
        self.calendar = None
        logger.info(f"Initialized with username: {self.username}, password_provided: {'Yes' if self.password else 'No'}, calendar_url: {self.calendar_url}")

    def authenticate(self):
        """
        Authenticates with the Apple Calendar (iCloud CalDAV) server.
        Note: For iCloud, you might need an app-specific password.
        """
        logger.info("Attempting authentication...")
        if not self.username or not self.password:
            logger.error(f"Username ({self.username}) or password (provided: {'Yes' if self.password else 'No'}) missing for authentication.")
            raise ValueError("Username and password are required for Apple Calendar authentication.")

        # Default iCloud CalDAV URL if not provided
        if not self.calendar_url:
            self.calendar_url = f"https://{quote(self.username)}:{quote(self.password)}@caldav.icloud.com"
            logger.info(f"Using default iCloud CalDAV URL: {self.calendar_url.split('@')[-1]} (password hidden). Username: {self.username}, Password length: {len(self.password) if self.password else 0}")

        try:
            logger.info(f"Connecting to DAVClient at {self.calendar_url.split('@')[-1]}...")
            self.client = caldav.DAVClient(self.calendar_url)
            self.principal = self.client.principal()
            logger.info(f"Principal discovered: {self.principal.url}")

            calendars = self.principal.calendars()
            logger.info(f"Found Apple Calendars: {[cal.name for cal in calendars]}") # Log all calendar names
            if calendars:
                if self.config.calendar_name: # Check if a specific calendar name is provided in config
                    found_calendar = None
                    for cal in calendars:
                        if cal.name == self.config.calendar_name:
                            found_calendar = cal
                            break
                    if found_calendar:
                        self.calendar = found_calendar
                        logger.info(f"Successfully authenticated and connected to Apple Calendar: {self.calendar.name} (URL: {self.calendar.url})")
                        return True
                    else:
                        logger.error(f"Specified Apple Calendar '{self.config.calendar_name}' not found for the authenticated user. Available calendars: {[c.name for c in calendars]}")
                        raise Exception(f"Specified Apple Calendar '{self.config.calendar_name}' not found.")
                else:
                    self.calendar = calendars[0] # Use the first calendar found if no specific name is provided
                    logger.info(f"Successfully authenticated and connected to Apple Calendar: {self.calendar.name} (URL: {self.calendar.url})")
                    return True
            else:
                logger.error("No calendars found for the authenticated user.")
                raise Exception("No calendars found for the authenticated user.")
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            self.client = None
            self.principal = None
            self.calendar = None
            return False # Return False on authentication failure

    def get_events(self, start_time: datetime, end_time: datetime):
        """
        Fetches events from the Apple Calendar within the specified time range.
        """
        if not self.principal:
            logger.error("Not authenticated. Cannot fetch events.")
            raise Exception("Not authenticated to Apple Calendar. Call authenticate() first.")

        logger.info(f"Fetching events from {start_time} to {end_time}...")

        # Ensure start_time and end_time are timezone-aware, preferably UTC
        if start_time.tzinfo is None:
            start_time = pytz.utc.localize(start_time)
            logger.info(f"Localized start_time to UTC: {start_time}")
        if end_time.tzinfo is None:
            end_time = pytz.utc.localize(end_time)
            logger.info(f"Localized end_time to UTC: {end_time}")

        all_events = []
        target_calendars = []

        if self.config.calendar_name:
            # If a specific calendar name is provided, use only that calendar
            if self.calendar: # self.calendar would be set during authentication if a specific name was found
                target_calendars.append(self.calendar)
            else:
                logger.warning(f"Specific calendar '{self.config.calendar_name}' not found during authentication. Cannot fetch events.")
                return []
        else:
            # If no specific calendar name is provided, fetch from all calendars
            try:
                target_calendars = self.principal.calendars()
                logger.info(f"Fetching events from all available Apple Calendars: {[c.name for c in target_calendars]}")
            except Exception as e:
                logger.error(f"Could not retrieve all calendars from principal: {e}")
                return []

        for calendar_obj in target_calendars:
            logger.info(f"Fetching events from calendar: {calendar_obj.name}")
            try:
                caldav_events = calendar_obj.date_search(start=start_time, end=end_time)
                logger.info(f"Found {len(caldav_events)} raw CalDAV events from {calendar_obj.name}.")
                for event_obj in caldav_events:
                    try:
                        logger.info(f"Parsing iCal data for event: {event_obj.url.path}")
                        cal = icalendar.Calendar.from_ical(event_obj.data)
                        for component in cal.walk():
                            if component.name == "VEVENT":
                                summary = str(component.get('summary'))
                                start = component.get('dtstart').dt
                                end = component.get('dtend').dt
                                description = str(component.get('description')) if component.get('description') else None
                                location = str(component.get('location')) if component.get('location') else None

                                all_events.append({
                                    "id": event_obj.url.path, # Use URL path as a unique ID
                                    "summary": summary,
                                    "start": start,
                                    "end": end,
                                    "description": description,
                                    "location": location,
                                    "raw_ical": event_obj.data
                                })
                                logger.info(f"Successfully parsed event: {summary}")
                    except Exception as parse_e:
                        logger.error(f"Error parsing iCal data for event {event_obj.url.path} from {calendar_obj.name}: {parse_e}")
                        all_events.append({
                            "id": event_obj.url.path,
                            "summary": f"Unparseable Event (raw iCal): {event_obj.data[:50]}...",
                            "start": None, "end": None, "description": None, "location": None,
                            "raw_ical": event_obj.data
                        })
            except Exception as e:
                logger.error(f"Error fetching Apple Calendar events from {calendar_obj.name}: {e}")

        logger.info(f"Returning {len(all_events)} parsed events from all processed calendars.")
        return all_events

    def create_event(self, summary, start_time, end_time, description=None, location=None):
        """
        Creates a new event in the Apple Calendar.
        """
        if not self.calendar:
            logger.error("Not authenticated. Cannot create event.")
            raise Exception("Not authenticated to Apple Calendar. Call authenticate() first.")

        logger.info(f"Attempting to create event: '{summary}' from {start_time} to {end_time}")
        event = icalendar.Event()
        event.add('summary', summary)
        event.add('dtstart', start_time)
        event.add('dtend', end_time)
        event.add('dtstamp', datetime.now(pytz.utc)) # Event creation timestamp
        event.add('uid', str(uuid.uuid4()) + '@calmind.com') # Unique ID for the event

        if description:
            event.add('description', description)
        if location:
            event.add('location', location)

        try:
            cal = icalendar.Calendar()
            cal.add_component(event)
            
            new_event_url = self.calendar.save_event(cal.to_ical())
            logger.info(f"Successfully created event: {summary} at {new_event_url}")
            return {"status": "success", "message": "Event created successfully.", "event_url": new_event_url}
        except Exception as e:
            logger.error(f"Error creating event '{summary}': {e}")
            raise

    def update_event(self, event_id, summary=None, start_time=None, end_time=None, description=None, location=None):
        """
        Updates an existing event in the Apple Calendar.
        event_id should be the URL path of the event (e.g., from get_events result).
        """
        if not self.calendar:
            logger.error("Not authenticated. Cannot update event.")
            raise Exception("Not authenticated to Apple Calendar. Call authenticate() first.")

        logger.info(f"Attempting to update event with ID: {event_id}")
        try:
            event_obj = self.calendar.event_by_url(event_id)
            if not event_obj:
                logger.error(f"Event with ID {event_id} not found for update.")
                raise ValueError(f"Event with ID {event_id} not found.")

            cal = icalendar.Calendar.from_ical(event_obj.data)
            vevent = None
            for component in cal.walk():
                if component.name == "VEVENT":
                    vevent = component
                    break
            
            if not vevent:
                logger.error(f"No VEVENT component found in event {event_id}.")
                raise ValueError(f"No VEVENT component found in event {event_id}.")

            if summary is not None:
                vevent['summary'] = summary
                logger.info(f"Updating summary to '{summary}'")
            if start_time is not None:
                vevent['dtstart'] = start_time
                logger.info(f"Updating start_time to '{start_time}'")
            if end_time is not None:
                vevent['dtend'] = end_time
                logger.info(f"Updating end_time to '{end_time}'")
            if description is not None:
                vevent['description'] = description
                logger.info(f"Updating description")
            if location is not None:
                vevent['location'] = location
                logger.info(f"Updating location to '{location}'")

            vevent['dtstamp'] = datetime.now(pytz.utc)

            self.calendar.save_event(cal.to_ical(), url=event_obj.url)
            logger.info(f"Successfully updated event: {event_id}")
            return {"status": "success", "message": "Event updated successfully.", "event_url": event_id}
        except Exception as e:
            logger.error(f"Error updating event {event_id}: {e}")
            raise

    def delete_event(self, event_id):
        """
        Deletes an event from the Apple Calendar.
        event_id should be the URL path of the event (e.g., from get_events result).
        """
        if not self.calendar:
            logger.error("Not authenticated. Cannot delete event.")
            raise Exception("Not authenticated to Apple Calendar. Call authenticate() first.")

        logger.info(f"Attempting to delete event with ID: {event_id}")
        try:
            event_obj = self.calendar.event_by_url(event_id)
            if not event_obj:
                logger.error(f"Event with ID {event_id} not found for deletion.")
                raise ValueError(f"Event with ID {event_id} not found for deletion.")

            self.calendar.delete_event(event_obj.url)
            logger.info(f"Successfully deleted event: {event_id}")
            return {"status": "success", "message": "Event deleted successfully."}
        except Exception as e:
            logger.error(f"Error deleting event {event_id}: {e}")
            raise