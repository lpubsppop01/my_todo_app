#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Implement configuration class."""

import json
import os


class Config:
    """Configuration class."""

    def __init__(self, path: str):
        self.main_window_geometry: str = '1024x600'
        self.main_window_zoomed: bool = False
        self.theme_fontfamily: str = 'Arial'
        self._path: str = path
        self._load()

    def save(self):
        values = dict()
        values['main_window_geometry'] = self.main_window_geometry
        values['main_window_zoomed'] = self.main_window_zoomed
        values['theme_fontfamily'] = self.theme_fontfamily
        values_str = json.dumps(values, indent=2)
        if not os.path.exists(self._path):
            os.makedirs(os.path.dirname(self._path), exist_ok=True)
        with open(self._path, 'w', encoding='utf-8', newline='') as file:
            file.write(values_str)

    def _load(self):
        if not os.path.exists(self._path):
            return
        with open(self._path, 'r', encoding='utf-8', newline='\n') as file:
            values_str = file.read()
        values = json.loads(values_str)
        if 'main_window_geometry' in values:
            self.main_window_geometry = values['main_window_geometry']
        if 'main_window_zoomed' in values:
            self.main_window_zoomed = values['main_window_zoomed']
        if 'theme_fontfamily' in values:
            self.theme_fontfamily = values['theme_fontfamily']
