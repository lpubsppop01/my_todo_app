#! /usr/bin/env python
# -*- coding: utf-8-unix -*-

"""The SQLite3 based task database implementation."""

import os
import sqlite3
from typing import *

from my_todo_app.task import TaskDatabase, Task, TaskList


class SQLite3TaskDatabase(TaskDatabase):
    """A SQLite3 based database for task management."""

    def __init__(self, path: str):
        super().__init__()
        db_exists = os.path.exists(path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self._conn: sqlite3.Connection = sqlite3.connect(path)
        self._cursor: Optional[sqlite3.Cursor] = None
        if not db_exists:
            self._create_tables()

    def __del__(self):
        self._conn.close()

    def _begin_transaction(self):
        self._cursor = self._conn.cursor()

    def _end_transaction(self):
        self._conn.commit()
        self._cursor = None

    def _create_tables(self):
        if self._cursor:
            cursor = self._cursor
        else:
            cursor = self._conn.cursor()

        cursor.execute('''
            create table if not exists tasks (
                id text primary key not null,
                parent_id text,
                name text,
                tags text,
                done bool,
                created_at integer,
                updated_at integer,
                sort_key float
            )''')
        cursor.execute('create index task_done_index on tasks(done)')
        cursor.execute('''
            create table if not exists task_lists (
                id text primary key not null,
                name text,
                sort_key float
            )''')

        if not self._cursor:
            self._conn.commit()

    def upsert_task(self, task: Task) -> None:
        if self._cursor:
            cursor = self._cursor
        else:
            cursor = self._conn.cursor()

        upsert_sql = '''
            insert or replace into tasks (id, parent_id, name, tags, done, created_at, updated_at, sort_key)
            values (?, ?, ?, ?, ?, ?, ?, ?);
        '''
        cursor.execute(upsert_sql, [task.id, task.parent_id, task.name, task.tags, task.done, task.created_at,
                                    task.updated_at, task.sort_key])

        if not self._cursor:
            self._conn.commit()

    def upsert_task_list(self, task_list: TaskList) -> None:
        if self._cursor:
            cursor = self._cursor
        else:
            cursor = self._conn.cursor()

        upsert_sql = '''
            insert or replace into task_lists (id, name, sort_key)
            values (?, ?, ?);
        '''
        cursor.execute(upsert_sql, [task_list.id, task_list.name, task_list.sort_key])

        if not self._cursor:
            self._conn.commit()

    def delete_task(self, id_: str) -> None:
        if self._cursor:
            cursor = self._cursor
        else:
            cursor = self._conn.cursor()

        delete_sql = 'delete from tasks where id = ?'
        cursor.execute(delete_sql, [id_])

        if not self._cursor:
            self._conn.commit()

    def delete_task_list(self, id_: str) -> None:
        if self._cursor:
            cursor = self._cursor
        else:
            cursor = self._conn.cursor()

        delete_sql = 'delete from task_lists where id = ?'
        cursor.execute(delete_sql, [id_])

        if not self._cursor:
            self._conn.commit()

    def get_tasks(self, id_: Optional[str] = None, parent_id: Optional[str] = None,
                  done: Optional[bool] = None) -> List[Task]:
        select_sql = 'select * from tasks'
        select_params = []
        if id_ is not None:
            select_sql += ' and' if select_params else ' where'
            select_sql += ' id = ?'
            select_params.append(id_)
        if parent_id is not None:
            select_sql += ' and' if select_params else ' where'
            select_sql += ' parent_id = ?'
            select_params.append(parent_id)
        if done is not None:
            select_sql += ' and' if select_params else ' where'
            select_sql += ' done = ?'
            select_params.append(int(done))
        select_sql += ' order by sort_key'
        tasks = []
        for row in self._conn.execute(select_sql, select_params):
            id_: str = row[0]
            parent_id: str = row[1]
            name: str = row[2]
            tags: str = row[3]
            done: bool = bool(int(row[4]))
            created_at: int = row[5]
            updated_at: int = row[6]
            sort_key: float = float(row[7])
            tasks.append(Task(id_, parent_id, name, tags, done, created_at, updated_at, sort_key))
        return tasks

    def get_task_lists(self, id_: Optional[str] = None) -> List[TaskList]:
        select_sql = 'select * from task_lists'
        select_params = []
        if id_ is not None:
            select_sql += ' and' if select_params else ' where'
            select_sql += ' id = ?'
            select_params.append(id_)
        select_sql += ' order by sort_key'
        task_lists = []
        for row in self._conn.execute(select_sql, select_params):
            id_: str = row[0]
            name: str = row[1]
            sort_key: float = row[2]
            task_lists.append(TaskList(id_, name, sort_key))
        return task_lists
