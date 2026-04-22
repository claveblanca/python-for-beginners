"""
Chapter 13 — Example 04: Multiple NLP Tasks with Pipelines
===========================================================
Expanding beyond sentiment analysis — the same pipeline API
works for a wide range of NLP tasks. This file demonstrates
six common tasks, each with practical examples.

Tasks covered:
  1. Named Entity Recognition (NER)
  2. Text Summarisation
  3. Question Answering (extractive)
  4. Zero-shot Classification
  5. Text Generation
  6. Translation

Install:
    pip install transformers torch sentencepiece
"""

from transformers import pipeline

# ── 1. Named Entity Recognition (NER) ────────────────────────────────────────

print("=" * 60)
print("1. NAMED ENTITY RECOGNITION")
print("=" * 60)

# aggregation_strategy="simple" merges sub-word tokens back into full words
ner = pipeline("ner", aggregation_strategy="simple")

texts = [
    "Elon Musk founded SpaceX in 2002 and Tesla is headquartered in Austin, Texas.",
    "Apple released the iPhone 15 in September 2023 at the Steve Jobs Theater.",
    "The European Central Bank, based in Frankfurt, raised interest rates last week.",
]

for text in texts:
    print(f"\nText: {text}")
    entities = ner(text)
    print(f"  {'Entity':<25} {'Type':<10} {'Score'}")
    print("  " + "-" * 50)
    for ent in entities:
        print(f"  {ent['word']:<25} {ent['entity_group']:<10} {ent['score']:.3f}")


# ── 2. Text Summarisation ─────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("2. TEXT SUMMARISATION")
print("=" * 60)

summariser = pipeline(
    "summarization",
    model="sshleifer/distilbart-cnn-6-6",
    min_length=20,
    max_length=80,
    do_sample=False,
)

article = """
Python was created by Guido van Rossum and first released in 1991. It was designed
with an emphasis on code readability, and its syntax allows programmers to express
concepts in fewer lines of code than would be possible in languages such as C++ or
Java. Python provides constructs intended to enable clear programs on both a small
and large scale. In 2008, Python 3.0 was released as a significant revision of the
language that is not entirely backward-compatible. Python 2.7, the last major version
of Python 2, is not officially supported since January 2020. Python consistently ranks
as one of the most popular programming languages in developer surveys, and its
ecosystem of libraries for data science, machine learning, and web development
continues to grow rapidly.
"""

summary = summariser(article.strip())
print("Original length :", len(article.split()), "words")
print("Summary         :", summary[0]["summary_text"].strip())
print("Summary length  :", len(summary[0]["summary_text"].split()), "words")


# ── 3. Extractive Question Answering ──────────────────────────────────────────

print("\n" + "=" * 60)
print("3. EXTRACTIVE QUESTION ANSWERING")
print("=" * 60)

qa = pipeline(
    "question-answering",
    model="deepset/roberta-base-squad2",
)

context = """
The Hugging Face Transformers library was created in 2018 and has since become
the most widely used NLP library in the Python ecosystem. It provides thousands
of pre-trained models that can be used for tasks including text classification,
named entity recognition, question answering, text generation, and translation.
The library is maintained by Hugging Face, a company founded in 2016 and
headquartered in New York City. As of 2024, the Hugging Face Hub hosts over
500,000 models.
"""

questions = [
    "When was the Transformers library created?",
    "What company maintains the library?",
    "Where is Hugging Face headquartered?",
    "How many models does the Hub host?",
]

print(f"Context: {context[:80].strip()}...\n")
for question in questions:
    result = qa(question=question, context=context)
    print(f"Q: {question}")
    print(f"A: {result['answer']}  (score: {result['score']:.3f})")
    print()


# ── 4. Zero-shot Classification ───────────────────────────────────────────────

print("=" * 60)
print("4. ZERO-SHOT CLASSIFICATION")
print("=" * 60)

# No fine-tuning needed — the model reasons about arbitrary label names
zero_shot = pipeline("zero-shot-classification")

