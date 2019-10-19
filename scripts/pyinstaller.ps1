#! /bin/env pwsh

$pyinstaller = "pyinstaller"
if ($env:PYTHON -ne $null -and $(Test-Path -Type Container $env:PYTHON)) {
    $pyinstaller = Join-Path $env:PYTHON 'Scripts/pyinstaller'
}

$projectPath = Split-Path -Parent $PSScriptRoot
cd $projectPath
&$pyinstaller --noconsole --icon images/myicon_my_todo.ico -y my_todo_app/app/main.py
robocopy /mir images dist/main/images /xf *.svg
