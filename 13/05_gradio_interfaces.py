"""
Chapter 13 — Example 05: Gradio Interfaces — Basic to Advanced
===============================================================
Covers sections 13.3 and 13.4:
  - gr.Interface: the simplest path to a working UI
  - gr.Label: confidence bar charts for classifiers
  - Adding examples, title, description, and flagging
  - gr.Blocks: custom layouts with rows, columns, and tabs
  - Maintaining conversation state
  - Streaming output for text generation
  - Sharing and launch options

Run any app in this file with:
    python 05_gradio_interfaces.py --app <1-5>

Install:
    pip install gradio transformers torch
"""

import argparse
import gradio as gr
from transformers import pipeline

# ── Shared models (loaded once) ───────────────────────────────────────────────

sentiment_pipe  = pipeline(
    "text-classification",
    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
    top_k=None,
)
summariser_pipe = pipeline(
    "summarization",
    model="sshleifer/distilbart-cnn-6-6",
    min_length=20, max_length=100, do_sample=False,
)
zero_shot_pipe  = pipeline("zero-shot-classification")
generator_pipe  = pipeline(
    "text-generation", model="gpt2",
    max_new_tokens=80, do_sample=True,
    temperature=0.8, top_p=0.92,
    pad_token_id=50256,
)


# ════════════════════════════════════════════════════════════════════════════
# APP 1 — Minimal sentiment interface (section 13.3 baseline)
# ════════════════════════════════════════════════════════════════════════════

def analyze_sentiment(text: str) -> str:
    """The function from section 13.2 — simple string output."""
    if not text.strip():
        return "Please enter some text."
    result = sentiment_pipe(text)[0]
    label  = result["label"]
    score  = result["score"]
    return f"Sentiment: {label}\nConfidence: {score:.2f}"


app1 = gr.Interface(
    fn          = analyze_sentiment,
    inputs      = gr.Textbox(lines=3, placeholder="Enter text here..."),
    outputs     = "text",
    title       = "Sentiment Analysis App",
    description = "Analyse text sentiment using a pretrained transformer model.",
    examples    = [
        ["I absolutely loved this product!"],
        ["The delivery was late and the item was damaged."],
        ["It works fine, nothing special."],
    ],
    flagging_mode = "never",
)


# ════════════════════════════════════════════════════════════════════════════
# APP 2 — Confidence bar chart with gr.Label (better for classifiers)
# ════════════════════════════════════════════════════════════════════════════

LABEL_EMOJI = {"positive": "😊", "neutral": "😐", "negative": "😞"}

def analyze_with_scores(text: str) -> dict:
    """
    Returns a dict for gr.Label — renders as a confidence bar chart.
    Key = display label, value = confidence score (0-1).
    """
    if not text.strip():
        return {}
    results = sentiment_pipe(text)[0]   # list of {label, score}
    return {
        f"{LABEL_EMOJI.get(r['label'].lower(), '')} {r['label'].capitalize()}": r["score"]
        for r in results
    }


app2 = gr.Interface(
    fn          = analyze_with_scores,
    inputs      = gr.Textbox(
                    lines=4,
                    placeholder="Type a review, tweet, or any sentence…",
                    label="Input Text",
                  ),
    outputs     = gr.Label(label="Sentiment Scores", num_top_classes=3),
    title       = "🔍 Sentiment Analyser",
    description = (
        "Powered by **RoBERTa** trained on Twitter data. "
        "Enter any text to see confidence scores for all three classes."
    ),
    examples    = [
        ["Best purchase I've made this year — absolutely love it! 🎉"],
        ["Arrived broken. Customer service refused a refund. Avoid."],
        ["It's okay, does what it says on the tin."],
        ["Wow, genuinely surprised by the quality for this price 😮"],
    ],
    flagging_mode = "never",
)


# ════════════════════════════════════════════════════════════════════════════
# APP 3 — Multi-task app with gr.Blocks and tabs
# ════════════════════════════════════════════════════════════════════════════

def summarise_text(text: str) -> str:
    if len(text.split()) < 20:
        return "⚠️ Please enter at least 20 words for a meaningful summary."
    result = summariser_pipe(text.strip())
    return result[0]["summary_text"].strip()


def classify_zero_shot(text: str, labels_raw: str) -> dict:
    labels = [l.strip() for l in labels_raw.split(",") if l.strip()]
    if not text.strip():
        return {}
    if len(labels) < 2:
        return {"error — enter at least 2 comma-separated labels": 1.0}
    result = zero_shot_pipe(text, candidate_labels=labels)
    return dict(zip(result["labels"], result["scores"]))


