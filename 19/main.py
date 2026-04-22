# main.py — chat function + Gradio UI (from chapter 18), updated with logger calls
import logging
import gradio as gr
from transformers import pipeline, Conversation

import config  # noqa: F401  — loads env vars and configures logging on import

logger = logging.getLogger(__name__)

chat_pipeline = pipeline("conversational", model=config.MODEL_NAME)


def chat(user_message, history):
    logger.info("user_message=%r history_len=%d", user_message, len(history))

    if not user_message.strip():
        logger.warning("blank input rejected")
        return "", history

    conversation = Conversation(user_message)
    conversation = chat_pipeline(conversation)
    bot_reply = conversation.generated_responses[-1]

    history = history + [(user_message, bot_reply)]
    return "", history


with gr.Blocks() as demo:
    chatbot = gr.Chatbot()
    msg = gr.Textbox(placeholder="Say something...")
    clear = gr.Button("Clear")

    msg.submit(chat, [msg, chatbot], [msg, chatbot])
    clear.click(lambda: ([], ""), None, [chatbot, msg])


if __name__ == "__main__":
    logger.info("starting server on port %d", config.SERVER_PORT)
    demo.launch(server_name="0.0.0.0", server_port=config.SERVER_PORT)
