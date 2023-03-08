import schedule
import time
from core import fetch_and_save_events_with_retry


fetch_and_save_events_with_retry()
schedule.every(5).minutes.do(fetch_and_save_events_with_retry)

while 1:
    schedule.run_pending()
    time.sleep(1)
