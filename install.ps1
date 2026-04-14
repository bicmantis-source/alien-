$ErrorActionPreference = "Stop"

Write-Host "Instalando MISTRALApp..." -ForegroundColor Cyan

$dest = "$env:LOCALAPPDATA\MISTRALApp"
$exe = "$dest\MISTRALApp.exe"
$desktop = [Environment]::GetFolderPath("Desktop")

# Crear carpeta
if (!(Test-Path $dest)) {
    New-Item -ItemType Directory -Path $dest | Out-Null
}

# ==============================
# INSTALAR OLLAMA
# ==============================

Write-Host "Verificando Ollama..." -ForegroundColor Yellow

$ollamaExe = "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"

if (!(Test-Path $ollamaExe)) {

    Write-Host "Ollama no encontrado. Instalando..." -ForegroundColor Yellow

    $installer = "$env:TEMP\OllamaSetup.exe"
    $ollamaUrl = "https://ollama.com/download/OllamaSetup.exe"

    try {
        Invoke-WebRequest -Uri $ollamaUrl -OutFile $installer -UseBasicParsing
    } catch {
        Write-Host "Fallo con Invoke-WebRequest, usando método alternativo..." -ForegroundColor Red
        try {
            (New-Object System.Net.WebClient).DownloadFile($ollamaUrl, $installer)
        } catch {
            Write-Host "Error descargando Ollama." -ForegroundColor Red
            exit
        }
    }

    Write-Host "Instalando Ollama..." -ForegroundColor Yellow
    Start-Process -FilePath $installer -ArgumentList "/S" -Wait

    Start-Sleep -Seconds 5

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
# INICIAR OLLAMA (OCULTO)
# ==============================

Write-Host "Iniciando Ollama..." -ForegroundColor Yellow

try {
    Start-Process $ollamaExe -ArgumentList "serve" -WindowStyle Hidden
    Start-Sleep -Seconds 3
} catch {
    Write-Host "No se pudo iniciar Ollama automáticamente." -ForegroundColor Red
}

# ==============================
# DESCARGAR MODELO (OPCIONAL)
# ==============================

Write-Host "Preparando modelo IA..." -ForegroundColor Yellow

try {
    Start-Process $ollamaExe -ArgumentList "pull mistral" -WindowStyle Hidden
} catch {
    Write-Host "No se pudo descargar el modelo automáticamente." -ForegroundColor Red
}

# ==============================
# DESCARGAR EXE
# ==============================

Write-Host "Descargando MISTRALApp..." -ForegroundColor Yellow

$appUrl = "https://github.com/bicmantis-source/alien-/releases/download/v1.0/MISTRAL.exe"

try {
    Invoke-WebRequest -Uri $appUrl -OutFile $exe -UseBasicParsing
} catch {
    Write-Host "Fallo con Invoke-WebRequest, usando método alternativo..." -ForegroundColor Red
    try {
        (New-Object System.Net.WebClient).DownloadFile($appUrl, $exe)
    } catch {
        Write-Host "Error al descargar el EXE." -ForegroundColor Red
        exit
    }
}

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

Write-Host "Instalación completada correctamente" -ForegroundColor Green
