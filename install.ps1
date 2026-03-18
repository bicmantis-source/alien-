$ErrorActionPreference = "Stop"

Write-Host "Instalando AlienApp..." -ForegroundColor Cyan

$dest = "$env:LOCALAPPDATA\AlienApp"
$exe = "$dest\alien.exe"
$desktop = [Environment]::GetFolderPath("Desktop")

# Crear carpeta
if (!(Test-Path $dest)) {
    New-Item -ItemType Directory -Path $dest | Out-Null
}

Write-Host "Descargando aplicación..." -ForegroundColor Yellow

# Descargar EXE
$url = "https://github.com/bicmantis-source/alien-/releases/download/v1.0/alien.exe"
Invoke-WebRequest -Uri $url -OutFile $exe

Write-Host "Creando acceso directo..." -ForegroundColor Yellow

# Crear acceso directo
$WScriptShell = New-Object -ComObject WScript.Shell
$shortcut = $WScriptShell.CreateShortcut("$desktop\AlienApp.lnk")
$shortcut.TargetPath = $exe
$shortcut.Save()

Write-Host "Ejecutando aplicación..." -ForegroundColor Green

# Ejecutar
Start-Process $exe

Write-Host "Instalación completada" -ForegroundColor Green