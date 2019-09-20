#! /usr/bin/env python
# -*- coding: utf-8-unix -*-

"""The task database implementation base."""

from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import *


class Task:
    """A task."""

    def __init__(self, id_: str, parent_id: str, name: str, tags: str, done: bool, created_at: int, updated_at: int,
                 sort_key: float):
        self.id: str = id_
        self.parent_id: str = parent_id
        self.name: str = name
        self.tags: str = tags
        self.done: bool = done
        self.created_at: int = created_at
        self.updated_at: int = updated_at
        self.sort_key: float = sort_key

    def equals(self, another: Task):
        if self.id != another.id:
            return False
        if self.parent_id != another.parent_id:
            return False
        if self.name != another.name:
            return False
        if self.tags != another.tags:
            return False
        if self.created_at != another.created_at:
            return False
        if self.updated_at != another.updated_at:
            return False
        if self.sort_key != another.sort_key:
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
    def _begin_transaction(self) -> None:
        pass

    @abstractmethod
    def _end_transaction(self) -> None:
        pass

    @abstractmethod
    def upsert_task(self, task: Task) -> None:
        pass

    @abstractmethod
    def upsert_task_list(self, task_list: TaskList) -> None:
        pass

    @abstractmethod
    def delete_task(self, id_: str) -> None:
        pass

    @abstractmethod
    def delete_task_list(self, id_: str) -> None:
        pass

    @abstractmethod
    def get_tasks(self, id_: Optional[str] = None, parent_id: Optional[str] = None,
                  done: Optional[bool] = None) -> List[Task]:
        pass

    @abstractmethod
    def get_task_lists(self, id_: Optional[str] = None) -> List[TaskList]:
        pass
