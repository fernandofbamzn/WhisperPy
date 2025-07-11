import os
import subprocess
import sys
import logging
from pathlib import Path
from env_manager import EnvironmentManager  # Importar EnvironmentManager


logger = logging.getLogger(__name__)


def convert_audio(input_path: str) -> str:
    """Convert an audio file to WAV using FFmpeg and return the new path."""
    if not EnvironmentManager.check_ffmpeg_executable():
        msg = (
            "Se requiere FFmpeg para convertir el archivo de audio. "
            "FFmpeg no se encontró en el sistema o no está en el PATH."
        )
        logger.error(msg)
        raise RuntimeError(msg)

    output_path = os.path.splitext(input_path)[0] + ".wav"
    logger.info("Convirtiendo %s a %s", input_path, output_path)
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", input_path, output_path], check=True
        )
    except subprocess.CalledProcessError as e:
        logger.error("Error al convertir audio: %s", e)
        raise RuntimeError(f"Error al convertir audio: {e}")

    return output_path


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
        Also if FFmpeg is required but not found.
    """
    audio_path = Path(audio_path).resolve()
    output_dir = audio_path.parent
    base_name = audio_path.stem
    file_extension = audio_path.suffix.lower()  # Obtener la extensión del archivo


    default_output = output_dir / f"{base_name}.txt"
    target_output = output_dir / f"{base_name}_transc.txt"
    logger.info("Preparando transcripción de %s", audio_path)

    supported = {".wav", ".m4a", ".mp3", ".ogg", ".flac", ".webm"}
    audio_for_whisper = audio_path

    # Convertir archivos con extensiones desconocidas a WAV
    if file_extension not in supported:
        if status_cb:
            status_cb("Convirtiendo audio...")
        audio_for_whisper = convert_audio(audio_path)
    # Verificar FFmpeg para extensiones que dependen de él
    elif file_extension in [".m4a", ".mp3", ".ogg", ".flac", ".webm"]:
        if not EnvironmentManager.check_ffmpeg_executable():
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

    # Configuración de los comandos y entorno para el subproceso de Whisper
    # Crear un diccionario de entorno copiando el actual y configurando PYTHONIOENCODING
    whisper_env = os.environ.copy()
    whisper_env['PYTHONIOENCODING'] = 'utf-8'

    if env_path:
        env_path = Path(env_path)
        python_exe = (
            env_path / "Scripts" / "python.exe"
            if os.name == "nt"
            else env_path / "bin" / "python"
        )
        if not python_exe.exists():
            raise RuntimeError(f"No se encontró el intérprete de Python en {python_exe}")
        cmd = [python_exe, "-m", "whisper", audio_for_whisper,
               "--model", model,
               "--output_format", "txt",
               "--output_dir", str(output_dir)]
        logger.info("Usando intérprete de entorno: %s", python_exe)
    else:
        cmd = [sys.executable, "-m", "whisper", audio_for_whisper,
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
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', check=True, env=whisper_env)
        # Registramos la salida estándar y de error para depuración, incluso si no hay error
        if result.stdout:
            logger.info("Salida estándar de Whisper:\n%s", result.stdout.strip())
        if result.stderr:
            logger.warning("Salida de error de Whisper:\n%s", result.stderr.strip())

    except subprocess.CalledProcessError as e:
        msg = e.stderr.strip() or e.stdout.strip() or str(e)
        logger.error("Error al ejecutar Whisper: %s", msg)
        raise RuntimeError(f"Error al ejecutar Whisper: {msg}")

    if not os.path.exists(default_output):
        error_msg = f"No se encontró el archivo de salida esperado: {default_output}. " \
                    "Verifica los logs anteriores para posibles errores de Whisper."
        logger.error(error_msg)
        raise RuntimeError(error_msg)


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

    return target_output


def diarize_transcription(audio_path: str, transcript_file: str, status_cb=None) -> str:
    """Assign speaker labels to the transcription using whisperx.

    Parameters
    ----------
    audio_path : str
        Path to the audio file.
    transcript_file : str
        Path to the transcription text generated by :func:`transcribe_audio`.
    status_cb : callable, optional
        Callback to emit status messages during the process.

    Returns
    -------
    str
        Path to the new transcription file with speaker labels.
    """

    try:
        import torch
        import whisperx
    except Exception as exc:  # pragma: no cover - handled at runtime
        raise RuntimeError(
            "La biblioteca 'whisperx' no está instalada: " f"{exc}"
        ) from exc

    device = "cuda" if torch.cuda.is_available() else "cpu"
    if status_cb:
        status_cb("Asignando hablantes...")

    model = whisperx.load_model("small", device)
    result = model.transcribe(audio_path)
    diarize_model = whisperx.DiarizationPipeline(use_auth_token=None, device=device)
    diarize_segments = diarize_model(audio_path)
    result = whisperx.assign_word_speakers(diarize_segments, result)

    out_file = os.path.splitext(transcript_file)[0] + "_spk.txt"
    with open(out_file, "w", encoding="utf-8") as fh:
        for seg in result.get("segments", []):
            spk = seg.get("speaker", "SPEAKER")
            text = seg.get("text", "").strip()
            fh.write(f"{spk}: {text}\n")

    logger.info("Archivo con hablantes guardado en %s", out_file)
    return out_file

