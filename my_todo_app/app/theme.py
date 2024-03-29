#! /usr/bin/env python
# -*- coding: utf-8 -*-

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
        self.monospaced_fontfamily = 'Courier'
        self.small_fontsize = 9
        self.normal_fontsize = 12
        self.large_fontsize = 18
        self._accent_background = 'maroon'
        self._accent_background_selected = 'brown'
        self._accent_foreground = 'silver'
        self._accent_foreground_selected = 'white'
        self._main_background = 'whitesmoke'
        self._main_background_selected = 'gainsboro'
        self._main_foreground = 'black'
        self._main_foreground_selected = 'black'
        self._main_done_foreground = 'gray'
        self._sub_background = 'white'
        self._sub_foreground = 'black'

    # noinspection PyMethodMayBeStatic
    def configure_style(self, style: ttk.Style) -> None:
        style.theme_use('default')
        style.configure('.', indicatorsize='0')  # Hide treeview indicator
        style.configure('.', indicatormargins='10')  # Set inner left margin of treeview

    def configure_accent_treeview_style(self, style: ttk.Style, key: str, font: Tuple[str, int, str]) -> None:
        style.configure(key,
                        font=font, rowheight=font[1] * 3,
                        relief=tk.FLAT, borderwidth=0, highlightthickness=0,
                        background=self._accent_background,
                        fieldbackground=self._accent_background,
                        foreground=self._accent_foreground)
        style.map(key,
                  foreground=[('selected', self._accent_foreground_selected)],
                  background=[('selected', self._accent_background_selected)])

    def configure_main_treeview_style(self, style: ttk.Style, key: str, font: Tuple[str, int, str]) -> None:
        style.configure(key,
                        font=font, rowheight=font[1] * 3,
                        relief=tk.FLAT, borderwidth=0, highlightthickness=0,
                        background=self._main_background,
                        fieldbackground=self._main_background,
                        foreground=self._main_foreground)
        style.map(key,
                  foreground=[('selected', self._main_foreground_selected)],
                  background=[('selected', self._main_background_selected)])

    def configure_accent_frame_style(self, style: ttk.Style, key: str) -> None:
        style.configure(key, background=self._accent_background)

    def configure_main_frame_style(self, style: ttk.Style, key: str) -> None:
        style.configure(key, background=self._main_background)

    def configure_sub_frame_style(self, style: ttk.Style, key: str) -> None:
        style.configure(key, background=self._sub_background)

    def image_button_kwargs(self) -> Dict[str, Any]:
        return {'width': self.image_button_width, 'relief': tk.FLAT}

    def text_button_kwargs(self) -> Dict[str, Any]:
        return {'font': self.small_font, 'width': self.text_button_width, 'relief': tk.FLAT}

    def accent_color_kwargs(self) -> Dict[str, Any]:
        return {'background': self.accent_background,
                'activebackground': self.accent_background,
                'foreground': self.accent_foreground,
                'activeforeground': self.accent_foreground}

    def accent_selected_kwargs(self) -> Dict[str, Any]:
        return {'background': self.accent_background_selected,
                'activebackground': self.accent_background_selected,
                'foreground': self.accent_foreground_selected,
                'activeforeground': self.accent_foreground_selected}

    def main_color_kwargs(self) -> Dict[str, Any]:
        return {'background': self.main_background,
                'activebackground': self.main_background,
                'foreground': self.main_foreground,
                'activeforeground': self.main_foreground}

    def sub_color_kwargs(self) -> Dict[str, Any]:
        return {'background': self.sub_background,
                'activebackground': self.sub_background,
                'foreground': self.sub_foreground,
                'activeforeground': self.sub_foreground}

    @property
    def small_font(self) -> Tuple[str, int, str]:
        return self.fontfamily, self.small_fontsize, ''

    @property
    def normal_font(self) -> Tuple[str, int, str]:
        return self.fontfamily, self.normal_fontsize, ''

    @property
    def normal_completed_font(self) -> Tuple[str, int, str]:
        return self.fontfamily, self.normal_fontsize, 'overstrike'

    @property
    def normal_monospaced_font(self) -> Tuple[str, int, str]:
        return self.monospaced_fontfamily, self.normal_fontsize, ''

    @property
    def large_font(self) -> Tuple[str, int, str]:
        return self.fontfamily, self.large_fontsize, ''

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
    def accent_background_selected(self) -> str:
        return self._accent_background_selected

    @property
    def accent_foreground(self) -> str:
        return self._accent_foreground

    @property
    def accent_foreground_selected(self) -> str:
        return self._accent_foreground_selected

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

    @property
    def sub_background(self) -> str:
        return self._sub_background

    @property
    def sub_foreground(self) -> str:
        return self._sub_foreground
