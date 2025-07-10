import os
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
from model_manager import WhisperModelManager
import shlex
import wave

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
