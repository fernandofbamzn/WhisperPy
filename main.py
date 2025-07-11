import os
import sys
import tkinter as tk
import logging
from pathlib import Path
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
    base_dir = Path(__file__).resolve().parent
    env_path = base_dir / ENV_NAME
    manager = EnvironmentManager()
    manager.create_env(env_path)
    manager.install_dependencies(env_path, ["openai-whisper", "requests"])

    running_env = Path(sys.prefix).resolve()
    target_env = env_path.resolve()
    if running_env != target_env:
        python_exec = (
            env_path / "Scripts" / "python.exe"
            if os.name == "nt"
            else env_path / "bin" / "python"
        )
        logger.info("Reiniciando aplicación en el entorno virtual...")
        os.execv(str(python_exec), [str(python_exec)] + sys.argv)

    return str(env_path)


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
