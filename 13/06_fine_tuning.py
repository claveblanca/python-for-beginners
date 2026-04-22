"""
Chapter 13 — Example 06: Fine-tuning a Pre-trained Model
=========================================================
A preview of Chapter 14 — customising a model for your own domain.

Steps covered:
  1. Building a small labelled dataset (product reviews)
  2. Tokenising the dataset with map()
  3. Loading DistilBERT with a classification head
  4. Configuring TrainingArguments
  5. Training with the Trainer API
  6. Evaluating on a held-out test set
  7. Saving the fine-tuned model and loading it back
  8. Comparing base model vs fine-tuned model

Install:
    pip install transformers torch datasets scikit-learn accelerate
"""

import os
import numpy as np
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    pipeline,
)
from sklearn.metrics import classification_report, accuracy_score

MODEL_NAME  = "distilbert-base-uncased"
OUTPUT_DIR  = "./fine_tuned_reviews"
SEED        = 42
MAX_LENGTH  = 128


# ── 1. Build a labelled dataset ───────────────────────────────────────────────

print("=" * 60)
print("1. BUILDING THE LABELLED DATASET")
print("=" * 60)

# label: 0 = negative, 1 = positive
raw_data = {
    "text": [
        # Positive reviews
        "Incredible build quality. Feels premium and works flawlessly.",
        "Fast delivery, product exactly as described. Very happy.",
        "Best headphones I've owned. Sound quality is phenomenal.",
        "Exceeded my expectations in every way. Five stars.",
        "Setup was easy and performance is outstanding.",
        "Great value for money. Would definitely buy again.",
        "Packaging was perfect and arrived ahead of schedule.",
        "The battery life is unbelievable — still going after 3 days.",
        "Looks exactly like the photos and feels solid.",
        "Customer support was incredibly helpful and fast.",
        "Works perfectly with my laptop. Zero issues so far.",
        "Brilliant product, my whole family loves it.",
        # Negative reviews
        "Stopped working after two weeks. Absolute waste of money.",
        "Completely different from the description. Very disappointed.",
        "Arrived cracked and the returns process is a nightmare.",
        "Cheap plastic, feels like it'll break any second.",
        "Customer service ignored my emails for two weeks.",
        "Battery drains in under an hour. Useless.",
        "Missing key features that were advertised. Misleading.",
        "Returned immediately. Nothing like the photos shown.",
        "Worst purchase decision I've made. Avoid at all costs.",
        "Defective out of the box. No response from seller.",
        "Broke after one day of light use. Shocking quality.",
        "Overpriced rubbish. Do not buy.",
    ],
    "label": [1] * 12 + [0] * 12,
}

dataset = Dataset.from_dict(raw_data)
split   = dataset.train_test_split(test_size=0.25, seed=SEED)
train_ds = split["train"]
test_ds  = split["test"]

print(f"Train samples : {len(train_ds)}")
print(f"Test samples  : {len(test_ds)}")
print(f"Label counts  : {dict(zip(*np.unique(train_ds['label'], return_counts=True)))}")


# ── 2. Tokenise ───────────────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("2. TOKENISING THE DATASET")
print("=" * 60)

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

def tokenise(batch):
    return tokenizer(
        batch["text"],
        truncation=True,
        padding="max_length",
        max_length=MAX_LENGTH,
    )

# Dataset.map() applies the function to every example efficiently
train_tokenised = train_ds.map(tokenise, batched=True)
test_tokenised  = test_ds.map(tokenise,  batched=True)

# Tell the dataset which columns are model inputs
train_tokenised = train_tokenised.rename_column("label", "labels")
test_tokenised  = test_tokenised.rename_column("label", "labels")
train_tokenised.set_format("torch", columns=["input_ids", "attention_mask", "labels"])
test_tokenised.set_format("torch",  columns=["input_ids", "attention_mask", "labels"])

print(f"Columns after tokenisation: {train_tokenised.column_names}")
print(f"Sample input_ids length   : {len(train_tokenised[0]['input_ids'])}")


# ── 3. Load model with classification head ────────────────────────────────────

print("\n" + "=" * 60)
print("3. LOADING MODEL WITH CLASSIFICATION HEAD")
print("=" * 60)

# num_labels=2 adds a 2-class linear head on top of DistilBERT
# id2label / label2id are stored in the model config
model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=2,
    id2label={0: "NEGATIVE", 1: "POSITIVE"},
    label2id={"NEGATIVE": 0, "POSITIVE": 1},
)

