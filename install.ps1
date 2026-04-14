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
        Write-Host "Error descargando Ollama." -ForegroundColor Red
        exit
    }

    Start-Process -FilePath $installer -ArgumentList "/S" -Wait
    Start-Sleep -Seconds 5
}

# ==============================
# INICIAR OLLAMA
# ==============================

Write-Host "Iniciando Ollama..." -ForegroundColor Yellow

try {
    Start-Process $ollamaExe -ArgumentList "serve" -WindowStyle Hidden
    Start-Sleep -Seconds 5
} catch {
    Write-Host "No se pudo iniciar Ollama." -ForegroundColor Red
}

# ==============================
# DESCARGAR MODELO (SI NO EXISTE)
# ==============================

Write-Host "Verificando modelo IA..." -ForegroundColor Yellow

try {
    $models = & $ollamaExe list
    if ($models -notmatch "mistral") {
        Write-Host "Descargando modelo mistral..." -ForegroundColor Yellow
        Start-Process $ollamaExe -ArgumentList "pull mistral" -WindowStyle Hidden
    }
} catch {
    Write-Host "No se pudo verificar el modelo." -ForegroundColor Red
}

# ==============================
# DESCARGAR EXE (ARREGLADO)
# ==============================

Write-Host "Descargando MISTRALApp..." -ForegroundColor Yellow

$appUrl = "https://github.com/bicmantis-source/alien-/releases/latest/download/MISTRAL.exe"

try {
    Invoke-WebRequest -Uri $appUrl -OutFile $exe -MaximumRedirection 10 -UseBasicParsing
} catch {
    Write-Host "Error descargando desde GitHub." -ForegroundColor Red
    exit
}

# Verificar descarga
if (!(Test-Path $exe)) {
    Write-Host "El archivo no se descargó correctamente." -ForegroundColor Red
    exit
}

# Desbloquear archivo
Unblock-File -Path $exe -ErrorAction SilentlyContinue

# ==============================
# CREAR ACCESO DIRECTO
# ==============================

Write-Host "Creando acceso directo..." -ForegroundColor Yellow

$WScriptShell = New-Object -ComObject WScript.Shell
$shortcut = $WScriptShell.CreateShortcut("$desktop\MISTRALApp.lnk")
$shortcut.TargetPath = $exe
$shortcut.WorkingDirectory = $dest
$shortcut.IconLocation = $exe
$shortcut.Save()

# ==============================
# ABRIR WEB
# ==============================

Start-Process "https://bicmantis-source.github.io/alien-/web.html"

# ==============================
# EJECUTAR APP
# ==============================

Write-Host "Ejecutando MISTRALApp..." -ForegroundColor Green
Start-Process $exe

Write-Host "Instalación completada correctamente" -ForegroundColor Green
