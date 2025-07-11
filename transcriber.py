import os
import subprocess
import sys
import logging
import re
from pathlib import Path
from env_manager import EnvironmentManager  # Importar EnvironmentManager


logger = logging.getLogger(__name__)


def convert_audio(input_path: str) -> str:
    """Convert an audio file to a Whisper-compatible WAV and return its path."""
    if not EnvironmentManager.check_ffmpeg_executable():
        msg = (
            "Se requiere FFmpeg para convertir el archivo de audio. "
            "FFmpeg no se encontró en el sistema o no está en el PATH."
        )
        logger.error(msg)
        raise RuntimeError(msg)

    output_path = os.path.splitext(input_path)[0] + ".wav"
    if Path(output_path).exists():
        logger.info("Usando WAV existente: %s", output_path)
        return output_path

    logger.info("Convirtiendo %s a %s", input_path, output_path)
    try:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                input_path,
                "-ar",
                "16000",
                "-ac",
                "1",
                output_path,
            ],
            check=True,
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
    target_output = output_dir / f"{base_name}_{model}.txt"
    logger.info("Preparando transcripción de %s", audio_path)

    audio_for_whisper = audio_path
    if file_extension != ".wav":
        if not EnvironmentManager.check_ffmpeg_executable():
            msg = (
                "Se requiere FFmpeg para procesar el archivo de audio. "
                "FFmpeg no se encontró en el sistema o no está en el PATH."
            )
            logger.error(msg)
            if status_cb:
                status_cb(f"ERROR: {msg}")
            raise RuntimeError(msg)
        if status_cb:
            status_cb("Convirtiendo audio...")
        audio_for_whisper = convert_audio(audio_path)

    # Configuración del entorno para Whisper
    whisper_env = os.environ.copy()
    whisper_env['PYTHONIOENCODING'] = 'utf-8'

    # Definir la ruta local para guardar los modelos
    app_base_dir = os.path.dirname(os.path.abspath(__file__))
    local_models_dir = os.path.join(app_base_dir, "models")
    os.makedirs(local_models_dir, exist_ok=True)  # Asegurarse de que la carpeta 'models' exista

    # Establecer WHISPER_CACHE_DIR para que Whisper guarde los modelos aquí
    whisper_env['WHISPER_CACHE_DIR'] = local_models_dir
    whisper_env['XDG_CACHE_HOME'] = local_models_dir
    logger.info(f"Los modelos de Whisper se gestionarán en: {local_models_dir}")

    if env_path:
        env_path = Path(env_path)
        python_exe = (
            env_path / "Scripts" / "python.exe"
            if os.name == "nt"
            else env_path / "bin" / "python"
        )
        if not python_exe.exists():
            raise RuntimeError(f"No se encontró el intérprete de Python en {python_exe}")
        cmd = [
            str(python_exe),
            "-m",
            "whisper",
            str(audio_for_whisper),
            "--model",
            model,
            "--model_dir",
            local_models_dir,
            "--output_format",
            "txt",
            "--output_dir",
            str(output_dir),
        ]
        logger.info("Usando intérprete de entorno: %s", python_exe)
    else:
        cmd = [
            sys.executable,
            "-m",
            "whisper",
            str(audio_for_whisper),
            "--model",
            model,
            "--model_dir",
            local_models_dir,
            "--output_format",
            "txt",
            "--output_dir",
            str(output_dir),
        ]
        logger.info("Usando intérprete actual: %s", sys.executable)

    if language:
        cmd.extend(["--language", language])
    logger.info("Ejecutando comando: %s", " ".join(cmd))

    model_file = Path(local_models_dir) / f"{model}.pt"
    downloading = False
    if status_cb:
        if not model_file.exists():
            status_cb("Descargando modelo...")
            downloading = True
        else:
            status_cb("Transcribiendo audio...")
    logger.info("Iniciando transcripción con modelo %s", model)

    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            env=whisper_env,
        )

        fp16_warning = "FP16 is not supported on CPU; using FP32 instead"
        # Captura las líneas de progreso "XX%|" que muestra HuggingFace durante
        # la descarga de modelos para convertirlas en un mensaje más legible
        progress_re = re.compile(r"(?P<pct>\d{1,3})%")
        for line in process.stdout:
            if downloading and model_file.exists():
                if status_cb:
                    status_cb("Transcribiendo audio...")
                downloading = False
            line = line.rstrip()
            if not line:
                continue
            if fp16_warning in line:
                logger.info("Whisper: %s", fp16_warning)
                continue
            m = progress_re.search(line)
            if m:
                pct = m.group("pct")
                msg = f"Descargando modelo... {pct}%"
                logger.info("Whisper: %s", msg)
                if status_cb:
                    status_cb(msg)
                continue
            logger.info("Whisper: %s", line)
            if status_cb:
                status_cb(line)

        process.wait()
        if process.returncode != 0:
            raise RuntimeError(f"Whisper finalizó con código {process.returncode}")

    except Exception as e:
        logger.error("Error al ejecutar Whisper: %s", e)
        raise RuntimeError(f"Error al ejecutar Whisper: {e}")

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

