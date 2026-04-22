# test_chat.py
from unittest.mock import patch, MagicMock
from main import chat


def test_blank_input_returns_unchanged_history():
    cleared, history = chat("   ", [])
    assert cleared == ""
    assert history == []   # history must not change


def test_valid_message_appends_to_history():
    mock_conv = MagicMock()
    mock_conv.generated_responses = ["Hello, how can I help?"]
    with patch("main.chat_pipeline", return_value=mock_conv):
        _, history = chat("Hi", [])
    assert len(history) == 1
    assert history[0] == ("Hi", "Hello, how can I help?")
