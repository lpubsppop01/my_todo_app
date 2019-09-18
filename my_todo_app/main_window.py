#! /usr/bin/env python
# -*- coding: utf-8-unix -*-

"""The main window implementation."""

import tkinter as tk
import tkinter.scrolledtext as tkst
from tkinter import ttk

from my_todo_app.task import TaskDatabase


class MainWindow:
    """A main window."""

    def __init__(self, db: TaskDatabase):
        self._db = db

        self._root = tk.Tk()
        self._root.title('My Todo')
        self._root.geometry('1024x600')
        self._root.grid_rowconfigure(0, weight=1)
        self._root.grid_columnconfigure(0, weight=1)

        frame = ttk.Frame(self._root)
        frame.grid()

        text = tkst.ScrolledText(self._root)
        text.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))

    def show(self):
        self._root.mainloop()
