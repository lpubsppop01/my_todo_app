#! /usr/bin/env python
# -*- coding: utf-8-unix -*-

import os
import uuid
from unittest import TestCase

from my_todo_app.engine.task import TaskList, Task
from my_todo_app.engine.task_sqlite3 import SQLite3TaskDatabase


class TestTaskDatabase(TestCase):

    def test_it_works(self):
        db_path = os.path.join(os.path.dirname(__file__), 'TestTaskDatabase_test_it_works.sqlite3')
        if os.path.exists(db_path):
            os.remove(db_path)
        db = SQLite3TaskDatabase(db_path)

        self.assertEqual(0, len(db.get_tasklists()))
        self.assertEqual(0, len(db.get_tasks()))

        # Insert 2 task lists
        inbox = TaskList(str(uuid.uuid4()), 'Inbox', 0)
        next_action = TaskList(str(uuid.uuid4()), 'Next Action', 10)
        db.upsert_tasklist(inbox)
        db.upsert_tasklist(next_action)
        tasklists = db.get_tasklists()
        self.assertEqual(2, len(tasklists))
        self.assertTrue(inbox.equals(tasklists[0]))
        self.assertTrue(next_action.equals(tasklists[1]))

        # Delete 1 of the task lists
        db.delete_tasklist(next_action.id)
        tasklists = db.get_tasklists()
        self.assertEqual(1, len(tasklists))

        # Reinsert the deleted task list and update it
        db.upsert_tasklist(next_action)
        next_action.name = 'Foo'
        next_action.sort_key = -10
        db.upsert_tasklist(next_action)
        tasklists = db.get_tasklists()
        self.assertEqual(2, len(tasklists))
        self.assertTrue(next_action.equals(tasklists[0]))
        self.assertTrue(inbox.equals(tasklists[1]))

        # Insert 2 tasks and 1 sub task
        task1 = Task(str(uuid.uuid4()), inbox.id, '', 'Task 1', 'test', False, 100, 110, 0)  # Set newer updated_at
        task2 = Task(str(uuid.uuid4()), inbox.id, '', 'Task 2', 'test', False, 100, 100, 0)
        task2_1 = Task(str(uuid.uuid4()), inbox.id, task2.id, 'Task 2-1', 'test', False, 100, 100, 0)
        db.upsert_task(task1)
        db.upsert_task(task2)
        db.upsert_task(task2_1)
        inbox_tasks = db.get_tasks(list_id=inbox.id)
        self.assertEqual(3, len(inbox_tasks))
        self.assertTrue(task1.equals(inbox_tasks[0]))
        self.assertTrue(task2.equals(inbox_tasks[1]))
        self.assertTrue(task2_1.equals(inbox_tasks[2]))
        self.assertEqual(0, len(db.get_tasks(list_id=next_action.id)))

        # Delete 1 of the tasks
        db.delete_task(task1.id)
        inbox_tasks = db.get_tasks(list_id=inbox.id)
        self.assertEqual(2, len(inbox_tasks))

        # Reinsert the deleted task and update it
        db.upsert_task(task1)
        task1.list_id = next_action.id
        task1.name = 'Bar'
        task1.tags = 'test2'
        task1.created_at = 50
        task1.updated_at = 150
        task1.completed_at = 15
        db.upsert_task(task1)
        inbox_tasks = db.get_tasks(list_id=inbox.id)
        next_action_tasks = db.get_tasks(list_id=next_action.id)
        self.assertEqual(2, len(inbox_tasks))
        self.assertTrue(task2.equals(inbox_tasks[0]))
        self.assertTrue(task2_1.equals(inbox_tasks[1]))
        self.assertEqual(1, len(next_action_tasks))
        self.assertTrue(task1.equals(next_action_tasks[0]))

        # todo: Test that moving only sub task fails
        # todo: Test that moving a parent task also follows sub tasks

        del db
        os.remove(db_path)
