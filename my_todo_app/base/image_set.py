#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Implement image set base class that provides access to resource images."""

import os
import sys
import tkinter as tk

from my_todo_app.base.lazy import Lazy


class ImageSet:
    """Image set base class that provides access to resource images."""

    def __init__(self, dir_name: str) -> None:
        self._dir_path = self._get_resource_directory_path(dir_name)

    # noinspection PyProtectedMember
    @staticmethod
    def _get_resource_directory_path(dir_name: str) -> str:
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, dir_name)
        project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        return os.path.join(project_path, dir_name)

    def _get_lazy_image(self, filename: str) -> Lazy[tk.PhotoImage]:
        file_path = os.path.join(self._dir_path, filename)
        return Lazy[tk.PhotoImage](lambda: tk.PhotoImage(file=file_path))
