#! /usr/bin/env python
# -*- coding: utf-8-unix -*-

import os
from datetime import datetime
from unittest import TestCase

from freezegun import freeze_time

from my_todo_app.engine.engine import TaskEngine
from my_todo_app.engine.task_sqlite3 import SQLite3TaskDatabase


class TestTaskEngine(TestCase):

    def test_it_works(self):
        db_path = os.path.join(os.path.dirname(__file__), 'TestTaskEngine_test_it_works.sqlite3')
        if os.path.exists(db_path):
            os.remove(db_path)
        db = SQLite3TaskDatabase(db_path)
        engine = TaskEngine(db)

        self.assertEqual(0, len(engine.shown_tasklists))
        self.assertEqual(0, len(engine.shown_tasks))
        self.assertEqual(None, engine.selected_tasklist)
        self.assertEqual(None, engine.selected_task)

        engine.add_tasklist('Inbox')
        engine.add_tasklist('Foo')
        engine.add_tasklist('Bar')
        engine.add_tasklist('Baz')

        self.assertEqual(4, len(engine.shown_tasklists))
        self.assertEqual('Inbox', engine.shown_tasklists[0].name)
        self.assertEqual('Foo', engine.shown_tasklists[1].name)
        self.assertEqual('Bar', engine.shown_tasklists[2].name)
        self.assertEqual('Baz', engine.shown_tasklists[3].name)
        self.assertEqual(engine.shown_tasklists[3], engine.selected_tasklist)
        self.assertEqual(None, engine.selected_task)

        engine.select_tasklist(engine.shown_tasklists[1].id)
        engine.edit_selected_tasklist('Next Action')

        self.assertEqual(engine.shown_tasklists[1], engine.selected_tasklist)
        self.assertEqual('Next Action', engine.selected_tasklist.name)

        engine.select_tasklist(engine.shown_tasklists[2].id)
        engine.remove_selected_tasklist()

        self.assertEqual(3, len(engine.shown_tasklists))
        self.assertEqual(engine.shown_tasklists[2], engine.selected_tasklist)
        self.assertEqual('Baz', engine.selected_tasklist.name)

        engine.remove_selected_tasklist()

        self.assertEqual(2, len(engine.shown_tasklists))
        self.assertEqual(engine.shown_tasklists[1], engine.selected_tasklist)
        self.assertEqual('Next Action', engine.selected_tasklist.name)

        engine.select_tasklist(engine.shown_tasklists[0].id)
        datetime_20190927_120000 = datetime(2019, 9, 27, 12, 0, 0)
        with freeze_time(datetime_20190927_120000):
            engine.add_task()

        self.assertEqual(1, len(engine.shown_tasks))
        self.assertEqual('', engine.shown_tasks[0].name)
        self.assertEqual(datetime_20190927_120000.timestamp(), engine.shown_tasks[0].created_at)
        self.assertEqual(datetime_20190927_120000.timestamp(), engine.shown_tasks[0].updated_at)
        self.assertEqual(engine.shown_tasks[0], engine.selected_task)
        self.assertEqual(engine.selected_tasklist.id, engine.selected_task.list_id)

        datetime_20190927_120500 = datetime(2019, 9, 27, 12, 5, 0)
        with freeze_time(datetime_20190927_120500):
            engine.edit_selected_task(name='Add TaskEngine unit tests')

        self.assertEqual('Add TaskEngine unit tests', engine.selected_task.name)
        self.assertEqual(datetime_20190927_120500.timestamp(), engine.selected_task.updated_at)

        datetime_20190927_121000 = datetime(2019, 9, 27, 12, 10, 0)
        with freeze_time(datetime_20190927_121000):
            engine.add_task()

        self.assertEqual(2, len(engine.shown_tasks))
        self.assertEqual('', engine.shown_tasks[0].name)
        self.assertEqual(datetime_20190927_121000.timestamp(), engine.shown_tasks[0].updated_at)
        self.assertEqual('Add TaskEngine unit tests', engine.shown_tasks[1].name)
        self.assertEqual(engine.shown_tasks[0], engine.selected_task)

        engine.select_task(engine.shown_tasks[1].id)
        datetime_20190927_121500 = datetime(2019, 9, 27, 12, 15, 0)
        with freeze_time(datetime_20190927_121500):
            engine.edit_selected_task(list_id=engine.shown_tasklists[1].id)

        self.assertEqual(1, len(engine.shown_tasks))

        engine.select_tasklist(engine.shown_tasklists[1].id)

        self.assertEqual(1, len(engine.shown_tasks))
        self.assertEqual('Add TaskEngine unit tests', engine.shown_tasks[0].name)
        self.assertEqual(datetime_20190927_121500.timestamp(), engine.shown_tasks[0].updated_at)
        self.assertEqual(engine.shown_tasks[0], engine.selected_task)
        self.assertEqual(engine.selected_tasklist.id, engine.selected_task.list_id)

        datetime_20190927_121500 = datetime(2019, 9, 27, 12, 15, 0)
        datetime_20190927_122000 = datetime(2019, 9, 27, 12, 20, 0)
        datetime_20190927_122500 = datetime(2019, 9, 27, 12, 25, 0)
        with freeze_time(datetime_20190927_121500):
            engine.add_task(name='Foo')
        with freeze_time(datetime_20190927_122000):
            engine.add_task(name='Bar')
        with freeze_time(datetime_20190927_122500):
            engine.add_task(name='Baz')

        self.assertEqual(4, len(engine.shown_tasks))
        self.assertEqual('Foo', engine.shown_tasks[2].name)
        self.assertEqual(datetime_20190927_121500.timestamp(), engine.shown_tasks[2].updated_at)
        self.assertEqual('Bar', engine.shown_tasks[1].name)
        self.assertEqual(datetime_20190927_122000.timestamp(), engine.shown_tasks[1].updated_at)
        self.assertEqual('Baz', engine.shown_tasks[0].name)
        self.assertEqual(datetime_20190927_122500.timestamp(), engine.shown_tasks[0].updated_at)
        self.assertEqual(engine.shown_tasks[0], engine.selected_task)

        engine.select_task(engine.shown_tasks[2].id)
        engine.remove_selected_task()

        self.assertEqual(3, len(engine.shown_tasks))
        self.assertEqual('Add TaskEngine unit tests', engine.shown_tasks[2].name)
        self.assertEqual('Bar', engine.shown_tasks[1].name)
        self.assertEqual('Baz', engine.shown_tasks[0].name)
        self.assertEqual(engine.shown_tasks[2], engine.selected_task)

        engine.remove_selected_task()

        self.assertEqual(2, len(engine.shown_tasks))
        self.assertEqual('Bar', engine.shown_tasks[1].name)
        self.assertEqual('Baz', engine.shown_tasks[0].name)
        self.assertEqual(engine.shown_tasks[1], engine.selected_task)

        db._conn.close()
        os.remove(db_path)
