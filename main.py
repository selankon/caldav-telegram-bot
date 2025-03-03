from secrets import TELEGRAM_BOT_TOKEN, CALDAV_URL, CALDAV_USERNAME, CALDAV_PASSWORD, TELEGRAM_CHAT_ID, CALENDAR_ID
import caldav
from datetime import datetime
import logging
import pytz
from telegram import Bot
from telegram.constants import ParseMode
import asyncio

from settings import REFETCH_INTERVAL, MESSAGE_TEMPLATE

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

bot = Bot(token=TELEGRAM_BOT_TOKEN)

# Track scheduled events to avoid duplicates
scheduled_events = set()


def fetch_calendar_events(url, username, password):
    """Fetch events from the CalDAV calendar."""
    logging.info("Connecting to CalDAV server...")
    client = caldav.DAVClient(url, username=username, password=password)
    principal = client.principal()
    calendars = principal.calendars()

    if not calendars:
        logging.warning("No calendars found.")
        return []

    calendar = calendars[0]
    # If CALENDAR_ID exists and is set on secrets.py, use it
    if CALENDAR_ID != "":
        # search calendar by name set on settins.py, if not found use the first one
        for cal in calendars:
            if cal.name == CALENDAR_ID:
                calendar = cal
                break

    logging.info(f"Using calendar: {calendar.name}")

    events = calendar.events()
    event_data = []

    for event in events:
        vevent = event.vobject_instance.vevent
        start = vevent.dtstart.value
        summary = vevent.summary.value
        description = getattr(vevent, 'description', None)
        location = getattr(vevent, 'location', None)

        # Ensure start is timezone-aware
        if not isinstance(start, datetime):
            start = datetime.combine(start, datetime.min.time())

        if start.tzinfo is None:
            start = pytz.UTC.localize(start)  # Assume UTC if no timezone is present

        event_data.append({
            "summary": summary,
            "description": description.value if description else "",
            "location": "📍 " + location.value if location else "",
            "start_time": start,
        })

    logging.info(f"Fetched {len(event_data)} events from the calendar.")
    return event_data


async def send_event_to_telegram(summary, description, location):
    """Send the event details to a Telegram chat."""
    try:
        message = MESSAGE_TEMPLATE.format(summary=summary, description=description, location=location)
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode=ParseMode.HTML)
        logging.info(f"Sent to Telegram: {message}")
    except Exception as e:
        logging.error(f"Failed to send message to Telegram: {e}")


async def schedule_event(event):
    """Schedule an event to send a message at the specified start time."""
    now = datetime.now(pytz.UTC)
    delay = (event['start_time'] - now).total_seconds()

    logging.info("Event delay " + str(delay))

    if delay > 0:
        logging.info(f"[*] Adding asynchio task for '{event['summary']}' at {event['start_time']}")
        await asyncio.sleep(delay)  # Wait until the event time
        if (event['summary'], event['start_time']) in scheduled_events:  # Double-check the event has not been removed
            await send_event_to_telegram(event['summary'], event['description'], event['location'])
            scheduled_events.remove((event['summary'], event['start_time']))


async def fetch_and_schedule_events():
    """Fetch events and schedule them."""
    global scheduled_events
    logging.info("Fetching updated events...")
    events = fetch_calendar_events(CALDAV_URL, CALDAV_USERNAME, CALDAV_PASSWORD)

    newEvents= 0
    for event in events:
        event_key = (event['summary'], event['start_time'])
        if event_key not in scheduled_events:
            newEvents = newEvents + 1
            logging.info("Found new event: " + event['summary'] + " at " + str(event['start_time']))
            scheduled_events.add(event_key)
            asyncio.create_task(schedule_event(event))
    if newEvents == 0:
        logging.info("No new events found.")
    else:
        logging.info(f"Found {newEvents} new events.")


async def main():
    logging.info("Starting the event scheduler...")
    while True:
        await fetch_and_schedule_events()
        await asyncio.sleep(REFETCH_INTERVAL)  # Refresh every minute

if __name__ == "__main__":
    asyncio.run(main())