# Count trainable parameters
total_params     = sum(p.numel() for p in model.parameters())
trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
print(f"Total parameters     : {total_params:,}")
print(f"Trainable parameters : {trainable_params:,}")
print(f"Model architecture   : {model.__class__.__name__}")


# ── 4. Define evaluation metrics ─────────────────────────────────────────────

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=1)
    return {
        "accuracy": accuracy_score(labels, preds),
    }


# ── 5. Configure training ─────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("4. TRAINING CONFIGURATION")
print("=" * 60)

training_args = TrainingArguments(
    output_dir                  = OUTPUT_DIR,
    num_train_epochs            = 5,
    per_device_train_batch_size = 4,
    per_device_eval_batch_size  = 4,
    learning_rate               = 3e-5,
    weight_decay                = 0.01,
    eval_strategy               = "epoch",
    save_strategy               = "epoch",
    load_best_model_at_end      = True,
    metric_for_best_model       = "accuracy",
    seed                        = SEED,
    logging_steps               = 5,
    report_to                   = "none",   # disable wandb / MLflow
)

print(f"Epochs       : {training_args.num_train_epochs}")
print(f"Batch size   : {training_args.per_device_train_batch_size}")
print(f"Learning rate: {training_args.learning_rate}")
print(f"Output dir   : {training_args.output_dir}")


# ── 6. Train ──────────────────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("5. TRAINING")
print("=" * 60)

trainer = Trainer(
    model           = model,
    args            = training_args,
    train_dataset   = train_tokenised,
    eval_dataset    = test_tokenised,
    compute_metrics = compute_metrics,
)

print("Starting training… (this may take a few minutes on CPU)")
train_result = trainer.train()
print(f"\nTraining complete.")
print(f"  Train loss     : {train_result.training_loss:.4f}")
print(f"  Steps          : {train_result.global_step}")
print(f"  Time (seconds) : {train_result.metrics['train_runtime']:.1f}")


# ── 7. Evaluate ───────────────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("6. EVALUATION ON TEST SET")
print("=" * 60)

eval_result = trainer.evaluate()
print(f"Test accuracy: {eval_result['eval_accuracy']:.4f}")
print(f"Test loss    : {eval_result['eval_loss']:.4f}")

# Detailed classification report
predictions = trainer.predict(test_tokenised)
pred_labels = np.argmax(predictions.predictions, axis=1)
true_labels = predictions.label_ids

print("\nClassification report:")
print(classification_report(
    true_labels, pred_labels,
    target_names=["NEGATIVE", "POSITIVE"],
))


# ── 8. Save and reload ────────────────────────────────────────────────────────

print("=" * 60)
print("7. SAVING AND RELOADING THE MODEL")
print("=" * 60)

save_path = os.path.join(OUTPUT_DIR, "best_model")
trainer.save_model(save_path)
tokenizer.save_pretrained(save_path)
print(f"Model saved to: {save_path}")

# Load the saved model directly into a pipeline
fine_tuned_pipeline = pipeline(
    "text-classification",
    model=save_path,
    tokenizer=save_path,
)
print("Fine-tuned model loaded back successfully.")


# ── 9. Compare base vs fine-tuned ────────────────────────────────────────────

print("\n" + "=" * 60)
print("8. BASE MODEL vs FINE-TUNED MODEL")
print("=" * 60)

base_pipeline = pipeline(
    "text-classification",
    model="distilbert-base-uncased-finetuned-sst-2-english",
)

domain_texts = [
    "Fast delivery, product exactly as described. Very happy.",      # positive
    "Battery drains in under an hour. Useless.",                      # negative
    "Arrived cracked and the returns process is a nightmare.",        # negative
    "Best headphones I've owned. Sound quality is phenomenal.",       # positive
    "Broke after one day of light use. Shocking quality.",            # negative
]

print(f"{'Text':<55} {'Base':<20} {'Fine-tuned'}")
print("-" * 100)
for text in domain_texts:
    base   = base_pipeline(text)[0]
    tuned  = fine_tuned_pipeline(text)[0]
    b_str  = f"{base['label']} ({base['score']:.2f})"
    t_str  = f"{tuned['label']} ({tuned['score']:.2f})"
    print(f"{text[:53]:<55} {b_str:<20} {t_str}")
