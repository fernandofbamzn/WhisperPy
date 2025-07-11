import os
import sys
import tempfile
from pathlib import Path
from unittest import mock

import pytest

import subprocess
import io

sys.path.append(str(Path(__file__).resolve().parents[1]))
from transcriber import transcribe_audio


def fake_popen(cmd, stdout=subprocess.PIPE, stderr=None, text=True, encoding='utf-8', env=None, **kwargs):
    # Simulate whisper by creating output file and returning dummy process
    output_dir = Path(cmd[cmd.index('--output_dir') + 1])
    audio_index = cmd.index('whisper') + 1
    audio_path = Path(cmd[audio_index])
    default_output = output_dir / f"{audio_path.stem}.txt"
    default_output.write_text('dummy')

    class DummyProc:
        def __init__(self):
            self.stdout = io.StringIO('')
            self.returncode = 0

        def wait(self):
            return self.returncode

    return DummyProc()


def test_transcriber_handles_space_in_path(tmp_path):
    space_dir = tmp_path / "dir with space"
    space_dir.mkdir()
    audio_file = space_dir / "audio.wav"
    audio_file.write_text("fake")

    with mock.patch('subprocess.Popen', side_effect=fake_popen):
        result = transcribe_audio(str(audio_file), model='base', language='en')

    assert Path(result).exists()
    assert Path(result).parent == space_dir
    assert Path(result).name == 'audio_base.txt'
