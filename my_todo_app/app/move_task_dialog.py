#! /usr/bin/env python
# -*- coding: utf-8-unix -*-

"""Implement dialog to specify parameters for Move-Task operation."""

import tkinter as tk
from tkinter import ttk
from typing import *

from my_todo_app.app.window_utility import show_dialog, get_center_geometry
from my_todo_app.engine.task import TaskList


class MoveTaskDialog:
    """Dialog to specify parameters for Move-Task operation."""

    def __init__(self, parent: tk.Tk, task_lists: List[TaskList]) -> None:
        assert task_lists
        self._parent: tk.Tk = parent
        self._task_lists: List[TaskList] = task_lists
        self.result_task_list: Optional[TaskList] = task_lists[0]
        self._ok: bool = False
        self._layout()

    def _layout(self) -> None:
        margin = 4
        margin_half = 2

        self._dialog = tk.Toplevel(self._parent)
        self._dialog.title('Move Task')
        self._dialog.geometry(get_center_geometry(self._parent, 300, 200))
        self._dialog.resizable(False, False)
        self._dialog.grid_rowconfigure(0, weight=1)
        self._dialog.grid_rowconfigure(1, weight=0)
        self._dialog.grid_columnconfigure(0, weight=1)
        self._dialog.bind('<Any-KeyPress>', self._key_pressed)

        top_frame = ttk.Frame(self._dialog)
        top_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W),
                       padx=(margin, margin), pady=(margin, margin_half))
        top_frame.grid_rowconfigure(0, weight=1)
        top_frame.grid_columnconfigure(0, weight=1)
        top_frame.grid_columnconfigure(1, weight=0)

        self._task_list_listbox = tk.Listbox(top_frame, exportselection=False, width=15)
        self._task_list_listbox.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W),
                                     padx=(margin, margin_half), pady=(margin_half, margin))
        index = 0
        for task_list in self._task_lists:
            label = task_list.name if task_list.name else 'Empty'
            self._task_list_listbox.insert(index, label)
            index += 1
        self._task_list_listbox.selection_set(0)
        self._task_list_listbox.focus_set()

        task_list_listbox_scrollbar = ttk.Scrollbar(top_frame, orient=tk.VERTICAL,
                                                    command=self._task_list_listbox.yview)
        self._task_list_listbox['yscrollcommand'] = task_list_listbox_scrollbar.set
        task_list_listbox_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        bottom_frame = ttk.Frame(self._dialog)
        bottom_frame.grid(row=1, column=0, sticky=(tk.N, tk.S, tk.E),
                          padx=(margin, margin), pady=(margin_half, margin))
        bottom_frame.grid_rowconfigure(0, weight=1)
        bottom_frame.grid_columnconfigure(0, weight=1)

        ok_button = ttk.Button(bottom_frame, text='OK', command=self._ok_button_clicked)
        ok_button.grid(row=0, column=0, sticky=tk.E)

        cancel_button = ttk.Button(bottom_frame, text='Cancel', command=self._cancel_button_clicked)
        cancel_button.grid(row=0, column=1, sticky=tk.E)

    def _key_pressed(self, event) -> None:
        if event.keysym == 'Return':
            self._on_ok()
        elif event.keysym == 'Escape':
            self._on_cancel()

    def _ok_button_clicked(self) -> None:
        self._on_ok()

    def _on_ok(self) -> None:
        self.result_task_list = self._get_selected_task_list()
        self._ok = True
        self._dialog.destroy()

    def _get_selected_task_list(self) -> Optional[TaskList]:
        selected_task_list: Optional[TaskList] = None
        selected_indices = self._task_list_listbox.curselection()
        if selected_indices:
            selected_task_list = self._task_lists[selected_indices[0]]
        return selected_task_list

    def _cancel_button_clicked(self) -> None:
        self._on_cancel()

    def _on_cancel(self) -> None:
        self._dialog.destroy()

    def show_dialog(self) -> bool:
        show_dialog(self._dialog, self._parent)
        return self._ok
