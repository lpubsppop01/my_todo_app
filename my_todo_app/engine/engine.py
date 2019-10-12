#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Implement task management application engine."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import *

from my_todo_app.engine.task import TaskList, Task, TaskDatabase
from my_todo_app.engine.tree import TreeTraversal


class InsertTo(Enum):
    FIRST_SIBLING = 0
    LAST_SIBLING = 1
    FIRST_CHILD = 2
    LAST_CHILD = 3


class _TrySelect(Enum):
    FIRST = 0
    SAME_ID = 1
    NEAR_SORT_KEY = 2


class TaskTreeTraversal(TreeTraversal):
    """Task tree structure traversal."""

    def __init__(self, db: TaskDatabase) -> None:
        super().__init__()
        self._db: TaskDatabase = db

    def children(self, self_: Any) -> List[Any]:
        self_task: Task = self_
        return self._db.get_tasks(parent_task_id=self_task.id)

    def parent(self, self_: Any) -> Optional[Any]:
        self_task: Task = self_
        if not self_task.parent_task_id:
            return None
        parent_task = self._db.get_tasks(id_=self_task.parent_task_id)
        if not parent_task:
            return None
        return parent_task[0]


class TaskEngine:
    """Task management application engine."""

    def __init__(self, db: TaskDatabase):
        self._db: TaskDatabase = db
        self._task_traversal: TaskTreeTraversal = TaskTreeTraversal(db)
        self._shows_archive: bool = False
        self._shown_tasklists: List[TaskList] = []
        self._shown_tasks: List[Task] = []
        self._selected_tasklist: Optional[TaskList] = None
        self._selected_task: Optional[Task] = None
        self._update_shown_tasklists()

    @property
    def shows_archive(self) -> bool:
        return self._shows_archive

    @shows_archive.setter
    def shows_archive(self, value) -> None:
        self._shows_archive = value
        self._update_shown_tasks(try_select=_TrySelect.NEAR_SORT_KEY)

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

    def select_tasklist(self, tasklist_id: str) -> None:
        matched_tasklists = [t for t in self._shown_tasklists if t.id == tasklist_id]
        if not matched_tasklists:
            raise RuntimeError('Task list with passed ID is not shown')
        self._selected_tasklist = matched_tasklists[0]
        self._update_shown_tasks(try_select=_TrySelect.FIRST)

    def select_task(self, task_id) -> None:
        matched_tasks = [t for t in self._shown_tasks if t.id == task_id]
        if not matched_tasks:
            raise RuntimeError('Task with passed ID is not shown')
        self._selected_task = matched_tasks[0]

    def add_tasklist(self, name: str) -> None:
        new_tasklist = TaskList(str(uuid.uuid4()), name, 0)
        if self._shown_tasklists:
            sort_key_max = max([t.sort_key for t in self._shown_tasklists])
            new_tasklist.sort_key = sort_key_max + 1
        self._selected_tasklist = new_tasklist
        self._db.upsert_tasklist(new_tasklist)
        self._update_shown_tasklists()

    def edit_selected_tasklist(self, name: str) -> None:
        if self._selected_tasklist is None:
            raise RuntimeError('No task list is selected')

        self._selected_tasklist.name = name
        self._db.upsert_tasklist(self._selected_tasklist)
        self._update_shown_tasklists()

    def remove_selected_tasklist(self) -> None:
        if self._selected_tasklist is None:
            raise RuntimeError('No task list is selected')
        if self._shown_tasks:
            raise RuntimeError('The selected task list is not empty')

        self._db.delete_tasklist(self._selected_tasklist.id)
        self._update_shown_tasklists()

    def can_up_selected_tasklist(self) -> bool:
        if self._selected_tasklist is None:
            return False
        if self._selected_tasklist == self._shown_tasklists[0]:
            return False
        return True

    def up_selected_tasklist(self) -> None:
        if self._selected_tasklist is None:
            raise RuntimeError('No task list is selected')
        if self._selected_tasklist == self._shown_tasklists[0]:
            raise RuntimeError('The selected task list is top one')

        selected_index = self._shown_tasklists.index(self._selected_tasklist)
        if selected_index > 1:
            self._selected_tasklist.sort_key = (self._shown_tasklists[selected_index - 1].sort_key +
                                                self._shown_tasklists[selected_index - 2].sort_key) / 2
        else:
            self._selected_tasklist.sort_key = self._shown_tasklists[selected_index - 1].sort_key - 1
        self._db.upsert_tasklist(self._selected_tasklist)
        self._update_shown_tasklists()

    def can_down_selected_tasklist(self) -> bool:
        if self._selected_tasklist is None:
            return False
        if self._selected_tasklist == self._shown_tasklists[-1]:
            return False
        return True

    def down_selected_tasklist(self) -> None:
        if self._selected_tasklist is None:
            raise RuntimeError('No task list is selected')
        if self._selected_tasklist == self._shown_tasklists[-1]:
            raise RuntimeError('The selected task list is bottom one')

        selected_index = self._shown_tasklists.index(self._selected_tasklist)
        if selected_index < len(self.shown_tasklists) - 2:
            self._selected_tasklist.sort_key = (self._shown_tasklists[selected_index + 1].sort_key +
                                                self._shown_tasklists[selected_index + 2].sort_key) / 2
        else:
            self._selected_tasklist.sort_key = self._shown_tasklists[selected_index + 1].sort_key + 1
        self._db.upsert_tasklist(self._selected_tasklist)
        self._update_shown_tasklists()

    def add_task(self, name: Optional[str] = None, to: InsertTo = InsertTo.FIRST_SIBLING) -> None:
        if self._selected_tasklist is None:
            raise RuntimeError('No task list is selected')

        id_ = str(uuid.uuid4())
        list_id = self._selected_tasklist.id
        timestamp = int(datetime.now().timestamp())
        new_task = Task(id_, list_id, '', '', '', '', False, False, timestamp, timestamp, 0, 0)
        if name is not None:
            new_task.name = name

        if self._selected_task:
            if to == InsertTo.FIRST_SIBLING or to == InsertTo.LAST_SIBLING:
                new_task.parent_task_id = self._selected_task.parent_task_id
            elif to == InsertTo.FIRST_CHILD or to == InsertTo.LAST_CHILD:
                new_task.parent_task_id = self._selected_task.id

        self_task = self._selected_task if self._selected_task is not None else self._db.get_first_task()
        if self_task is None:
            pass
        elif to == InsertTo.FIRST_SIBLING:
            first_sibling = self._db.get_first_task(parent_task_id=self_task.parent_task_id)
            prev_of_that = self._db.get_last_task(sort_key_before=first_sibling.sort_key)
            if prev_of_that is not None:
                new_task.sort_key = (prev_of_that.sort_key + first_sibling.sort_key) / 2
            else:
                new_task.sort_key = first_sibling.sort_key - 1
        elif to == InsertTo.LAST_SIBLING:
            last_sibling = self._db.get_last_task(parent_task_id=self_task.parent_task_id)
            next_of_that = self._db.get_first_task(sort_key_after=last_sibling.sort_key)
            if next_of_that is not None:
                new_task.sort_key = (last_sibling.sort_key + next_of_that.sort_key) / 2
            else:
                new_task.sort_key = last_sibling.sort_key + 1
        elif to == InsertTo.FIRST_CHILD:
            next_of_selected = self._db.get_first_task(sort_key_after=self_task.sort_key)
            if next_of_selected is not None:
                new_task.sort_key = (self_task.sort_key + next_of_selected.sort_key) / 2
            else:
                new_task.sort_key = self_task.sort_key + 1
        elif to == InsertTo.LAST_CHILD:
            next_sibling = self._db.get_first_task(parent_task_id=self_task.parent_task_id,
                                                   sort_key_after=self_task.sort_key)
            last_child = self._db.get_last_task(parent_task_id=self_task.id)
            if next_sibling is not None:
                if last_child is not None:
                    new_task.sort_key = (last_child.sort_key + next_sibling.sort_key) / 2
                else:
                    new_task.sort_key = (self_task.sort_key + next_sibling.sort_key) / 2
            elif last_child is not None:
                new_task.sort_key = last_child.sort_key + 1
            else:
                new_task.sort_key = self_task.sort_key + 1

        self._selected_task = new_task
        self._db.upsert_task(self._selected_task)
        self._update_shown_tasks(try_select=_TrySelect.SAME_ID)

    def edit_selected_task(self, name: Optional[str] = None, memo: Optional[str] = None,
                           completed: Optional[bool] = None) -> None:
        if self._selected_task is None:
            raise RuntimeError('No task is selected')

        if name is not None:
            self._selected_task.name = name
        if memo is not None:
            self.selected_task.memo = memo
        if completed is not None:
            self._selected_task.completed = completed
            self._selected_task.completed_at = int(datetime.now().timestamp())
        self._selected_task.updated_at = int(datetime.now().timestamp())
        self._db.upsert_task(self._selected_task)
        self._update_shown_tasks(try_select=_TrySelect.SAME_ID)

    def can_archive_selected_task(self) -> bool:
        if self._selected_task is None:
            return False
        if self._selected_task.archived:
            return False
        return True

    def archive_selected_task(self) -> None:
        if not self.can_archive_selected_task():
            raise RuntimeError('Can not archive selected task and its descendants')

        target_tasks: List[Task] = self._task_traversal.descendants_and_self(self._selected_task)
        for target_task in target_tasks:
            if target_task.archived:
                continue
            target_task.archived = True
            target_task.archived_at = int(datetime.now().timestamp())
            self._db.upsert_task(target_task)

        self._update_shown_tasks(try_select=_TrySelect.NEAR_SORT_KEY)

    def can_unarchive_selected_task(self) -> bool:
        if self._selected_task is None:
            return False
        if not self._selected_task.archived:
            return False
        ancestors: List[Task] = self._task_traversal.ancestors(self._selected_task)
        for ancestor in ancestors:
            if ancestor.archived:
                return False
        return True

    def unarchive_selected_task(self):
        if not self.can_unarchive_selected_task():
            raise RuntimeError('Can not unarchive selected task and its descendants')

        target_tasks: List[Task] = self._task_traversal.descendants_and_self(self._selected_task)
        for target_task in target_tasks:
            if not target_task.archived:
                continue
            target_task.archived = False
            self._db.upsert_task(target_task)

        self._update_shown_tasks(try_select=_TrySelect.SAME_ID)

    def can_move_selected_task(self) -> bool:
        if self._selected_task is None:
            return False
        if self._selected_task.parent_task_id:
            return False
        return True

    def move_selected_task(self, list_id: str):
        if self._selected_task is None:
            raise RuntimeError('No task is selected')
        if self._selected_task.parent_task_id:
            raise RuntimeError('Can not move sub task only')

        self._move_task(self._selected_task, list_id)
        self._update_shown_tasks(try_select=_TrySelect.NEAR_SORT_KEY)

    def _move_task(self, task: Task, list_id: str):
        task.list_id = list_id
        task.updated_at = int(datetime.now().timestamp())
        self._db.upsert_task(task)

        children = self._db.get_tasks(parent_task_id=task.id)
        for child in children:
            self._move_task(child, list_id)

    def remove_selected_task(self):
        if self._selected_task is None:
            raise RuntimeError('No task is selected')

        target_tasks: List[Task] = self._task_traversal.descendants_and_self(self._selected_task)
        for target_task in target_tasks:
            self._db.delete_task(target_task.id)

        self._update_shown_tasks(try_select=_TrySelect.NEAR_SORT_KEY)

    def can_up_selected_task(self) -> bool:
        if self._selected_task is None:
            return False
        first_index = self._get_first_sibling_task_index()
        if self._selected_task == self._shown_tasks[first_index]:
            return False
        return True

    def up_selected_task(self) -> None:
        if self._selected_task is None:
            raise RuntimeError('No task is selected')
        first_index = self._get_first_sibling_task_index()
        if self._selected_task == self._shown_tasks[first_index]:
            raise RuntimeError('The selected task is bottom one')

        prev_index = self._get_prev_sibling_task_index()
        assert prev_index is not None
        next_index = self._get_next_sibling_task_index()

        src_sort_key_after = self._shown_tasks[prev_index].sort_key
        if next_index is None:
            src_sort_key_before = self._selected_task.sort_key + 1
        else:
            src_sort_key_before = self._shown_tasks[next_index].sort_key

        if prev_index > 0:
            dest_sort_key_after = self._shown_tasks[prev_index - 1].sort_key
        else:
            dest_sort_key_after = self._shown_tasks[prev_index].sort_key - 1
        dest_sort_key_before = self._shown_tasks[prev_index].sort_key

        target_tasks: List[Task] = self._task_traversal.descendants_and_self(self._selected_task)
        for target_task in target_tasks:
            sort_key_ratio = (target_task.sort_key - src_sort_key_after) / (src_sort_key_before - src_sort_key_after)
            target_task.sort_key = dest_sort_key_after + (dest_sort_key_before - dest_sort_key_after) * sort_key_ratio
            self._db.upsert_task(target_task)

        self._update_shown_tasks(try_select=_TrySelect.SAME_ID)

    def can_down_selected_task(self) -> bool:
        if self._selected_task is None:
            return False
        last_index = self._get_last_sibling_task_index()
        if self._selected_task == self._shown_tasks[last_index]:
            return False
        return True

    def down_selected_task(self) -> None:
        if self._selected_task is None:
            raise RuntimeError('No task is selected')
        last_index = self._get_last_sibling_task_index()
        if self._selected_task == self._shown_tasks[last_index]:
            raise RuntimeError('The selected task is top one')

        next_index = self._get_next_sibling_task_index()
        assert next_index is not None
        prev_index = self._get_prev_sibling_task_index()

        if prev_index is None:
            src_sort_key_after = self._selected_task.sort_key - 1
        else:
            src_sort_key_after = self._shown_tasks[prev_index].sort_key
        src_sort_key_before = self._shown_tasks[next_index].sort_key

        dest_sort_key_after = self._shown_tasks[next_index].sort_key
        if next_index < len(self.shown_tasks) - 1:
            dest_sort_key_before = self._shown_tasks[next_index + 1].sort_key
        else:
            dest_sort_key_before = self._shown_tasks[next_index].sort_key + 1

        target_tasks: List[Task] = self._task_traversal.descendants_and_self(self._selected_task)
        for target_task in target_tasks:
            sort_key_ratio = (target_task.sort_key - src_sort_key_after) / (src_sort_key_before - src_sort_key_after)
            target_task.sort_key = dest_sort_key_after + (dest_sort_key_before - dest_sort_key_after) * sort_key_ratio
            self._db.upsert_task(target_task)

        self._update_shown_tasks(try_select=_TrySelect.SAME_ID)

    def _get_first_sibling_task_index(self):
        first_index = 0
        for i in range(0, len(self._shown_tasks)):
            if self._shown_tasks[i].parent_task_id == self._selected_task.parent_task_id:
                first_index = i
                break
        return first_index

    def _get_last_sibling_task_index(self):
        last_index = len(self._shown_tasks) - 1
        for i in range(len(self._shown_tasks) - 1, -1, -1):
            if self._shown_tasks[i].parent_task_id == self._selected_task.parent_task_id:
                last_index = i
                break
        return last_index

    def _get_next_sibling_task_index(self) -> Optional[int]:
        next_index: Optional[int] = None
        found = False
        for i in range(0, len(self._shown_tasks)):
            if self._shown_tasks[i] == self._selected_task:
                found = True
            elif self._shown_tasks[i].parent_task_id == self._selected_task.parent_task_id:
                if found:
                    next_index = i
                    break
        return next_index

    def _get_prev_sibling_task_index(self) -> Optional[int]:
        prev_index: Optional[int] = None
        for i in range(0, len(self._shown_tasks)):
            if self._shown_tasks[i] == self._selected_task:
                break
            elif self._shown_tasks[i].parent_task_id == self._selected_task.parent_task_id:
                prev_index = i
        return prev_index

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
        self._update_shown_tasks(try_select=_TrySelect.SAME_ID)

    def _update_shown_tasks(self, try_select: _TrySelect):
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
                    if not self._selected_task or try_select == _TrySelect.FIRST:
                        task_to_select_is_fixed = True
                    elif try_select == _TrySelect.SAME_ID:
                        if task.id == self.selected_task.id:
                            task_to_select_is_fixed = True
                    elif try_select == _TrySelect.NEAR_SORT_KEY:
                        if self._selected_task.sort_key <= task.sort_key:
                            task_to_select_is_fixed = True
                    else:
                        assert False
            self._selected_task = task_to_select
        else:
            self._shown_tasks = []
            self._selected_task = None
