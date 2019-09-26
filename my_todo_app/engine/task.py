#! /usr/bin/env python
# -*- coding: utf-8-unix -*-

"""The task database implementation base."""

from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import *


class Task:
    """A task."""

    def __init__(self, id_: str, list_id: str, parent_task_id: str, name: str, tags: str, memo: str, completed: bool,
                 archived: bool, created_at: int, updated_at: int, completed_at: int):
        self.id: str = id_
        self.list_id: str = list_id
        self.parent_task_id: str = parent_task_id
        self.name: str = name
        self.tags: str = tags
        self.memo: str = memo
        self.completed: bool = completed
        self.archived: bool = archived
        self.created_at: int = created_at
        self.updated_at: int = updated_at
        self.completed_at: int = completed_at

    def equals(self, another: Task):
        if self.id != another.id:
            return False
        if self.list_id != another.list_id:
            return False
        if self.parent_task_id != another.parent_task_id:
            return False
        if self.name != another.name:
            return False
        if self.tags != another.tags:
            return False
        if self.memo != another.memo:
            return False
        if self.completed != another.completed:
            return False
        if self.archived != another.archived:
            return False
        if self.created_at != another.created_at:
            return False
        if self.updated_at != another.updated_at:
            return False
        if self.completed_at != another.completed_at:
            return False
        return True


class TaskList:
    """A task list."""

    def __init__(self, id_: str, name: str, sort_key: float):
        self.id: str = id_
        self.name: str = name
        self.sort_key: float = sort_key

    def equals(self, another: TaskList):
        if self.id != another.id:
            return False
        if self.name != another.name:
            return False
        if self.sort_key != another.sort_key:
            return False
        return True


class TaskDatabase(metaclass=ABCMeta):
    """A database for task management."""

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def _begin_transaction(self) -> None:
        pass

    @abstractmethod
    def _end_transaction(self) -> None:
        pass

    @abstractmethod
    def upsert_task(self, task: Task) -> None:
        pass

    @abstractmethod
    def upsert_tasklist(self, tasklist: TaskList) -> None:
        pass

    @abstractmethod
    def delete_task(self, id_: str) -> None:
        pass

    @abstractmethod
    def delete_tasklist(self, id_: str) -> None:
        pass

    @abstractmethod
    def get_tasks(self, id_: Optional[str] = None, list_id: Optional[str] = None, parent_task_id: Optional[str] = None,
                  completed: Optional[bool] = None, archived: Optional[bool] = None) -> List[Task]:
        pass

    @abstractmethod
    def get_tasklists(self, id_: Optional[str] = None) -> List[TaskList]:
        pass
