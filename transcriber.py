import os
import subprocess
import sys
import logging
from pathlib import Path
from env_manager import EnvironmentManager  # Importar EnvironmentManager

logger = logging.getLogger(__name__)


def transcribe_audio(audio_path, model, language, env_path=None, status_cb=None):
    """Transcribe an audio file using Whisper.

    Parameters
    ----------
    audio_path : str
        Path to the audio file.
    model : str
        Whisper model to use.
    language : str
        Language of the audio.
    env_path : str, optional
        Path to a virtual environment whose Python interpreter should be
        used to run Whisper. If not provided, the system's default
        interpreter will be used.
    status_cb : callable, optional
        Function called with status messages during the process.

    Returns
    -------
    str
        Path to the generated transcription file.

    Raises
    ------
    RuntimeError
        If Whisper execution fails or the output file is not created.
    """
    audio_path = Path(audio_path).resolve()
    output_dir = audio_path.parent
    base_name = audio_path.stem
    file_extension = audio_path.suffix.lower()  # Obtener la extensión del archivo

    default_output = output_dir / f"{base_name}.txt"
    target_output = output_dir / f"{base_name}_transc.txt"
    logger.info("Preparando transcripción de %s", audio_path)
    
    # Formatos de audio comunes que definitivamente necesitan FFmpeg para ser procesados por Whisper.
    # Los archivos WAV a veces pueden ser procesados sin FFmpeg si cumplen ciertos requisitos.
    if file_extension in ['.m4a', '.mp3', '.ogg', '.flac', '.webm']: # Puedes añadir más extensiones si es necesario
        if not EnvironmentManager.check_ffmpeg_executable(): # Utiliza el método estático de EnvironmentManager
            msg = (
                f"El archivo '{audio_path.name}' es de tipo '{file_extension}' "
                "y requiere FFmpeg para su procesamiento. "
                "FFmpeg no se encontró en el sistema o no está en el PATH. "
                "Por favor, instala FFmpeg y asegúrate de que esté accesible. "
                "Puedes descargarlo desde: https://ffmpeg.org/download.html"
            )
            logger.error(msg)
            if status_cb:
                status_cb(f"ERROR: {msg}")
            raise RuntimeError(msg)
    if env_path:
        env_path = Path(env_path)
        python_exe = (
            env_path / "Scripts" / "python.exe"
            if os.name == "nt"
            else env_path / "bin" / "python"
        )
        if not python_exe.exists():
            raise RuntimeError(f"No se encontró el intérprete de Python en {python_exe}")
        cmd = [str(python_exe), "-m", "whisper", str(audio_path),
               "--model", model,
               "--output_format", "txt",
               "--output_dir", str(output_dir)]
        logger.info("Usando intérprete de entorno: %s", python_exe)
    else:
        cmd = [sys.executable, "-m", "whisper", str(audio_path),
               "--model", model,
               "--output_format", "txt",
               "--output_dir", str(output_dir)]
        logger.info("Usando intérprete actual: %s", sys.executable)

    if language:
        cmd.extend(["--language", language])
    logger.info("Ejecutando comando: %s", " ".join(cmd))

    cache_dir = Path(os.path.expanduser("~")) / ".cache" / "whisper"
    model_file = cache_dir / f"{model}.pt"
    if status_cb and not model_file.exists():
        status_cb("Descargando modelo...")

    if status_cb:
        status_cb("Transcribiendo audio...")
    logger.info("Iniciando transcripción con modelo %s", model)

    try:
        # Almacenamos el resultado de subprocess.run para acceder a stdout/stderr
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', check=True)
        
        # Registramos la salida estándar y de error para depuración, incluso si no hay error
        if result.stdout:
            logger.info("Salida estándar de Whisper:\n%s", result.stdout.strip())
        if result.stderr:
            logger.warning("Salida de error de Whisper:\n%s", result.stderr.strip())

    except subprocess.CalledProcessError as e:
        msg = e.stderr.strip() or e.stdout.strip() or str(e)
        logger.error("Error al ejecutar Whisper: %s", msg)
        raise RuntimeError(f"Error al ejecutar Whisper: {msg}")

    if not default_output.exists():
        raise RuntimeError(f"No se encontró el archivo de salida esperado: {default_output}")

    try:
        os.replace(default_output, target_output)
        if status_cb:
            status_cb("Transcripción finalizada")
        logger.info("Transcripción finalizada: %s", target_output)
    except Exception as e:
        logger.error("Error al mover el archivo de salida: %s", e)
        raise RuntimeError(f"Error al mover el archivo de salida: {e}")

    if not target_output.exists() or target_output.stat().st_size <= 0:
        raise RuntimeError('Transcripción vacía')

    return str(target_output)
