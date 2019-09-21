#! /usr/bin/env python
# -*- coding: utf-8-unix -*-

"""The task list dialog."""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as ttk_messagebox

from my_todo_app.app.window_utility import show_dialog, get_center_geometry


class TaskListDialog:
    """A task list dialog."""

    def __init__(self, parent: tk.Tk) -> None:
        self._parent: tk.Tk = parent
        self._ok: bool = False
        self._layout()

    def _layout(self) -> None:
        margin = 4
        margin_half = 2
        margin_double = 8

        self._dialog = tk.Toplevel(self._parent)
        self._dialog.title('Add Task List')
        self._dialog.geometry(get_center_geometry(self._parent, 300, 70))
        self._dialog.resizable(False, False)
        self._dialog.grid_rowconfigure(0, weight=1)
        self._dialog.grid_rowconfigure(1, weight=0)
        self._dialog.grid_columnconfigure(0, weight=1)
        self._dialog.bind('<Any-KeyPress>', self._key_pressed)

        top_frame = ttk.Frame(self._dialog)
        top_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W),
                       padx=(margin, margin), pady=(margin, margin_half))
        top_frame.grid_rowconfigure(0, weight=1)
        top_frame.grid_columnconfigure(0, weight=0)
        top_frame.grid_columnconfigure(1, weight=1)

        name_label = ttk.Label(top_frame, text='Name')
        name_label.grid(row=0, column=0, sticky=(tk.N, tk.W), padx=(0, margin_double))

        self._name_entry = ttk.Entry(top_frame)
        self._name_entry.grid(row=0, column=1, sticky=(tk.N, tk.E, tk.W))
        self._name_entry.focus_set()

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
        self.result_name = self._name_entry.get()
        if self.result_name:
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
