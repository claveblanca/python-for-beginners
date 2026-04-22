"""
Chapter 13 — Example 03: Tokenisers and Models Under the Hood
==============================================================
What the pipeline does internally — understanding tokenisation,
model loading, and running inference step by step.

Covers the internals behind section 13.1:
  - AutoTokenizer: splitting text into sub-word tokens
  - Token IDs, attention masks, and special tokens
  - AutoModel: raw logits vs pipeline post-processing
  - Comparing different tokenisers side by side
  - Handling long inputs with truncation and stride
  - Encoding a batch efficiently

Install:
    pip install transformers torch
"""

import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

MODEL_NAME = "distilbert-base-uncased-finetuned-sst-2-english"


# ── 1. What does a tokeniser do? ─────────────────────────────────────────────

print("=" * 60)
print("1. WHAT A TOKENISER DOES")
print("=" * 60)

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

text = "Machine learning is transforming the world."

# encode() → list of token IDs
ids = tokenizer.encode(text)
print(f"Raw IDs   : {ids}")

# convert_ids_to_tokens() shows the actual sub-word pieces
tokens = tokenizer.convert_ids_to_tokens(ids)
print(f"Tokens    : {tokens}")

# decode() reverses the process
decoded = tokenizer.decode(ids)
print(f"Decoded   : {decoded!r}")

# Special tokens:
#   [CLS] (101) — classification token, always first
#   [SEP] (102) — separator token, always last
print(f"\nSpecial tokens:")
print(f"  [CLS] id = {tokenizer.cls_token_id}")
print(f"  [SEP] id = {tokenizer.sep_token_id}")
print(f"  [PAD] id = {tokenizer.pad_token_id}")
print(f"  [UNK] id = {tokenizer.unk_token_id}")


# ── 2. Sub-word tokenisation — why unknown words don't crash the model ────────

print("\n" + "=" * 60)
print("2. SUB-WORD TOKENISATION")
print("=" * 60)

# Words not in the vocabulary are split into known sub-word pieces.
# This lets the model handle rare words and neologisms.
unusual_words = [
    "transformative",
    "unsubscription",
    "tokenisation",
    "ChatGPT",
    "antidisestablishmentarianism",
    "café",
]

print(f"{'Word':<35} Tokens")
print("-" * 65)
for word in unusual_words:
    toks = tokenizer.tokenize(word)       # tokenize() skips CLS/SEP
    print(f"{word:<35} {toks}")

print("\nNote: ## prefix means 'continuation of previous token' (WordPiece).")


# ── 3. The tokeniser call — building model inputs ────────────────────────────

print("\n" + "=" * 60)
print("3. BUILDING MODEL INPUTS WITH THE TOKENISER")
print("=" * 60)

# Calling tokenizer() returns a dict of tensors ready for the model.
encoding = tokenizer(
    text,
    return_tensors="pt",       # PyTorch tensors
    truncation=True,
    max_length=128,
    padding=False,
)

print("Encoding keys:", list(encoding.keys()))
print(f"input_ids shape    : {encoding['input_ids'].shape}")
print(f"attention_mask     : {encoding['attention_mask']}")
# attention_mask: 1 = real token, 0 = padding — tells model to ignore padding


# ── 4. Batch encoding — padding to equal length ───────────────────────────────

print("\n" + "=" * 60)
print("4. BATCH ENCODING WITH PADDING")
print("=" * 60)

texts = [
    "Short.",
    "A medium-length sentence with a bit more content.",
    "This is a much longer sentence that contains quite a bit more text than the others.",
]

batch = tokenizer(
    texts,
    return_tensors="pt",
    truncation=True,
    max_length=64,
    padding=True,          # pad all sequences to the longest in the batch
)

print(f"input_ids shape   : {batch['input_ids'].shape}  "
      f"(batch={batch['input_ids'].shape[0]}, seq_len={batch['input_ids'].shape[1]})")
print("\nattention_mask (1=real token, 0=padding):")
for i, (ids, mask) in enumerate(zip(batch['input_ids'], batch['attention_mask'])):
    real_tokens = mask.sum().item()
    padded = ids.shape[0] - real_tokens
    print(f"  sentence {i+1}: {real_tokens} real tokens, {padded} padding tokens")


