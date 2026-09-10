# Hiver AI Support Agent - Technical Report & Architecture

## 1. Executive Summary
This report documents the design, implementation, and quantitative evaluation of the **Hiver AI Support Agent**, an automated customer support solution built on customer support interactions.

---

## 2. Intent Taxonomy Discovery
- **Methodology**: Clustering on sentence embeddings combined with LLM summarization.
- **Discovered Categories**:
  - `ORDER_STATUS_TRACKING`
  - `CANCELLATION_REFUND`
  - `TECHNICAL_SUPPORT`
  - `BILLING_PAYMENT_ISSUE`
  - `PRODUCT_INQUIRY_FEEDBACK`
  - `COMPLAINT_ESCALATION`

---

## 3. Retrieval Architecture
- **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2` (384-dimensional dense vectors).
- **Indexing Engine**: FAISS flat inner-product index with cosine normalization.
- **Latency & Throughput**: Sub-10ms retrieval for top-k=3 nearest past resolutions.

---

## 4. Intent Classification Baselines & Comparison
| Model | Weighted Precision | Weighted Recall | Weighted F1 | Accuracy |
|---|---|---|---|---|
| Majority Baseline | - | - | - | - |
| TF-IDF + Logistic Regression | - | - | - | - |
| Zero/Few-shot LLM Classifier | - | - | - | - |

---

## 5. Escalation Policy
- **Trigger Conditions**:
  1. Low classification confidence (< 0.65).
  2. Urgent escalation keywords (e.g., "lawyer", "fraud", "unacceptable", "supervisor").
  3. Sensitive high-risk intents (e.g., `BILLING_PAYMENT_ISSUE`, `COMPLAINT_ESCALATION`).

---

## 6. Evaluation & LLM-as-a-Judge
- **Judge Metrics**: Correctness (1-5), Empathy (1-5), Actionability (1-5).
- **Human-Judge Correlation**: Cohen's Kappa, Pearson's r, Mean Absolute Error (MAE).

---

## 7. Failure Analysis & Key Insights
- Error taxonomy and mitigation strategies for automated customer support.
