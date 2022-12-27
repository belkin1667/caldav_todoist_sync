import schedule
import time
from datetime import datetime, timedelta, timezone

import caldav
from todoist_api_python.api import TodoistAPI
from todoist_api_python.models import Task as TodoistTask

from credentials import *

caldavapi = caldav.DAVClient(url=caldav_url, username=username, password=password)
todoist = TodoistAPI(todoist_token)

lookbehind_minutes = 90
lookahead_days = 14

caldav_task_id_mark = "CalDEV identifier: "
last_updated_task_description_template = '* Last Updated: '
monitoring_task_mark = 'Monitoring'
import_label = 'calendar_import'


class MyEvent:
    id: str = None
    title: str = None
    description: str = None
    timezone: str = None
    start: datetime = None
    start_iso_str: str = None
    end: datetime = None
    conference: str = None
    url: str = None
    categories: [str] = []

    def __init__(self, external_event: caldav.Event):
        self.id = external_event.vobject_instance.vevent.uid.value
        self.title = external_event.vobject_instance.vevent.summary.value
        try:
            self.description = external_event.vobject_instance.vevent.description.value
        except:
            self.description = None
        try:
            self.timezone = external_event.vobject_instance.vtimezone.tzid.value
        except:
            self.timezone = None
        self.start = external_event.vobject_instance.vevent.dtstart.value
        self.start_iso_str = to_iso_at_zulu(self.start)
        self.end = external_event.vobject_instance.vevent.dtend.value
        try:
            self.conference = external_event.vobject_instance.vevent.conference.value
        except:
            self.conference = None
        self.url = external_event.vobject_instance.vevent.url.value
        self.categories = external_event.vobject_instance.vevent.categories.value

    def __str__(self):
        return self.__dict__.__str__()

    def description_with_conference(self):
        result = ''
        if self.description is not None:
            result = self.description

        if self.conference is None or self.conference in result:
            return result
        else:
            return result + '\nConference: ' + self.conference


def to_iso_at_zulu(dt: datetime):
    return dt.astimezone(timezone.utc).__str__().replace(' ', 'T').replace('+00:00', 'Z')


def fetch_tasks(project_id):
    return todoist.get_tasks(project_id=project_id, label=import_label)


def delete_tasks(tasks):
    for task in tasks:
        todoist.delete_task(task_id=task.id)


def create_or_update_task_from_event(event: MyEvent, tasks_map: dict):
    if event.id in tasks_map:
        task = tasks_map[event.id]
    else:
        task = None

    if task is None:
        print('Task not found for event! Creating new task')
        save_event_as_task(event)  # not found existing task - creating new
        print('Task created!')
    else:
        print('Task found for event!', task, 'Updating task..')
        update_task_from_event(task, event)  # found existing task - updating it
        tasks_map.pop(event.id)  # means we updated task, all remaining tasks will be deleted from todoist
        print('Task updated!')


def create_or_update_last_saved_mark(task: TodoistTask):
    if task is not None:
        return todoist.update_task(
            task_id=task.id,
            content=last_updated_task_description_template + to_iso_at_zulu(datetime.now()),
            labels=[import_label],
            description=monitoring_task_mark,
            order=0
        )
    else:
        return todoist.add_task(
            project_id=meetings_project_id,
            content=last_updated_task_description_template + to_iso_at_zulu(datetime.now()),
            description=monitoring_task_mark,
            labels=[import_label],
            order=0
        )


def save_event_as_task(event: MyEvent):
    return todoist.add_task(
        project_id=meetings_project_id,
        content=event.title,
        description=event.description_with_conference() + "\n\n" + caldav_task_id_mark + event.id,
        due_datetime=event.start_iso_str,
        labels=[import_label]
    )


def update_task_from_event(task: TodoistTask, event: MyEvent):
    return todoist.update_task(
        task_id=task.id,
        content=event.title,
        description=event.description_with_conference() + "\n\n" + caldav_task_id_mark + event.id,
        due_datetime=event.start_iso_str,
        labels=[import_label]
    )


def get_caldav_id_from(task: TodoistTask):
    try:
        return task.description.split(caldav_task_id_mark)[1].strip()
    except:
        raise Exception('Could not find CalDAV id of task', task)


def fetch_and_save_events():
    my_principal = caldavapi.principal()
    calendars = my_principal.calendars()

    calendars_by_name = {}
    for c in calendars:
        calendars_by_name[c.name] = c

    calendar: caldav.Calendar = calendars_by_name[calendar_name]
    print('Fetching events...')
    events_fetched = calendar.search(
        start=datetime.now().__add__(timedelta(minutes=-lookbehind_minutes)),
        end=datetime.now().__add__(timedelta(days=lookahead_days)),
        event=True,
        expand=True
    )
    print(len(events_fetched), ' events found!')
    events_map = {}
    events = []
    for ev in events_fetched:
        event = MyEvent(ev)
        events_map[event.id] = event
        events.append(event)
        print('Event', event, 'added to event map!')

    print('Fetching tasks...')
    tasks = fetch_tasks(meetings_project_id)  # fetching tasks in project and with our technical label
    print(len(tasks), ' tasks found!')
    monitoring_task = None
    tasks_map = {}
    for task in tasks:
        print('Processing task ', task)
        if monitoring_task_mark in task.description.strip():
            print('Found monitoring task ', task)
            monitoring_task = task
        else:
            print('Found event task ', task)
            tasks_map[get_caldav_id_from(task)] = task

    print(len(events), 'events to be processed')
    for event in events:
        print('Processing event: ', event)
        create_or_update_task_from_event(event, tasks_map)

    print('Found ', len(tasks_map.values()), ' tasks to delete. Deleting..')
    delete_tasks(tasks_map.values())  # delete tasks that are not in calendar anymore
    print('Deleted!')

    create_or_update_last_saved_mark(monitoring_task)  # for monitoring of tool activity

fetch_and_save_events()
schedule.every(25).minutes.do(fetch_and_save_events)

while 1:
    schedule.run_pending()
    time.sleep(1)
