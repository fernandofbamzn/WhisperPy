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
