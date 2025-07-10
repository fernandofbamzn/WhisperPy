import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Dict

try:
    import requests
except Exception:
    requests = None

try:
    import whisper
except Exception:
    whisper = None


class WhisperModelManager:
    """Obtiene modelos de Whisper."""

    FALLBACK_MODELS = {
        "tiny": "Muy rápido, baja precisión (~39 MB)",
        "base": "Rápido, precisión media (~74 MB)",
        "small": "Compromiso velocidad/precisión (~244 MB)",
        "medium": "Precisión alta, más lento (~769 MB)",
        "large": "Máxima precisión, muy lento (~1.5 GB)",
    }

    @staticmethod
    def obtener_modelos_online() -> Dict[str, str]:
        if not requests:
            return WhisperModelManager.FALLBACK_MODELS
        try:
            url = "https://huggingface.co/api/models?search=openai/whisper"
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            modelos = {
                m["id"].replace("openai/whisper-", ""): WhisperModelManager.FALLBACK_MODELS.get(
                    m["id"].split("-")[-1], "Modelo disponible"
                )
                for m in data
                if "openai/whisper-" in m.get("id", "")
            }
            return modelos or WhisperModelManager.FALLBACK_MODELS
        except Exception:
            return WhisperModelManager.FALLBACK_MODELS


class WhisperGUI:
    """Interfaz gráfica para transcribir audios."""

    IDIOMAS = ["es", "en", "fr", "de", "it", "pt"]

    def __init__(self, master: tk.Tk) -> None:
        self.master = master
        master.title("🎙️ Transcriptor Whisper Avanzado")
        master.geometry("700x500")

        self.file_path = tk.StringVar()
        self.usar_entorno = tk.BooleanVar(value=False)
        self.modelo = tk.StringVar(value="base")
        self.idioma = tk.StringVar(value="es")

        self._build_widgets()

    def _build_widgets(self) -> None:
        cont = ttk.Frame(self.master, padding=10)
        cont.pack(fill=tk.BOTH, expand=True)

        file_frame = ttk.Frame(cont)
        file_frame.pack(fill=tk.X, pady=5)
        ttk.Label(file_frame, text="Archivo de audio:").pack(side=tk.LEFT)
        ttk.Entry(file_frame, textvariable=self.file_path, width=50).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=5
        )
        ttk.Button(file_frame, text="Seleccionar", command=self.seleccionar_archivo).pack(side=tk.LEFT)

        opciones = WhisperModelManager.obtener_modelos_online()
        modelos = list(opciones.keys())

        config_frame = ttk.Frame(cont)
        config_frame.pack(fill=tk.X, pady=5)
        ttk.Label(config_frame, text="Modelo:").pack(side=tk.LEFT)
        self.combo_modelo = ttk.Combobox(config_frame, textvariable=self.modelo, values=modelos, width=15)
        self.combo_modelo.pack(side=tk.LEFT, padx=5)
        ttk.Label(config_frame, text="Idioma:").pack(side=tk.LEFT)
        self.combo_idioma = ttk.Combobox(config_frame, textvariable=self.idioma, values=self.IDIOMAS, width=5)
        self.combo_idioma.pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(config_frame, text="Usar entorno", variable=self.usar_entorno).pack(side=tk.LEFT, padx=5)

        ttk.Button(cont, text="Transcribir", command=self.iniciar_transcripcion).pack(pady=10)

        self.progress = ttk.Progressbar(cont, mode="indeterminate")
        self.progress.pack(fill=tk.X, pady=5)

        self.texto_mensajes = tk.Text(cont, height=10, state=tk.DISABLED)
        self.texto_mensajes.pack(fill=tk.BOTH, expand=True)


    def seleccionar_archivo(self) -> None:
        tipos = [
            ("Audio", "*.wav *.mp3 *.flac *.m4a"),
            ("Todos", "*.*"),
        ]
        archivo = filedialog.askopenfilename(title="Seleccionar audio", filetypes=tipos)
        if archivo:
            self.file_path.set(archivo)

    def iniciar_transcripcion(self) -> None:
        if not self.file_path.get():
            messagebox.showwarning("Aviso", "Debe seleccionar un archivo de audio")
            return
        self.progress.start()
        hilo = threading.Thread(target=self._transcribir, daemon=True)
        hilo.start()

    def _append_message(self, texto: str) -> None:
        self.texto_mensajes.configure(state=tk.NORMAL)
        self.texto_mensajes.insert(tk.END, texto + "\n")
        self.texto_mensajes.see(tk.END)
        self.texto_mensajes.configure(state=tk.DISABLED)

    def _transcribir(self) -> None:
        ruta = self.file_path.get()
        modelo = self.modelo.get()
        idioma = self.idioma.get() or None
        nombre_salida = os.path.join(
            os.path.dirname(ruta), f"{os.path.splitext(os.path.basename(ruta))[0]}_transc.txt"
        )
        if whisper is None:
            self._append_message("El paquete 'whisper' no está disponible.")
            self.progress.stop()
            return
        try:
            self._append_message("Transcribiendo...")
            modelo_whisper = whisper.load_model(modelo)
            resultado = modelo_whisper.transcribe(ruta, language=idioma)
            with open(nombre_salida, "w", encoding="utf-8") as f:
                f.write(resultado.get("text", ""))
            self._append_message(f"Transcripción completada: {nombre_salida}")
        except Exception as e:
            self._append_message(f"Error: {e}")
        finally:
            self.progress.stop()


if __name__ == "__main__":
    root = tk.Tk()
    WhisperGUI(root)
    root.mainloop()
