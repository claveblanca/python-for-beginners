"""
chat.py
Core chat function and conversation history management.

The history list is the only persistent state in the application.
Every call to chat() receives the full history, builds a DialoGPT
prompt from it (turns joined by <|endoftext|>), runs inference, and
returns the updated history alongside an empty string to clear the
input box.

Note: transformers v5 removed the Conversation class. DialoGPT is
driven directly via the text-generation pipeline with EOS-delimited
prompts.

Dependencies:
    pip install transformers torch
"""

from transformers import GenerationConfig
from model import get_pipeline

# DialoGPT's maximum context window in tokens.
# Conversations longer than this will have early turns silently
# truncated by the tokeniser. MAX_TURNS enforces an explicit limit.
CONTEXT_WINDOW_TOKENS = 1024
MAX_TURNS = 20   # conservative limit; each turn consumes ~50 tokens on average


def _normalise_history(history: list) -> list[tuple[str, str]]:
    """
    Normalise Gradio history to a consistent list of (user, bot) tuples.

    Gradio ≥5 passes history as a flat list of message dicts:
        [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}, ...]
    Older Gradio passed paired tuples:
        [("user msg", "bot reply"), ...]
    Both formats are handled here.
    """
    if not history:
        return []
    # messages format: list of dicts with 'role' and 'content'
    if isinstance(history[0], dict):
        pairs = []
        messages = [m for m in history if isinstance(m.get("content"), str)]
        # zip consecutive user/assistant pairs
        i = 0
        while i < len(messages) - 1:
            if messages[i].get("role") == "user" and messages[i + 1].get("role") == "assistant":
                pairs.append((messages[i]["content"], messages[i + 1]["content"]))
                i += 2
            else:
                i += 1
        return pairs
    # tuples/lists format: [(user, bot), ...]
    return [(str(u), str(b)) for u, b in history]


def _build_prompt(history: list, user_message: str, eos: str) -> str:
    """
    Reconstruct a DialoGPT prompt from history + the new user message.

    DialoGPT expects all turns (user and bot) concatenated with EOS
    tokens as separators, ending with the new user turn + EOS so the
    model generates the next bot reply.

    Args:
        history:      Gradio history (tuples or message dicts).
        user_message: The new user message to append.
        eos:          The model's EOS token string (<|endoftext|>).

    Returns:
        A single prompt string ready for the text-generation pipeline.
    """
    parts = []
    for user_turn, bot_turn in _normalise_history(history):
        parts.append(user_turn)
        parts.append(bot_turn)
    parts.append(user_message)
    return eos.join(parts) + eos


def trim_history(history: list, max_turns: int = MAX_TURNS) -> list:
    """
    Drop the oldest turns when history exceeds max_turns.

    Prevents silent tokeniser truncation by making the context limit
    explicit and controllable. The most recent turns are kept.

    Args:
        history:   Full conversation history (any Gradio format).
        max_turns: Maximum number of (user, bot) pairs to retain.

    Returns:
        Trimmed history list, at most max_turns pairs long.
    """
    pairs = _normalise_history(history)
    if len(pairs) > max_turns:
        dropped = len(pairs) - max_turns
        print(f"[trim_history] Dropped {dropped} oldest turn(s) "
              f"to stay within the {max_turns}-turn limit.")
        pairs = pairs[-max_turns:]
    return pairs


def chat(
    user_message: str,
    history: list[tuple[str, str]],
) -> str:
    """
    Process one user turn and return the bot's reply string.

    Designed to be used as fn= for gr.ChatInterface. Gradio manages
    history state and appends each (user, bot) pair automatically —
    this function only needs to return the reply text.

    Steps:
        1. Reject blank input — return empty string.
        2. Trim history to avoid context-window overflow.
        3. Build a DialoGPT prompt from history + new message.
        4. Run inference and extract only the newly generated reply.

    Args:
        user_message: The new message typed by the user.
        history:      List of (user_message, bot_reply) pairs so far,
                      provided and updated by Gradio automatically.

    Returns:
        The bot's reply as a plain string.
    """
    # Step 1 — guard against empty input
    if not user_message.strip():
        return ""

    # Step 2 — trim to avoid silent truncation
    history = trim_history(history)

    # Step 3 — build prompt from history + new message
    pipe = get_pipeline()
    eos  = pipe.tokenizer.eos_token
    prompt = _build_prompt(history, user_message, eos)

    # Step 4 — run inference using GenerationConfig to avoid deprecation warning
    gen_config = GenerationConfig(
        max_new_tokens=200,
        pad_token_id=pipe.tokenizer.eos_token_id,
    )
    result    = pipe(prompt, generation_config=gen_config)
    generated = result[0]["generated_text"]
    bot_reply = generated[len(prompt):].split(eos)[0].strip()

    return bot_reply


if __name__ == "__main__":
    # Manually simulate two turns to verify history is threaded correctly
    history: list = []
    reply1 = chat("My name is Alex.", history)
    history.append({"role": "user", "content": "My name is Alex."})
    history.append({"role": "assistant", "content": reply1})
    reply2 = chat("What is my name?", history)
    print("Bot reply:", reply2)
    # Expected: something like "Your name is Alex."
