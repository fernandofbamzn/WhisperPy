import os
import subprocess
import venv
from typing import List


class EnvironmentManager:
    """Utility class to manage virtual environments."""

    def create_env(self, path: str) -> None:
        """Create a virtual environment if it does not already exist."""
        if not os.path.isdir(path):
            venv.create(path, with_pip=True)

    def install_dependencies(self, env_path: str, packages: List[str]) -> None:
        """Install the given packages into the virtual environment."""
        if not packages:
            return
        python_exe = os.path.join(env_path, 'Scripts', 'python.exe') if os.name == 'nt' else os.path.join(env_path, 'bin', 'python')
        cmd = [python_exe, '-m', 'pip', 'install', *packages]
        subprocess.check_call(cmd)
