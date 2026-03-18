$ErrorActionPreference = "Stop"

Write-Host "Instalando MISTRALApp..." -ForegroundColor Cyan

$dest = "$env:LOCALAPPDATA\MISTRALApp"
$exe = "$dest\MISTRALApp.exe"
$desktop = [Environment]::GetFolderPath("Desktop")

# Crear carpeta si no existe
if (!(Test-Path $dest)) {
    New-Item -ItemType Directory -Path $dest | Out-Null
}

Write-Host "Descargando MISTRALApp..." -ForegroundColor Yellow

# URL CORRECTA DEL EXE
$url = "https://github.com/bicmantis-source/alien-/releases/download/v1.0/MISTRAL.exe"

# Descarga robusta (funciona con archivos grandes)
try {
    $wc = New-Object System.Net.WebClient
    $wc.Headers.Add("User-Agent", "Mozilla/5.0")
    $wc.DownloadFile($url, $exe)
} catch {
    Write-Host "Error al descargar el archivo desde GitHub." -ForegroundColor Red
    exit
}

# Verificar que se descargó
if (!(Test-Path $exe)) {
    Write-Host "El archivo no se descargó correctamente." -ForegroundColor Red
    exit
}

Write-Host "Creando acceso directo..." -ForegroundColor Yellow

# Crear acceso directo en escritorio
$WScriptShell = New-Object -ComObject WScript.Shell
$shortcut = $WScriptShell.CreateShortcut("$desktop\MISTRALApp.lnk")
$shortcut.TargetPath = $exe
$shortcut.WorkingDirectory = $dest
$shortcut.Save()

Write-Host "Ejecutando MISTRALApp..." -ForegroundColor Green

# Ejecutar app
Start-Process $exe

Write-Host "Instalación de MISTRALApp completada" -ForegroundColor Green
