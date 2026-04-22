"""
Chapter 13 — Example 07: Complete Production-Ready App
=======================================================
The complete app from section 13.5 — extended with:
  - Robust input validation and error handling
  - Sentence-level breakdown
  - CSV batch upload and download
  - Comparison of two different models side by side
  - Confidence threshold warning
  - Clean, themed Gradio Blocks layout

Run:
    python 07_complete_app.py [--share]

Install:
    pip install gradio transformers torch pandas
"""

import argparse
import io
import re
import pandas as pd
import gradio as gr
from transformers import pipeline

# ── Model loading — once at startup ──────────────────────────────────────────

print("Loading models… (first run will download weights)")

# Two models for the comparison tab
MODEL_A_NAME = "distilbert-base-uncased-finetuned-sst-2-english"
MODEL_B_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"

model_a = pipeline("text-classification", model=MODEL_A_NAME, top_k=None)
model_b = pipeline("text-classification", model=MODEL_B_NAME, top_k=None)

print("Models loaded.")

# ── Constants ─────────────────────────────────────────────────────────────────

MAX_CHARS    = 512
MIN_CONF     = 0.60
LABEL_EMOJI  = {"positive": "😊 Positive", "neutral": "😐 Neutral",
                "negative": "😞 Negative", "uncertain": "❓ Uncertain"}


# ── Core logic functions ──────────────────────────────────────────────────────

def run_inference(text: str, pipe) -> dict:
    """Run a pipeline and return label, confidence, and all scores."""
    text = text.strip()[:MAX_CHARS]
    raw  = pipe(text)[0]
    top  = max(raw, key=lambda x: x["score"])
    return {
        "label":      top["label"].lower(),
        "confidence": top["score"],
        "all_scores": {r["label"].lower(): r["score"] for r in raw},
    }


def analyse_single(text: str) -> tuple:
    """
    Returns (scores_dict_for_gr_Label, detail_text).
    Used by the main analysis tab.
    """
    if not text.strip():
        return {}, "⚠️ Please enter some text."

    result = run_inference(text, model_b)
    label  = result["label"]
    conf   = result["confidence"]

    # Confidence warning
    warning = ""
    if conf < MIN_CONF:
        label   = "uncertain"
        warning = f"\n\n⚠️ Low confidence ({conf:.1%}) — result may not be reliable."

    scores_display = {
        LABEL_EMOJI.get(k, k): v
        for k, v in result["all_scores"].items()
    }

    detail = (
        f"**Top prediction:** {label.capitalize()}  ({conf:.1%})\n\n"
        f"**Model:** {MODEL_B_NAME}"
        + warning
    )

    return scores_display, detail


def analyse_sentences(text: str) -> str:
    """Split text into sentences and score each one."""
    if not text.strip():
        return "Please enter some text."

    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
    if len(sentences) < 2:
        return "Enter at least two sentences to see a breakdown."

    lines = ["| Sentence | Sentiment | Confidence |", "|---|---|---|"]
    for sent in sentences[:15]:     # cap at 15 for display
        result = run_inference(sent, model_b)
        label  = result["label"]
        conf   = result["confidence"]
        emoji  = {"positive": "✅", "negative": "❌", "neutral": "➖"}.get(label, "❓")
        lines.append(f"| {sent[:60]} | {emoji} {label} | {conf:.1%} |")

    return "\n".join(lines)


def compare_models(text: str) -> tuple:
    """Run both models and return gr.Label dicts for side-by-side display."""
    if not text.strip():
        return {}, {}

    res_a = run_inference(text, model_a)
    res_b = run_inference(text, model_b)

    scores_a = {k.capitalize(): v for k, v in res_a["all_scores"].items()}
    scores_b = {k.capitalize(): v for k, v in res_b["all_scores"].items()}

    return scores_a, scores_b


