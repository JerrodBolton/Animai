from types import SimpleNamespace

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
