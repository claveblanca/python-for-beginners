"""
ui.py
Gradio chat interface definition.

Constructs the gr.ChatInterface widget and exposes a build_ui()
factory so the interface can be created independently of launching,
making it easy to embed in larger Gradio Blocks layouts.

Dependencies:
    pip install gradio
"""

import gradio as gr
from chat import chat


def build_ui() -> gr.ChatInterface:
    """
    Build and return the Gradio ChatInterface.

    gr.ChatInterface is purpose-built for chatbots:
        - Renders a scrollable message thread automatically.
        - Injects and retrieves the history list on every turn.
        - Places the input box and submit button in the expected position.

    Returns:
        Configured gr.ChatInterface object (not yet launched).
    """
    return gr.ChatInterface(
        fn          = chat,
        title       = "Python Chatbot",
        description = (
            "Powered by DialoGPT-medium. "
            "Each reply considers the full conversation so far."
        ),
        examples    = [
            "Hello!",
            "Tell me a joke.",
            "What is Python?",
            "Explain machine learning in simple terms.",
        ],
    )


if __name__ == "__main__":
    # Preview the interface without launching the full app
    app = build_ui()
    app.launch(inbrowser=True)
