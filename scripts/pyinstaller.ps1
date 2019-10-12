#! /bin/env pwsh

$projectPath = Split-Path -Parent $PSScriptRoot
cd $projectPath
pyinstaller --noconsole .\my_todo_app\app\main.py --icon .\images\myicon_my_todo.ico -y
robocopy /mir images dist\main\images /xf *.svg
