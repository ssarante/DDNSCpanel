# -*- coding: utf-8 -*-

import customtkinter as ctk
import threading
import time
import json
import os
import requests
import sys
import shutil
from datetime import datetime
from PIL import Image

# ========= DETECTAR MODO =========
IS_EXE = getattr(sys, 'frozen', False)

# ========= RUTAS =========
BASE_DIR = r"C:\DDNSAgent"
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# ========= APP =========

class DDNSAgent(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.running = False
        self.tray = None

        # Preparación segura
        self.ensure_base_dir()

        if IS_EXE:
            self.ensure_exe_location()
            self.ensure_startup()

        self.load_config()

        # UI
        self.title("Dynamic DNS Agent")
        self.geometry("460x360")
        self.resizable(False, False)

        ctk.CTkLabel(
            self,
            text="Dynamic DNS Agent",
            font=("Segoe UI", 22, "bold")
        ).pack(pady=12)

        self.status_label = ctk.CTkLabel(self, text="Estado: Detenido", text_color="red")
        self.status_label.pack()

        self.last_run_label = ctk.CTkLabel(self, text="Última ejecución: --")
        self.last_run_label.pack(pady=5)

        self.url_entry = self.create_entry(
            "URL DDNS",
            self.config.get("url", "")
        )

        self.interval_entry = self.create_entry(
            "Intervalo (minutos)",
            str(self.config.get("interval", 5))
        )

        ctk.CTkButton(self, text="Guardar configuración", command=self.save_config).pack(pady=8)
        ctk.CTkButton(self, text="Iniciar", command=self.start_agent).pack()

        if IS_EXE:
            ctk.CTkButton(self, text="Minimizar a bandeja", command=self.minimize_to_tray).pack(pady=10)

        # Arranque automático
        if self.config.get("url"):
            self.start_agent()

    # ========= PREPARACIÓN =========

    def ensure_base_dir(self):
        os.makedirs(BASE_DIR, exist_ok=True)

    def ensure_exe_location(self):
        exe_path = sys.executable
        target = os.path.join(BASE_DIR, os.path.basename(exe_path))

        if exe_path.lower() != target.lower():
            try:
                shutil.copy(exe_path, target)
                os.startfile(target)
                sys.exit(0)
            except Exception:
                pass

    def ensure_startup(self):
        try:
            import win32com.client

            startup = os.path.join(
                os.environ["APPDATA"],
                "Microsoft",
                "Windows",
                "Start Menu",
                "Programs",
                "Startup"
            )

            shortcut_path = os.path.join(startup, "DDNSAgent.lnk")

            if not os.path.exists(shortcut_path):
                shell = win32com.client.Dispatch("WScript.Shell")
                shortcut = shell.CreateShortcut(shortcut_path)
                shortcut.TargetPath = os.path.join(BASE_DIR, os.path.basename(sys.executable))
                shortcut.WorkingDirectory = BASE_DIR
                shortcut.WindowStyle = 7
                shortcut.Description = "Dynamic DNS Agent"
                shortcut.Save()

        except Exception:
            pass

    # ========= UI =========

    def create_entry(self, label, value):
        frame = ctk.CTkFrame(self)
        frame.pack(fill="x", padx=30, pady=6)

        ctk.CTkLabel(frame, text=label, width=140, anchor="w").pack(side="left")
        entry = ctk.CTkEntry(frame)
        entry.pack(side="right", fill="x", expand=True)
        entry.insert(0, value)
        return entry

    # ========= CONFIG =========

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                self.config = json.load(f)
        else:
            self.config = {}

    def save_config(self):
        try:
            interval = int(self.interval_entry.get())
        except ValueError:
            self.status_label.configure(text="Intervalo inválido", text_color="orange")
            return

        self.config = {
            "url": self.url_entry.get().strip(),
            "interval": interval
        }

        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=4)

        self.status_label.configure(text="Configuración guardada", text_color="green")

    # ========= CORE =========

    def start_agent(self):
        if self.running:
            return

        self.running = True
        self.status_label.configure(text="Estado: Ejecutándose", text_color="green")
        threading.Thread(target=self.loop, daemon=True).start()

    def loop(self):
        self.execute()
        while self.running:
            time.sleep(self.config.get("interval", 5) * 60)
            self.execute()

    def execute(self):
        url = self.url_entry.get().strip()
        if not url:
            self.status_label.configure(text="URL DDNS no configurada", text_color="orange")
            return

        try:
            r = requests.get(url, timeout=15)
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if r.status_code == 200:
                self.status_label.configure(text="Actualización exitosa", text_color="green")
            else:
                self.status_label.configure(text=f"HTTP {r.status_code}", text_color="red")

            self.last_run_label.configure(text=f"Última ejecución: {now}")

        except Exception as e:
            self.status_label.configure(text=f"Error: {e}", text_color="red")

    # ========= TRAY (solo EXE) =========

    def minimize_to_tray(self):
        from pystray import Icon, MenuItem, Menu

        self.withdraw()
        image = Image.new("RGB", (64, 64), "blue")

        menu = Menu(
            MenuItem("Abrir", self.restore),
            MenuItem("Salir", self.exit_app)
        )

        self.tray = Icon("DDNSAgent", image, "Dynamic DNS Agent", menu)
        threading.Thread(target=self.tray.run, daemon=True).start()

    def restore(self, icon=None, item=None):
        if self.tray:
            self.tray.stop()
            self.tray = None
        self.deiconify()

    def exit_app(self, icon=None, item=None):
        if self.tray:
            self.tray.stop()
        self.running = False
        self.destroy()
        sys.exit(0)

# ========= MAIN =========

if __name__ == "__main__":
    app = DDNSAgent()
    app.mainloop()
