# Discord Purdue Course Monitor

**Note: This is a one-and-done project. It will not be maintained except for bug fixes. Hopefully, it continues to work. If any bugs are found, feel free to submit an Issue/PR.**

## Usage

1. Install Python 3.6 or higher
2. Install the required packages with `pip install -r requirements.txt`
3. Create a Discord bot and get its token
4. Create a Webhook and get its URL
5. Copy `.env.example` to `.env` and fill in the values
6. Run `python discord-bot.py`

## Commands

- `/add_course SEMESTER YEAR SUBJECT NUMBER` - Add a course to monitor
- `/remove_course SEMESTER YEAR SUBJECT NUMBER` - Remove a course from monitoring
- `/list_courses` - List all courses being monitored
