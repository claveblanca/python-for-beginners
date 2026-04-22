"""
chat.py
Core chat function and conversation history management.

The history list is the only persistent state in the application.
Every call to chat() receives the full history, rebuilds the
Conversation object from it, runs inference, and returns the
updated history alongside an empty string to clear the input box.

Dependencies:
    pip install transformers torch
"""

from transformers import Conversation
from model import get_pipeline

# DialoGPT's maximum context window in tokens.
# Conversations longer than this will have early turns silently
# truncated by the tokeniser. MAX_TURNS enforces an explicit limit.
CONTEXT_WINDOW_TOKENS = 1024
MAX_TURNS = 20   # conservative limit; each turn consumes ~50 tokens on average


def _rebuild_conversation(history: list[tuple[str, str]]) -> Conversation:
    """
    Reconstruct a Conversation object from a history list.

    The pipeline has no persistent state between calls, so the full
    exchange must be replayed on every invocation.

    Args:
        history: List of (user_message, bot_reply) string pairs,
                 ordered oldest-first.

    Returns:
        A Conversation object containing all prior turns, ready for
        a new user input to be added.
    """
    conv = Conversation()
    for user_turn, bot_turn in history:
        conv.add_user_input(user_turn)
        conv.mark_processed()
        conv.append_response(bot_turn)
    return conv


def trim_history(
    history: list[tuple[str, str]],
    max_turns: int = MAX_TURNS,
) -> list[tuple[str, str]]:
    """
    Drop the oldest turns when history exceeds max_turns.

    Prevents silent tokeniser truncation by making the context limit
    explicit and controllable. The most recent turns are kept.

    Args:
        history:   Full conversation history.
        max_turns: Maximum number of (user, bot) pairs to retain.

    Returns:
        Trimmed history list, at most max_turns pairs long.
    """
    if len(history) > max_turns:
        dropped = len(history) - max_turns
        print(f"[trim_history] Dropped {dropped} oldest turn(s) "
              f"to stay within the {max_turns}-turn limit.")
        return history[-max_turns:]
    return history


def chat(
    user_message: str,
    history: list[tuple[str, str]],
) -> tuple[str, list[tuple[str, str]]]:
    """
    Process one user turn and return the bot's reply.

    Designed to be used directly as the fn= argument for
    gr.ChatInterface, which passes and receives (message, history).

    Steps:
        1. Reject blank input — return early without changing history.
        2. Trim history to avoid context-window overflow.
        3. Rebuild the Conversation object from history.
        4. Add the new user message and run inference.
        5. Append the new (user, bot) pair to history and return.

    Args:
        user_message: The new message typed by the user.
        history:      List of (user_message, bot_reply) pairs so far.

    Returns:
        Tuple of (cleared_input, updated_history).
        cleared_input is always "" — signals Gradio to clear the box.
    """
    # Step 1 — guard against empty input
    if not user_message.strip():
        return "", history

    # Step 2 — trim to avoid silent truncation
    history = trim_history(history)

    # Step 3 — rebuild Conversation from history
    conv = _rebuild_conversation(history)

    # Step 4 — add new message and run inference
    conv.add_user_input(user_message)
    result    = get_pipeline()(conv)
    bot_reply = result.generated_responses[-1]

    # Step 5 — update history and return
    history.append((user_message, bot_reply))
    return "", history


if __name__ == "__main__":
    # Manually simulate two turns to verify history is threaded correctly
    history = []
    _, history = chat("My name is Alex.", history)
    _, history = chat("What is my name?", history)
    print("Bot reply:", history[-1][1])
    # Expected: something like "Your name is Alex."
