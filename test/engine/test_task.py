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

        self.assertEqual(0, len(db.get_task_lists()))
        self.assertEqual(0, len(db.get_tasks()))

        # Insert 2 task lists
        inbox = TaskList(str(uuid.uuid4()), 'Inbox', 0)
        next_action = TaskList(str(uuid.uuid4()), 'Next Action', 10)
        db.upsert_task_list(inbox)
        db.upsert_task_list(next_action)
        task_lists = db.get_task_lists()
        self.assertEqual(2, len(task_lists))
        self.assertTrue(inbox.equals(task_lists[0]))
        self.assertTrue(next_action.equals(task_lists[1]))

        # Delete 1 of the task lists
        db.delete_task_list(next_action.id)
        task_lists = db.get_task_lists()
        self.assertEqual(1, len(task_lists))

        # Reinsert the deleted task list and update it
        db.upsert_task_list(next_action)
        next_action.name = 'Foo'
        next_action.sort_key = -10
        db.upsert_task_list(next_action)
        task_lists = db.get_task_lists()
        self.assertEqual(2, len(task_lists))
        self.assertTrue(next_action.equals(task_lists[0]))
        self.assertTrue(inbox.equals(task_lists[1]))

        # Insert 2 tasks
        task1 = Task(str(uuid.uuid4()), inbox.id, 'Task 1', 'test', False, 100, 100, 0)
        task2 = Task(str(uuid.uuid4()), inbox.id, 'Task 2', 'test', False, 100, 100, 10)
        db.upsert_task(task1)
        db.upsert_task(task2)
        inbox_tasks = db.get_tasks(parent_id=inbox.id)
        self.assertEqual(2, len(inbox_tasks))
        self.assertTrue(task1.equals(inbox_tasks[0]))
        self.assertTrue(task2.equals(inbox_tasks[1]))
        self.assertEqual(0, len(db.get_tasks(parent_id=next_action.id)))

        # Delete 1 of the tasks
        db.delete_task(task2.id)
        inbox_tasks = db.get_tasks(parent_id=inbox.id)
        self.assertEqual(1, len(inbox_tasks))

        # Reinsert the deleted task and update it
        db.upsert_task(task2)
        task2.parent_id = next_action.id
        task2.name = 'Bar'
        task2.tags = 'test2'
        task2.created_at = 50
        task2.updated_at = 150
        task2.sort_key = -10
        db.upsert_task(task2)
        inbox_tasks = db.get_tasks(parent_id=inbox.id)
        next_action_tasks = db.get_tasks(parent_id=next_action.id)
        self.assertEqual(1, len(inbox_tasks))
        self.assertTrue(task1.equals(inbox_tasks[0]))
        self.assertEqual(1, len(next_action_tasks))
        self.assertTrue(task2.equals(next_action_tasks[0]))

        del db
        os.remove(db_path)
