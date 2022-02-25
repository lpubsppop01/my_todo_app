#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Script to download external icon files."""

import os

import requests
from reportlab.graphics import renderPM
from svglib.svglib import svg2rlg


def download_file(url: str, path: str) -> None:
    if not os.path.exists(path):
        res = requests.get(url, stream=True)
        size: int = 0
        with open(path, 'wb') as f:
            for chunk in res.iter_content(chunk_size=2 ** 19):
                f.write(chunk)
                size += len(chunk)
        if size == 0:
            os.remove(path)
            raise RuntimeError('Download failure')


def download_material_design_icon(dir_path: str, category: str, name: str) -> None:
    png_path = os.path.join(dir_path, name + '.png')
    png_url = 'https://github.com/google/material-design-icons/raw/3.0.2/{}/1x_web/{}.png'.format(category, name)
    download_file(png_url, png_path)


def download_modern_ui_icon(dir_path: str, name: str) -> None:
    svg_path = os.path.join(dir_path, name + '.svg')
    svg_url = 'https://github.com/Templarian/WindowsIcons/raw/master/WindowsPhone/svg/{}.svg'.format(name)
    download_file(svg_url, svg_path)
    drawing = svg2rlg(svg_path)
    drawing.scale(0.5, 0.5)
    drawing.shift(-6, -6)
    png_path = os.path.join(dir_path, name + '.png')
    renderPM.drawToFile(drawing, png_path, fmt="PNG", dpi=24)


images_path = os.path.join(os.path.dirname(__file__), '../images')
os.makedirs(images_path, exist_ok=True)
download_material_design_icon(images_path, 'content', 'ic_add_circle_white_24dp')
download_material_design_icon(images_path, 'content', 'ic_create_white_24dp')
download_material_design_icon(images_path, 'action', 'ic_delete_white_24dp')
download_material_design_icon(images_path, 'navigation', 'ic_arrow_upward_white_24dp')
download_material_design_icon(images_path, 'navigation', 'ic_arrow_downward_white_24dp')
download_material_design_icon(images_path, 'content', 'ic_add_circle_black_24dp')
download_material_design_icon(images_path, 'action', 'ic_delete_black_24dp')
download_material_design_icon(images_path, 'navigation', 'ic_arrow_upward_black_24dp')
download_material_design_icon(images_path, 'navigation', 'ic_arrow_downward_black_24dp')
download_modern_ui_icon(images_path, 'appbar.social.github.octocat.solid')
