#! /bin/env pwsh

$pyinstaller = pyinstaller
if ($env:PYTHON -ne '') {
    $pyinstaller = Join-Path $env:PYTHON 'Scripts\pyinstaller'
}

$projectPath = Split-Path -Parent $PSScriptRoot
cd $projectPath
&$pyinstaller --noconsole .\my_todo_app\app\main.py --icon .\images\myicon_my_todo.ico -y
robocopy /mir images dist\main\images /xf *.svg
