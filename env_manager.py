import os
import subprocess
import venv
import logging
from pathlib import Path
from typing import List


logger = logging.getLogger(__name__)


class EnvironmentManager:
    """Utility class to manage virtual environments."""

    def create_env(self, path: str | Path) -> None:
        """Create a virtual environment if it does not already exist."""
        p = Path(path)
        if not p.is_dir():
            logger.info(f"Creando entorno virtual en: {p}")
            venv.create(p, with_pip=True)

    def install_dependencies(self, env_path: str | Path, packages: List[str]) -> None:
        """Install the given packages into the virtual environment."""
        if not packages:
            return

        env_path = Path(env_path)
        python_exe = (
            env_path / "Scripts" / "python.exe"
            if os.name == "nt"
            else env_path / "bin" / "python"
        )
        logger.info("Verificando dependencias...")
        to_install: List[str] = []

        for pkg in packages:
            try:
                subprocess.run(
                    [str(python_exe), "-m", "pip", "show", pkg],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=True,
                )
                print(f"  '{pkg}' ya está instalado")
            except subprocess.CalledProcessError:
                logger.info(f"  '{pkg}' no está instalado")
                to_install.append(pkg)

        if not to_install:
            logger.info("Todas las dependencias están satisfechas.")
            return

        logger.info(f"Instalando dependencias: {' '.join(to_install)}")
        cmd = [str(python_exe), "-m", "pip", "install", *to_install]

        subprocess.check_call(cmd)
        print("Instalación completada")
        
    @staticmethod
    def check_ffmpeg_executable() -> bool:
        """Comprueba si el ejecutable de FFmpeg está disponible en el PATH."""
        try:
            # Intentar ejecutar ffmpeg -version para verificar su presencia
            subprocess.run(
                ["ffmpeg", "-version"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )
            logger.info("FFmpeg encontrado en el sistema.")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning(
                "FFmpeg no encontrado o no accesible en el PATH del sistema."
            )
            return False