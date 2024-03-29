#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""The application entry point."""

import os
from datetime import datetime

import uuid

from my_todo_app.app.config import Config
from my_todo_app.app.main_window import MainWindow
from my_todo_app.app.my_image_set import MyImageSet
from my_todo_app.engine.task import TaskList, TaskDatabase, Task
from my_todo_app.engine.task_sqlite3 import SQLite3TaskDatabase


def get_db_path():
    appdata = os.getenv('APPDATA')
    if appdata is not None:
        return os.path.join(appdata, 'lpubsppop01', 'my_todo', 'db.sqlite3')
    return '~/.lpubsppop01/my_todo/db.sqlite3'


def get_config_path():
    appdata = os.getenv('APPDATA')
    if appdata is not None:
        return os.path.join(appdata, 'lpubsppop01', 'my_todo', 'config.json')
    return '~/.lpubsppop01/my_todo/config.json'


def insert_sample_if_empty(db: TaskDatabase):
    if db.get_tasklists():
        return
    db.upsert_tasklist(TaskList('inbox', 'Inbox', 0))
    db.upsert_tasklist(TaskList('next_action', 'Next Action', 1))
    db.upsert_tasklist(TaskList('someday', 'Someday', 2))
    timestamp = int(datetime.now().timestamp())
    db.upsert_task(Task(str(uuid.uuid4()), 'inbox', '', 'Foo', '', '', False, False, timestamp, timestamp, 0, 0))
    db.upsert_task(Task(str(uuid.uuid4()), 'inbox', '', 'Bar', '', '', False, True, timestamp, timestamp, 0, 1))


def main():
    db_path = get_db_path()
    db = SQLite3TaskDatabase(db_path)
    insert_sample_if_empty(db)
    config = Config(get_config_path())
    images = MyImageSet()
    window = MainWindow(db, config, images)
    window.show()
    db.close()


if __name__ == '__main__':
    main()
