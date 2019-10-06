#! /usr/bin/env python
# -*- coding: utf-8-unix -*-

"""Implement UI theme that provides tkinter style information."""

import tkinter as tk
from tkinter import ttk
from typing import *


class Theme:
    """UI theme that provides tkinter style information."""

    def __init__(self):
        self._margin = 8
        self._button_width = 8
        self.fontfamily = 'Arial'
        self._small_fontsize = 9
        self._normal_fontsize = 12
        self._large_fontsize = 18
        self._accent_background = 'maroon'
        self._accent_background_selected = 'brown'
        self._accent_foreground = 'white'
        self._accent_foreground_selected = 'white'
        self._main_background = 'whitesmoke'
        self._main_background_selected = 'gainsboro'
        self._main_foreground = 'black'
        self._main_foreground_selected = 'black'
        self._main_done_foreground = 'gray'
        self._sub_background = 'white'
        self._sub_foreground = 'black'

    # noinspection PyMethodMayBeStatic
    def configure(self, style: ttk.Style) -> None:
        style.theme_use('default')
        style.configure('.', indicatorsize='0')  # Hide treeview indicator
        style.configure('.', indicatormargins='10')  # Set inner left margin of treeview

    def configure_accent_treeview(self, style: ttk.Style, key: str, font: Tuple[str, int, str]) -> None:
        style.configure(key,
                        font=font, rowheight=font[1] * 3,
                        relief=tk.FLAT, borderwidth=0, highlightthickness=0,
                        background=self._accent_background,
                        fieldbackground=self._accent_background,
                        foreground=self._accent_foreground)
        style.map(key,
                  foreground=[('selected', self._accent_foreground_selected)],
                  background=[('selected', self._accent_background_selected)])

    def configure_main_treeview(self, style: ttk.Style, key: str, font: Tuple[str, int, str]) -> None:
        style.configure(key,
                        font=font, rowheight=font[1] * 3,
                        relief=tk.FLAT, borderwidth=0, highlightthickness=0,
                        background=self._main_background,
                        fieldbackground=self._main_background,
                        foreground=self._main_foreground)
        style.map(key,
                  foreground=[('selected', self._main_foreground_selected)],
                  background=[('selected', self._main_background_selected)])

    def configure_accent_frame(self, style: ttk.Style, key: str) -> None:
        style.configure(key, background=self._accent_background)

    def configure_main_frame(self, style: ttk.Style, key: str) -> None:
        style.configure(key, background=self._main_background)

    def configure_sub_frame(self, style: ttk.Style, key: str) -> None:
        style.configure(key, background=self._sub_background)

    @property
    def small_font(self) -> Tuple[str, int, str]:
        return self.fontfamily, self._normal_fontsize, ''

    @property
    def normal_font(self) -> Tuple[str, int, str]:
        return self.fontfamily, self._normal_fontsize, ''

    @property
    def normal_completed_font(self) -> Tuple[str, int, str]:
        return self.fontfamily, self._normal_fontsize, 'overstrike'

    @property
    def large_font(self) -> Tuple[str, int, str]:
        return self.fontfamily, self._large_fontsize, ''

    @property
    def margin(self) -> int:
        return self._margin

    @property
    def margin_half(self) -> int:
        return int(self._margin / 2)

    @property
    def margin_double(self) -> int:
        return self._margin * 2

    @property
    def text_button_width(self) -> int:
        return self._button_width

    @property
    def image_button_width(self) -> int:
        return 24

    @property
    def accent_background(self) -> str:
        return self._accent_background

    @property
    def main_background(self) -> str:
        return self._main_background

    @property
    def main_background_selected(self) -> str:
        return self._main_background_selected

    @property
    def main_foreground(self) -> str:
        return self._main_foreground

    @property
    def main_foreground_selected(self) -> str:
        return self._main_foreground_selected

    @property
    def main_completed_foreground(self) -> str:
        return self._main_done_foreground
