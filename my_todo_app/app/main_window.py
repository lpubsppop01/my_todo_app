#! /usr/bin/env python
# -*- coding: utf-8-unix -*-

"""The main window."""

import tkinter as tk
import tkinter.messagebox as ttk_messagebox
import tkinter.scrolledtext as tk_scrolledtext
from tkinter import ttk
from typing import *

from my_todo_app.app.task_list_dialog import TaskListDialog
from my_todo_app.engine.task import TaskDatabase, TaskList, Task


class MainWindow:
    """A main window."""

    def __init__(self, db: TaskDatabase):
        self._db: TaskDatabase = db
        self._shown_task_lists: List[TaskList] = []
        self._shown_tasks: List[Task] = []
        self._last_selected_task_list: Optional[TaskList] = None
        self._last_selected_task: Optional[Task] = None
        self._layout()
        self._update_task_list_listbox()

    def _layout(self):
        margin = 4
        margin_half = 2
        list_font = 'Sans 21 bold'
        name_font = 'Sans 21 bold'
        memo_font = 'Sans 12 bold'

        self._root = tk.Tk()
        self._root.title('My Todo')
        self._root.geometry('1024x600')
        self._root.grid_rowconfigure(0, weight=1)
        self._root.grid_columnconfigure(0, weight=0)
        self._root.grid_columnconfigure(1, weight=0)
        self._root.grid_columnconfigure(2, weight=1)

        # style = ttk.Style(self._root)
        # style.theme_use('classic')
        # style.configure('Test.TLabel', background='brown')

        left_frame = ttk.Frame(self._root)
        left_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        left_frame.grid_rowconfigure(1, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)

        left_top_frame = ttk.Frame(left_frame)
        left_top_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E),
                            padx=(margin, margin_half), pady=(margin, margin_half))

        add_task_list_button = ttk.Button(left_top_frame, text='Add',
                                          command=self._add_task_list_button_clicked)
        add_task_list_button.grid(row=0, column=0, sticky=tk.E)

        remove_task_list_button = ttk.Button(left_top_frame, text='Edit',
                                             command=self._edit_task_list_button_clicked)
        remove_task_list_button.grid(row=0, column=1, sticky=tk.E)

        remove_task_list_button = ttk.Button(left_top_frame, text='Remove',
                                             command=self._remove_task_list_button_clicked)
        remove_task_list_button.grid(row=0, column=2, sticky=tk.E)

        self._task_list_listbox = tk.Listbox(left_frame, exportselection=False, width=15, font=list_font)
        self._task_list_listbox.grid(row=1, column=0, sticky=(tk.N, tk.S, tk.E, tk.W),
                                     padx=(margin, margin_half), pady=(margin_half, margin))
        self._task_list_listbox.bind('<<ListboxSelect>>', self._task_list_listbox_selected)

        center_frame = ttk.Frame(self._root)
        center_frame.grid(row=0, column=1, sticky=(tk.N, tk.S, tk.E, tk.W))
        center_frame.grid_rowconfigure(1, weight=1)
        center_frame.grid_columnconfigure(0, weight=1)

        center_top_frame = ttk.Frame(center_frame)
        center_top_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E),
                              padx=(margin_half, margin_half), pady=(margin, margin_half))

        add_task_button = ttk.Button(center_top_frame, text='Add')
        add_task_button.grid(row=0, column=0, sticky=tk.E)

        add_task_button = ttk.Button(center_top_frame, text='Up')
        add_task_button.grid(row=0, column=1, sticky=tk.E)

        add_task_button = ttk.Button(center_top_frame, text='Down')
        add_task_button.grid(row=0, column=2, sticky=tk.E)

        self._task_listbox = tk.Listbox(center_frame, exportselection=False, width=18, font=list_font)
        self._task_listbox.grid(row=1, column=0, sticky=(tk.N, tk.S, tk.E, tk.W),
                                padx=(margin_half, margin_half), pady=(margin_half, margin))
        self._task_listbox.bind('<<ListboxSelect>>', self._task_listbox_selected)

        right_frame = ttk.Frame(self._root)
        right_frame.grid(row=0, column=2, sticky=(tk.N, tk.S, tk.E, tk.W))
        right_frame.grid_rowconfigure(2, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        right_top_frame = ttk.Frame(right_frame)
        right_top_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E),
                             padx=(margin_half, margin), pady=(margin, margin_half))

        move_task_button = ttk.Button(right_top_frame, text='Move')
        move_task_button.grid(row=0, column=0, sticky=tk.E)

        remove_task_button = ttk.Button(right_top_frame, text='Remove')
        remove_task_button.grid(row=0, column=1, sticky=tk.E)

        self._name_entry = ttk.Entry(right_frame, font=name_font)
        self._name_entry.grid(row=1, column=0, sticky=(tk.N, tk.S, tk.E, tk.W),
                              padx=(margin_half, margin), pady=(margin, margin_half))

        self._memo_text = tk_scrolledtext.ScrolledText(right_frame, font=memo_font)
        self._memo_text.grid(row=2, column=0, sticky=(tk.N, tk.S, tk.E, tk.W),
                             padx=(margin_half, margin), pady=(margin_half, margin))

    def _add_task_list_button_clicked(self):
        dialog = TaskListDialog(self._root)
        if dialog.show_dialog():
            if self._shown_task_lists:
                sort_key_max = max([task_list.sort_key for task_list in self._shown_task_lists])
                dialog.result_task_list.sort_key = sort_key_max + 1
            self._db.upsert_task_list(dialog.result_task_list)
            self._update_task_list_listbox()

    def _edit_task_list_button_clicked(self):
        if self._last_selected_task_list is None:
            ttk_messagebox.showerror('Error', 'Task list is not selected.')
            return

        dialog = TaskListDialog(self._root, self._last_selected_task_list)
        if dialog.show_dialog():
            self._last_selected_task_list = dialog.result_task_list
            self._db.upsert_task_list(dialog.result_task_list)
            self._update_task_list_listbox()

    def _remove_task_list_button_clicked(self):
        if self._last_selected_task_list is None:
            ttk_messagebox.showerror('Error', 'Task list is not selected.')
            return

        message = 'Really remove {}?'.format(self._last_selected_task_list.name)
        if ttk_messagebox.askokcancel('Confirm', message):
            self._db.delete_task_list(self._last_selected_task_list.id)
            self._update_task_list_listbox()

    # noinspection PyUnusedLocal
    def _task_list_listbox_selected(self, event):
        self._update_task_listbox()

    # noinspection PyUnusedLocal
    def _task_listbox_selected(self, event):
        self._update_task_controls()

    def _update_task_list_listbox(self):
        self._shown_task_lists = self._db.get_task_lists()
        self._task_list_listbox.delete(0, tk.END)
        index = 0
        index_to_select = 0
        for task_list in self._shown_task_lists:
            self._task_list_listbox.insert(index, task_list.name)
            if self._last_selected_task_list and self._last_selected_task_list.id == task_list.id:
                index_to_select = index
            index += 1
        if self._shown_task_lists:
            self._task_list_listbox.selection_set(index_to_select)
        self._update_task_listbox()

    def _update_task_listbox(self):
        selected_task_list: Optional[TaskList] = None
        selected_indices = self._task_list_listbox.curselection()
        if selected_indices:
            selected_task_list = self._shown_task_lists[selected_indices[0]]
        if selected_task_list == self._last_selected_task_list:
            return

        self._shown_tasks = self._db.get_tasks(parent_id=selected_task_list.id)
        self._last_selected_task_list = selected_task_list
        self._task_listbox.delete(0, tk.END)
        index = 0
        index_to_select = 0
        for task in self._shown_tasks:
            self._task_listbox.insert(index, task.name)
            if self._last_selected_task and self._last_selected_task.id == task.id:
                index_to_select = index
            index += 1
        if self._shown_tasks:
            self._task_listbox.selection_set(index_to_select)
        self._update_task_controls()

    def _update_task_controls(self):
        selected_task: Optional[Task] = None
        selected_indices = self._task_listbox.curselection()
        if selected_indices:
            selected_task = self._shown_tasks[selected_indices[0]]
        if selected_task == self._last_selected_task:
            return

        self._last_selected_task = selected_task
        self._name_entry.delete(0, tk.END)
        self._memo_text.delete(1.0, tk.END)
        if self._last_selected_task:
            self._name_entry.config(state=tk.NORMAL)
            self._name_entry.insert(tk.END, selected_task.name)
            self._memo_text.config(state=tk.NORMAL)
            self._memo_text.insert(tk.END, selected_task.name)
        else:
            self._name_entry.config(state=tk.DISABLED)
            self._memo_text.config(state=tk.DISABLED)

    def show(self):
        self._root.mainloop()