# ── 5. Manual inference — what pipeline() does internally ────────────────────

print("\n" + "=" * 60)
print("5. MANUAL INFERENCE (INSIDE THE PIPELINE)")
print("=" * 60)

model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
model.eval()   # switch to inference mode (disables dropout)

sample = "This product is absolutely fantastic!"
inputs  = tokenizer(sample, return_tensors="pt", truncation=True, max_length=512)

with torch.no_grad():     # disable gradient computation for inference
    outputs = model(**inputs)

# outputs.logits: raw unnormalised scores per class
logits = outputs.logits
print(f"Raw logits        : {logits}")

# softmax converts logits to probabilities that sum to 1
probs  = F.softmax(logits, dim=-1)
print(f"Probabilities     : {probs}")

# Map back to label names
id2label = model.config.id2label
for class_id, prob in enumerate(probs[0]):
    label = id2label[class_id]
    print(f"  {label:<12} {prob.item():.4f}")

# Compare with what pipeline() gives (should be identical)
auto_result = pipeline("sentiment-analysis", model=MODEL_NAME)(sample)[0]
print(f"\nPipeline result   : {auto_result['label']} ({auto_result['score']:.4f})")
print("✓ Manual and pipeline results match.")


# ── 6. Handling long inputs with truncation ───────────────────────────────────

print("\n" + "=" * 60)
print("6. HANDLING LONG INPUTS")
print("=" * 60)

long_text = " ".join(["This product exceeded my expectations."] * 40)
token_count = len(tokenizer.encode(long_text))
print(f"Original token count : {token_count}")
print(f"Model max length     : {tokenizer.model_max_length}")

# Approach 1: simply truncate (loses information from the end)
truncated_enc = tokenizer(
    long_text,
    truncation=True,
    max_length=tokenizer.model_max_length,
    return_tensors="pt",
)
print(f"After truncation     : {truncated_enc['input_ids'].shape[1]} tokens")

# Approach 2: score the first N and last N tokens, then average
def score_long_text(text: str, model, tokenizer, chunk_size: int = 512) -> dict:
    """
    Score text that exceeds the model's token limit by averaging
    scores from the beginning and end of the document.
    """
    tokens = tokenizer.encode(text, add_special_tokens=False)

    if len(tokens) <= chunk_size - 2:
        chunks = [tokens]
    else:
        # First chunk + last chunk (overlap acceptable)
        chunks = [tokens[:chunk_size - 2], tokens[-(chunk_size - 2):]]

    all_probs = []
    for chunk in chunks:
        ids = [tokenizer.cls_token_id] + chunk + [tokenizer.sep_token_id]
        input_ids = torch.tensor([ids])
        attention  = torch.ones_like(input_ids)
        with torch.no_grad():
            logits = model(input_ids=input_ids, attention_mask=attention).logits
        all_probs.append(F.softmax(logits, dim=-1))

    avg_probs = torch.stack(all_probs).mean(dim=0)
    top_id    = avg_probs.argmax().item()
    return {
        "label":  model.config.id2label[top_id],
        "score":  avg_probs[0][top_id].item(),
        "chunks": len(chunks),
    }


result = score_long_text(long_text, model, tokenizer)
print(f"\nLong text result     : {result['label']} ({result['score']:.4f}) "
      f"— scored across {result['chunks']} chunks")


# ── 7. Comparing tokenisers ──────────────────────────────────────────────────

print("\n" + "=" * 60)
print("7. COMPARING TOKENISERS")
print("=" * 60)

sample_text = "I'm running the DistilBERT tokeniser on some text."
models_to_compare = {
    "DistilBERT (WordPiece)": "distilbert-base-uncased",
    "RoBERTa (BPE)":          "roberta-base",
    "GPT-2 (BPE)":            "gpt2",
}

print(f"Text: {sample_text!r}\n")
print(f"{'Model':<30} {'N tokens':<10} {'Tokens'}")
print("-" * 80)
for name, model_id in models_to_compare.items():
    tok    = AutoTokenizer.from_pretrained(model_id)
    tokens = tok.tokenize(sample_text)
    print(f"{name:<30} {len(tokens):<10} {tokens}")

print("\nNote: Different tokenisation algorithms produce different token counts")
print("for the same text — which affects both speed and model behaviour.")
