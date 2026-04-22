# Chapter 18 — Building a Chatbot with Python

Code from *Machine Learning with Python*, Chapter 18.  
A multi-turn conversational chatbot powered by DialoGPT and served through a Gradio browser UI.

---

## Project layout

```
chatbot_ch18/
├── model.py          Load and cache the DialoGPT pipeline
├── chat.py           Core chat function and history management
├── ui.py             Gradio ChatInterface definition
├── main.py           Entry point — CLI flags, model pre-load, launch
├── requirements.txt
└── README.md
```

---

## Installation

```bash
pip install -r requirements.txt
```

The DialoGPT model weights are downloaded from Hugging Face Hub on the
first run and cached locally — subsequent starts load from disk in seconds.

---

## Running the app

**Default (medium model, local only):**
```bash
python main.py
```
Opens `http://localhost:7860` in your browser automatically.

**With a public shareable link:**
```bash
python main.py --share
```
Prints a `https://abc123.gradio.live` URL valid for 72 hours.
Anyone with the link can use the chatbot — no Python required on their end.

**All options:**
```
python main.py --help

  --share              Generate a public Gradio link (valid 72 hours)
  --port PORT          Local port (default: 7860)
  --no-browser         Suppress automatic browser opening
  --model-size {small,medium,large}
                       DialoGPT variant to load (default: medium)
```

**Choosing a model size:**

| Flag | Model | Download | Best for |
|---|---|---|---|
| `--model-size small` | DialoGPT-small | ~120 MB | Fast local testing |
| `--model-size medium` | DialoGPT-medium | ~350 MB | Quality/speed balance |
| `--model-size large` | DialoGPT-large | ~760 MB | Highest reply quality |

---

## Module reference

### `model.py`

Loads the DialoGPT pipeline once and caches it as a module-level singleton.

```python
from model import get_pipeline
from transformers import Conversation

pipe = get_pipeline("medium")   # loads on first call; instant on subsequent calls

conv   = Conversation("Hello! What can you help me with?")
result = pipe(conv)
print(result.generated_responses[-1])
# → "I can help you with anything you need."
```

`get_pipeline(size)` — accepts `"small"`, `"medium"`, or `"large"`.
The size argument is only used on the first call; the singleton is returned on all subsequent calls regardless of the argument.

---

### `chat.py`

The core stateful chat function and two helper utilities.

#### `chat(user_message, history)`

```python
from chat import chat

history = []

_, history = chat("My name is Alex.", history)
_, history = chat("What is my name?", history)

print(history[-1][1])   # last bot reply
# → "Your name is Alex."
```

**How it works:**

1. Returns immediately if `user_message.strip()` is empty — no model call made.
2. Calls `trim_history()` to drop the oldest turns when the history exceeds `MAX_TURNS`.
3. Rebuilds a `Conversation` object by replaying every prior turn — the pipeline has no persistent state between calls.
4. Adds the new user message, runs inference, and appends the `(user, bot)` pair to history.
5. Returns `("", updated_history)` — the empty string signals Gradio to clear the input box.

**Signature:** `chat(user_message: str, history: list[tuple[str, str]]) -> tuple[str, list]`

This exact signature is what `gr.ChatInterface` expects for its `fn=` argument.

#### `trim_history(history, max_turns)`

```python
from chat import trim_history

# Keep only the 20 most recent turns (default)
history = trim_history(history)

# Keep only the 5 most recent turns
history = trim_history(history, max_turns=5)
```

DialoGPT has a hard limit of 1,024 tokens. Without trimming, long conversations are silently truncated by the tokeniser — the model loses context without warning. `trim_history` makes the limit explicit and controllable.

#### `_rebuild_conversation(history)` *(internal)*

Replays a history list into a fresh `Conversation` object using `add_user_input`, `mark_processed`, and `append_response`. Called automatically inside `chat()`; no need to call it directly.

---

### `ui.py`

Constructs the Gradio interface without launching it, so it can be embedded in larger apps.

```python
from ui import build_ui

app = build_ui()
app.launch()                        # basic local launch
app.launch(share=True)              # with public link
app.launch(server_port=8080)        # on a specific port
```

**`gr.ChatInterface` vs `gr.Interface`:**

| Component | Use when |
|---|---|
| `gr.Interface` | Generic input/output layouts (e.g. the sentiment app in ch. 13) |
| `gr.ChatInterface` | Chatbots — manages the history list automatically |
| `gr.Blocks` | Fully custom layouts with multiple components |

---

### `main.py`

Entry point only — no logic of its own. Pre-loads the model before the UI starts (avoids a cold-start delay on the first user message), then passes CLI flags to `app.launch()`.

---

## How the history works

The history list is the **only** persistent state in the application. On every user turn:

```
User types → chat(message, history)
               │
               ├─ 1. reject blank
               ├─ 2. trim to MAX_TURNS
               ├─ 3. rebuild Conversation from history
               ├─ 4. add message → run pipeline → get reply
               └─ 5. append (message, reply) → return ("", new_history)
                                                              │
                                              Gradio stores this and passes
                                              it back on the next turn
```

The pipeline itself is stateless — it sees the full conversation only because the caller reconstructs it on every invocation.

---

## Context window note

DialoGPT processes a maximum of **1,024 tokens**. A typical conversational turn uses roughly 40–60 tokens, so conversations of 15–25 turns approach the limit. `chat.py` enforces a `MAX_TURNS = 20` default that drops the oldest turns when exceeded. To change the limit:

```python
# chat.py
MAX_TURNS = 10   # tighter limit for faster inference
MAX_TURNS = 40   # looser limit if your turns are short
```

For a permanent URL, deploy to **Hugging Face Spaces** (free):
1. Create a Space at <https://huggingface.co/spaces>
2. Choose the Gradio SDK
3. Upload `main.py`, `model.py`, `chat.py`, `ui.py`, and `requirements.txt`
4. The Space builds automatically and gives you a permanent public URL
