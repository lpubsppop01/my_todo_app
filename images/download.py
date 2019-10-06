#! /usr/bin/env python
# -*- coding: utf-8-unix -*-

"""Script to download resource images."""

import os

import requests


def download_material_design_icon(dir_path: str, category: str, name: str) -> None:
    path = os.path.join(dir_path, name)
    url = 'https://github.com/google/material-design-icons/raw/master/{}/1x_web/{}'.format(category, name)
    if not os.path.exists(path):
        zip_res = requests.get(url, stream=True)
        zip_size: int = 0
        with open(path, 'wb') as f:
            for chunk in zip_res.iter_content(chunk_size=2 ** 19):
                f.write(chunk)
                zip_size += len(chunk)
        if zip_size == 0:
            os.remove(path)
            raise RuntimeError('Download failure')


here = os.path.dirname(__file__)
download_material_design_icon(here, 'content', 'ic_add_circle_white_24dp.png')
download_material_design_icon(here, 'content', 'ic_create_white_24dp.png')
download_material_design_icon(here, 'action', 'ic_delete_white_24dp.png')
download_material_design_icon(here, 'navigation', 'ic_arrow_upward_white_24dp.png')
download_material_design_icon(here, 'navigation', 'ic_arrow_downward_white_24dp.png')
