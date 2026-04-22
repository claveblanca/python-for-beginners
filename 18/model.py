"""
model.py
Load and cache the DialoGPT conversational pipeline.

Handles the one-time model download and exposes a single
get_pipeline() function used by every other module.

Dependencies:
    pip install transformers torch
"""

from transformers import pipeline as hf_pipeline, Conversation

# Valid model sizes — swap to trade quality for speed
MODEL_SIZES = {
    "small":  "microsoft/DialoGPT-small",   # ~120 MB  — fast local testing
    "medium": "microsoft/DialoGPT-medium",  # ~350 MB  — best quality/speed balance
    "large":  "microsoft/DialoGPT-large",   # ~760 MB  — highest reply quality
}

# Module-level singleton — loaded once, reused on every call
_pipeline = None


def get_pipeline(size: str = "medium"):
    """
    Return the DialoGPT conversational pipeline, loading it on first call.

    The model is downloaded from Hugging Face Hub on the first call and
    cached locally — subsequent calls load from disk in seconds.

    Args:
        size: Model size — 'small' | 'medium' | 'large'.
              Ignored after the first call (singleton pattern).

    Returns:
        A Hugging Face conversational pipeline object.

    Raises:
        ValueError: if size is not one of the valid options.
    """
    global _pipeline
    if _pipeline is None:
        if size not in MODEL_SIZES:
            raise ValueError(
                f"Invalid size {size!r}. Choose from: {list(MODEL_SIZES)}"
            )
        model_name = MODEL_SIZES[size]
        print(f"Loading {model_name} … (download on first run)")
        _pipeline = hf_pipeline(
            "conversational",
            model=model_name,
        )
        print("Model ready.")
    return _pipeline


if __name__ == "__main__":
    # Quick smoke-test: send one message and print the reply
    pipe = get_pipeline("medium")
    conv = Conversation("Hello! What can you help me with?")
    result = pipe(conv)
    print("Bot:", result.generated_responses[-1])
