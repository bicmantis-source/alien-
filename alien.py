import sys
sys.stdout.reconfigure(encoding='utf-8')

import subprocess
import random
import psutil
import datetime
import platform
import cv2
import mediapipe as mp
import asyncio
import tempfile
import threading
import queue
import pyttsx3
import edge_tts
from playsound import playsound
import os
import requests
import zipfile
import io
import os

from PySide6.QtWidgets import QFileDialog  # agrega esto al inicio con tus otros imports

# ---------------- CONFIG GITHUB ----------------
GITHUB_TOKEN = "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"
GITHUB_USER = "Bicmantis-source"
GITHUB_REPO = "nuevas-paginas"
GITHUB_BRANCH = "main"  # o gh-pages si tu Pages usa esa rama

def publish_to_github(file_path):
    """
    Sube un archivo HTML a GitHub usando la API y devuelve la URL de GitHub Pages.
    """
    import base64
    import requests
    import os

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    content_b64 = base64.b64encode(content.encode()).decode()
    filename = os.path.basename(file_path)

    url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{filename}"

    # Verificar si ya existe para obtener sha
    response = requests.get(url, headers={"Authorization": f"token {GITHUB_TOKEN}"})
    sha = response.json()["sha"] if response.status_code == 200 else None

    data = {
        "message": f"Agregar/actualizar {filename}",
        "content": content_b64,
        "branch": GITHUB_BRANCH
    }

    if sha:
        data["sha"] = sha

    response = requests.put(url, json=data, headers={"Authorization": f"token {GITHUB_TOKEN}"})

    if response.status_code in [200, 201]:
        pages_url = f"https://{GITHUB_USER}.github.io/{GITHUB_REPO}/{filename}"
        return f"Página subida correctamente: {pages_url}"
    else:
        return f"Error al subir: {response.json()}"

def select_and_publish():
    from PySide6.QtWidgets import QFileDialog

    path, _ = QFileDialog.getOpenFileName(
        None,
        "Seleccionar página",
        "",
        "HTML (*.html)"
    )

    if not path:
        return "No se seleccionó archivo."

    return publish_to_github(path)

from PySide6.QtWidgets import (
    QApplication, QWidget, QTextEdit, QLineEdit,
    QVBoxLayout, QHBoxLayout, QLabel, QProgressBar,
    QFrame, QPushButton, QFileDialog
)
from PySide6.QtCore import QTimer, Qt, QPoint, Signal
from PySide6.QtGui import QFont, QImage, QPixmap

# ---------------- DETECTAR MODELO IA ----------------

def select_model():

    ram = psutil.virtual_memory().total / (1024**3)
    cpu = psutil.cpu_count(logical=False)

    gpu = False
    try:
        import torch  # type: ignore[import-untyped]
        gpu = torch.cuda.is_available()
    except:
        pass

    # selección inteligente
    if ram < 6:
        model = "tinyllama"

    elif ram < 12:
        model = "mistral"

    elif ram < 24:
        model = "mistral"

    else:
        model = "mixtral"

    # si hay GPU se puede usar modelo más grande
    if gpu and ram >= 16:
        model = "mixtral"

    print(f"[AI SYSTEM]")
    print(f"RAM: {ram:.1f} GB")
    print(f"CPU CORES: {cpu}")
    print(f"GPU DETECTED: {gpu}")
    print(f"SELECTED MODEL: {model}")

    return model

AI_MODEL = select_model()

# ---------------- VOZ IA ----------------

engine = pyttsx3.init()
voices = engine.getProperty('voices')
spanish_voice = None
for voice in voices:
    if "spanish" in voice.name.lower() or "es" in voice.id.lower():
        spanish_voice = voice.id
        break

if spanish_voice:
    engine.setProperty('voice', spanish_voice)

engine.setProperty('rate',160)

voice_queue = queue.Queue()
voice_lock = threading.Lock()

# -------- FUNCIÓN DE VOZ (ARREGLADA) --------

