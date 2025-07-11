import os
import subprocess
import sys


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
    audio_path = os.path.abspath(audio_path)
    output_dir = os.path.dirname(audio_path)
    base_name = os.path.splitext(os.path.basename(audio_path))[0]
    default_output = os.path.join(output_dir, f"{base_name}.txt")
    target_output = os.path.join(output_dir, f"{base_name}_transc.txt")

    if env_path:
        python_exe = os.path.join(env_path, "Scripts", "python.exe") if os.name == "nt" else os.path.join(env_path, "bin", "python")
        if not os.path.exists(python_exe):
            raise RuntimeError(f"No se encontró el intérprete de Python en {python_exe}")
        cmd = [python_exe, "-m", "whisper", audio_path,
               "--model", model,
               "--output_format", "txt",
               "--output_dir", output_dir]
    else:
        cmd = [sys.executable, "-m", "whisper", audio_path,
               "--model", model,
               "--output_format", "txt",
               "--output_dir", output_dir]

    if language:
        cmd.extend(["--language", language])

    cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "whisper")
    model_file = os.path.join(cache_dir, f"{model}.pt")
    if status_cb and not os.path.exists(model_file):
        status_cb("Descargando modelo...")

    if status_cb:
        status_cb("Transcribiendo audio...")

    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        msg = e.stderr.strip() or e.stdout.strip() or str(e)
        raise RuntimeError(f"Error al ejecutar Whisper: {msg}")

    if not os.path.exists(default_output):
        raise RuntimeError(f"No se encontró el archivo de salida esperado: {default_output}")

    try:
        os.replace(default_output, target_output)
        if status_cb:
            status_cb("Transcripción finalizada")
    except Exception as e:
        raise RuntimeError(f"Error al mover el archivo de salida: {e}")

    if not os.path.exists(target_output) or os.path.getsize(target_output) <= 0:
        raise RuntimeError('Transcripción vacía')

    return target_output
