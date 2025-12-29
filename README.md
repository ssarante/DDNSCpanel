# DDNSAgent – Dynamic DNS Agent para cPanel (Windows)

DDNSAgent es una aplicación ligera para **Windows** que permite actualizar
automáticamente un **Dynamic DNS (DDNS)** en **cPanel** mediante una **URL personalizada**.

Está pensada para entornos con **IP dinámica**, funcionando en segundo plano,
con interfaz gráfica, arranque automático con Windows y minimización a la bandeja
del sistema.

---

## 🚀 Características

- ✅ Actualización DDNS mediante URL HTTP
- 🖥️ Interfaz gráfica moderna
- ⚙️ Configuración simple (URL + intervalo)
- 🔁 Primera ejecución inmediata
- ⏱️ Intervalo configurable en minutos
- 🔔 Minimiza a la bandeja del sistema (tray)
- 🔄 Inicio automático con Windows (Startup Folder)
- 💾 Configuración persistente (`config.json`)
- 📦 Ejecutable independiente (no requiere Python)

---

## 📁 Estructura de Archivos (Producción)

```text
C:\DDNSAgent\
 ├── DDNSAgent.exe
 └── config.json



AUTOR
Samuel Sarante
República Dominicana

Requisitos (Modo Desarrollo)
Windows 10 / 11
Python 3.9 o superior

Dependencias
pip install customtkinter pystray pillow requests pywin32

Compilar a EXE (Modo Producción)

Para generar el ejecutable final sin necesidad de Python instalado:
pyinstaller --onefile --noconsole --name DDNSAgent ddnscpanel.py


El archivo resultante se genera en:
dist\DDNSAgent.exe