def speak(text):
    def run():
        async def tts():
            try:
                voice = "es-MX-DaliaNeural"
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                    filename = f.name
                communicate = edge_tts.Communicate(text, voice)
                await communicate.save(filename)
                import time
                for _ in range(20):
                    if os.path.exists(filename) and os.path.getsize(filename) > 0:
                        break
                    time.sleep(0.05)
                with voice_lock:
                    try:
                        playsound(filename, block=True)
                    except:
                        pass
                try:
                    os.remove(filename)
                except:
                    pass
            except Exception as e:
                print("VOICE ERROR:", e)
        asyncio.run(tts())
    threading.Thread(target=run, daemon=True).start()


# ---------------- IA ----------------

def ask_ai(prompt):
    try:
        p = (prompt or "").strip()
        system_prompt = (
            "Eres una IA llamada Nexa. "
            "Respondes SOLO en español, de forma clara, natural y directa, como un desarrollador experto y amable. "
            "Responde solo a lo que pregunta el usuario y no expliques tus reglas internas ni tu personalidad."
        )
        final_prompt = f"{system_prompt}\nUsuario: {p}\nAsistente:"
        result = subprocess.run(
            ["ollama","run",AI_MODEL,final_prompt],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=300
        )
        if result.returncode != 0:
            result = subprocess.run(
                ["ollama","run","tinyllama",final_prompt],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                timeout=300
            )
        response = result.stdout.strip()
        remove_words = ["Assistant:","assistant:","AI:","User:","Usuario:","Asistente:"]
        for w in remove_words:
            response = response.replace(w,"")
        import re
        response = re.sub(r"\(.*?\)","",response)
        response = re.sub(r"\n{4,}","\n\n",response).strip()
        cleaned_lines = []
        for ln in response.split("\n"):
            low = ln.lower().strip()
            if not low:
                cleaned_lines.append(ln)
                continue
            if any(key in low for key in ["eres","reglas","reglas de respuesta","personalidad","resuelves lo pedido","resuelvo lo pedido","soy una ia","soy un modelo"]):
                continue
            if low.startswith("- "):
                ln = ln[2:].lstrip()
            cleaned_lines.append(ln)
        response = "\n".join(cleaned_lines).strip()
        return response.strip()
    except subprocess.TimeoutExpired:
        return "Sigo pensando y mi equipo tardó más de lo esperado. Vuelve a intentar o usa un modelo más ligero."
    except Exception as e:
        return str(e)

# ---------------- SCAN WINDOW ----------------

class ScanWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("HUMAN SCANNER")
        self.resize(700,500)

        layout = QVBoxLayout()
        self.label = QLabel()
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.cap = cv2.VideoCapture(0)

        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()

        self.mp_face = mp.solutions.face_detection
        self.face = self.mp_face.FaceDetection()

        self.mp_draw = mp.solutions.drawing_utils

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def update_frame(self):

        ret, frame = self.cap.read()
        if not ret:
            return

        frame = cv2.flip(frame,1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        pose_results = self.pose.process(rgb)
        face_results = self.face.process(rgb)

        if pose_results.pose_landmarks:
            self.mp_draw.draw_landmarks(
                frame,
                pose_results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS
            )

        if face_results.detections:
            for detection in face_results.detections:

                bbox = detection.location_data.relative_bounding_box
                h,w,_ = frame.shape

                x = int(bbox.xmin*w)
                y = int(bbox.ymin*h)
                bw = int(bbox.width*w)
                bh = int(bbox.height*h)

                cv2.rectangle(frame,(x,y),(x+bw,y+bh),(0,140,255),2)

                cv2.putText(frame,"HUMAN",(x,y-10),
                            cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,140,255),2)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        h,w,ch = frame.shape
        img = QImage(frame.data,w,h,ch*w,QImage.Format_RGB888)

        self.label.setPixmap(QPixmap.fromImage(img))

    def closeEvent(self,event):

        if self.cap.isOpened():
            self.cap.release()

        event.accept()

        try:
            terminal_window.scan_window = None
        except:
            pass

# ---------------- TERMINAL ----------------

