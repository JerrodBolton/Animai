import os
from types import SimpleNamespace

import numpy as np

import voice
from characters import SHARK
from main_app import Companion, build_system_prompt, is_exit_command


class FakeClient:
    """Stands in for the Anthropic client so tests don't call the real API."""

    def __init__(self, reply_text, stop_reason="end_turn"):
        self.calls = []
        self.reply_text = reply_text
        self.stop_reason = stop_reason
        self.beta = SimpleNamespace(messages=SimpleNamespace(create=self.create))

    def create(self, **kwargs):
        # Copy the history, since the app keeps appending to the same list.
        self.calls.append({**kwargs, "messages": list(kwargs["messages"])})
        return SimpleNamespace(
            content=[SimpleNamespace(type="text", text=self.reply_text)],
            stop_reason=self.stop_reason,
        )


def test_system_prompt_includes_character():
    prompt = build_system_prompt(SHARK)
    assert SHARK["name"] in prompt
    assert SHARK["personality"] in prompt
    assert SHARK["backstory"] in prompt


def test_exit_commands():
    assert is_exit_command("exit") is True
    assert is_exit_command("  Bye! ") is True
    assert is_exit_command("help me focus") is False


def test_reply_returns_model_text():
    companion = Companion(SHARK, client=FakeClient("Stay sharp."))
    assert companion.reply("hello") == "Stay sharp."


def test_reply_remembers_conversation():
    client = FakeClient("Keep swimming.")
    companion = Companion(SHARK, client=client)
    companion.reply("first")
    companion.reply("second")

    roles = [m["role"] for m in client.calls[-1]["messages"]]
    assert roles == ["user", "assistant", "user"]
    assert client.calls[-1]["system"] == companion.system_prompt


def test_refusal_gets_in_character_reply():
    companion = Companion(SHARK, client=FakeClient("", stop_reason="refusal"))
    assert "not something I can help with" in companion.reply("something off limits")


def test_audio_level_is_louder_for_louder_sound():
    quiet = np.full(1600, 10, dtype=np.int16)
    loud = np.full(1600, 2000, dtype=np.int16)
    assert voice.audio_level(loud) > voice.audio_level(quiet)
    assert voice.audio_level(np.zeros(1600, dtype=np.int16)) == 0


def test_listen_returns_empty_when_speech_not_understood(monkeypatch):
    class FakeRecognizer:
        def recognize_google(self, audio):
            raise voice.sr.UnknownValueError()

    monkeypatch.setattr(voice, "record_until_silence", lambda: b"\x00\x00" * 1600)
    monkeypatch.setattr(voice.sr, "Recognizer", FakeRecognizer)
    assert voice.listen() == ""


def test_speak_cleans_up_audio_file_even_on_error(monkeypatch):
    saved_files = []

    class FakeTTS:
        def __init__(self, text, lang):
            pass

        def save(self, path):
            saved_files.append(path)

    def broken_player(path):
        raise RuntimeError("no speaker")

    monkeypatch.setattr(voice, "gTTS", FakeTTS)
    monkeypatch.setattr(voice, "playsound", broken_player)
    voice.speak("Stay sharp.")

    assert len(saved_files) == 1
    assert not os.path.exists(saved_files[0])
