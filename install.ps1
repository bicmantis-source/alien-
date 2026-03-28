$ErrorActionPreference = "Stop"

Write-Host "Instalando MISTRALApp..." -ForegroundColor Cyan

$dest = "$env:LOCALAPPDATA\MISTRALApp"
$exe = "$dest\MISTRALApp.exe"
$desktop = [Environment]::GetFolderPath("Desktop")

# Crear carpeta si no existe
if (!(Test-Path $dest)) {
    New-Item -ItemType Directory -Path $dest | Out-Null
}

# ==============================
# INSTALAR OLLAMA PRIMERO
# ==============================

Write-Host "Verificando Ollama..." -ForegroundColor Yellow

$ollamaPath = "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"

if (!(Test-Path $ollamaPath)) {

    Write-Host "Ollama no encontrado. Descargando..." -ForegroundColor Yellow

    $ollamaInstaller = "$env:TEMP\OllamaSetup.exe"
    $ollamaUrl = "https://ollama.com/download/OllamaSetup.exe"

    try {
        $wc = New-Object System.Net.WebClient
        $wc.Headers.Add("User-Agent", "Mozilla/5.0")
        $wc.DownloadFile($ollamaUrl, $ollamaInstaller)
    } catch {
        Write-Host "Error descargando Ollama." -ForegroundColor Red
        exit
    }

    Write-Host "Instalando Ollama..." -ForegroundColor Yellow

    Start-Process -FilePath $ollamaInstaller -ArgumentList "/S" -Wait

    Start-Sleep -Seconds 5
}

# ==============================
# DESCARGAR MODELO (IMPORTANTE)
# ==============================

Write-Host "Descargando modelo IA..." -ForegroundColor Yellow

try {
    Start-Process "ollama" -ArgumentList "pull mistral" -Wait
} catch {
    Write-Host "No se pudo descargar el modelo automáticamente." -ForegroundColor Red
}

# ==============================
# DESCARGAR TU EXE
# ==============================

Write-Host "Descargando MISTRALApp..." -ForegroundColor Yellow

$url = "https://github.com/bicmantis-source/alien-/releases/download/v1.0/MISTRAL.exe"

try {
    $wc = New-Object System.Net.WebClient
    $wc.Headers.Add("User-Agent", "Mozilla/5.0")
    $wc.DownloadFile($url, $exe)
} catch {
    Write-Host "Error al descargar el archivo desde GitHub." -ForegroundColor Red
    exit
}

# Verificar descarga
if (!(Test-Path $exe)) {
    Write-Host "El archivo no se descargó correctamente." -ForegroundColor Red
    exit
}

# ==============================
# CREAR ACCESO DIRECTO
# ==============================

Write-Host "Creando acceso directo..." -ForegroundColor Yellow

$WScriptShell = New-Object -ComObject WScript.Shell
$shortcut = $WScriptShell.CreateShortcut("$desktop\MISTRALApp.lnk")
$shortcut.TargetPath = $exe
$shortcut.WorkingDirectory = $dest
$shortcut.Save()

# ==============================
# EJECUTAR APP (YA CON OLLAMA)
# ==============================

Write-Host "Ejecutando MISTRALApp..." -ForegroundColor Green

Start-Process $exe

Write-Host "Instalación de MISTRALApp completada" -ForegroundColor Green
