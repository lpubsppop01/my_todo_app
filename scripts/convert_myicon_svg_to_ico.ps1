#! /bin/env pwsh

$inkscape = 'C:\Program Files\Inkscape\inkscape.exe'
$imagemagick_convert = "D:\opt\ImageMagick-7.0.8-61-portable-Q16-x64\convert.exe"
$projectPath = Split-Path -Parent $PSScriptRoot
$imagesPath = Join-Path $projectPath 'images'

$svgPath = Join-Path $imagesPath 'myicon_my_todo.svg'
$pngSizes = 16, 24, 32, 48, 64, 128, 256
$pngPaths = @()
foreach ($pngSize in $pngSizes) {
    $pngPath = Join-Path $imagesPath "myicon_my_todo_${pngSize}x${pngSize}.png"
    &$inkscape -f $svgPath -e $pngPath -w $pngSize -h $pngSize
    $pngPaths += $pngPath
}
Write-Host $pngPaths
$icoPath = Join-Path $imagesPath 'myicon_my_todo.ico'
&$imagemagick_convert $pngPaths $icoPath
