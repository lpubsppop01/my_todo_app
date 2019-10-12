#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Implement dialog to specify the task list parameters to add or edit."""

import copy
import tkinter as tk
import uuid
from tkinter import ttk
import tkinter.messagebox as ttk_messagebox
from typing import *

from my_todo_app.app.theme import Theme
from my_todo_app.app.window_utility import show_dialog, get_center_geometry
from my_todo_app.engine.task import TaskList


class AddOrEditTaskListDialog:
    """Dialog to specify the task list parameters to add or edit."""

    def __init__(self, parent: tk.Tk, theme: Theme, item_to_edit: Optional[TaskList] = None) -> None:
        self._parent: tk.Tk = parent
        self._theme: Theme = theme
        if item_to_edit is not None:
            self.result_tasklist: TaskList = copy.deepcopy(item_to_edit)
            self._edits: bool = True
        else:
            self.result_tasklist: TaskList = TaskList(str(uuid.uuid4()), '', 0)
            self._edits: bool = False
        self._ok: bool = False
        self._layout()

    def _layout(self) -> None:
        self._dialog = tk.Toplevel(self._parent)
        self._dialog.title('Edit Task List' if self._edits else 'Add Task List')
        self._dialog.geometry(get_center_geometry(self._parent, 300, 70))
        self._dialog.resizable(False, False)
        self._dialog.grid_rowconfigure(0, weight=1)
        self._dialog.grid_rowconfigure(1, weight=0)
        self._dialog.grid_columnconfigure(0, weight=1)
        self._dialog.bind('<Any-KeyPress>', self._key_pressed)

        STYLE_FRAME = 'dialog.TFrame'
        STYLE_LABEL = 'dialog.TLabel'

        style = ttk.Style(self._dialog)
        self._theme.configure(style)
        self._theme.configure_main_frame(style, STYLE_FRAME)
        style.configure(STYLE_LABEL, font=self._theme.normal_font,
                        foreground=self._theme.main_foreground, background=self._theme.main_background)

        dialog_frame = ttk.Frame(self._dialog, style=STYLE_FRAME)
        dialog_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        dialog_frame.grid_rowconfigure(0, weight=1)
        dialog_frame.grid_columnconfigure(0, weight=1)

        top_frame = ttk.Frame(dialog_frame, style=STYLE_FRAME)
        top_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W),
                       padx=(self._theme.margin, self._theme.margin),
                       pady=(self._theme.margin, self._theme.margin_half))
        top_frame.grid_rowconfigure(0, weight=1)
        top_frame.grid_columnconfigure(0, weight=0)
        top_frame.grid_columnconfigure(1, weight=1)

        name_label = ttk.Label(top_frame, text='Name', style=STYLE_LABEL)
        name_label.grid(row=0, column=0, sticky=tk.W, padx=(0, self._theme.margin_double))

        self._name_entry = tk.Entry(top_frame, font=self._theme.normal_font, borderwidth=0)
        self._name_entry.grid(row=0, column=1, sticky=(tk.E, tk.W))
        self._name_entry.insert(0, self.result_tasklist.name)
        self._name_entry.focus_set()

        bottom_frame = ttk.Frame(dialog_frame, style=STYLE_FRAME)
        bottom_frame.grid(row=1, column=0, sticky=(tk.N, tk.S, tk.E),
                          padx=(self._theme.margin, self._theme.margin),
                          pady=(self._theme.margin_half, self._theme.margin))
        bottom_frame.grid_rowconfigure(0, weight=1)
        bottom_frame.grid_columnconfigure(0, weight=1)

        ok_button = tk.Button(bottom_frame, text='OK', width=self._theme.text_button_width, relief=tk.FLAT,
                              command=self._ok_button_clicked)
        ok_button.grid(row=0, column=0, sticky=tk.E)

        cancel_button = tk.Button(bottom_frame, text='Cancel', width=self._theme.text_button_width, relief=tk.FLAT,
                                  command=self._cancel_button_clicked)
        cancel_button.grid(row=0, column=1, sticky=tk.E, padx=(self._theme.margin, 0))

    def _key_pressed(self, event) -> None:
        if event.keysym == 'Return':
            self._on_ok()
        elif event.keysym == 'Escape':
            self._on_cancel()

    def _ok_button_clicked(self) -> None:
        self._on_ok()

    def _on_ok(self) -> None:
        self.result_tasklist.name = self._name_entry.get()
        if self.result_tasklist.name:
            self._ok = True
            self._dialog.destroy()
        else:
            ttk_messagebox.showerror('Error', 'Name is required.')

    def _cancel_button_clicked(self) -> None:
        self._on_cancel()

    def _on_cancel(self) -> None:
        self._dialog.destroy()

    def show_dialog(self) -> bool:
        show_dialog(self._dialog, self._parent)
        return self._ok