class IronTerminal(QWidget):
    ai_response_signal = Signal(str)

    def __init__(self):
        super().__init__()

        self.ai_active = False
        self.awaiting_save_confirm = False
        self.last_generated_code = ""
        self.ai_response_signal.connect(self._on_ai_response)

        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setWindowTitle("TERMINAL OS")
        self.resize(1400,800)

        self.is_maximized = False
        self.old_pos = None

        self.title_bar = QWidget()
        self.title_bar.setStyleSheet("background-color: #111;")
        self.title_bar.setFixedHeight(35)

        self.title_label = QLabel("TERMINAL OS")
        self.title_label.setStyleSheet("color: #00ffaa; margin-left: 10px;")
        self.title_label.setFont(QFont("Consolas", 10))

        self.btn_min = QPushButton("-")
        self.btn_max = QPushButton("□")
        self.btn_close = QPushButton("X")

        btn_style = """
            QPushButton {
                background-color: #111;
                color: #00ffaa;
                border: none;
                font-size: 16px;
                width: 35px;
            }
            QPushButton:hover {
                background-color: #333;
            }
        """

        self.btn_close.setStyleSheet(btn_style + "QPushButton:hover {background-color: #e74c3c;}")
        self.btn_min.setStyleSheet(btn_style)
        self.btn_max.setStyleSheet(btn_style)

        self.btn_min.clicked.connect(self.showMinimized)
        self.btn_max.clicked.connect(self.toggle_max_restore)
        self.btn_close.clicked.connect(self.close)

        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(0,0,0,0)
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        title_layout.addWidget(self.btn_min)
        title_layout.addWidget(self.btn_max)
        title_layout.addWidget(self.btn_close)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.addWidget(self.title_bar)

        layout = QHBoxLayout()

        self.left = self.left_panel()
        self.center = self.center_terminal()
        self.right = self.right_panel()

        layout.addWidget(self.left,1)
        layout.addWidget(self.center,3)
        layout.addWidget(self.right,1)

        main_layout.addLayout(layout)

        self.scan_window = None
        self.last_net = psutil.net_io_counters()

        self.start_updates()

    # -------- Barra personalizada --------

    def toggle_max_restore(self):

        if self.isMaximized():
            self.showNormal()
            self.is_maximized = False
            self.btn_max.setText("□")
        else:
            self.showMaximized()
            self.is_maximized = True
            self.btn_max.setText("❐")

    def mousePressEvent(self, event):

        if event.button() == Qt.LeftButton and int(event.position().y()) <= self.title_bar.height():
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):

        if self.old_pos:
            delta = QPoint(event.globalPosition().toPoint() - self.old_pos)
            self.move(self.pos() + delta)
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

    # -------- LEFT PANEL --------

    def left_panel(self):

        frame = QFrame()
        layout = QVBoxLayout()

        title = QLabel("SYSTEM")
        title.setFont(QFont("Consolas",12))

        self.cpu_bar = QProgressBar()
        self.ram_bar = QProgressBar()
        self.disk_bar = QProgressBar()

        layout.addWidget(title)
        layout.addWidget(QLabel("CPU"))
        layout.addWidget(self.cpu_bar)
        layout.addWidget(QLabel("RAM"))
        layout.addWidget(self.ram_bar)
        layout.addWidget(QLabel("DISK"))
        layout.addWidget(self.disk_bar)

        self.logs = QTextEdit()
        self.logs.setReadOnly(True)
        layout.addWidget(QLabel("LOG STREAM"))
        layout.addWidget(self.logs)

        frame.setLayout(layout)
        return frame

    # -------- CENTER --------

    def center_terminal(self):

        frame = QFrame()
        layout = QVBoxLayout()

        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)

        self.ai_chat = QTextEdit()
        self.ai_chat.setReadOnly(True)

        self.input = QLineEdit()
        self.input.returnPressed.connect(self.handle_command)

        button_layout = QHBoxLayout()

        clear_btn = QPushButton("CLEAR")
        clear_btn.clicked.connect(lambda:self.run_internal("clear"))

        sys_btn = QPushButton("SYS INFO")
        sys_btn.clicked.connect(lambda:self.run_internal("sysinfo"))

        net_btn = QPushButton("NETWORK")
        net_btn.clicked.connect(lambda:self.run_internal("net"))

        scan_btn = QPushButton("SCAN")
        scan_btn.clicked.connect(lambda:self.run_internal("scan"))

        proc_btn = QPushButton("PROCESSES")
        proc_btn.clicked.connect(lambda:self.run_internal("process"))

        ai_btn = QPushButton("AI")
        ai_btn.clicked.connect(self.toggle_ai)

        for btn in [clear_btn, sys_btn, net_btn, scan_btn, proc_btn, ai_btn]:
            button_layout.addWidget(btn)

        layout.addWidget(QLabel("TERMINAL"))
        layout.addLayout(button_layout)
        layout.addWidget(self.terminal)

        layout.addWidget(QLabel("AI CHAT"))
        layout.addWidget(self.ai_chat)

        layout.addWidget(self.input)

        frame.setLayout(layout)
        return frame

    # -------- RIGHT PANEL --------

    def right_panel(self):

        frame = QFrame()
        layout = QVBoxLayout()

        self.clock = QLabel("")
        self.clock.setFont(QFont("Consolas",16))
        layout.addWidget(QLabel("TIME"))
        layout.addWidget(self.clock)

        self.network = QLabel("")
        layout.addWidget(QLabel("NETWORK"))
        layout.addWidget(self.network)

        self.processes = QTextEdit()
        self.processes.setReadOnly(True)
        layout.addWidget(QLabel("TOP PROCESSES"))
        layout.addWidget(self.processes)

        frame.setLayout(layout)
        return frame

    # -------- IA --------

    def toggle_ai(self):

        self.ai_active = not self.ai_active

        if self.ai_active:
            self.ai_chat.append(f"AI ACTIVATED ({AI_MODEL})")
            self.ai_chat.setStyleSheet("color:#00ffff")
        else:
            self.ai_chat.append("AI OFFLINE")
            self.ai_chat.setStyleSheet("color:#00ffaa")

    def ai_process(self,prompt):

        response = ask_ai(prompt)

        self.ai_response_signal.emit(response)

    def _looks_like_code(self, text: str) -> bool:

        t = (text or "").strip().lower()

        markers = [
            "import ",
            "from ",
            "def ",
            "class ",
            "if __name__",
            "print(",
            "for ",
            "while ",
            "return ",
            "=",
        ]

        if any(m in t for m in markers):
            return True

        if t.count("\n") >= 2:
            return True

        return False

    def _clean_code_for_save(self, text: str) -> str:

        import re

        t = (text or "").replace("\r\n", "\n")

        # detectar bloque de código ``` ```
        code_blocks = re.findall(r"```(?:\w+)?\n(.*?)```", t, re.DOTALL)

        if code_blocks:
            code = code_blocks[0].strip()
            return code

        lines = []
        for ln in t.split("\n"):

            l = ln.strip().lower()

            # ignorar explicaciones comunes
            if l.startswith("para ") or l.startswith("puedes ") or l.startswith("este código"):
                continue

            if l.startswith("para ejecutar") or l.startswith("copialo") or l.startswith("a continuación"):
                continue

            # ignorar identificadores de lenguaje
            if l in ["python", "html", "javascript", "css", "bash"]:
                continue

            lines.append(ln)

        code = "\n".join(lines).strip()
        return code

    def _looks_like_html(self, text: str) -> bool:
        """
        Detecta si el texto generado por la IA es HTML.
        """
        t = (text or "").strip().lower()
        return t.startswith("<!doctype html") or t.startswith("<html")

    def _on_ai_response(self, response: str):
        self.ai_chat.append("AI: " + response)
        speak(response)

        if self._looks_like_code(response):
            code = self._clean_code_for_save(response)
            if code:
                self.last_generated_code = code
                self.awaiting_save_confirm = True
                self.ai_chat.append("¿Deseas guardar este código? (y/n)")

    # -------- COMMANDS --------

    def handle_command(self):

        cmd = self.input.text().strip()
        self.terminal.append("> "+cmd)

        if cmd == "ai":
            self.toggle_ai()
            self.input.clear()
            return

        if self.ai_active:

            # ----- COMANDO PUBLICAR -----
            if cmd.lower() == "/publicar":
                result = select_and_publish()
                self.ai_chat.append(result)

                if result.startswith("Página publicada"):
                    speak("Página publicada correctamente")

                self.input.clear()
                return
            # ----------------------------

            if self.awaiting_save_confirm:
                c = cmd.strip().lower()
                if c == "y":
                    path, _ = QFileDialog.getSaveFileName(
                        self,
                        "Guardar código",
                        "",
                        "Python (*.py);;Todos los archivos (*.*)"
                    )
                    if not path:
                        self.ai_chat.append("Guardado cancelado.")
                    else:
                        try:
                            with open(path, "w", encoding="utf-8") as f:
                                f.write(self.last_generated_code)
                            self.ai_chat.append(f"Código guardado en: {path}")
                        except Exception as e:
                            self.ai_chat.append("Error al guardar: " + str(e))

                    self.awaiting_save_confirm = False
                    self.last_generated_code = ""
                    self.input.clear()
                    return

                if c == "n":
                    self.ai_chat.append("Listo, no se guardó.")
                    self.awaiting_save_confirm = False
                    self.last_generated_code = ""
                    self.input.clear()
                    return

                self.ai_chat.append("Responde con y (sí) o n (no).")
                self.input.clear()
                return

            self.ai_chat.append("AI: Pensando...")
            self.ai_chat.append("YOU: " + cmd)

            threading.Thread(
                target=self.ai_process,
                args=(cmd,),
                daemon=True
            ).start()

            self.input.clear()
            return

        if cmd in ["help","clear","sysinfo","scan","net","process","exit"]:
            self.run_internal(cmd)
        else:
            self.run_system(cmd)

        self.input.clear()

    def run_internal(self,cmd):

        if cmd=="help":
            self.terminal.append("""
help
clear
sysinfo
scan
net
process
exit
ai
""")

        elif cmd=="clear":
            self.terminal.clear()

        elif cmd=="sysinfo":

            info=f"""
OS: {platform.system()}
CPU CORES: {psutil.cpu_count()}
RAM: {psutil.virtual_memory().total/1024**3:.2f} GB
DISK: {psutil.disk_usage('/').percent}%
"""
            self.terminal.append(info)

        elif cmd=="scan":

            if self.scan_window is None:
                self.scan_window = ScanWindow()

            self.scan_window.show()

        elif cmd=="net":

            net = psutil.net_if_addrs()

            for i in net:
                self.terminal.append(i)

        elif cmd=="process":

            for p in psutil.process_iter(['name','cpu_percent']):
                self.terminal.append(
                    f"{p.info['name']} {p.info['cpu_percent']}%"
                )

        elif cmd=="exit":
            sys.exit()

    def run_system(self,cmd):

        try:
            result = subprocess.check_output(
                cmd,
                shell=True,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )

        except Exception as e:
            result=str(e)

        self.terminal.append(result)

    # -------- STATS --------

    def update_stats(self):

        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent

        self.cpu_bar.setValue(int(cpu))
        self.ram_bar.setValue(int(ram))
        self.disk_bar.setValue(int(disk))

        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.clock.setText(now)

        net = psutil.net_io_counters()

        down=(net.bytes_recv-self.last_net.bytes_recv)/1024
        up=(net.bytes_sent-self.last_net.bytes_sent)/1024

        self.network.setText(f"DOWN {down:.1f} KB/s\nUP {up:.1f} KB/s")

        self.last_net = net

        procs=sorted(
            psutil.process_iter(['name','cpu_percent']),
            key=lambda p:p.info['cpu_percent'],
            reverse=True
        )[:5]

        txt=""
        for p in procs:
            txt+=f"{p.info['name']} {p.info['cpu_percent']}%\n"

        self.processes.setText(txt)

    def start_updates(self):

        timer = QTimer(self)
        timer.timeout.connect(self.update_stats)
        timer.start(1000)

# ---------------- MAIN ----------------

app = QApplication(sys.argv)
window = IronTerminal()
terminal_window = window
window.show()
sys.exit(app.exec())