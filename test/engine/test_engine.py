#! /usr/bin/env python
# -*- coding: utf-8-unix -*-

import os
from unittest import TestCase

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
        engine.add_empty_task()

        self.assertEqual(1, len(engine.shown_tasks))
        self.assertEqual('', engine.shown_tasks[0].name)
        self.assertEqual(engine.shown_tasks[0], engine.selected_task)
        self.assertEqual(engine.selected_tasklist.id, engine.selected_task.list_id)

        engine.edit_selected_task_name('Add TaskEngine unit tests')

        self.assertEqual('Add TaskEngine unit tests', engine.selected_task.name)

        engine.add_empty_task()

        self.assertEqual(2, len(engine.shown_tasks))
        self.assertEqual('', engine.shown_tasks[0].name)
        self.assertEqual('Add TaskEngine unit tests', engine.shown_tasks[1].name)
        self.assertEqual(engine.shown_tasks[0], engine.selected_task)

        engine.select_task(engine.shown_tasks[1].id)
        engine.move_selected_task(engine.shown_tasklists[1].id)

        self.assertEqual(1, len(engine.shown_tasks))

        engine.select_tasklist(engine.shown_tasklists[1].id)

        self.assertEqual(1, len(engine.shown_tasks))
        self.assertEqual('Add TaskEngine unit tests', engine.shown_tasks[0].name)
        self.assertEqual(engine.shown_tasks[0], engine.selected_task)
        self.assertEqual(engine.selected_tasklist.id, engine.selected_task.list_id)

        # todo

        db._conn.close()
        os.remove(db_path)
