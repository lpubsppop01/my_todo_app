#! /usr/bin/env python
# -*- coding: utf-8-unix -*-

"""The main window."""

import tkinter as tk
import tkinter.messagebox as ttk_messagebox
import tkinter.scrolledtext as tk_scrolledtext
import uuid
from datetime import datetime
from tkinter import ttk
from typing import *

from my_todo_app.app.movetask_dialog import MoveTaskDialog
from my_todo_app.app.tasklist_dialog import AddOrEditTaskListDialog
from my_todo_app.app.theme import Theme
from my_todo_app.engine.task import TaskDatabase, TaskList, Task


class MainWindow:
    """A main window."""

    def __init__(self, db: TaskDatabase):
        self._db: TaskDatabase = db
        self._shown_tasklists: List[TaskList] = []
        self._shown_tasks: List[Task] = []
        self._last_selected_tasklist: Optional[TaskList] = None
        self._last_selected_task: Optional[Task] = None
        self._layout()
        self._update_tasklist_treeview()

    def _layout(self):
        self._root = tk.Tk()
        self._root.title('My Todo')
        self._root.geometry('1024x600')
        self._root.grid_rowconfigure(0, weight=1)
        self._root.grid_columnconfigure(0, weight=0)
        self._root.grid_columnconfigure(1, weight=0)
        self._root.grid_columnconfigure(2, weight=1)
        self._root.bind('<Any-KeyPress>', self._key_pressed)

        STYLE_TASKLIST_TREEVIEW = 'tasklist_treeview.Treeview'
        STYLE_TASK_TREEVIEW = 'task_treeview.Treeview'
        STYLE_LEFT_FRAME = 'left.TFrame'
        STYLE_CENTER_FRAME = 'center.TFrame'
        STYLE_RIGHT_FRAME = 'right.TFrame'

        style = ttk.Style(self._root)
        self._theme = Theme()
        self._theme.configure(style)
        self._theme.configure_accent_treeview(style, STYLE_TASKLIST_TREEVIEW, self._theme.normal_font)
        self._theme.configure_main_treeview(style, STYLE_TASK_TREEVIEW, self._theme.normal_font)
        self._theme.configure_accent_frame(style, STYLE_LEFT_FRAME)
        self._theme.configure_main_frame(style, STYLE_CENTER_FRAME)
        self._theme.configure_sub_frame(style, STYLE_RIGHT_FRAME)

        # Avoid Treeview bug: https://bugs.python.org/issue36468
        # def fixed_map(option):
        #     return [e for e in style.map('Treeview', query_opt=option) if e[:2] != ('!disabled', '!selected')]
        # style.map('Treeview', foreground=fixed_map('foreground'), background=fixed_map('background'))

        left_frame = ttk.Frame(self._root, style=STYLE_LEFT_FRAME)
        left_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        left_frame.grid_rowconfigure(1, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)

        left_top_frame = ttk.Frame(left_frame, style=STYLE_LEFT_FRAME)
        left_top_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.W),
                            padx=(self._theme.margin, self._theme.margin),
                            pady=(self._theme.margin, self._theme.margin_half))

        add_tasklist_button = tk.Button(left_top_frame, text='Add', width=self._theme.button_width, relief=tk.FLAT,
                                        command=self._add_tasklist_button_clicked)
        add_tasklist_button.grid(row=0, column=0, sticky=tk.E)

        remove_tasklist_button = tk.Button(left_top_frame, text='Edit', width=self._theme.button_width, relief=tk.FLAT,
                                           command=self._edit_tasklist_button_clicked)
        remove_tasklist_button.grid(row=0, column=1, sticky=tk.E, padx=(self._theme.margin, 0))

        remove_tasklist_button = tk.Button(left_top_frame, text='Remove', width=self._theme.button_width,
                                           relief=tk.FLAT, command=self._remove_tasklist_button_clicked)
        remove_tasklist_button.grid(row=0, column=2, sticky=tk.E, padx=(self._theme.margin, 0))

        up_tasklist_button = tk.Button(left_top_frame, text='Up', width=self._theme.button_width, relief=tk.FLAT)
        up_tasklist_button.grid(row=1, column=0, sticky=tk.E, pady=(self._theme.margin, 0))

        down_tasklist_button = tk.Button(left_top_frame, text='Down', width=self._theme.button_width, relief=tk.FLAT)
        down_tasklist_button.grid(row=1, column=1, sticky=tk.E,
                                  padx=(self._theme.margin, 0), pady=(self._theme.margin, 0))

        self._tasklist_treeview = ttk.Treeview(left_frame, show='tree', style=STYLE_TASKLIST_TREEVIEW)
        self._tasklist_treeview.column('#0', width=200)
        self._tasklist_treeview.grid(row=1, column=0, sticky=(tk.N, tk.S, tk.E, tk.W),
                                     pady=(self._theme.margin_half, self._theme.margin))
        self._tasklist_treeview.bind('<<TreeviewSelect>>', self._tasklist_treeview_selected)

        center_frame = ttk.Frame(self._root, style=STYLE_CENTER_FRAME)
        center_frame.grid(row=0, column=1, sticky=(tk.N, tk.S, tk.E, tk.W))
        center_frame.grid_rowconfigure(1, weight=1)
        center_frame.grid_columnconfigure(0, weight=1)

        center_top_frame = ttk.Frame(center_frame, style=STYLE_CENTER_FRAME)
        center_top_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.N, tk.S, tk.W),
                              padx=(self._theme.margin, self._theme.margin),
                              pady=(self._theme.margin, self._theme.margin_half))

        add_task_button = tk.Button(center_top_frame, text='Add', width=self._theme.button_width, relief=tk.FLAT,
                                    command=self._add_task_button_clicked)
        add_task_button.grid(row=0, column=0, sticky=tk.E)

        remove_task_button = tk.Button(center_top_frame, text='Remove', width=self._theme.button_width, relief=tk.FLAT,
                                       command=self._remove_task_button_clicked)
        remove_task_button.grid(row=0, column=1, sticky=tk.E, padx=(self._theme.margin, 0))

        up_task_button = tk.Button(center_top_frame, text='Up', width=self._theme.button_width, relief=tk.FLAT)
        up_task_button.grid(row=0, column=2, sticky=tk.E, padx=(self._theme.margin, 0))

        down_task_button = tk.Button(center_top_frame, text='Down', width=self._theme.button_width, relief=tk.FLAT)
        down_task_button.grid(row=0, column=3, sticky=tk.E, padx=(self._theme.margin, 0))

        move_task_button = tk.Button(center_top_frame, text='Complete', width=self._theme.button_width, relief=tk.FLAT)
        move_task_button.grid(row=1, column=0, sticky=tk.E, pady=(self._theme.margin, 0))

        move_task_button = tk.Button(center_top_frame, text='Move', width=self._theme.button_width, relief=tk.FLAT,
                                     command=self._move_task_button_clicked)
        move_task_button.grid(row=1, column=1, sticky=tk.E, padx=(self._theme.margin, 0), pady=(self._theme.margin, 0))

        self._task_treeview = ttk.Treeview(center_frame, show='tree', style=STYLE_TASK_TREEVIEW)
        self._task_treeview.column('#0', width=300)
        # self._tasklist_treeview.tag_configure('done', background='yellow')
        self._task_treeview.grid(row=1, column=0, sticky=(tk.N, tk.S, tk.E, tk.W),
                                 pady=(self._theme.margin_half, self._theme.margin))
        self._task_treeview.bind('<<TreeviewSelect>>', self._task_treeview_selected)

        task_treeview_scrollbar = tk.Scrollbar(center_frame, orient=tk.VERTICAL,
                                               command=self._task_treeview.yview)
        self._task_treeview['yscrollcommand'] = task_treeview_scrollbar.set
        task_treeview_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S),
                                     pady=(self._theme.margin_half, self._theme.margin))

        right_frame = ttk.Frame(self._root, style=STYLE_RIGHT_FRAME)
        right_frame.grid(row=0, column=2, sticky=(tk.N, tk.S, tk.E, tk.W))
        right_frame.grid_rowconfigure(2, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        right_top_frame = ttk.Frame(right_frame, style=STYLE_RIGHT_FRAME)
        right_top_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.W),
                             padx=(self._theme.margin, self._theme.margin),
                             pady=(self._theme.margin, self._theme.margin_half))

        zoom_up_button = tk.Button(right_top_frame, text='Zoom In', width=self._theme.button_width, relief=tk.FLAT)
        zoom_up_button.grid(row=0, column=0, sticky=tk.E)

        zoom_out_button = tk.Button(right_top_frame, text='Zoom Out', width=self._theme.button_width, relief=tk.FLAT)
        zoom_out_button.grid(row=0, column=1, sticky=tk.E, padx=(self._theme.margin, 0))

        self._task_name_entry = tk.Entry(right_frame, font=self._theme.large_font, borderwidth=0)
        self._task_name_entry.grid(row=1, column=0, sticky=(tk.N, tk.S, tk.E, tk.W),
                                   padx=(self._theme.margin_double, self._theme.margin),
                                   pady=(self._theme.margin, self._theme.margin_half))
        self._task_name_entry.bind("<FocusOut>", self._task_name_entry_focused_out)

        self._task_memo_text = tk_scrolledtext.ScrolledText(right_frame, font=self._theme.normal_font, borderwidth=0)
        self._task_memo_text.grid(row=2, column=0, sticky=(tk.N, tk.S, tk.E, tk.W),
                                  padx=(self._theme.margin_double, self._theme.margin),
                                  pady=(self._theme.margin_half, self._theme.margin))

    def _add_tasklist_button_clicked(self):
        dialog = AddOrEditTaskListDialog(self._root, self._theme)
        if dialog.show_dialog():
            if self._shown_tasklists:
                sort_key_max = max([tasklist.sort_key for tasklist in self._shown_tasklists])
                dialog.result_tasklist.sort_key = sort_key_max + 1
            self._db.upsert_tasklist(dialog.result_tasklist)
            self._update_tasklist_treeview()

    def _edit_tasklist_button_clicked(self):
        if self._last_selected_tasklist is None:
            ttk_messagebox.showerror('Error', 'No task list is selected.')
            return

        dialog = AddOrEditTaskListDialog(self._root, self._theme, self._last_selected_tasklist)
        if dialog.show_dialog():
            self._last_selected_tasklist = dialog.result_tasklist
            self._db.upsert_tasklist(dialog.result_tasklist)
            self._update_tasklist_treeview()

    def _remove_tasklist_button_clicked(self):
        if self._last_selected_tasklist is None:
            ttk_messagebox.showerror('Error', 'No task list is selected.')
            return

        message = 'Really remove {}?'.format(self._last_selected_tasklist.name)
        if ttk_messagebox.askokcancel('Confirm', message):
            self._db.delete_tasklist(self._last_selected_tasklist.id)
            self._update_tasklist_treeview()

    def _add_task_button_clicked(self):
        if self._last_selected_tasklist is None:
            ttk_messagebox.showerror('Error', 'No task list is selected.')
            return

        id_ = str(uuid.uuid4())
        parent_id = self._last_selected_tasklist.id
        timestamp = int(datetime.now().timestamp())
        sort_key = 0.0
        if self._shown_tasks:
            sort_key_max = max([task.sort_key for task in self._shown_tasks])
            sort_key = sort_key_max + 1
        self._last_selected_task = Task(id_, parent_id, '', '', False, timestamp, timestamp, sort_key)
        self._db.upsert_task(self._last_selected_task)
        self._update_task_treeview()
        self._task_name_entry.focus_set()

    def _move_task_button_clicked(self):
        if self._last_selected_task is None:
            ttk_messagebox.showerror('Error', 'No task is selected.')
            return

        candidate_tasklists = [tasklist for tasklist in self._shown_tasklists
                               if tasklist.id != self._last_selected_task.parent_id]

        dialog = MoveTaskDialog(self._root, self._theme, candidate_tasklists)
        if dialog.show_dialog():
            self._last_selected_task.parent_id = dialog.result_tasklist.id
            self._db.upsert_task(self._last_selected_task)
            self._update_task_treeview()

    def _remove_task_button_clicked(self):
        if self._last_selected_task is None:
            ttk_messagebox.showerror('Error', 'No task is selected.')
            return

        message = 'Really remove {}?'.format(self._last_selected_task.name)
        if ttk_messagebox.askokcancel('Confirm', message):
            self._db.delete_task(self._last_selected_task.id)
            self._update_task_treeview()

    def _key_pressed(self, event) -> None:
        if event.widget == self._task_name_entry:
            self._task_name_entry_key_pressed(event)

    def _task_name_entry_key_pressed(self, event):
        if event.keysym == 'Return':
            self._task_name_entry_entered()
        elif event.keysym == 'Escape':
            self._task_name_entry.delete(0, tk.END)
            self._task_name_entry.insert(0, self._last_selected_task.name)

    # noinspection PyUnusedLocal
    def _task_name_entry_focused_out(self, event):
        self._task_name_entry_entered()

    def _task_name_entry_entered(self):
        if self._last_selected_task is None:
            ttk_messagebox.showerror('Error', 'No task is selected.')
            return

        self._last_selected_task.name = self._task_name_entry.get()
        self._db.upsert_task(self._last_selected_task)
        self._update_task_treeview()

    # noinspection PyUnusedLocal
    def _tasklist_treeview_selected(self, event):
        self._last_selected_task = None
        self._update_task_treeview()

    # noinspection PyUnusedLocal
    def _task_treeview_selected(self, event):
        self._update_task_controls()

    def _update_tasklist_treeview(self):
        self._shown_tasklists = self._db.get_tasklists()
        self._tasklist_treeview.delete(*self._tasklist_treeview.get_children())
        item_id_to_select: Optional[str] = None
        item_id_to_select_is_fixed: bool = False
        for tasklist in self._shown_tasklists:
            label = tasklist.name if tasklist.name else 'Empty'
            item_id = self._tasklist_treeview.insert('', tk.END, iid=tasklist.id, text=label, tags=('undone',))
            if not item_id_to_select_is_fixed:
                item_id_to_select = item_id
                if not self._last_selected_tasklist or self._last_selected_tasklist.sort_key <= tasklist.sort_key:
                    item_id_to_select_is_fixed = True
        if item_id_to_select:
            self._tasklist_treeview.selection_set(item_id_to_select)
        self._update_task_treeview()

    def _update_task_treeview(self):
        self._last_selected_tasklist = self._get_selected_tasklist()
        self._task_treeview.delete(*self._task_treeview.get_children())
        if self._last_selected_tasklist:
            self._shown_tasks = self._db.get_tasks(parent_id=self._last_selected_tasklist.id)
            item_id_to_select: Optional[str] = None
            item_id_to_select_is_fixed: bool = False
            for task in self._shown_tasks:
                label = task.name if task.name else 'Empty'
                item_id = self._task_treeview.insert('', tk.END, text=label, values=task.id)
                if not item_id_to_select_is_fixed:
                    item_id_to_select = item_id
                    if not self._last_selected_task or self._last_selected_task.sort_key <= task.sort_key:
                        item_id_to_select_is_fixed = True
            if item_id_to_select:
                self._task_treeview.selection_set(item_id_to_select)
        else:
            self._shown_tasks = []
        self._update_task_controls()

    def _get_selected_tasklist(self) -> Optional[TaskList]:
        selected_tasklist: Optional[TaskList] = None
        for tasklist_id in self._tasklist_treeview.selection():
            selected_tasklist = [t for t in self._shown_tasklists if t.id == tasklist_id][0]
        return selected_tasklist

    def _update_task_controls(self) -> None:
        self._last_selected_task = self._get_selected_task()
        self._task_name_entry.delete(0, tk.END)
        self._task_memo_text.delete(1.0, tk.END)
        if self._last_selected_task:
            self._task_name_entry.config(state=tk.NORMAL)
            self._task_name_entry.insert(tk.END, self._last_selected_task.name)
            self._task_memo_text.config(state=tk.NORMAL)
            self._task_memo_text.insert(tk.END, self._last_selected_task.name)
        else:
            self._task_name_entry.config(state=tk.DISABLED)
            self._task_memo_text.config(state=tk.DISABLED)

    def _get_selected_task(self) -> Optional[Task]:
        selected_task: Optional[Task] = None
        for item_id in self._task_treeview.selection():
            item = self._task_treeview.item(item_id)
            task_id = item['values'][0]
            selected_task = [t for t in self._shown_tasks if t.id == task_id][0]
        return selected_task

    def show(self):
        self._root.mainloop()
