import schedule
import time
from core import fetch_and_save_events

fetch_and_save_events()
schedule.every(25).minutes.do(fetch_and_save_events)

while 1:
    schedule.run_pending()
    time.sleep(1)
