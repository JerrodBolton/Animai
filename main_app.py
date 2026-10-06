"""Animai Kingdom - typed conversation prototype.

Chat with an animal companion in the terminal. The character's personality
comes from characters.py, and the replies come from Claude.

Run it with:  python main_app.py
"""

import anthropic
from dotenv import load_dotenv

from characters import SHARK

MODEL = "claude-opus-5-5"
EXIT_WORDS = {"exit", "quit", "bye", "goodbye"}


def build_system_prompt(character):
    """Turn a character dictionary into instructions for the AI model."""
    return (
        f"You are {character['name']}, a {character['animal']} who lives in "
        f"Animai Kingdom and works as a desk companion for the user.\n\n"
        f"Personality: {character['personality']}\n\n"
        f"Backstory: {character['backstory']}\n\n"
        f"Speaking style: {character['speaking_style']}\n\n"
        f"You help with: {character['helps_with']}\n\n"
        "Stay in character at all times. Your replies will be spoken aloud, "
        "so keep them to two or three short sentences and use plain words "
        "only: no lists, no markdown, no emoji. Latency-sensitive; begin your "
        "answer immediately."
    )


def is_exit_command(text):
    """Check if the user wants to end the conversation."""
    return text.strip().lower().strip(".!") in EXIT_WORDS


class Companion:
    """An animal companion that remembers the conversation."""

    def __init__(self, character, client=None):
        self.character = character
        self.system_prompt = build_system_prompt(character)
        self.client = client or anthropic.Anthropic()
        self.messages = []

    def reply(self, user_text):
        """Send what the user said to the AI model and return the reply."""
        self.messages.append({"role": "user", "content": user_text})

        response = self.client.beta.messages.create(
            model=MODEL,
            max_tokens=2000,
            system=self.system_prompt,
            messages=self.messages,
            output_config={"effort": "low"},
            # If the model declines a request, retry it on a fallback model.
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )

        # Keep the full response (not just the text) so the history stays valid.
        self.messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "refusal":
            return "That's not something I can help with. Pick another target."

        text = "".join(block.text for block in response.content if block.type == "text")
        return text.strip()


def main():
    load_dotenv()
    companion = Companion(SHARK)
    name = SHARK["name"]

    print(f"{name}: {SHARK['greeting']}")
    print("(Type 'exit' to quit.)\n")

    while True:
        try:
            user_text = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user_text:
            continue
        if is_exit_command(user_text):
            break

        try:
            answer = companion.reply(user_text)
        except anthropic.AuthenticationError:
            print("Error: no valid API key. Add ANTHROPIC_API_KEY to your .env file.")
            break
        except anthropic.APIConnectionError:
            print("Error: can't reach the AI service. Check your internet connection.")
            companion.messages.pop()
            continue
        except anthropic.APIStatusError as e:
            print(f"Error from the AI service ({e.status_code}): {e.message}")
            companion.messages.pop()
            continue

        print(f"{name}: {answer}\n")

    print(f"{name}: {SHARK['farewell']}")


if __name__ == "__main__":
    main()
