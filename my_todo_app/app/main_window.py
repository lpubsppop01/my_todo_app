#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""The main window."""

import math
import os
import tkinter as tk
import tkinter.messagebox as ttk_messagebox
import tkinter.scrolledtext as tk_scrolledtext
import webbrowser
from tkinter import ttk
from typing import *

import markdown2
from tk_html_widgets import HTMLScrolledText

from my_todo_app.app.config import Config
from my_todo_app.app.movetask_dialog import MoveTaskDialog
from my_todo_app.app.tasklist_dialog import AddOrEditTaskListDialog
from my_todo_app.app.theme import Theme
from my_todo_app.engine.engine import TaskEngine, InsertTo
from my_todo_app.engine.task import TaskDatabase


class MainWindow:
    """A main window."""

    def __init__(self, db: TaskDatabase, config: Config, images_path: str) -> None:
        self._engine: TaskEngine = TaskEngine(db)
        self._config: Config = config
        self._images_path = images_path
        self._layout()
        self._update_tasklist_treeview()

    def _layout(self) -> None:
        self._root = tk.Tk()
        self._root.title('My Todo')
        self._root.geometry(self._config.main_window_geometry)
        if self._config.main_window_zoomed:
            self._root.state('zoomed')
        self._root.grid_rowconfigure(0, weight=1)
        self._root.grid_columnconfigure(0, weight=0)
        self._root.grid_columnconfigure(1, weight=0, minsize=700)
        self._root.grid_columnconfigure(2, weight=1)
        self._root.bind('<Any-KeyPress>', self._key_pressed)
        self._root.bind("<Configure>", self._configure)

        STYLE_TASKLIST_TREEVIEW = 'tasklist_treeview.Treeview'
        STYLE_TASK_TREEVIEW = 'task_treeview.Treeview'
        STYLE_LEFT_FRAME = 'left.TFrame'
        STYLE_CENTER_FRAME = 'center.TFrame'
        STYLE_RIGHT_FRAME = 'right.TFrame'

        style = ttk.Style(self._root)
        self._theme = Theme()
        self._theme.fontfamily = self._config.theme_fontfamily
        self._theme.monospaced_fontfamily = self._config.theme_monospaced_fontfamily
        self._theme.configure_style(style)
        self._theme.configure_accent_treeview_style(style, STYLE_TASKLIST_TREEVIEW, self._theme.normal_font)
        self._theme.configure_main_treeview_style(style, STYLE_TASK_TREEVIEW, self._theme.normal_font)
        self._theme.configure_accent_frame_style(style, STYLE_LEFT_FRAME)
        self._theme.configure_main_frame_style(style, STYLE_CENTER_FRAME)
        self._theme.configure_sub_frame_style(style, STYLE_RIGHT_FRAME)

        # Avoid Treeview bug: https://bugs.python.org/issue36468
        # def fixed_map(option):
        #     return [e for e in style.map('Treeview', query_opt=option) if e[:2] != ('!disabled', '!selected')]
        # style.map('Treeview', foreground=fixed_map('foreground'), background=fixed_map('background'))

        self._images = dict()

        def add_image(key: str, filename: str):
            path = os.path.join(self._images_path, filename)
            self._images[key] = tk.PhotoImage(file=path)

        add_image('icon_add_accent', 'ic_add_circle_white_24dp.png')
        add_image('icon_edit_accent', 'ic_create_white_24dp.png')
        add_image('icon_delete_accent', 'ic_delete_white_24dp.png')
        add_image('icon_arrow_up_accent', 'ic_arrow_upward_white_24dp.png')
        add_image('icon_arrow_down_accent', 'ic_arrow_downward_white_24dp.png')
        add_image('icon_add_main', 'ic_add_circle_black_24dp.png')
        add_image('icon_insert_as_last_child_main', 'myicon_insert_as_last_child_24x24.png')
        add_image('icon_delete_main', 'ic_delete_black_24dp.png')
        add_image('icon_move_to_list_main', 'myicon_move_to_list_24x24.png')
        add_image('icon_check_main', 'myicon_check_24x24.png')
        add_image('icon_uncheck_main', 'myicon_uncheck_24x24.png')
        add_image('icon_archive_main', 'myicon_archive_24x24.png')
        add_image('icon_unarchive_main', 'myicon_unarchive_24x24.png')
        add_image('icon_arrow_up_main', 'ic_arrow_upward_black_24dp.png')
        add_image('icon_arrow_down_main', 'ic_arrow_downward_black_24dp.png')
        add_image('icon_archive_is_visible_main', 'myicon_archive_is_visible_24x24.png')
        add_image('icon_archive_is_invisible_main', 'myicon_archive_is_invisible_24x24.png')
        add_image('icon_github', 'appbar.social.github.octocat.solid.png')
        add_image('icon_my_todo', 'myicon_my_todo_16x16.png')

        self._root.iconphoto(True, self._images['icon_my_todo'])

        left_frame = ttk.Frame(self._root, style=STYLE_LEFT_FRAME)
        left_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        left_frame.grid_rowconfigure(1, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)

        left_top_frame = ttk.Frame(left_frame, style=STYLE_LEFT_FRAME)
        left_top_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.W),
                            padx=(self._theme.margin, self._theme.margin),
                            pady=(self._theme.margin, self._theme.margin_half))

        add_tasklist_button = tk.Button(left_top_frame, image=self._images['icon_add_accent'],
                                        **self._theme.image_button_kwargs(),
                                        **self._theme.accent_color_kwargs(),
                                        command=self._add_tasklist_button_clicked)
        add_tasklist_button.grid(row=0, column=0, sticky=tk.W)

        self._edit_tasklist_button = tk.Button(left_top_frame, image=self._images['icon_edit_accent'],
                                               **self._theme.image_button_kwargs(),
                                               **self._theme.accent_color_kwargs(),
                                               command=self._edit_tasklist_button_clicked)
        self._edit_tasklist_button.grid(row=0, column=1, sticky=tk.E, padx=(self._theme.margin, 0))

        self._remove_tasklist_button = tk.Button(left_top_frame, image=self._images['icon_delete_accent'],
                                                 **self._theme.image_button_kwargs(),
                                                 **self._theme.accent_color_kwargs(),
                                                 command=self._remove_tasklist_button_clicked)
        self._remove_tasklist_button.grid(row=0, column=2, sticky=tk.E, padx=(self._theme.margin, 0))

        self._up_tasklist_button = tk.Button(left_top_frame, image=self._images['icon_arrow_up_accent'],
                                             **self._theme.image_button_kwargs(),
                                             **self._theme.accent_color_kwargs(),
                                             command=self._up_tasklist_button_clicked)
        self._up_tasklist_button.grid(row=0, column=3, sticky=tk.E, padx=(self._theme.margin, 0))

        self._down_tasklist_button = tk.Button(left_top_frame, image=self._images['icon_arrow_down_accent'],
                                               **self._theme.image_button_kwargs(),
                                               **self._theme.accent_color_kwargs(),
                                               command=self._down_tasklist_button_clicked)
        self._down_tasklist_button.grid(row=0, column=4, sticky=tk.E, padx=(self._theme.margin, 0))

        self._tasklist_treeview = ttk.Treeview(left_frame, show='tree', style=STYLE_TASKLIST_TREEVIEW)
        self._tasklist_treeview.column('#0', width=200)
        self._tasklist_treeview.grid(row=1, column=0, sticky=(tk.N, tk.S, tk.E, tk.W),
                                     pady=(self._theme.margin_half, self._theme.margin))
        self._tasklist_treeview.bind('<<TreeviewSelect>>', self._tasklist_treeview_selected)

        center_frame = ttk.Frame(self._root, style=STYLE_CENTER_FRAME)
        center_frame.grid(row=0, column=1, sticky=(tk.N, tk.S, tk.E, tk.W))
        center_frame.grid_rowconfigure(0, weight=0)
        center_frame.grid_rowconfigure(1, weight=1)
        center_frame.grid_columnconfigure(0, weight=1)
        center_frame.grid_columnconfigure(1, weight=0)

        center_top_frame = ttk.Frame(center_frame, style=STYLE_CENTER_FRAME)
        center_top_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.N, tk.S, tk.E, tk.W),
                              padx=(self._theme.margin, self._theme.margin),
                              pady=(self._theme.margin, self._theme.margin_half))
        center_top_frame.grid_columnconfigure(8, weight=1)

        self._add_task_button = tk.Button(center_top_frame, image=self._images['icon_add_main'],
                                          **self._theme.image_button_kwargs(),
                                          **self._theme.main_color_kwargs(),
                                          command=self._add_task_button_clicked)
        self._add_task_button.grid(row=0, column=0, sticky=tk.E)

        self._add_child_task_button = tk.Button(center_top_frame, image=self._images['icon_insert_as_last_child_main'],
                                                **self._theme.image_button_kwargs(),
                                                **self._theme.main_color_kwargs(),
                                                command=self._add_child_task_button_clicked)
        self._add_child_task_button.grid(row=0, column=1, sticky=tk.E, padx=(self._theme.margin, 0))

        self._remove_task_button = tk.Button(center_top_frame, image=self._images['icon_delete_main'],
                                             **self._theme.image_button_kwargs(),
                                             **self._theme.main_color_kwargs(),
                                             command=self._remove_task_button_clicked)
        self._remove_task_button.grid(row=0, column=2, sticky=tk.E, padx=(self._theme.margin, 0))

        self._complete_task_button = tk.Button(center_top_frame, image=self._images['icon_check_main'],
                                               **self._theme.image_button_kwargs(),
                                               **self._theme.main_color_kwargs(),
                                               command=self._complete_task_button_clicked)
        self._complete_task_button.grid(row=0, column=3, sticky=tk.E, padx=(self._theme.margin, 0))

        self._archive_task_button = tk.Button(center_top_frame, image=self._images['icon_archive_main'],
                                              **self._theme.image_button_kwargs(),
                                              **self._theme.main_color_kwargs(),
                                              command=self._archive_task_button_clicked)
        self._archive_task_button.grid(row=0, column=4, sticky=tk.E, padx=(self._theme.margin, 0))

        self._move_task_button = tk.Button(center_top_frame, image=self._images['icon_move_to_list_main'],
                                           **self._theme.image_button_kwargs(),
                                           **self._theme.main_color_kwargs(),
                                           command=self._move_task_button_clicked)
        self._move_task_button.grid(row=0, column=5, sticky=tk.E, padx=(self._theme.margin, 0))

        self._up_task_button = tk.Button(center_top_frame, image=self._images['icon_arrow_up_main'],
                                         **self._theme.image_button_kwargs(),
                                         **self._theme.main_color_kwargs(),
                                         command=self._up_task_button_clicked)
        self._up_task_button.grid(row=0, column=6, sticky=tk.E, padx=(self._theme.margin, 0))

        self._down_task_button = tk.Button(center_top_frame, image=self._images['icon_arrow_down_main'],
                                           **self._theme.image_button_kwargs(),
                                           **self._theme.main_color_kwargs(),
                                           command=self._down_task_button_clicked)
        self._down_task_button.grid(row=0, column=7, sticky=tk.E, padx=(self._theme.margin, 0))

        self._toggle_shows_archive_button = tk.Button(center_top_frame,
                                                      image=self._images['icon_archive_is_invisible_main'],
                                                      **self._theme.image_button_kwargs(),
                                                      **self._theme.main_color_kwargs(),
                                                      command=self._toggle_shows_archive_button_clicked)
        self._toggle_shows_archive_button.grid(row=0, column=8, sticky=tk.E)

        self._task_treeview = ttk.Treeview(center_frame, show='tree', style=STYLE_TASK_TREEVIEW)
        self._task_treeview.column('#0', width=300)
        self._task_treeview.tag_configure('completed',
                                          font=self._theme.normal_completed_font)
        self._task_treeview.tag_configure('archived',
                                          foreground=self._theme.main_completed_foreground)
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
        right_top_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W),
                             padx=(self._theme.margin, self._theme.margin),
                             pady=(self._theme.margin, self._theme.margin_half))
        right_top_frame.grid_columnconfigure(3, weight=1)

        self._memo_mode_is_edit: bool = False

        memo_mode_label = tk.Label(right_top_frame, text='Memo', font=self._theme.small_font,
                                   background=self._theme.sub_background)
        memo_mode_label.grid(row=0, column=0, sticky=tk.E)

        self._memo_mode_edit_button = tk.Button(right_top_frame, text='Edit',
                                                **self._theme.text_button_kwargs(),
                                                command=self._memo_mode_edit_button_clicked)
        self._memo_mode_edit_button.grid(row=0, column=1, sticky=tk.E, padx=(self._theme.margin, 0))

        self._memo_mode_render_button = tk.Button(right_top_frame, text='Render',
                                                  **self._theme.text_button_kwargs(),
                                                  command=self._memo_mode_render_button_clicked)
        self._memo_mode_render_button.grid(row=0, column=2, sticky=tk.E)

        open_github_button = tk.Button(right_top_frame,
                                       image=self._images['icon_github'],
                                       **self._theme.image_button_kwargs(),
                                       **self._theme.sub_color_kwargs(),
                                       command=self._open_github_button_clicked)
        open_github_button.grid(row=0, column=3, sticky=tk.E)

        self._task_name_entry = tk.Entry(right_frame, font=self._theme.large_font, borderwidth=0)
        self._task_name_entry.grid(row=1, column=0, sticky=(tk.N, tk.S, tk.E, tk.W),
                                   padx=(self._theme.margin_double, self._theme.margin),
                                   pady=(self._theme.margin, self._theme.margin_half))
        self._task_name_entry.bind("<FocusOut>", self._task_name_entry_focused_out)

        self._task_memo_text = tk_scrolledtext.ScrolledText(right_frame, font=self._theme.normal_monospaced_font,
                                                            borderwidth=0)
        self._task_memo_text_grid_remember = lambda: (
            self._task_memo_text.grid(row=2, column=0, sticky=(tk.N, tk.S, tk.E, tk.W),
                                      padx=(self._theme.margin_double, self._theme.margin),
                                      pady=(self._theme.margin_half, self._theme.margin))
        )
        self._task_memo_text_grid_remember()
        self._task_memo_text.bind("<FocusOut>", self._task_memo_text_focused_out)

        self._task_memo_html_text = HTMLScrolledText(right_frame, borderwidth=0)
        self._task_memo_html_text.html_parser.DEFAULT_TEXT_FONT_FAMILY = self._theme.fontfamily
        self._task_memo_html_text.html_parser.PREFORMATTED_FONT_FAMILY = self._theme.monospaced_fontfamily
        self._task_memo_html_text_grid_remember = lambda: (
            self._task_memo_html_text.grid(row=2, column=0, sticky=(tk.N, tk.S, tk.E, tk.W),
                                           padx=(self._theme.margin_double, self._theme.margin),
                                           pady=(self._theme.margin_half, self._theme.margin))
        )
        self._task_memo_html_text_grid_remember()

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
        if not self._engine.can_move_selected_task():
            ttk_messagebox.showerror('Error', 'Unable to move selected task.')
            return

        candidate_tasklists = [tasklist for tasklist in self._engine.shown_tasklists
                               if tasklist.id != self._engine.selected_task.list_id]

        dialog = MoveTaskDialog(self._root, self._theme, candidate_tasklists)
        if dialog.show_dialog():
            self._engine.move_selected_task(list_id=dialog.result_tasklist.id)
            self._update_task_treeview()

    def _remove_task_button_clicked(self) -> None:
        if self._engine.selected_task is None:
            ttk_messagebox.showerror('Error', 'No task is selected.')
            return

        message = 'Really remove {} and its descendants?'.format(self._engine.selected_task.name)
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

        if self._engine.selected_task.archived:
            self._engine.unarchive_selected_task()
        else:
            self._engine.archive_selected_task()
        self._update_task_treeview()

    def _toggle_shows_archive_button_clicked(self) -> None:
        self._engine.shows_archive = not self._engine.shows_archive

        if self._engine.shows_archive:
            self._toggle_shows_archive_button.config(image=self._images['icon_archive_is_visible_main'])
        else:
            self._toggle_shows_archive_button.config(image=self._images['icon_archive_is_invisible_main'])

        self._update_task_treeview()

    @staticmethod
    def _open_github_button_clicked() -> None:
        webbrowser.open('https://github.com/lpubsppop01/my_todo_app')

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

    def _memo_mode_edit_button_clicked(self) -> None:
        self._memo_mode_is_edit = True
        self._update_task_controls()

    def _memo_mode_render_button_clicked(self) -> None:
        self._task_memo_text_entered()
        self._memo_mode_is_edit = False
        self._update_task_controls()

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

        new_memo = self._task_memo_text.get(1.0, tk.END)[0:-1]  # Remove extra '\n'
        self._engine.edit_selected_task(memo=new_memo)

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
            self._tasklist_treeview.insert('', tk.END, iid=tasklist.id, text=label)
        if self._engine.selected_tasklist:
            self._tasklist_treeview.selection_set(self._engine.selected_tasklist.id)
        self._update_tasklist_controls()
        self._update_task_treeview()

    def _update_tasklist_controls(self) -> None:
        if self._engine.selected_tasklist is not None:
            self._edit_tasklist_button.config(state=tk.NORMAL)
        else:
            self._edit_tasklist_button.config(state=tk.DISABLED)

        if self._engine.selected_tasklist is not None:
            self._remove_tasklist_button.config(state=tk.NORMAL)
        else:
            self._remove_tasklist_button.config(state=tk.DISABLED)

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
            tags: Tuple[str] = tuple()
            if task.completed:
                tags += ('completed',)
            if task.archived:
                tags += ('archived',)
            self._task_treeview.insert(task.parent_task_id, tk.END, iid=task.id, text=label, values=task.id,
                                       open=True, tags=tags)
        if self._engine.selected_task:
            self._task_treeview.selection_set(self._engine.selected_task.id)
        self._update_task_controls()

    def _update_task_controls(self) -> None:
        if self._engine.selected_tasklist is not None:
            self._add_task_button.config(state=tk.NORMAL)
        else:
            self._add_task_button.config(state=tk.DISABLED)

        self._task_name_entry.delete(0, tk.END)
        self._task_memo_text.delete(1.0, tk.END)
        if self._engine.selected_task:
            self._add_child_task_button.config(state=tk.NORMAL)
            self._remove_task_button.config(state=tk.NORMAL)
            self._complete_task_button.config(state=tk.NORMAL)
            self._task_name_entry.config(state=tk.NORMAL)
            self._task_name_entry.insert(tk.END, self._engine.selected_task.name)
            self._task_memo_text.config(state=tk.NORMAL)
            self._task_memo_text.insert(tk.END, self._engine.selected_task.memo)
            html_str = self._markdown_to_html(self._engine.selected_task.memo)
            self._task_memo_html_text.set_html(html_str)
        else:
            self._add_child_task_button.config(state=tk.DISABLED)
            self._remove_task_button.config(state=tk.DISABLED)
            self._complete_task_button.config(state=tk.DISABLED)
            self._task_name_entry.config(state=tk.DISABLED)
            self._task_memo_text.config(state=tk.DISABLED)

        if self._engine.selected_task and self._engine.selected_task.completed:
            self._complete_task_button.config(image=self._images['icon_uncheck_main'])
        else:
            self._complete_task_button.config(image=self._images['icon_check_main'])

        if self._engine.can_move_selected_task():
            self._move_task_button.config(state=tk.NORMAL)
        else:
            self._move_task_button.config(state=tk.DISABLED)

        if self._engine.can_up_selected_task():
            self._up_task_button.config(state=tk.NORMAL)
        else:
            self._up_task_button.config(state=tk.DISABLED)

        if self._engine.can_down_selected_task():
            self._down_task_button.config(state=tk.NORMAL)
        else:
            self._down_task_button.config(state=tk.DISABLED)

        if self._engine.selected_task and self._engine.selected_task.archived:
            self._archive_task_button.config(image=self._images['icon_unarchive_main'])
            if self._engine.can_unarchive_selected_task():
                self._archive_task_button.config(state=tk.NORMAL)
            else:
                self._archive_task_button.config(state=tk.DISABLED)
        else:
            self._archive_task_button.config(image=self._images['icon_archive_main'])
            if self._engine.can_archive_selected_task():
                self._archive_task_button.config(state=tk.NORMAL)
            else:
                self._archive_task_button.config(state=tk.DISABLED)

        if self._memo_mode_is_edit:
            self._memo_mode_edit_button.config(**self._theme.accent_selected_kwargs())
            self._memo_mode_render_button.config(**self._theme.accent_color_kwargs())
            self._task_memo_text_grid_remember()
            self._task_memo_html_text.grid_forget()
        else:
            self._memo_mode_edit_button.config(**self._theme.accent_color_kwargs())
            self._memo_mode_render_button.config(**self._theme.accent_selected_kwargs())
            self._task_memo_text.grid_forget()
            self._task_memo_html_text_grid_remember()

    def _markdown_to_html(self, markdown_str: str) -> str:
        # Generate HTMl
        # - Set font size
        # - Replace <h1> ～ <h6> to <p> to disable bold
        html_str = markdown2.markdown(markdown_str, extras=['cuddled-lists'])
        html_str = html_str.replace('<p', '<p style="font-size: {}px"'.format(self._theme.normal_fontsize))
        html_str = html_str.replace('<li', '<li style="font-size: {}px"'.format(self._theme.normal_fontsize))
        html_str = html_str.replace('<a', '<a style="font-size: {}px"'.format(self._theme.normal_fontsize))
        html_str = html_str.replace('<pre', '<pre style="font-size: {}px"'.format(self._theme.normal_fontsize))
        html_str = html_str.replace('<h1', '<p style="font-size: {}px"'.format(self._theme.large_fontsize))
        html_str = html_str.replace('</h1>', '</p>')
        delta_fontsize = self._theme.large_fontsize - self._theme.normal_fontsize
        h2_fontsize = int(math.floor(self._theme.normal_fontsize + delta_fontsize * 2.0 / 3.0))
        html_str = html_str.replace('<h2', '<p style="font-size: {}px"'.format(h2_fontsize))
        html_str = html_str.replace('</h2>', '</p>')
        h3_fontsize = int(math.floor(self._theme.normal_fontsize + delta_fontsize * 1.0 / 3.0))
        html_str = html_str.replace('<h3', '<p style="font-size: {}px"'.format(h3_fontsize))
        html_str = html_str.replace('</h3>', '</p>')
        html_str = html_str.replace('<h4', '<p style="font-size: {}px"'.format(self._theme.normal_fontsize))
        html_str = html_str.replace('</h4>', '</p>')
        html_str = html_str.replace('<h5', '<p style="font-size: {}px"'.format(self._theme.normal_fontsize))
        html_str = html_str.replace('</h5>', '</p>')
        html_str = html_str.replace('<h6', '<p style="font-size: {}px"'.format(self._theme.normal_fontsize))
        html_str = html_str.replace('</h6>', '</p>')
        html_str = '<html><body>{}</body></html>'.format(html_str)
        return html_str

    # noinspection PyUnusedLocal
    def _configure(self, event):
        self._config.main_window_zoomed = 'zoomed' in self._root.state()
        if not self._config.main_window_zoomed:
            self._config.main_window_geometry = self._root.geometry()
        self._config.save()

    def show(self) -> None:
        self._root.mainloop()
