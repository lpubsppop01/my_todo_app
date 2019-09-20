#! /usr/bin/env python
# -*- coding: utf-8-unix -*-

"""Functions for window manipulation."""

import tkinter as tk
from typing import *


def get_center_geometry(master: Any, width: int, height: int) -> str:
    master_x = master.winfo_x()
    master_y = master.winfo_y()
    master_width = master.winfo_width()
    master_height = master.winfo_height()
    x = master_x + int(master_width / 2) - int(width / 2)
    y = master_y + int(master_height / 2) - int(height / 2)
    return '{}x{}+{}+{}'.format(width, height, x, y)


def show_dialog(dialog: tk.Toplevel, parent: Any) -> None:
    dialog.focus_set()
    dialog.transient(parent)
    dialog.grab_set()
    parent.wait_window(dialog)
