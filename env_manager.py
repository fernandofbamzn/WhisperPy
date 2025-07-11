import os
import subprocess
import venv
from typing import List


class EnvironmentManager:
    """Utility class to manage virtual environments."""

    def create_env(self, path: str) -> None:
        """Create a virtual environment if it does not already exist."""
        if not os.path.isdir(path):
            print(f"Creando entorno virtual en: {path}")
            venv.create(path, with_pip=True)

    def install_dependencies(self, env_path: str, packages: List[str]) -> None:
        """Install the given packages into the virtual environment."""
        if not packages:
            return

        python_exe = os.path.join(
            env_path,
            "Scripts",
            "python.exe",
        ) if os.name == "nt" else os.path.join(env_path, "bin", "python")

        print("Verificando dependencias...")
        to_install: List[str] = []

        for pkg in packages:
            try:
                subprocess.run(
                    [python_exe, "-m", "pip", "show", pkg],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=True,
                )
                print(f"  '{pkg}' ya está instalado")
            except subprocess.CalledProcessError:
                print(f"  '{pkg}' no está instalado")
                to_install.append(pkg)

        if not to_install:
            print("Todas las dependencias están satisfechas.")
            return

        print(f"Instalando dependencias: {' '.join(to_install)}")
        cmd = [python_exe, "-m", "pip", "install", *to_install]
        subprocess.check_call(cmd)
        print("Instalación completada")