with gr.Blocks(title="NLP Toolkit", theme=gr.themes.Soft()) as app3:
    gr.Markdown("# 🧠 NLP Toolkit\nThree NLP tasks in one app.")

    with gr.Tabs():

        # ── Tab 1: Sentiment ──────────────────────────────────────────────
        with gr.TabItem("😊 Sentiment"):
            gr.Markdown("### Sentiment Analysis\nClassify text as positive, neutral, or negative.")
            with gr.Row():
                with gr.Column():
                    sent_input = gr.Textbox(
                        lines=4, placeholder="Enter text to analyse…",
                        label="Input",
                    )
                    sent_btn = gr.Button("Analyse", variant="primary")
                with gr.Column():
                    sent_output = gr.Label(label="Sentiment", num_top_classes=3)

            sent_btn.click(fn=analyze_with_scores, inputs=sent_input, outputs=sent_output)

            gr.Examples(
                examples=[["Exceptional product, would buy again!"],
                           ["Terrible — broke after one day."]],
                inputs=sent_input,
            )

        # ── Tab 2: Summarisation ──────────────────────────────────────────
        with gr.TabItem("📝 Summarise"):
            gr.Markdown("### Text Summarisation\nPaste a long text and get a concise summary.")
            with gr.Row():
                with gr.Column():
                    summ_input = gr.Textbox(
                        lines=8, placeholder="Paste a long article or paragraph…",
                        label="Long text",
                    )
                    summ_btn = gr.Button("Summarise", variant="primary")
                with gr.Column():
                    summ_output = gr.Textbox(label="Summary", lines=4)

            summ_btn.click(fn=summarise_text, inputs=summ_input, outputs=summ_output)

        # ── Tab 3: Zero-shot ──────────────────────────────────────────────
        with gr.TabItem("🏷️ Classify"):
            gr.Markdown(
                "### Zero-shot Classification\n"
                "Define your own labels — no training needed."
            )
            with gr.Row():
                with gr.Column():
                    zs_text   = gr.Textbox(lines=4, label="Text to classify")
                    zs_labels = gr.Textbox(
                        label="Labels (comma-separated)",
                        placeholder="urgent, normal, low priority",
                        value="urgent, normal, low priority",
                    )
                    zs_btn = gr.Button("Classify", variant="primary")
                with gr.Column():
                    zs_output = gr.Label(label="Classification", num_top_classes=5)

            zs_btn.click(
                fn      = classify_zero_shot,
                inputs  = [zs_text, zs_labels],
                outputs = zs_output,
            )
            gr.Examples(
                examples=[
                    ["My account was charged twice!", "billing issue, technical bug, account problem"],
                    ["The fan is making a loud grinding noise.", "hardware failure, user error, software bug"],
                ],
                inputs=[zs_text, zs_labels],
            )


# ════════════════════════════════════════════════════════════════════════════
# APP 4 — Stateful chat interface (conversation history)
# ════════════════════════════════════════════════════════════════════════════

def chat_sentiment(user_message: str, history: list[list]) -> tuple[list[list], str]:
    """
    Analyse each message and maintain a running history.
    history is a list of [user_msg, bot_response] pairs.
    """
    if not user_message.strip():
        return history, ""

    result  = sentiment_pipe(user_message)[0]
    top     = max(result, key=lambda x: x["score"])
    label   = top["label"].lower()
    score   = top["score"]

    emoji   = {"positive": "😊", "neutral": "😐", "negative": "😞"}.get(label, "❓")
    response = (
        f"{emoji} **{label.capitalize()}** — confidence {score:.1%}\n\n"
        + "All scores: " + ", ".join(f"{r['label'].lower()}: {r['score']:.2f}" for r in result)
    )

    history = history + [[user_message, response]]
    return history, ""


with gr.Blocks(title="Sentiment Chat") as app4:
    gr.Markdown("## 💬 Sentiment Chat\nType anything — the bot tells you its emotional tone.")
    chatbot    = gr.Chatbot(height=400)
    msg_input  = gr.Textbox(placeholder="Type a sentence…", label="Your message")
    clear_btn  = gr.Button("Clear history")

    msg_input.submit(
        fn      = chat_sentiment,
        inputs  = [msg_input, chatbot],
        outputs = [chatbot, msg_input],
    )
    clear_btn.click(fn=lambda: ([], ""), outputs=[chatbot, msg_input])


# ════════════════════════════════════════════════════════════════════════════
# APP 5 — Streaming text generation
# ════════════════════════════════════════════════════════════════════════════

def generate_text(prompt: str, max_tokens: int, temperature: float):
    """
    Yield text token by token for streaming output.
    gr.Interface with stream=True feeds this to the UI progressively.
    """
    if not prompt.strip():
        yield "Please enter a prompt."
        return

    outputs = generator_pipe(
        prompt,
        max_new_tokens=int(max_tokens),
        temperature=float(temperature),
        do_sample=True,
    )
    # Return full generated text (streaming via generator)
    full_text = outputs[0]["generated_text"]
    # Simulate streaming by yielding growing slices
    for i in range(10, len(full_text) + 1, 10):
        yield full_text[:i]
    yield full_text   # ensure the final full text is always shown


app5 = gr.Interface(
    fn    = generate_text,
    inputs = [
        gr.Textbox(lines=2, placeholder="Enter a prompt…", label="Prompt"),
        gr.Slider(20, 150, value=60, step=10, label="Max new tokens"),
        gr.Slider(0.3, 1.5, value=0.8, step=0.1, label="Temperature"),
    ],
    outputs = gr.Textbox(lines=6, label="Generated text"),
    title   = "✍️ GPT-2 Text Generator",
    description = (
        "Enter a prompt and GPT-2 will complete it. "
        "Higher temperature = more creative; lower = more predictable."
    ),
    examples = [
        ["Python is the most popular language for machine learning because", 80, 0.8],
        ["Once upon a time in a land of data and algorithms,", 100, 1.0],
    ],
    flagging_mode = "never",
)


# ── Entry point ───────────────────────────────────────────────────────────────

APPS = {
    "1": ("Minimal sentiment (text output)",  app1),
    "2": ("Sentiment with confidence bars",   app2),
    "3": ("Multi-task NLP toolkit (tabs)",    app3),
    "4": ("Stateful sentiment chat",          app4),
    "5": ("Streaming text generation",        app5),
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--app", default="2", choices=APPS.keys(),
                        help="Which app to launch (1-5)")
    parser.add_argument("--share", action="store_true",
                        help="Generate a public shareable link")
    args = parser.parse_args()

    name, demo = APPS[args.app]
    print(f"\nLaunching App {args.app}: {name}")
    print("Available apps:")
    for k, (n, _) in APPS.items():
        marker = " ← running" if k == args.app else ""
        print(f"  {k}. {n}{marker}")
    print()
    demo.launch(share=args.share)
