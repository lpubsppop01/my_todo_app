#! /usr/bin/env python
# -*- coding: utf-8-unix -*-

"""Implement task management application engine."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import *

from my_todo_app.engine.task import TaskList, Task, TaskDatabase


class TaskEngine:
    """Task management application engine."""

    def __init__(self, db: TaskDatabase):
        self._db: TaskDatabase = db
        self._shows_archive: bool = False
        self._shown_tasklists: List[TaskList] = []
        self._shown_tasks: List[Task] = []
        self._selected_tasklist: Optional[TaskList] = None
        self._selected_task: Optional[Task] = None

    @property
    def shows_archive(self):
        return self._shows_archive

    @property
    def shown_tasklists(self) -> List[TaskList]:
        return self._shown_tasklists

    @property
    def shown_tasks(self) -> List[Task]:
        return self._shown_tasks

    @property
    def selected_tasklist(self) -> Optional[TaskList]:
        return self._selected_tasklist

    @property
    def selected_task(self) -> Optional[Task]:
        return self._selected_task

    def add_tasklist(self, new_tasklist: TaskList) -> None:
        if self._shown_tasklists:
            sort_key_max = max([tasklist.sort_key for tasklist in self._shown_tasklists])
            new_tasklist.sort_key = sort_key_max + 1
        self._db.upsert_tasklist(new_tasklist)
        self._update_shown_tasklists()

    def edit_selected_tasklist(self, new_tasklist: TaskList) -> None:
        if self._selected_tasklist is None:
            raise RuntimeError('No task list is selected')
        if self._selected_tasklist.id != new_tasklist.id:
            raise RuntimeError('ID of passed task list does not match selected')

        self._selected_tasklist = new_tasklist
        self._db.upsert_tasklist(new_tasklist)
        self._update_shown_tasklists()

    def remove_selected_tasklist(self) -> None:
        if self._selected_tasklist is None:
            raise RuntimeError('No task list is selected')
        if self._shown_tasks:
            raise RuntimeError('The selected task list is not empty')

        self._db.delete_tasklist(self._selected_tasklist.id)
        self._update_shown_tasklists()

    def add_empty_task(self) -> None:
        if self._selected_tasklist is None:
            raise RuntimeError('No task list is selected')

        id_ = str(uuid.uuid4())
        parent_id = self._selected_tasklist.id
        timestamp = int(datetime.now().timestamp())
        self._selected_task = Task(id_, parent_id, '', '', '', '', False, False, timestamp, timestamp, 0)
        self._db.upsert_task(self._selected_task)
        self._update_shown_tasks()

    def move_selected_task(self, list_id: str) -> None:
        if self._selected_task is None:
            raise RuntimeError('No task is selected')

        self._selected_task.list_id = list_id
        self._selected_task.updated_at = int(datetime.now().timestamp())
        self._db.upsert_task(self._selected_task)
        self._update_shown_tasks()

    def edit_selected_task_name(self, name: str):
        if self._selected_task is None:
            raise RuntimeError('No task is selected')

        self._selected_task.name = name
        self._selected_task.updated_at = int(datetime.now().timestamp())
        self._db.upsert_task(self._selected_task)
        self._update_shown_tasks()

    def remove_selected_task(self):
        if self._selected_task is None:
            raise RuntimeError('No task is selected')

        self._db.delete_task(self._selected_task.id)
        self._update_shown_tasks()

    def _update_shown_tasklists(self):
        self._shown_tasklists = self._db.get_tasklists()
        tasklist_to_select: Optional[TaskList] = None
        tasklist_to_select_is_fixed: bool = False
        for tasklist in self._shown_tasklists:
            if not tasklist_to_select_is_fixed:
                tasklist_to_select = tasklist
                if not self._selected_tasklist or self._selected_tasklist.sort_key <= tasklist.sort_key:
                    tasklist_to_select_is_fixed = True
        self._selected_tasklist = tasklist_to_select
        self._update_shown_tasks()

    def _update_shown_tasks(self):
        if self._selected_tasklist:
            archived: Optional[bool] = None
            if not self._shows_archive:
                archived = False
            self._shown_tasks = self._db.get_tasks(list_id=self._selected_tasklist.id, archived=archived)
            task_to_select: Optional[Task] = None
            task_to_select_is_fixed: bool = False
            for task in self._shown_tasks:
                if not task_to_select_is_fixed:
                    task_to_select = task
                    if not self._selected_task or self._selected_task.updated_at >= task.updated_at:
                        task_to_select_is_fixed = True
            self._selected_task = task_to_select
        else:
            self._shown_tasks = []
            self._selected_task = None
