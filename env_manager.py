import os
import subprocess
import venv
import logging
from typing import List


logger = logging.getLogger(__name__)


class EnvironmentManager:
    """Utility class to manage virtual environments."""

    def create_env(self, path: str) -> None:
        """Create a virtual environment if it does not already exist."""
        if not os.path.isdir(path):
            logger.info(f"Creando entorno virtual en: {path}")
            venv.create(path, with_pip=True)

    def install_dependencies(self, env_path: str, packages: List[str]) -> None:
        """Install the given packages into the virtual environment."""
        if not packages:
            return
        python_exe = os.path.join(env_path, 'Scripts', 'python.exe') if os.name == 'nt' else os.path.join(env_path, 'bin', 'python')
        logger.info("Instalando dependencias...")
        cmd = [python_exe, '-m', 'pip', 'install', *packages]
        subprocess.check_call(cmd)
