import os
import sys
import tempfile
from pathlib import Path
from unittest import mock

import pytest

import subprocess

sys.path.append(str(Path(__file__).resolve().parents[1]))
from transcriber import transcribe_audio


def fake_run(cmd, capture_output=True, text=True, encoding='utf-8', check=True):
    # Simulate whisper by creating output file
    output_dir = Path(cmd[cmd.index('--output_dir') + 1])
    audio_index = cmd.index('whisper') + 1
    audio_path = Path(cmd[audio_index])
    default_output = output_dir / f"{audio_path.stem}.txt"
    default_output.write_text('dummy')
    return subprocess.CompletedProcess(cmd, 0, stdout='ok', stderr='')


def test_transcriber_handles_space_in_path(tmp_path):
    space_dir = tmp_path / "dir with space"
    space_dir.mkdir()
    audio_file = space_dir / "audio.wav"
    audio_file.write_text("fake")

    with mock.patch('subprocess.run', side_effect=fake_run):
        result = transcribe_audio(str(audio_file), model='base', language='en')

    assert Path(result).exists()
    assert Path(result).parent == space_dir
