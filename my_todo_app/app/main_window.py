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

from my_todo_app.app.move_task_dialog import MoveTaskDialog
from my_todo_app.app.add_or_edit_task_list_dialog import AddOrEditTaskListDialog
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
        button_width = 5
        task_list_listbox_font = 'Arial 12 bold'
        task_treeview_fontname = 'Arial'
        task_treeview_fontsize = 15
        task_treeview_rowheight = 15 * 3
        name_font = 'Arial 21 bold'
        memo_font = 'Arial 15'

        self._root = tk.Tk()
        self._root.title('My Todo')
        self._root.geometry('1024x600')
        self._root.grid_rowconfigure(0, weight=1)
        self._root.grid_columnconfigure(0, weight=0)
        self._root.grid_columnconfigure(1, weight=0)
        self._root.grid_columnconfigure(2, weight=1)
        self._root.bind('<Any-KeyPress>', self._key_pressed)

        # style = ttk.Style(self._root)
        # style.theme_use('classic')
        # style.configure('Test.TLabel', background='brown')

        style = ttk.Style(self._root)
        style.configure("Treeview", font=(task_treeview_fontname, task_treeview_fontsize))
        style.configure('Treeview', rowheight=task_treeview_rowheight)

        left_frame = ttk.Frame(self._root)
        left_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        left_frame.grid_rowconfigure(1, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)

        left_top_frame = ttk.Frame(left_frame)
        left_top_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E),
                            padx=(margin, margin_half), pady=(margin, margin_half))

        add_task_list_button = ttk.Button(left_top_frame, text='Add', width=button_width,
                                          command=self._add_task_list_button_clicked)
        add_task_list_button.grid(row=0, column=0, sticky=tk.E)

        up_task_list_button = ttk.Button(left_top_frame, text='Up', width=button_width)
        up_task_list_button.grid(row=0, column=1, sticky=tk.E)

        down_task_list_button = ttk.Button(left_top_frame, text='Down', width=button_width)
        down_task_list_button.grid(row=0, column=2, sticky=tk.E)

        remove_task_list_button = ttk.Button(left_top_frame, text='Edit', width=button_width,
                                             command=self._edit_task_list_button_clicked)
        remove_task_list_button.grid(row=0, column=3, sticky=tk.E)

        remove_task_list_button = ttk.Button(left_top_frame, text='Remove', width=button_width,
                                             command=self._remove_task_list_button_clicked)
        remove_task_list_button.grid(row=0, column=4, sticky=tk.E)

        self._task_list_listbox = tk.Listbox(left_frame, exportselection=False, width=15, font=task_list_listbox_font)
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

        add_task_button = ttk.Button(center_top_frame, text='Add', width=button_width,
                                     command=self._add_task_button_clicked)
        add_task_button.grid(row=0, column=0, sticky=tk.E)

        up_task_button = ttk.Button(center_top_frame, text='Up', width=button_width)
        up_task_button.grid(row=0, column=1, sticky=tk.E)

        down_task_button = ttk.Button(center_top_frame, text='Down', width=button_width)
        down_task_button.grid(row=0, column=2, sticky=tk.E)

        self._task_treeview = ttk.Treeview(center_frame, show='tree')
        self._task_treeview.column('#0', width=300)
        self._task_treeview.grid(row=1, column=0, sticky=(tk.N, tk.S, tk.E, tk.W),
                                 padx=(margin_half, margin_half), pady=(margin_half, margin))
        self._task_treeview.bind('<<TreeviewSelect>>', self._task_treeview_selected)

        right_frame = ttk.Frame(self._root)
        right_frame.grid(row=0, column=2, sticky=(tk.N, tk.S, tk.E, tk.W))
        right_frame.grid_rowconfigure(2, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        right_top_frame = ttk.Frame(right_frame)
        right_top_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E),
                             padx=(margin_half, margin), pady=(margin, margin_half))

        move_task_button = ttk.Button(right_top_frame, text='Move', width=button_width,
                                      command=self._move_task_button_clicked)
        move_task_button.grid(row=0, column=0, sticky=tk.E)

        remove_task_button = ttk.Button(right_top_frame, text='Remove', width=button_width,
                                        command=self._remove_task_button_clicked)
        remove_task_button.grid(row=0, column=1, sticky=tk.E)

        self._task_name_entry = ttk.Entry(right_frame, font=name_font)
        self._task_name_entry.grid(row=1, column=0, sticky=(tk.N, tk.S, tk.E, tk.W),
                                   padx=(margin_half, margin), pady=(margin, margin_half))
        self._task_name_entry.bind("<FocusOut>", self._task_name_entry_focused_out)

        self._task_memo_text = tk_scrolledtext.ScrolledText(right_frame, font=memo_font)
        self._task_memo_text.grid(row=2, column=0, sticky=(tk.N, tk.S, tk.E, tk.W),
                                  padx=(margin_half, margin), pady=(margin_half, margin))

    def _add_task_list_button_clicked(self):
        dialog = AddOrEditTaskListDialog(self._root)
        if dialog.show_dialog():
            if self._shown_task_lists:
                sort_key_max = max([task_list.sort_key for task_list in self._shown_task_lists])
                dialog.result_task_list.sort_key = sort_key_max + 1
            self._db.upsert_task_list(dialog.result_task_list)
            self._update_task_list_listbox()

    def _edit_task_list_button_clicked(self):
        if self._last_selected_task_list is None:
            ttk_messagebox.showerror('Error', 'No task list is selected.')
            return

        dialog = AddOrEditTaskListDialog(self._root, self._last_selected_task_list)
        if dialog.show_dialog():
            self._last_selected_task_list = dialog.result_task_list
            self._db.upsert_task_list(dialog.result_task_list)
            self._update_task_list_listbox()

    def _remove_task_list_button_clicked(self):
        if self._last_selected_task_list is None:
            ttk_messagebox.showerror('Error', 'No task list is selected.')
            return

        message = 'Really remove {}?'.format(self._last_selected_task_list.name)
        if ttk_messagebox.askokcancel('Confirm', message):
            self._db.delete_task_list(self._last_selected_task_list.id)
            self._update_task_list_listbox()

    def _add_task_button_clicked(self):
        if self._last_selected_task_list is None:
            ttk_messagebox.showerror('Error', 'No task list is selected.')
            return

        id_ = str(uuid.uuid4())
        parent_id = self._last_selected_task_list.id
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

        candidate_task_lists = [task_list for task_list in self._shown_task_lists
                                if task_list.id != self._last_selected_task.parent_id]

        dialog = MoveTaskDialog(self._root, candidate_task_lists)
        if dialog.show_dialog():
            self._last_selected_task.parent_id = dialog.result_task_list.id
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
    def _task_list_listbox_selected(self, event):
        self._last_selected_task = None
        self._update_task_treeview()

    # noinspection PyUnusedLocal
    def _task_treeview_selected(self, event):
        self._update_task_controls()

    def _update_task_list_listbox(self):
        self._shown_task_lists = self._db.get_task_lists()
        self._task_list_listbox.delete(0, tk.END)
        index = 0
        index_to_select = 0
        for task_list in self._shown_task_lists:
            label = task_list.name if task_list.name else 'Empty'
            self._task_list_listbox.insert(index, label)
            if self._last_selected_task_list and self._last_selected_task_list.sort_key > task_list.sort_key:
                index_to_select += 1
            index += 1
        if self._shown_task_lists:
            index_to_select = min(index_to_select, len(self._shown_task_lists) - 1)
            self._task_list_listbox.selection_set(index_to_select)
        self._update_task_treeview()

    def _update_task_treeview(self):
        self._last_selected_task_list = self._get_selected_task_list()
        self._task_treeview.delete(*self._task_treeview.get_children())
        if self._last_selected_task_list:
            self._shown_tasks = self._db.get_tasks(parent_id=self._last_selected_task_list.id)
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

    def _get_selected_task_list(self) -> Optional[TaskList]:
        selected_task_list: Optional[TaskList] = None
        selected_indices = self._task_list_listbox.curselection()
        if selected_indices:
            selected_task_list = self._shown_task_lists[selected_indices[0]]
        return selected_task_list

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
            selected_task = [task for task in self._shown_tasks if task.id == task_id][0]
        return selected_task

    def show(self):
        self._root.mainloop()
