#! /usr/bin/env python
# -*- coding: utf-8-unix -*-

"""The SQLite3 based task database implementation."""

import os
import sqlite3
from typing import *

from my_todo_app.engine.task import TaskDatabase, Task, TaskList


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

    def close(self):
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
                list_id text,
                parent_task_id text,
                name text,
                tags text,
                memo text,
                completed bool,
                archived bool,
                created_at integer,
                updated_at integer,
                completed_at integer
            )''')
        cursor.execute('create index task_completed_index on tasks(completed)')
        cursor.execute('''
            create table if not exists tasklists (
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
            insert or replace into tasks (id, list_id, parent_task_id, name, tags, memo, completed, archived,
                                          created_at, updated_at, completed_at)
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        '''
        cursor.execute(upsert_sql, [task.id, task.list_id, task.parent_task_id, task.name, task.tags, task.memo,
                                    task.completed, task.archived, task.created_at, task.updated_at, task.completed_at])

        if not self._cursor:
            self._conn.commit()

    def upsert_tasklist(self, tasklist: TaskList) -> None:
        if self._cursor:
            cursor = self._cursor
        else:
            cursor = self._conn.cursor()

        upsert_sql = '''
            insert or replace into tasklists (id, name, sort_key)
            values (?, ?, ?);
        '''
        cursor.execute(upsert_sql, [tasklist.id, tasklist.name, tasklist.sort_key])

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

    def delete_tasklist(self, id_: str) -> None:
        if self._cursor:
            cursor = self._cursor
        else:
            cursor = self._conn.cursor()

        delete_sql = 'delete from tasklists where id = ?'
        cursor.execute(delete_sql, [id_])

        if not self._cursor:
            self._conn.commit()

    def get_tasks(self, id_: Optional[str] = None, list_id: Optional[str] = None, parent_task_id: Optional[str] = None,
                  completed: Optional[bool] = None, archived: Optional[bool] = None) -> List[Task]:
        select_sql = 'select * from tasks'
        select_params = []
        if id_ is not None:
            select_sql += ' and' if select_params else ' where'
            select_sql += ' id = ?'
            select_params.append(id_)
        if list_id is not None:
            select_sql += ' and' if select_params else ' where'
            select_sql += ' list_id = ?'
            select_params.append(list_id)
        if parent_task_id is not None:
            select_sql += ' and' if select_params else ' where'
            select_sql += ' parent_task_id = ?'
            select_params.append(parent_task_id)
        if completed is not None:
            select_sql += ' and' if select_params else ' where'
            select_sql += ' completed = ?'
            select_params.append(int(completed))
        if archived is not None:
            select_sql += ' and' if select_params else ' where'
            select_sql += ' archived = ?'
            select_params.append(int(archived))
        select_sql += ' order by updated_at desc'
        tasks = []
        for row in self._conn.execute(select_sql, select_params):
            id_: str = row[0]
            list_id: str = row[1]
            parent_task_id: str = row[2]
            name: str = row[3]
            tags: str = row[4]
            memo: str = row[5]
            completed: bool = bool(int(row[6]))
            archived: bool = bool(int(row[7]))
            created_at: int = row[8]
            updated_at: int = row[9]
            completed_at: int = row[10]
            tasks.append(Task(id_, list_id, parent_task_id, name, tags, memo, completed, archived,
                              created_at, updated_at, completed_at))
        return tasks

    def get_tasklists(self, id_: Optional[str] = None) -> List[TaskList]:
        select_sql = 'select * from tasklists'
        select_params = []
        if id_ is not None:
            select_sql += ' and' if select_params else ' where'
            select_sql += ' id = ?'
            select_params.append(id_)
        select_sql += ' order by sort_key'
        tasklists = []
        for row in self._conn.execute(select_sql, select_params):
            id_: str = row[0]
            name: str = row[1]
            sort_key: float = row[2]
            tasklists.append(TaskList(id_, name, sort_key))
        return tasklists
