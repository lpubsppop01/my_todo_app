#! /usr/bin/env python
# -*- coding: utf-8-unix -*-

import os
import sys
from datetime import datetime
from unittest import TestCase

from freezegun import freeze_time

from my_todo_app.engine.engine import TaskEngine, InsertTo
from my_todo_app.engine.task_sqlite3 import SQLite3TaskDatabase


class TestTaskEngine(TestCase):

    def test_tasklist_crud(self):
        class_name = self.__class__.__name__
        func_name = sys._getframe().f_code.co_name
        db_path = os.path.join(os.path.dirname(__file__), '{}_{}.sqlite3'.format(class_name, func_name))
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
        self.assertTrue(engine.can_up_selected_tasklist())

        engine.select_tasklist(engine.shown_tasklists[1].id)
        engine.edit_selected_tasklist(name='Next Action')

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

        db._conn.close()
        os.remove(db_path)

    def test_tasklist_up_down(self):
        class_name = self.__class__.__name__
        func_name = sys._getframe().f_code.co_name
        db_path = os.path.join(os.path.dirname(__file__), '{}_{}.sqlite3'.format(class_name, func_name))
        if os.path.exists(db_path):
            os.remove(db_path)
        db = SQLite3TaskDatabase(db_path)
        engine = TaskEngine(db)
        engine.add_tasklist('Inbox')
        engine.add_tasklist('Foo')
        engine.add_tasklist('Bar')
        engine.add_tasklist('Baz')

        self.assertTrue(engine.can_up_selected_tasklist())

        engine.up_selected_tasklist()

        self.assertEqual('Inbox', engine.shown_tasklists[0].name)
        self.assertEqual('Foo', engine.shown_tasklists[1].name)
        self.assertEqual('Baz', engine.shown_tasklists[2].name)
        self.assertEqual('Bar', engine.shown_tasklists[3].name)
        self.assertEqual(engine.shown_tasklists[2], engine.selected_tasklist)
        self.assertTrue(engine.can_up_selected_tasklist())

        engine.up_selected_tasklist()

        self.assertEqual('Inbox', engine.shown_tasklists[0].name)
        self.assertEqual('Baz', engine.shown_tasklists[1].name)
        self.assertEqual('Foo', engine.shown_tasklists[2].name)
        self.assertEqual('Bar', engine.shown_tasklists[3].name)
        self.assertEqual(engine.shown_tasklists[1], engine.selected_tasklist)
        self.assertTrue(engine.can_up_selected_tasklist())

        engine.up_selected_tasklist()

        self.assertEqual('Baz', engine.shown_tasklists[0].name)
        self.assertEqual('Inbox', engine.shown_tasklists[1].name)
        self.assertEqual('Foo', engine.shown_tasklists[2].name)
        self.assertEqual('Bar', engine.shown_tasklists[3].name)
        self.assertEqual(engine.shown_tasklists[0], engine.selected_tasklist)
        self.assertFalse(engine.can_up_selected_tasklist())
        self.assertTrue(engine.can_down_selected_tasklist())

        engine.down_selected_tasklist()

        self.assertEqual('Inbox', engine.shown_tasklists[0].name)
        self.assertEqual('Baz', engine.shown_tasklists[1].name)
        self.assertEqual('Foo', engine.shown_tasklists[2].name)
        self.assertEqual('Bar', engine.shown_tasklists[3].name)
        self.assertEqual(engine.shown_tasklists[1], engine.selected_tasklist)
        self.assertTrue(engine.can_down_selected_tasklist())

        engine.down_selected_tasklist()

        self.assertEqual('Inbox', engine.shown_tasklists[0].name)
        self.assertEqual('Foo', engine.shown_tasklists[1].name)
        self.assertEqual('Baz', engine.shown_tasklists[2].name)
        self.assertEqual('Bar', engine.shown_tasklists[3].name)
        self.assertEqual(engine.shown_tasklists[2], engine.selected_tasklist)
        self.assertTrue(engine.can_down_selected_tasklist())

        engine.down_selected_tasklist()

        self.assertEqual('Inbox', engine.shown_tasklists[0].name)
        self.assertEqual('Foo', engine.shown_tasklists[1].name)
        self.assertEqual('Bar', engine.shown_tasklists[2].name)
        self.assertEqual('Baz', engine.shown_tasklists[3].name)
        self.assertEqual(engine.shown_tasklists[3], engine.selected_tasklist)
        self.assertFalse(engine.can_down_selected_tasklist())

        db._conn.close()
        os.remove(db_path)

    def test_task_crud(self):
        class_name = self.__class__.__name__
        func_name = sys._getframe().f_code.co_name
        db_path = os.path.join(os.path.dirname(__file__), '{}_{}.sqlite3'.format(class_name, func_name))
        if os.path.exists(db_path):
            os.remove(db_path)
        db = SQLite3TaskDatabase(db_path)
        engine = TaskEngine(db)
        engine.add_tasklist('Inbox')
        engine.add_tasklist('Next Action')

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
            engine.edit_selected_task(name='Add TaskEngine unit tests', memo='Memo')

        self.assertEqual('Add TaskEngine unit tests', engine.selected_task.name)
        self.assertEqual('Memo', engine.selected_task.memo)
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
            engine.move_selected_task(list_id=engine.shown_tasklists[1].id)

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

        engine.select_task(engine.shown_tasks[1].id)
        datetime_20190927_123000 = datetime(2019, 9, 27, 12, 30, 0)
        with freeze_time(datetime_20190927_123000):
            engine.edit_selected_task(completed=True)

        self.assertTrue(engine.shown_tasks[1].completed)
        self.assertEqual(datetime_20190927_123000.timestamp(), engine.shown_tasks[1].completed_at)
        self.assertEqual(datetime_20190927_123000.timestamp(), engine.shown_tasks[1].updated_at)

        engine.select_task(engine.shown_tasks[1].id)
        datetime_20190927_123500 = datetime(2019, 9, 27, 12, 35, 0)
        with freeze_time(datetime_20190927_123500):
            engine.edit_selected_task(archived=True)

        self.assertEqual(1, len(engine.shown_tasks))
        self.assertEqual('Baz', engine.shown_tasks[0].name)
        self.assertFalse(engine.shown_tasks[0].archived)

        engine.shows_archive = True

        self.assertEqual(2, len(engine.shown_tasks))
        self.assertEqual(engine.shown_tasks[0], engine.selected_task)
        self.assertEqual('Bar', engine.shown_tasks[1].name)
        self.assertTrue(engine.shown_tasks[1].archived)
        self.assertEqual(datetime_20190927_123500.timestamp(), engine.shown_tasks[1].updated_at)

        db._conn.close()
        os.remove(db_path)

    def test_task_up_down(self):
        class_name = self.__class__.__name__
        func_name = sys._getframe().f_code.co_name
        db_path = os.path.join(os.path.dirname(__file__), '{}_{}.sqlite3'.format(class_name, func_name))
        if os.path.exists(db_path):
            os.remove(db_path)
        db = SQLite3TaskDatabase(db_path)
        engine = TaskEngine(db)
        engine.add_tasklist('Inbox')
        with freeze_time(datetime(2019, 9, 27, 12, 0, 0)):
            engine.add_task(name='Task1')
        with freeze_time(datetime(2019, 9, 27, 12, 5, 0)):
            engine.add_task(name='Task2', to=InsertTo.LAST_SIBLING)
        with freeze_time(datetime(2019, 9, 27, 12, 10, 0)):
            engine.add_task(name='Task3', to=InsertTo.LAST_SIBLING)

        self.assertTrue(engine.can_up_selected_task())

        engine.up_selected_task()

        self.assertEqual('Task1', engine.shown_tasks[0].name)
        self.assertEqual('Task3', engine.shown_tasks[1].name)
        self.assertEqual('Task2', engine.shown_tasks[2].name)
        self.assertEqual(engine.shown_tasks[1], engine.selected_task)
        self.assertTrue(engine.can_up_selected_task())

        engine.up_selected_task()

        self.assertEqual('Task3', engine.shown_tasks[0].name)
        self.assertEqual('Task1', engine.shown_tasks[1].name)
        self.assertEqual('Task2', engine.shown_tasks[2].name)
        self.assertEqual(engine.shown_tasks[0], engine.selected_task)
        self.assertFalse(engine.can_up_selected_task())

        engine.down_selected_task()

        self.assertEqual('Task1', engine.shown_tasks[0].name)
        self.assertEqual('Task3', engine.shown_tasks[1].name)
        self.assertEqual('Task2', engine.shown_tasks[2].name)
        self.assertEqual(engine.shown_tasks[1], engine.selected_task)
        self.assertTrue(engine.can_down_selected_task())

        engine.down_selected_task()

        self.assertEqual('Task1', engine.shown_tasks[0].name)
        self.assertEqual('Task2', engine.shown_tasks[1].name)
        self.assertEqual('Task3', engine.shown_tasks[2].name)
        self.assertEqual(engine.shown_tasks[2], engine.selected_task)
        self.assertFalse(engine.can_down_selected_task())

        db._conn.close()
        os.remove(db_path)

    def test_sub_task_crud(self):
        class_name = self.__class__.__name__
        func_name = sys._getframe().f_code.co_name
        db_path = os.path.join(os.path.dirname(__file__), '{}_{}.sqlite3'.format(class_name, func_name))
        if os.path.exists(db_path):
            os.remove(db_path)
        db = SQLite3TaskDatabase(db_path)
        engine = TaskEngine(db)
        engine.add_tasklist('Inbox')
        engine.add_tasklist('Next Action')
        engine.select_tasklist(engine.shown_tasklists[0].id)
        with freeze_time(datetime(2019, 9, 27, 12, 0, 0)):
            engine.add_task(name='Task1')
        with freeze_time(datetime(2019, 9, 27, 12, 5, 0)):
            engine.add_task(name='Task2', to=InsertTo.LAST_SIBLING)

        engine.select_task(engine.shown_tasks[0].id)
        datetime_20190927_124000 = datetime(2019, 9, 27, 12, 40, 0)
        with freeze_time(datetime_20190927_124000):
            engine.add_task(name='Sub1', to=InsertTo.LAST_CHILD)

        self.assertEqual(3, len(engine.shown_tasks))
        self.assertEqual(engine.shown_tasks[1], engine.selected_task)
        self.assertEqual('Sub1', engine.shown_tasks[1].name)
        self.assertEqual(engine.shown_tasks[0].id, engine.shown_tasks[1].parent_task_id)
        self.assertEqual(datetime_20190927_124000.timestamp(), engine.shown_tasks[1].updated_at)
        self.assertFalse(engine.can_move_selected_task())

        engine.select_task(engine.shown_tasks[0].id)
        datetime_20190927_125000 = datetime(2019, 9, 27, 12, 50, 0)
        with freeze_time(datetime_20190927_125000):
            engine.move_selected_task(list_id=engine._shown_tasklists[1].id)

        self.assertEqual(1, len(engine.shown_tasks))

        engine.select_tasklist(engine.shown_tasklists[1].id)

        self.assertEqual(2, len(engine.shown_tasks))

        db._conn.close()
        os.remove(db_path)

    def test_sub_task_up_down(self):
        class_name = self.__class__.__name__
        func_name = sys._getframe().f_code.co_name
        db_path = os.path.join(os.path.dirname(__file__), '{}_{}.sqlite3'.format(class_name, func_name))
        if os.path.exists(db_path):
            os.remove(db_path)
        db = SQLite3TaskDatabase(db_path)
        engine = TaskEngine(db)
        engine.add_tasklist('Inbox')
        with freeze_time(datetime(2019, 9, 27, 12, 0, 0)):
            engine.add_task(name='Task1')
        with freeze_time(datetime(2019, 9, 27, 12, 5, 0)):
            engine.add_task(name='Task2', to=InsertTo.LAST_SIBLING)
        engine.select_task(engine.shown_tasks[0].id)
        with freeze_time(datetime(2019, 9, 27, 12, 10, 0)):
            engine.add_task(name='Sub1', to=InsertTo.LAST_CHILD)
        with freeze_time(datetime(2019, 9, 27, 12, 15, 0)):
            engine.add_task(name='Sub2', to=InsertTo.LAST_SIBLING)
        with freeze_time(datetime(2019, 9, 27, 12, 20, 0)):
            engine.add_task(name='Sub3', to=InsertTo.LAST_SIBLING)
        engine.select_task(engine.shown_tasks[3].id)

        self.assertTrue(engine.can_up_selected_task())

        engine.up_selected_task()

        self.assertEqual('Sub1', engine.shown_tasks[1].name)
        self.assertEqual('Sub3', engine.shown_tasks[2].name)
        self.assertEqual('Sub2', engine.shown_tasks[3].name)
        self.assertEqual(engine.shown_tasks[2], engine.selected_task)
        self.assertTrue(engine.can_up_selected_task())

        engine.up_selected_task()

        self.assertEqual('Sub3', engine.shown_tasks[1].name)
        self.assertEqual('Sub1', engine.shown_tasks[2].name)
        self.assertEqual('Sub2', engine.shown_tasks[3].name)
        self.assertEqual(engine.shown_tasks[1], engine.selected_task)
        self.assertFalse(engine.can_up_selected_task())

        engine.down_selected_task()

        self.assertEqual('Sub1', engine.shown_tasks[1].name)
        self.assertEqual('Sub3', engine.shown_tasks[2].name)
        self.assertEqual('Sub2', engine.shown_tasks[3].name)
        self.assertEqual(engine.shown_tasks[2], engine.selected_task)
        self.assertTrue(engine.can_down_selected_task())

        engine.down_selected_task()

        self.assertEqual('Sub1', engine.shown_tasks[1].name)
        self.assertEqual('Sub2', engine.shown_tasks[2].name)
        self.assertEqual('Sub3', engine.shown_tasks[3].name)
        self.assertEqual(engine.shown_tasks[3], engine.selected_task)
        self.assertFalse(engine.can_down_selected_task())

        engine.select_task(engine.shown_tasks[0].id)
        engine.down_selected_task()

        self.assertEqual('Task2', engine.shown_tasks[0].name)
        self.assertEqual('Task1', engine.shown_tasks[1].name)
        self.assertEqual(engine.shown_tasks[1], engine.selected_task)
        self.assertTrue(engine.can_up_selected_task())
        self.assertFalse(engine.can_down_selected_task())

        engine.up_selected_task()

        self.assertEqual('Task1', engine.shown_tasks[0].name)
        self.assertEqual('Task2', engine.shown_tasks[4].name)
        self.assertEqual(engine.shown_tasks[0], engine.selected_task)
        self.assertFalse(engine.can_up_selected_task())
        self.assertTrue(engine.can_down_selected_task())

        db._conn.close()
        os.remove(db_path)
