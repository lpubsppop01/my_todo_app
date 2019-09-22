#! /usr/bin/env python
# -*- coding: utf-8-unix -*-

"""Implement dialog to specify parameters for Move-Task operation."""

import tkinter as tk
from tkinter import ttk
from typing import *

from my_todo_app.app.theme import Theme
from my_todo_app.app.window_utility import show_dialog, get_center_geometry
from my_todo_app.engine.task import TaskList


class MoveTaskDialog:
    """Dialog to specify parameters for Move-Task operation."""

    def __init__(self, parent: tk.Tk, theme: Theme, tasklists: List[TaskList]) -> None:
        assert tasklists
        self._parent: tk.Tk = parent
        self._theme: Theme = theme
        self._tasklists: List[TaskList] = tasklists
        self.result_tasklist: Optional[TaskList] = tasklists[0]
        self._ok: bool = False
        self._layout()

    def _layout(self) -> None:
        self._dialog = tk.Toplevel(self._parent)
        self._dialog.title('Move Task')
        self._dialog.geometry(get_center_geometry(self._parent, 300, 200))
        self._dialog.resizable(False, False)
        self._dialog.grid_rowconfigure(0, weight=1)
        self._dialog.grid_rowconfigure(1, weight=0)
        self._dialog.grid_columnconfigure(0, weight=1)
        self._dialog.bind('<Any-KeyPress>', self._key_pressed)

        STYLE_FRAME = 'dialog.TFrame'

        style = ttk.Style(self._dialog)
        self._theme.configure(style)
        self._theme.configure_main_frame(style, STYLE_FRAME)

        dialog_frame = ttk.Frame(self._dialog, style=STYLE_FRAME)
        dialog_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        dialog_frame.grid_rowconfigure(0, weight=1)
        dialog_frame.grid_columnconfigure(0, weight=1)

        top_frame = ttk.Frame(dialog_frame, style=STYLE_FRAME)
        top_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W),
                       padx=(0, self._theme.margin),
                       pady=(self._theme.margin, self._theme.margin_half))
        top_frame.grid_rowconfigure(0, weight=1)
        top_frame.grid_columnconfigure(0, weight=1)
        top_frame.grid_columnconfigure(1, weight=0)

        self._tasklist_listbox = tk.Listbox(top_frame, exportselection=False, width=15, relief=tk.FLAT,
                                            font=self._theme.normal_font, activestyle=tk.NONE,
                                            borderwidth=0, highlightthickness=0,
                                            background=self._theme.main_background,
                                            foreground=self._theme.main_foreground,
                                            selectbackground=self._theme.main_background_selected,
                                            selectforeground=self._theme.main_foreground_selected)
        self._tasklist_listbox.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        index = 0
        for tasklist in self._tasklists:
            label = tasklist.name if tasklist.name else 'Empty'
            self._tasklist_listbox.insert(index, label)
            index += 1
        self._tasklist_listbox.selection_set(0)
        self._tasklist_listbox.focus_set()

        tasklist_listbox_scrollbar = tk.Scrollbar(top_frame, orient=tk.VERTICAL,
                                                  command=self._tasklist_listbox.yview)
        self._tasklist_listbox['yscrollcommand'] = tasklist_listbox_scrollbar.set
        tasklist_listbox_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        bottom_frame = ttk.Frame(dialog_frame, style=STYLE_FRAME)
        bottom_frame.grid(row=1, column=0, sticky=(tk.N, tk.S, tk.E),
                          padx=(self._theme.margin, self._theme.margin),
                          pady=(self._theme.margin_half, self._theme.margin))
        bottom_frame.grid_rowconfigure(0, weight=1)
        bottom_frame.grid_columnconfigure(0, weight=1)

        ok_button = tk.Button(bottom_frame, text='OK', width=self._theme.button_width, relief=tk.FLAT,
                              command=self._ok_button_clicked)
        ok_button.grid(row=0, column=0, sticky=tk.E)

        cancel_button = tk.Button(bottom_frame, text='Cancel', width=self._theme.button_width, relief=tk.FLAT,
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
        self.result_tasklist = self._get_selected_tasklist()
        self._ok = True
        self._dialog.destroy()

    def _get_selected_tasklist(self) -> Optional[TaskList]:
        selected_tasklist: Optional[TaskList] = None
        selected_indices = self._tasklist_listbox.curselection()
        if selected_indices:
            selected_tasklist = self._tasklists[selected_indices[0]]
        return selected_tasklist

    def _cancel_button_clicked(self) -> None:
        self._on_cancel()

    def _on_cancel(self) -> None:
        self._dialog.destroy()

    def show_dialog(self) -> bool:
        show_dialog(self._dialog, self._parent)
        return self._ok