def process_csv(file) -> tuple[pd.DataFrame | None, str]:
    """
    Accept a CSV with a 'text' column, add 'sentiment' and 'confidence'.
    Returns (dataframe_for_display, csv_bytes_for_download).
    """
    if file is None:
        return None, None

    try:
        df = pd.read_csv(file.name)
    except Exception as e:
        return None, f"Could not read CSV: {e}"

    if "text" not in df.columns:
        return None, "CSV must contain a 'text' column."

    texts = df["text"].fillna("").astype(str).tolist()

    # Batch inference
    sentiments  = []
    confidences = []
    for text in texts:
        if not text.strip():
            sentiments.append("empty")
            confidences.append(0.0)
        else:
            r = run_inference(text.strip()[:MAX_CHARS], model_b)
            sentiments.append(r["label"])
            confidences.append(round(r["confidence"], 4))

    df["sentiment"]  = sentiments
    df["confidence"] = confidences

    # Prepare downloadable CSV
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    csv_bytes = buffer.getvalue().encode("utf-8")

    # Summary stats for display
    dist = df["sentiment"].value_counts()
    avg  = df["confidence"].mean()
    summary = (
        f"✅ Processed {len(df)} rows\n\n"
        + "\n".join(f"  {label}: {count}" for label, count in dist.items())
        + f"\n\nAvg confidence: {avg:.1%}"
    )

    return df[["text", "sentiment", "confidence"]].head(20), summary, csv_bytes


# ── Gradio Blocks layout ──────────────────────────────────────────────────────

css = """
.tab-selected { background: #2E74B5 !important; color: white !important; }
footer { display: none !important; }
"""

