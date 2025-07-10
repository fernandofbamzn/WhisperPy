import os
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import requests
import json
from typing import Dict
import shlex
import wave

from env_manager import EnvironmentManager

class WhisperModelManager:
    FALLBACK_MODELS = {
        "tiny": "Muy rápido, baja precisión (~39 MB)",
        "base": "Rápido, precisión media (~74 MB)",
        "small": "Compromiso velocidad/precisión (~244 MB)",
        "medium": "Precisión alta, más lento (~769 MB)",
        "large": "Máxima precisión, muy lento (~1.5 GB)",
    }

    @staticmethod
    def obtener_modelos_online() -> Dict[str, str]:
        try:
            url = "https://huggingface.co/api/models?search=openai/whisper"
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            modelos = {m['id'].replace('openai/whisper-', ''): WhisperModelManager.FALLBACK_MODELS.get(m['id'].split('-')[-1], "Modelo disponible")
                      for m in data if 'openai/whisper-' in m.get('id', '')}
            return modelos or WhisperModelManager.FALLBACK_MODELS
        except Exception:
            return WhisperModelManager.FALLBACK_MODELS

class WhisperGUI:
    def __init__(self, master):
        self.master = master
        master.title("🎙️ Transcriptor Whisper Avanzado")
        master.geometry("800x900")
        self.usar_entorno = tk.BooleanVar(master=self.master, value=False)
        self.modelo = tk.StringVar(master=self.master, value="medium")
        self.idioma = tk.StringVar(master=self.master, value="es")
        self.env_manager = EnvironmentManager()
        self.env_path = os.path.join(os.getcwd(), "env")

        ttk.Checkbutton(master, text="Usar entorno", variable=self.usar_entorno).pack(pady=5)
        ttk.Button(master, text="Preparar entorno", command=self.preparar_entorno).pack(pady=5)

    def preparar_entorno(self):
        """Create and prepare the virtual environment if selected."""
        if self.usar_entorno.get():
            self.env_manager.create_env(self.env_path)
            try:
                self.env_manager.install_dependencies(self.env_path, ["whisper"])
                messagebox.showinfo("Entorno", "Entorno preparado correctamente")
            except subprocess.CalledProcessError as exc:
                messagebox.showerror("Entorno", f"Error instalando dependencias: {exc}")


if __name__ == "__main__":
    root = tk.Tk()
    app = WhisperGUI(root)
    root.mainloop()
