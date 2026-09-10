# Hiver AI Support Agent

An end-to-end AI-powered customer support agent built on the Twitter Customer Support dataset. The system features intent taxonomy discovery, semantic retrieval, hybrid intent classification, context-aware reply generation, policy-based escalation, and comprehensive evaluation benchmarks.

---

## 📂 Project Structure

```
hiver-ai-support-agent/
│
├── README.md
├── requirements.txt
├── .env.example
│
├── data/
│   ├── raw/                # Raw downloaded datasets
│   ├── processed/          # Cleaned & structured conversation threads
│   └── golden/             # Golden test set for evaluation
│
├── src/
│   ├── data/
│   │   ├── download.py          # Script/module to download raw dataset
│   │   ├── preprocess.py        # Cleans tweets and standardizes format
│   │   └── build_threads.py     # Reconstructs multi-turn support threads
│   │
│   ├── taxonomy/
│   │   └── discover_intents.py  # Intent clustering & taxonomy generation
│   │
│   ├── retrieval/
│   │   ├── embeddings.py        # Text embeddings generation
│   │   ├── index.py             # Vector index (FAISS) management
│   │   └── retrieve.py          # Context retrieval for queries
│   │
│   ├── classification/
│   │   ├── baseline_majority.py # Majority class baseline
│   │   ├── baseline_tfidf.py    # TF-IDF + LogisticRegression baseline
│   │   └── llm_classifier.py    # Few-shot LLM intent classifier
│   │
│   ├── generation/
│   │   └── reply_generator.py   # Grounded response generation with LLM
│   │
│   ├── escalation/
│   │   └── policy.py            # Rule- & confidence-based escalation logic
│   │
│   └── agent.py                 # Core unified agent orchestration pipeline
│
├── evaluation/
│   ├── run_eval.py              # End-to-end evaluation runner
│   ├── metrics.py               # Classification & retrieval metrics
│   ├── judge.py                 # LLM-as-a-judge evaluation harness
│   ├── human_judge_agreement.py # Inter-annotator & judge agreement analysis
│   └── failure_analysis.py      # Error categorization and failure drill-downs
│
├── experiments/
│   └── results/                 # Experiment logs, JSON metrics, confusion matrices
│
├── report/
│   └── report.md                # Detailed technical report and analysis
│
└── tests/
    ├── test_classifier.py       # Unit tests for classification modules
    ├── test_retrieval.py        # Unit tests for retrieval pipeline
    └── test_agent.py            # Unit tests for agent pipeline
```

---

## 🚀 Getting Started

### 1. Environment Setup

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

### 2. Download Data

```powershell
python -m src.data.download
```

### 3. Preprocess & Build Threads

```powershell
python -m src.data.preprocess
python -m src.data.build_threads
```

### 4. Discover Taxonomy & Build Retrieval Index

```powershell
python -m src.taxonomy.discover_intents
python -m src.retrieval.index
```

### 5. Run Evaluations & Tests

```powershell
pytest tests/
python -m evaluation.run_eval
```
