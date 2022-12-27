# Sync your calendar to Todoist tasks!

## Installation guide
1. Download git repo
2. Add your CalDAV and Todoist credentials to `main.py` and `project_picker.py`
3. Install add dependencies from `requirements.txt`, note that python3.9 is minimum required python version
4. Run `project_picker.py` - choose project identifier (number near project name) you'd like use. Enter that id as string literal to `meetings_project_id` variable in `main.py`
5. Run `main.py` - every 25 minutes this tool will load all events from calendar and create/update/delete corresponding tasks in Todoist project you specified with special label `calendar_import` 
6. Add script to auto-launch on startup to your local computer or host it on some Cloud (you'll find MacOS launch script in this repo - `ru.belkinmike.caldav-todoist.sync.plist` and usage guide [here](https://stackoverflow.com/a/13372744/8054916))

## Please, note! 
- Maybe someday I'll pack this script as Todoist extension, but not today
- Do not change tasks created by script as script uses some textual marks in description and labels to identify tasks
- Script will recreate completed/deleted task (Todoist API I used does not support fetching completed tasks, unfortunately), so just wait for like 30 minutes (you can change this) after calendar event start time and task will disappear itself

## Contact Author:
Telegram: [@belkinmike](belkinmike.t.me)