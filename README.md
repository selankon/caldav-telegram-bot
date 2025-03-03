
# Telegram Event Reminder Bot

This Python script fetches events from a CalDAV calendar and sends reminders to a specified Telegram chat. It ensures you never miss an event by providing timely notifications with event details, including the summary, description, and location.

---

## Features

- **CalDAV Integration**: Fetch events from your CalDAV-compliant calendar.
- **Telegram Notifications**: Send reminders directly to your Telegram chat.
- **Event Details**: Notifications include the event summary, description, and location.
- **Real-Time Scheduling**: Dynamically schedules and sends reminders based on event start times.
- **Duplicate Prevention**: Tracks scheduled events to avoid sending duplicate notifications.

---

## Requirements

- Python 3.7 or higher
- A CalDAV-compatible calendar
- A Telegram bot with a valid API token
- The following Python packages:
  - `python-telegram-bot`
  - `caldav`
  - `pytz`

---

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/telegram-event-reminder.git
   cd telegram-event-reminder
   ```

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your secrets:
   - Create a `secrets.py` file in the project directory.
   - Add the following variables with your credentials:
     ```python
     TELEGRAM_BOT_TOKEN = "your-telegram-bot-token"
     TELEGRAM_CHAT_ID = "your-telegram-chat-id"
     CALDAV_URL = "your-caldav-calendar-url"
     CALDAV_USERNAME = "your-caldav-username"
     CALDAV_PASSWORD = "your-caldav-password"
     ```

4. Set the event refresh interval in `settings.py`:
   ```python
   REFETCH_INTERVAL = 60  # Time in seconds (e.g., 60 for 1 minute)
   ```
   
5. Add service to systemd:
   ```bash
   sudo cp caldavbot.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable caldavbot
   sudo systemctl start caldavbot
   ```
   
6. Optionally add a restart service timer:
   ```bash
   sudo cp caldavbot.timer /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable caldavbot.timer
   sudo systemctl start caldavbot.timer
   ```
   
You can see active timers with:
   ```
   systemctl list-timer
   ```

---

## Usage

Run the script with the following command:
```bash
python your_script_name.py
```

The bot will:
1. Fetch events from the CalDAV calendar.
2. Schedule reminders based on the event start time.
3. Send notifications to your specified Telegram chat.

---

## Notification Format

Each notification follows this template:
```
⏰Recordatori⏰
<b>Summary:</b> {summary}
<b>Description:</b> {description}
<b>Location:</b> {location}
```

---

## Logging

The script uses Python’s `logging` module to provide detailed logs about its operations. Logs include:
- Connection to the CalDAV server
- Events fetched and scheduled
- Notifications sent to Telegram
- Any errors encountered

