#! /usr/bin/env python
# -*- coding: utf-8-unix -*-

"""The main window."""

import tkinter as tk
import tkinter.messagebox as ttk_messagebox
import tkinter.scrolledtext as tk_scrolledtext
from tkinter import ttk

from my_todo_app.app.movetask_dialog import MoveTaskDialog
from my_todo_app.app.tasklist_dialog import AddOrEditTaskListDialog
from my_todo_app.app.theme import Theme
from my_todo_app.engine.engine import TaskEngine, InsertTo
from my_todo_app.engine.task import TaskDatabase


class MainWindow:
    """A main window."""

    def __init__(self, db: TaskDatabase) -> None:
        self._engine: TaskEngine = TaskEngine(db)
        self._layout()
        self._update_tasklist_treeview()

    def _layout(self) -> None:
        self._root = tk.Tk()
        self._root.title('My Todo')
        self._root.geometry('1024x600')
        self._root.grid_rowconfigure(0, weight=1)
        self._root.grid_columnconfigure(0, weight=0)
        self._root.grid_columnconfigure(1, weight=1, minsize=380)
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

        self._up_tasklist_button = tk.Button(left_top_frame, text='Up', width=self._theme.button_width, relief=tk.FLAT,
                                             command=self._up_tasklist_button_clicked)
        self._up_tasklist_button.grid(row=1, column=0, sticky=tk.E, pady=(self._theme.margin, 0))

        self._down_tasklist_button = tk.Button(left_top_frame, text='Down', width=self._theme.button_width,
                                               relief=tk.FLAT, command=self._down_tasklist_button_clicked)
        self._down_tasklist_button.grid(row=1, column=1, sticky=tk.E,
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

        add_child_task_button = tk.Button(center_top_frame, text='Add Child', width=self._theme.button_width,
                                          relief=tk.FLAT, command=self._add_child_task_button_clicked)
        add_child_task_button.grid(row=0, column=1, sticky=tk.E, padx=(self._theme.margin, 0))

        remove_task_button = tk.Button(center_top_frame, text='Remove', width=self._theme.button_width, relief=tk.FLAT,
                                       command=self._remove_task_button_clicked)
        remove_task_button.grid(row=0, column=2, sticky=tk.E, padx=(self._theme.margin, 0))

        self._complete_task_button = tk.Button(center_top_frame, text='Complete', width=self._theme.button_width,
                                               relief=tk.FLAT, command=self._complete_task_button_clicked)
        self._complete_task_button.grid(row=0, column=3, sticky=tk.E, padx=(self._theme.margin, 0))

        move_task_button = tk.Button(center_top_frame, text='Move', width=self._theme.button_width, relief=tk.FLAT,
                                     command=self._move_task_button_clicked)
        move_task_button.grid(row=0, column=4, sticky=tk.E, padx=(self._theme.margin, 0))

        self._up_task_button = tk.Button(center_top_frame, text='Up', width=self._theme.button_width, relief=tk.FLAT,
                                         command=self._up_task_button_clicked)
        self._up_task_button.grid(row=1, column=0, sticky=tk.E, pady=(self._theme.margin, 0))

        self._down_task_button = tk.Button(center_top_frame, text='Down', width=self._theme.button_width,
                                           relief=tk.FLAT, command=self._down_task_button_clicked)
        self._down_task_button.grid(row=1, column=1, sticky=tk.E,
                                    padx=(self._theme.margin, 0), pady=(self._theme.margin, 0))

        self._archive_task_button = tk.Button(center_top_frame, text='Archive', width=self._theme.button_width,
                                              relief=tk.FLAT, command=self._archive_task_button_clicked)
        self._archive_task_button.grid(row=1, column=2, sticky=tk.E,
                                       padx=(self._theme.margin, 0), pady=(self._theme.margin, 0))

        self._shows_archive_checkbox_value = tk.BooleanVar()
        self._shows_archive_checkbox = tk.Checkbutton(center_top_frame, text='Show Archive',
                                                      onvalue=True, offvalue=False,
                                                      variable=self._shows_archive_checkbox_value,
                                                      background=self._theme.main_background,
                                                      command=self._shows_archive_checkbox_changed)
        self._shows_archive_checkbox.grid(row=1, column=3, columnspan=2, sticky=tk.W,
                                          padx=(self._theme.margin, 0), pady=(self._theme.margin, 0))

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

    def _add_tasklist_button_clicked(self) -> None:
        dialog = AddOrEditTaskListDialog(self._root, self._theme)
        if dialog.show_dialog():
            self._engine.add_tasklist(dialog.result_tasklist.name)
            self._update_tasklist_treeview()

    def _edit_tasklist_button_clicked(self) -> None:
        if self._engine.selected_tasklist is None:
            ttk_messagebox.showerror('Error', 'No task list is selected.')
            return

        dialog = AddOrEditTaskListDialog(self._root, self._theme, self._engine.selected_tasklist)
        if dialog.show_dialog():
            self._engine.edit_selected_tasklist(dialog.result_tasklist.name)
            self._update_tasklist_treeview()

    def _remove_tasklist_button_clicked(self) -> None:
        if self._engine.selected_tasklist is None:
            ttk_messagebox.showerror('Error', 'No task list is selected.')
            return
        if self._engine.shown_tasks:
            ttk_messagebox.showerror('Error', 'The selected task list is not empty.')
            return

        message = 'Really remove {}?'.format(self._engine.selected_tasklist.name)
        if ttk_messagebox.askokcancel('Confirm', message):
            self._engine.remove_selected_tasklist()
            self._update_tasklist_treeview()

    def _up_tasklist_button_clicked(self) -> None:
        if not self._engine.can_up_selected_tasklist():
            ttk_messagebox.showerror('Error', 'Unable to up selected task list.')
            return

        self._engine.up_selected_tasklist()
        self._update_tasklist_treeview()

    def _down_tasklist_button_clicked(self) -> None:
        if not self._engine.can_down_selected_tasklist():
            ttk_messagebox.showerror('Error', 'Unable to down selected task list.')
            return

        self._engine.down_selected_tasklist()
        self._update_tasklist_treeview()

    def _add_task_button_clicked(self) -> None:
        if self._engine.selected_tasklist is None:
            ttk_messagebox.showerror('Error', 'No task list is selected.')
            return

        self._engine.add_task()
        self._update_task_treeview()
        self._task_name_entry.focus_set()

    def _add_child_task_button_clicked(self) -> None:
        if self._engine.selected_task is None:
            ttk_messagebox.showerror('Error', 'No task is selected.')
            return

        self._engine.add_task(to=InsertTo.LAST_CHILD)
        self._update_task_treeview()
        self._task_name_entry.focus_set()

    def _move_task_button_clicked(self) -> None:
        if self._engine.selected_task is None:
            ttk_messagebox.showerror('Error', 'No task is selected.')
            return

        candidate_tasklists = [tasklist for tasklist in self._engine.shown_tasklists
                               if tasklist.id != self._engine.selected_task.list_id]

        dialog = MoveTaskDialog(self._root, self._theme, candidate_tasklists)
        if dialog.show_dialog():
            self._engine.edit_selected_task(list_id=dialog.result_tasklist.id)
            self._update_task_treeview()

    def _remove_task_button_clicked(self) -> None:
        if self._engine.selected_task is None:
            ttk_messagebox.showerror('Error', 'No task is selected.')
            return

        message = 'Really remove {}?'.format(self._engine.selected_task.name)
        if ttk_messagebox.askokcancel('Confirm', message):
            self._engine.remove_selected_task()
            self._update_task_treeview()

    def _complete_task_button_clicked(self) -> None:
        if self._engine.selected_task is None:
            ttk_messagebox.showerror('Error', 'No task is selected.')
            return

        self._engine.edit_selected_task(completed=not self._engine.selected_task.completed)
        self._update_task_treeview()

    def _up_task_button_clicked(self) -> None:
        if not self._engine.can_up_selected_task():
            ttk_messagebox.showerror('Error', 'Unable to up selected task.')
            return

        self._engine.up_selected_task()
        self._update_task_treeview()

    def _down_task_button_clicked(self) -> None:
        if not self._engine.can_down_selected_task():
            ttk_messagebox.showerror('Error', 'Unable to down selected task.')
            return

        self._engine.down_selected_task()
        self._update_task_treeview()

    def _archive_task_button_clicked(self) -> None:
        if self._engine.selected_task is None:
            ttk_messagebox.showerror('Error', 'No task is selected.')
            return

        self._engine.edit_selected_task(archived=not self._engine.selected_task.archived)
        self._update_task_treeview()

    def _shows_archive_checkbox_changed(self) -> None:
        self._engine.shows_archive = self._shows_archive_checkbox_value.get()
        self._update_task_treeview()

    def _key_pressed(self, event) -> None:
        if event.widget == self._task_name_entry:
            self._task_name_entry_key_pressed(event)
        if event.widget == self._task_memo_text:
            self._task_memo_text_key_pressed(event)

    def _task_name_entry_key_pressed(self, event) -> None:
        if event.keysym == 'Return':
            self._task_name_entry_entered()
        elif event.keysym == 'Escape':
            self._task_name_entry.delete(0, tk.END)
            if self._engine.selected_task:
                self._task_name_entry.insert(tk.END, self._engine.selected_task.name)

    # noinspection PyUnusedLocal
    def _task_name_entry_focused_out(self, event) -> None:
        self._task_name_entry_entered()

    def _task_name_entry_entered(self) -> None:
        if self._engine.selected_task is None:
            ttk_messagebox.showerror('Error', 'No task is selected.')
            return

        self._engine.edit_selected_task(name=self._task_name_entry.get())
        self._update_task_treeview()

    def _task_memo_text_key_pressed(self, event) -> None:
        if event.keysym == 'Return':
            self._task_memo_text_entered()
        elif event.keysym == 'Escape':
            self._task_memo_text.delete(1.0, tk.END)
            if self._engine.selected_task:
                self._task_memo_text.insert(tk.END, self._engine.selected_task.memo)

    # noinspection PyUnusedLocal
    def _task_memo_text_focused_out(self, event) -> None:
        self._task_memo_text_entered()

    def _task_memo_text_entered(self) -> None:
        if self._engine.selected_task is None:
            ttk_messagebox.showerror('Error', 'No task is selected.')
            return

        self._engine.edit_selected_task(memo=self._task_memo_text.get(1.0, tk.END))
        self._update_task_treeview()

    # noinspection PyUnusedLocal
    def _tasklist_treeview_selected(self, event) -> None:
        for tasklist_id in self._tasklist_treeview.selection():
            self._engine.select_tasklist(tasklist_id)
            break
        self._update_tasklist_controls()
        self._update_task_treeview()

    # noinspection PyUnusedLocal
    def _task_treeview_selected(self, event) -> None:
        for task_id in self._task_treeview.selection():
            self._engine.select_task(task_id)
            break
        self._update_task_controls()

    def _update_tasklist_treeview(self) -> None:
        self._tasklist_treeview.delete(*self._tasklist_treeview.get_children())
        for tasklist in self._engine.shown_tasklists:
            label = tasklist.name if tasklist.name else 'Empty'
            self._tasklist_treeview.insert('', tk.END, iid=tasklist.id, text=label, tags=('undone',))
        if self._engine.selected_tasklist:
            self._tasklist_treeview.selection_set(self._engine.selected_tasklist.id)
        self._update_tasklist_controls()
        self._update_task_treeview()

    def _update_tasklist_controls(self) -> None:
        if self._engine.can_up_selected_tasklist():
            self._up_tasklist_button.config(state=tk.NORMAL)
        else:
            self._up_tasklist_button.config(state=tk.DISABLED)

        if self._engine.can_down_selected_tasklist():
            self._down_tasklist_button.config(state=tk.NORMAL)
        else:
            self._down_tasklist_button.config(state=tk.DISABLED)

    def _update_task_treeview(self) -> None:
        self._task_treeview.delete(*self._task_treeview.get_children())
        for task in self._engine.shown_tasks:
            label = task.name if task.name else 'Empty'
            self._task_treeview.insert('', tk.END, iid=task.id, text=label, values=task.id)
        if self._engine.selected_task:
            self._task_treeview.selection_set(self._engine.selected_task.id)
        self._update_task_controls()

    def _update_task_controls(self) -> None:
        self._task_name_entry.delete(0, tk.END)
        self._task_memo_text.delete(1.0, tk.END)
        if self._engine.selected_task:
            self._task_name_entry.config(state=tk.NORMAL)
            self._task_name_entry.insert(tk.END, self._engine.selected_task.name)
            self._task_memo_text.config(state=tk.NORMAL)
            self._task_memo_text.insert(tk.END, self._engine.selected_task.memo)
        else:
            self._task_name_entry.config(state=tk.DISABLED)
            self._task_memo_text.config(state=tk.DISABLED)

        if self._engine.selected_task and self._engine.selected_task.completed:
            self._complete_task_button.config(text='Uncomplete')
        else:
            self._complete_task_button.config(text='Complete')

        if self._engine.can_up_selected_task():
            self._up_task_button.config(state=tk.NORMAL)
        else:
            self._up_task_button.config(state=tk.DISABLED)

        if self._engine.can_down_selected_task():
            self._down_task_button.config(state=tk.NORMAL)
        else:
            self._down_task_button.config(state=tk.DISABLED)

        if self._engine.selected_task and self._engine.selected_task.archived:
            self._archive_task_button.config(text='Unarchive')
        else:
            self._archive_task_button.config(text='Archive')

    def show(self) -> None:
        self._root.mainloop()