examples = [
    {
        "text": "The new firmware update bricked my router and I can't get online.",
        "labels": ["software bug", "hardware failure", "user error", "billing issue"],
    },
    {
        "text": "I was charged twice for the same order and nobody is answering my emails.",
        "labels": ["refund request", "delivery problem", "billing issue", "product defect"],
    },
    {
        "text": "The lid cracked after one month of normal use.",
        "labels": ["manufacturing defect", "user damage", "shipping damage", "software bug"],
    },
]

for ex in examples:
    result = zero_shot(ex["text"], candidate_labels=ex["labels"])
    print(f"Text    : {ex['text'][:70]}")
    print(f"Labels  :")
    for label, score in zip(result["labels"], result["scores"]):
        bar  = "█" * int(score * 25)
        flag = " ← best" if label == result["labels"][0] else ""
        print(f"  {label:<25} {bar:<28} {score:.3f}{flag}")
    print()


# ── 5. Text Generation ────────────────────────────────────────────────────────

print("=" * 60)
print("5. TEXT GENERATION")
print("=" * 60)

generator = pipeline(
    "text-generation",
    model="gpt2",
    max_new_tokens=60,
    num_return_sequences=2,
    do_sample=True,
    temperature=0.8,        # lower = more deterministic, higher = more creative
    top_p=0.92,             # nucleus sampling
    pad_token_id=50256,     # GPT-2 doesn't have a pad token — use EOS
)

prompts = [
    "Python is the most popular language for machine learning because",
    "The best way to learn data science is",
]

for prompt in prompts:
    print(f"Prompt: {prompt!r}")
    outputs = generator(prompt)
    for i, out in enumerate(outputs, 1):
        # strip the prompt from the generated text for cleaner display
        generated = out["generated_text"][len(prompt):]
        print(f"  [{i}] ...{generated.strip()[:120]}")
    print()


# ── 6. Translation ───────────────────────────────────────────────────────────

print("=" * 60)
print("6. TRANSLATION")
print("=" * 60)

# Helsinki-NLP models cover 1,000+ language pairs
en_to_fr = pipeline("translation_en_to_fr", model="Helsinki-NLP/opus-mt-en-fr")
en_to_de = pipeline("translation_en_to_de", model="Helsinki-NLP/opus-mt-en-de")
en_to_es = pipeline("translation_en_to_es", model="Helsinki-NLP/opus-mt-en-es")

sentences = [
    "Machine learning is revolutionising every industry.",
    "Please enter your text in the box below.",
    "The model was unable to classify this input with high confidence.",
]

for sentence in sentences:
    fr = en_to_fr(sentence)[0]["translation_text"]
    de = en_to_de(sentence)[0]["translation_text"]
    es = en_to_es(sentence)[0]["translation_text"]
    print(f"EN: {sentence}")
    print(f"FR: {fr}")
    print(f"DE: {de}")
    print(f"ES: {es}")
    print()


# ── 7. Chaining pipelines — translate then classify ───────────────────────────

print("=" * 60)
print("7. CHAINING PIPELINES — TRANSLATE → CLASSIFY")
print("=" * 60)

# Non-English reviews → translate to English → classify sentiment
fr_to_en    = pipeline("translation_fr_to_en", model="Helsinki-NLP/opus-mt-fr-en")
classifier  = pipeline("sentiment-analysis")

french_reviews = [
    "Ce produit est absolument magnifique, je l'adore !",
    "Qualité médiocre, ne tenez pas compte des avis positifs.",
    "Livraison rapide, produit conforme à la description.",
]

print(f"{'French review':<45} {'English':<45} {'Sentiment'}")
print("-" * 110)
for review in french_reviews:
    english   = fr_to_en(review)[0]["translation_text"]
    sentiment = classifier(english)[0]
    print(f"{review[:43]:<45} {english[:43]:<45} "
          f"{sentiment['label']} ({sentiment['score']:.2f})")
