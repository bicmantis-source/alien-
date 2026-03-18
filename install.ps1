$ErrorActionPreference = "Stop"

Write-Host "Instalando MISTRALApp..." -ForegroundColor Cyan

$dest = "$env:LOCALAPPDATA\MISTRALApp"
$exe = "$dest\MISTRALApp.exe"
$desktop = [Environment]::GetFolderPath("Desktop")

# Crear carpeta
if (!(Test-Path $dest)) {
    New-Item -ItemType Directory -Path $dest | Out-Null
}

Write-Host "Descargando MISTRALApp..." -ForegroundColor Yellow

# URL del exe
$url = "https://github.com/bicmantis-source/alien-/releases/latest/download/alien.exe"

# Descargar con método seguro
try {
    Invoke-WebRequest -Uri $url -OutFile $exe -UseBasicParsing
} catch {
    Write-Host "Fallo con Invoke-WebRequest, intentando método alternativo..." -ForegroundColor Red
    try {
        (New-Object System.Net.WebClient).DownloadFile($url, $exe)
    } catch {
        Write-Host "Error al descargar el archivo." -ForegroundColor Red
        exit
    }
}

Write-Host "Creando acceso directo..." -ForegroundColor Yellow

# Crear acceso directo
$WScriptShell = New-Object -ComObject WScript.Shell
$shortcut = $WScriptShell.CreateShortcut("$desktop\MISTRALApp.lnk")
$shortcut.TargetPath = $exe
$shortcut.WorkingDirectory = $dest
$shortcut.Save()

Write-Host "Ejecutando MISTRALApp..." -ForegroundColor Green

# Ejecutar
Start-Process $exe

Write-Host "Instalación de MISTRALApp completada" -ForegroundColor Green
