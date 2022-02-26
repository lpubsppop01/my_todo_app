#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Implement image set class for this app."""

from my_todo_app.base.image_set import ImageSet


class MyImageSet(ImageSet):
    """Image set class for this app."""

    def __init__(self) -> None:
        super().__init__('images')
        self.icon_add_accent = self._get_lazy_image('ic_add_circle_white_24dp.png')
        self.icon_edit_accent = self._get_lazy_image('ic_create_white_24dp.png')
        self.icon_delete_accent = self._get_lazy_image('ic_delete_white_24dp.png')
        self.icon_arrow_up_accent = self._get_lazy_image('ic_arrow_upward_white_24dp.png')
        self.icon_arrow_down_accent= self._get_lazy_image('ic_arrow_downward_white_24dp.png')
        self.icon_add_main= self._get_lazy_image('ic_add_circle_black_24dp.png')
        self.icon_insert_as_last_child_main= self._get_lazy_image('myicon_insert_as_last_child_24x24.png')
        self.icon_delete_main= self._get_lazy_image('ic_delete_black_24dp.png')
        self.icon_move_to_list_main= self._get_lazy_image('myicon_move_to_list_24x24.png')
        self.icon_check_main= self._get_lazy_image('myicon_check_24x24.png')
        self.icon_uncheck_main= self._get_lazy_image('myicon_uncheck_24x24.png')
        self.icon_archive_main= self._get_lazy_image('myicon_archive_24x24.png')
        self.icon_unarchive_main= self._get_lazy_image('myicon_unarchive_24x24.png')
        self.icon_arrow_up_main= self._get_lazy_image('ic_arrow_upward_black_24dp.png')
        self.icon_arrow_down_main= self._get_lazy_image('ic_arrow_downward_black_24dp.png')
        self.icon_archive_is_visible_main= self._get_lazy_image('myicon_archive_is_visible_24x24.png')
        self.icon_archive_is_invisible_main= self._get_lazy_image('myicon_archive_is_invisible_24x24.png')
        self.icon_github= self._get_lazy_image('appbar.social.github.octocat.solid.png')
        self.icon_my_todo= self._get_lazy_image('myicon_my_todo_16x16.png')
