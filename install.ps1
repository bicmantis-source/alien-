$dest = "$env:LOCALAPPDATA\AlienApp"
$exe = "$dest\alien.exe"
$desktop = [Environment]::GetFolderPath("Desktop")

New-Item -ItemType Directory -Force -Path $dest | Out-Null

$url = "https://github.com/bicmantis-source/alien-/releases/download/v1.0/alien.exe"
Invoke-WebRequest -Uri $url -OutFile $exe

$WScriptShell = New-Object -ComObject WScript.Shell
$shortcut = $WScriptShell.CreateShortcut("$desktop\AlienApp.lnk")
$shortcut.TargetPath = $exe
$shortcut.Save()

Start-Process $exe