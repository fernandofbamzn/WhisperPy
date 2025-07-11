import os
import sys
import tkinter as tk

from gui import WhisperGUI


def ensure_venv():
    """Reejecuta el script usando la venv local si existe y no estamos en una."""
    # Comprobamos si no se ejecuta ya en un entorno virtual
    in_venv = sys.prefix != getattr(sys, "base_prefix", sys.prefix)
    if in_venv:
        return

    base_dir = os.path.dirname(os.path.abspath(__file__))
    venv_dir = os.path.join(base_dir, "venv")
    if not os.path.isdir(venv_dir):
        return

    if os.name == "nt":
        python_exec = os.path.join(venv_dir, "Scripts", "python.exe")
    else:
        python_exec = os.path.join(venv_dir, "bin", "python")

    if os.path.exists(python_exec):
        os.execv(python_exec, [python_exec] + sys.argv)


if __name__ == "__main__":
    ensure_venv()
    root = tk.Tk()
    app = WhisperGUI(root)
    root.mainloop()
