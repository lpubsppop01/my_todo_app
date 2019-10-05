#! /usr/bin/env python
# -*- coding: utf-8-unix -*-

import copy
import os
import uuid
from unittest import TestCase

from my_todo_app.engine.task import TaskList, Task
from my_todo_app.engine.task_sqlite3 import SQLite3TaskDatabase


class TestTaskDatabase(TestCase):

    def test_crud(self):
        db_path = os.path.join(os.path.dirname(__file__), 'TestTaskDatabase_test_crud.sqlite3')
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
        task1 = Task(str(uuid.uuid4()), inbox.id, '', 'Task 1', 'test', '', False, False, 10, 10, 0, 0)
        task2 = Task(str(uuid.uuid4()), inbox.id, '', 'Task 2', 'test', '', False, False, 10, 10, 0, 1)
        task2_1 = Task(str(uuid.uuid4()), inbox.id, task2.id, 'Task 2-1', 'test', '', False, False, 10, 10, 0, 2)
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

        db.close()
        os.remove(db_path)

    def test_equals(self):
        task = Task(str(uuid.uuid4()), '', '', '', '', '', False, False, 0, 0, 0, 0)

        not_changed = copy.deepcopy(task)
        self.assertTrue(task.equals(not_changed))

        id_changed = copy.deepcopy(task)
        id_changed.id = str(uuid.uuid4())
        self.assertFalse(task.equals(id_changed))

        list_id_changed = copy.deepcopy(task)
        list_id_changed.list_id = str(uuid.uuid4())
        self.assertFalse(task.equals(list_id_changed))

        parent_task_id_changed = copy.deepcopy(task)
        parent_task_id_changed.parent_task_id = str(uuid.uuid4())
        self.assertFalse(task.equals(parent_task_id_changed))

        name_changed = copy.deepcopy(task)
        name_changed.name = 'Task 1'
        self.assertFalse(task.equals(name_changed))

        tags_changed = copy.deepcopy(task)
        tags_changed.tags = 'test'
        self.assertFalse(task.equals(tags_changed))

        memo_changed = copy.deepcopy(task)
        memo_changed.memo = 'Memo'
        self.assertFalse(task.equals(memo_changed))

        completed_changed = copy.deepcopy(task)
        completed_changed.completed = True
        self.assertFalse(task.equals(completed_changed))

        archived_changed = copy.deepcopy(task)
        archived_changed.archived = True
        self.assertFalse(task.equals(archived_changed))

        created_at_changed = copy.deepcopy(task)
        created_at_changed.created_at = 20
        self.assertFalse(task.equals(created_at_changed))

        updated_at_changed = copy.deepcopy(task)
        updated_at_changed.updated_at = 20
        self.assertFalse(task.equals(updated_at_changed))

        completed_at_changed = copy.deepcopy(task)
        completed_at_changed.completed_at = 20
        self.assertFalse(task.equals(completed_at_changed))

        sort_key_changed = copy.deepcopy(task)
        sort_key_changed.sort_key = 10
        self.assertFalse(task.equals(sort_key_changed))

    def test_get_first_last(self):
        db_path = os.path.join(os.path.dirname(__file__), 'TestTaskDatabase_test_get_first_last.sqlite3')
        if os.path.exists(db_path):
            os.remove(db_path)
        db = SQLite3TaskDatabase(db_path)

        inbox = TaskList(str(uuid.uuid4()), 'Inbox', 0)
        db.upsert_tasklist(inbox)
        task1 = Task(str(uuid.uuid4()), inbox.id, '', 'Task 1', 'test', '', False, False, 10, 10, 0, 0)
        task2 = Task(str(uuid.uuid4()), inbox.id, '', 'Task 2', 'test', '', False, False, 10, 10, 0, 2)
        task2_1 = Task(str(uuid.uuid4()), inbox.id, task2.id, 'Task 2-1', 'test', '', False, False, 10, 10, 0, 2.1)
        task2_2 = Task(str(uuid.uuid4()), inbox.id, task2.id, 'Task 2-2', 'test', '', False, True, 10, 10, 0, 2.2)
        task2_3 = Task(str(uuid.uuid4()), inbox.id, task2.id, 'Task 2-3', 'test', '', False, False, 10, 10, 0, 2.3)
        task2_4 = Task(str(uuid.uuid4()), inbox.id, task2.id, 'Task 2-4', 'test', '', False, False, 10, 10, 0, 2.4)
        task2_5 = Task(str(uuid.uuid4()), inbox.id, task2.id, 'Task 2-5', 'test', '', False, True, 10, 10, 0, 2.5)
        task3 = Task(str(uuid.uuid4()), inbox.id, '', 'Task 3', 'test', '', False, False, 10, 10, 0, 3)
        db.upsert_task(task1)
        db.upsert_task(task2)
        db.upsert_task(task2_1)
        db.upsert_task(task2_2)
        db.upsert_task(task2_3)
        db.upsert_task(task2_4)
        db.upsert_task(task2_5)
        db.upsert_task(task3)

        self.assertTrue(task1.equals(db.get_first_task()))
        self.assertTrue(task3.equals(db.get_last_task()))
        self.assertTrue(task2_1.equals(db.get_first_task(parent_task_id=task2.id)))
        self.assertTrue(task2_5.equals(db.get_last_task(parent_task_id=task2.id)))
        self.assertTrue(task2_2.equals(db.get_last_task(sort_key_before=task2_3.sort_key)))
        self.assertTrue(task2_4.equals(db.get_first_task(sort_key_after=task2_3.sort_key)))
        self.assertTrue(task1.equals(db.get_last_task(parent_task_id='', sort_key_before=task2.sort_key)))
        self.assertTrue(task3.equals(db.get_first_task(parent_task_id='', sort_key_after=task2.sort_key)))

        db.close()
        os.remove(db_path)
