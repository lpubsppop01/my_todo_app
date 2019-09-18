#! /usr/bin/env python
# -*- coding: utf-8-unix -*-

"""The application entry point."""

import os

from my_todo_app.main_window import MainWindow
from my_todo_app.task_sqlite3 import SQLite3TaskDatabase


def get_db_path():
    appdata = os.getenv('APPDATA')
    if appdata is not None:
        return os.path.join(appdata, 'lpubsppop01', 'my_todo', 'db.sqlite3')
    return '~/.lpubsppop01/my_todo'

def main():
    db_path = get_db_path()
    db = SQLite3TaskDatabase(db_path)
    window = MainWindow(db)
    window.show()


if __name__ == '__main__':
    main()