with gr.Blocks(title="Sentiment Analysis Suite", theme=gr.themes.Soft(), css=css) as app:

    gr.Markdown(
        "# 🔍 Sentiment Analysis Suite\n"
        "Powered by **Hugging Face Transformers** — "
        "three modes: single text, sentence breakdown, model comparison, and batch CSV."
    )

    with gr.Tabs():

        # ── Tab 1: Single Text Analysis ───────────────────────────────────
        with gr.TabItem("📝 Analyse Text"):
            gr.Markdown("Enter any text to classify its sentiment.")
            with gr.Row():
                with gr.Column(scale=2):
                    txt_input = gr.Textbox(
                        lines=5,
                        placeholder="Type a review, tweet, or any sentence…",
                        label="Input text",
                        max_lines=10,
                    )
                    with gr.Row():
                        analyse_btn = gr.Button("Analyse", variant="primary", scale=2)
                        clear_btn   = gr.Button("Clear", scale=1)

                    gr.Examples(
                        examples=[
                            ["Best purchase I've made this year — absolutely love it! 🎉"],
                            ["Arrived broken. Customer service refused a refund. Avoid."],
                            ["It's okay, does what it says."],
                            ["I wasn't sure what to expect but I'm genuinely impressed."],
                            ["Three weeks and still no refund. This is unacceptable."],
                        ],
                        inputs=txt_input,
                    )

                with gr.Column(scale=1):
                    score_output  = gr.Label(label="Sentiment Scores", num_top_classes=3)
                    detail_output = gr.Markdown(label="Details")

            analyse_btn.click(
                fn      = analyse_single,
                inputs  = txt_input,
                outputs = [score_output, detail_output],
            )
            clear_btn.click(
                fn      = lambda: ("", {}, ""),
                outputs = [txt_input, score_output, detail_output],
            )
            txt_input.submit(
                fn      = analyse_single,
                inputs  = txt_input,
                outputs = [score_output, detail_output],
            )

        # ── Tab 2: Sentence Breakdown ─────────────────────────────────────
        with gr.TabItem("📊 Sentence Breakdown"):
            gr.Markdown(
                "Enter a multi-sentence review to see how each sentence scores individually."
            )
            with gr.Row():
                with gr.Column():
                    sent_input = gr.Textbox(
                        lines=6,
                        placeholder="Paste a multi-sentence review…",
                        label="Multi-sentence input",
                    )
                    sent_btn = gr.Button("Break down", variant="primary")

                    gr.Examples(
                        examples=[[
                            "The laptop arrived well-packaged and on time. "
                            "Setup was straightforward and the display is gorgeous. "
                            "However, the fan noise is quite loud under load. "
                            "Battery life is also disappointing — barely 6 hours. "
                            "Overall a mixed bag, but I'm keeping it for the screen."
                        ]],
                        inputs=sent_input,
                    )

                with gr.Column():
                    sent_output = gr.Markdown(label="Sentence scores")

            sent_btn.click(
                fn      = analyse_sentences,
                inputs  = sent_input,
                outputs = sent_output,
            )

        # ── Tab 3: Model Comparison ───────────────────────────────────────
        with gr.TabItem("⚖️ Model Comparison"):
            gr.Markdown(
                f"Compare **{MODEL_A_NAME}** (SST-2, formal reviews) "
                f"vs **{MODEL_B_NAME}** (Twitter, informal text)."
            )
            cmp_input = gr.Textbox(
                lines=3, placeholder="Enter text to compare both models…",
                label="Input",
            )
            cmp_btn = gr.Button("Compare", variant="primary")
            with gr.Row():
                with gr.Column():
                    gr.Markdown(f"**Model A:** `{MODEL_A_NAME.split('/')[-1]}`")
                    cmp_out_a = gr.Label(label="Scores A", num_top_classes=3)
                with gr.Column():
                    gr.Markdown(f"**Model B:** `{MODEL_B_NAME.split('/')[-1]}`")
                    cmp_out_b = gr.Label(label="Scores B", num_top_classes=3)

            cmp_btn.click(
                fn      = compare_models,
                inputs  = cmp_input,
                outputs = [cmp_out_a, cmp_out_b],
            )

            gr.Examples(
                examples=[
                    ["best thing ever omg so happy rn 😭💯"],
                    ["The board voted to restructure the executive team."],
                    ["cant believe how bad this is lol"],
                ],
                inputs=cmp_input,
            )

        # ── Tab 4: Batch CSV ──────────────────────────────────────────────
        with gr.TabItem("📂 Batch CSV"):
            gr.Markdown(
                "Upload a CSV file with a **`text`** column. "
                "The app will add `sentiment` and `confidence` columns "
                "and return a downloadable result file."
            )
            with gr.Row():
                with gr.Column():
                    file_input   = gr.File(
                        label="Upload CSV",
                        file_types=[".csv"],
                        type="filepath",
                    )
                    process_btn  = gr.Button("Process", variant="primary")
                    summary_out  = gr.Textbox(label="Summary", lines=6)

                with gr.Column():
                    table_out    = gr.Dataframe(label="Preview (first 20 rows)")
                    download_out = gr.File(label="Download results")

            def handle_csv(file):
                result = process_csv(file)
                if len(result) == 3:
                    df, summary, csv_bytes = result
                    if isinstance(csv_bytes, bytes):
                        out_path = "/tmp/sentiment_results.csv"
                        with open(out_path, "wb") as f:
                            f.write(csv_bytes)
                        return df, summary, out_path
                    return None, summary, None
                return None, result[1] if len(result) > 1 else "Error", None

            process_btn.click(
                fn      = handle_csv,
                inputs  = file_input,
                outputs = [table_out, summary_out, download_out],
            )

    gr.Markdown(
        "---\n"
        "Model: `cardiffnlp/twitter-roberta-base-sentiment-latest` • "
        "Built with 🤗 Transformers + Gradio"
    )


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--share", action="store_true",
                        help="Generate a public Gradio link (72 hrs)")
    parser.add_argument("--port", type=int, default=7860)
    args = parser.parse_args()

    print(f"\nLaunching app on http://127.0.0.1:{args.port}")
    if args.share:
        print("Generating public link… (this may take a few seconds)")
    print("Press Ctrl+C to stop.\n")

    app.launch(
        server_port = args.port,
        share       = args.share,
        inbrowser   = True,
    )
