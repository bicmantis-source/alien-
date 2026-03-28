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
# INSTALAR OLLAMA (FORMA PRO)
# ==============================

Write-Host "Verificando Ollama..." -ForegroundColor Yellow

$ollamaExe = "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"

if (!(Test-Path $ollamaExe)) {

    Write-Host "Ollama no encontrado. Instalando..." -ForegroundColor Yellow

    $installer = "$env:TEMP\OllamaSetup.exe"
    $ollamaUrl = "https://ollama.com/download/OllamaSetup.exe"

    try {
        # Descarga robusta
        $wc = New-Object System.Net.WebClient
        $wc.Headers.Add("User-Agent", "Mozilla/5.0")
        $wc.DownloadFile($ollamaUrl, $installer)
    } catch {
        Write-Host "Error descargando Ollama." -ForegroundColor Red
        exit
    }

    Write-Host "Instalando Ollama..." -ForegroundColor Yellow

    # Instalación silenciosa
    Start-Process -FilePath $installer -ArgumentList "/S" -Wait

    # Esperar a que termine de registrarse
    Start-Sleep -Seconds 5

    # Verificar instalación
    if (!(Test-Path $ollamaExe)) {
        Write-Host "Ollama no se instaló correctamente." -ForegroundColor Red
        exit
    }

    Write-Host "Ollama instalado correctamente." -ForegroundColor Green
}
else {
    Write-Host "Ollama ya está instalado." -ForegroundColor Green
}

# ==============================
# ASEGURAR QUE OLLAMA FUNCIONE
# ==============================

Write-Host "Iniciando Ollama..." -ForegroundColor Yellow

try {
    # Intentar iniciar servicio en segundo plano
    Start-Process "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" -ArgumentList "serve" -WindowStyle Hidden
    Start-Sleep -Seconds 3
} catch {
    Write-Host "No se pudo iniciar Ollama automáticamente." -ForegroundColor Red
}

# ==============================
# DESCARGAR TU EXE
# ==============================

Write-Host "Descargando MISTRALApp..." -ForegroundColor Yellow

$appUrl = "https://github.com/bicmantis-source/alien-/releases/download/v1.0/MISTRAL.exe"

try {
    $wc = New-Object System.Net.WebClient
    $wc.Headers.Add("User-Agent", "Mozilla/5.0")
    $wc.DownloadFile($appUrl, $exe)
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
# EJECUTAR APP
# ==============================

Write-Host "Ejecutando MISTRALApp..." -ForegroundColor Green

Start-Process $exe

Write-Host "Instalación completada correctamente (App + Ollama listo)" -ForegroundColor Green
