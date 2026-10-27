@echo off
rem 脱脂内示データ抽出.html のショートカットをデスクトップに作る
rem （アイコンは icon\dasshi_icon.ico）
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$d = (Get-Location).Path;" ^
  "$h = Get-ChildItem -LiteralPath $d -Filter '*.html' | Select-Object -First 1;" ^
  "if (-not $h) { exit 1 };" ^
  "$ws = New-Object -ComObject WScript.Shell;" ^
  "$lnk = $ws.CreateShortcut((Join-Path $ws.SpecialFolders('Desktop') ($h.BaseName + '.lnk')));" ^
  "$lnk.TargetPath = $h.FullName;" ^
  "$lnk.WorkingDirectory = $d;" ^
  "$lnk.IconLocation = (Join-Path $d 'icon\dasshi_icon.ico') + ',0';" ^
  "$lnk.Description = '脱脂内示データ抽出ツール';" ^
  "$lnk.Save()"
if errorlevel 1 (
  echo.
  echo ショートカットを作れませんでした。
  echo このファイルが「脱脂内示データ抽出.html」と同じフォルダにあるか確認してください。
) else (
  echo.
  echo デスクトップにショートカットを作りました。
  echo ※フォルダを移動したときは、もう一度このファイルを実行してください。
)
echo.
pause
