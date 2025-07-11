import os
import sys
import tkinter as tk

from env_manager import EnvironmentManager
from gui import WhisperGUI

ENV_NAME = "WhispVenv"


def prepare_env() -> str:
    """Ensure the WhispVenv environment exists and relaunch under it."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(base_dir, ENV_NAME)
    manager = EnvironmentManager()
    manager.create_env(env_path)
    manager.install_dependencies(env_path, ["openai-whisper", "requests"])

    running_env = os.path.abspath(sys.prefix)
    target_env = os.path.abspath(env_path)
    if running_env != target_env:
        python_exec = os.path.join(env_path, "Scripts", "python.exe") if os.name == "nt" else os.path.join(env_path, "bin", "python")
        print("Reiniciando aplicación en el entorno virtual...")
        os.execv(python_exec, [python_exec] + sys.argv)

    return env_path


if __name__ == "__main__":
    prepare_env()
    root = tk.Tk()
    app = WhisperGUI(root)
    root.mainloop()
