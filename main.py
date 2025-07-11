import os
import sys
import tkinter as tk
import logging
from typing import List

from env_manager import EnvironmentManager
from gui import WhisperGUI

ENV_NAME = "WhispVenv"

logger = logging.getLogger(__name__)
LOG_BUFFER: List[str] = []


class BufferHandler(logging.Handler):
    """Simple handler to store log messages before GUI is ready."""

    def emit(self, record):
        LOG_BUFFER.append(self.format(record))


def prepare_env() -> str:
    """Ensure the WhispVenv environment exists and relaunch under it."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(base_dir, ENV_NAME)
    manager = EnvironmentManager()
    manager.create_env(env_path)
    manager.install_dependencies(env_path, ["openai-whisper", "requests", "whisperx"])

    running_env = os.path.abspath(sys.prefix)
    target_env = os.path.abspath(env_path)
    if running_env != target_env:
        python_exec = os.path.join(env_path, "Scripts", "python.exe") if os.name == "nt" else os.path.join(env_path, "bin", "python")
        logger.info("Reiniciando aplicación en el entorno virtual...")
        os.execv(python_exec, [python_exec] + sys.argv)

    return env_path


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    buffer_handler = BufferHandler()
    buffer_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logging.getLogger().addHandler(buffer_handler)

    prepare_env()

    # Comprobar FFmpeg después de que prepare_env haya potencialmente reiniciado la app
    # y antes de iniciar la GUI principal. El mensaje se enviará al log.
    if not EnvironmentManager.check_ffmpeg_executable():
        logger.warning(
            "ADVERTENCIA: FFmpeg no se encontró en tu sistema o no está en el PATH. "
            "FFmpeg es esencial para procesar archivos de audio como .mp3 y .m4a. "
            "Sin él, la transcripción de estos formatos fallará. "
            "Por favor, instala FFmpeg y asegúrate de que esté en tu variable de entorno PATH. "
            "Puedes descargarlo desde: https://ffmpeg.org/download.html"
            "https://es.wikihow.com/instalar-FFmpeg-en-Windows"
            "https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z"
        )

    root = tk.Tk()
    app = WhisperGUI(root)

    for msg in LOG_BUFFER:
        app._append_message(msg)
    logging.getLogger().removeHandler(buffer_handler)

    root.mainloop()
