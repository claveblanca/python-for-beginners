"""
main.py
Entry point for the Chapter 18 chatbot application.

Run locally:
    python main.py

Run with a public shareable link (valid 72 hours):
    python main.py --share

Run on a specific port without opening the browser:
    python main.py --port 8080 --no-browser

The if __name__ == "__main__": guard ensures the Gradio server
only starts when this file is run directly — not when another
module imports from it.
"""

import argparse
from ui import build_ui


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Chapter 18 — DialoGPT chatbot with Gradio UI"
    )
    parser.add_argument(
        "--share",
        action="store_true",
        help="Generate a public Gradio link (valid for 72 hours)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=7860,
        help="Port to run the local server on (default: 7860)",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Suppress automatic browser opening",
    )
    parser.add_argument(
        "--model-size",
        choices=["small", "medium", "large"],
        default="medium",
        help="DialoGPT model size (default: medium)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    # Pre-load the model before the UI starts so the first user message
    # doesn't trigger a cold-start delay inside the request handler.
    from model import get_pipeline
    get_pipeline(args.model_size)

    app = build_ui()
    app.launch(
        share      = args.share,
        server_port= args.port,
        inbrowser  = not args.no_browser,
    )
