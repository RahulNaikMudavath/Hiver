# Hiver AI Customer Support Agent (AmazonHelp)

> **Submission for Hiver SDE Intern Take-Home Assignment**  
> An end-to-end, production-grade AI Customer Support Agent built on real customer service interactions from Twitter (`@AmazonHelp`).  
> Features a 17-class operational intent taxonomy, TF-IDF semantic retrieval over 178,000 historical resolutions, context-aware reply generation, policy-based escalation, and an LLM-as-a-judge evaluation harness with human agreement metrics.

---

## ⚡ 15-Minute Headline Reproduction

Reproduce all headline benchmark results across all 4 systems (Baseline 1, Baseline 2, RAG V1, and RAG V2) in **under 10 seconds**:

```powershell
# 1. Clone and enter repo
git clone https://github.com/RahulNaikMudavath/Hiver.git
cd Hiver

# 2. Setup environment (Python 3.10+)
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# 3. Reproduce all headline benchmark results instantly
python scripts/reproduce_headline_results.py
```

### Output:
```
========================================================================================
                      HIVER AI SUPPORT AGENT — HEADLINE RESULTS
========================================================================================
Model                        | Accuracy   | Weighted F1  | Weighted P  | Macro F1  
----------------------------------------------------------------------------------------
Baseline 1 (Keyword)         |    20.00% |       0.2407 |      0.4266 |     0.2302
Baseline 2 (Zero-shot LLM)   |    22.50% |       0.3047 |      0.6563 |     0.3082
RAG Agent V1                 |    63.00% |       0.6225 |      0.6449 |     0.5708
RAG Agent V2                 |    64.50% |       0.6506 |      0.6866 |     0.6143
========================================================================================
Key Improvement (RAG V2 vs Baseline 1): +44.50% absolute (+222.5% relative)
Key Improvement (RAG V2 vs Baseline 2): +42.00% absolute (+186.7% relative)
========================================================================================
```

---

## 🏗️ System Architecture

```
[Customer Query on Twitter] ──► [PII Masking Filter] ──► [TF-IDF Retrieval Index]
                                                                  │ (Top-5 Nearest
                                                                  │  Resolutions)
                                                                  ▼
[LLM Agent + Decision Policy] ◄───────────────────────────────────┘
         │
         ├──► 1. Intent Classification (17 Locked Taxonomy Classes)
         ├──► 2. Grounded Reply Drafting (Aligned with Amazon policy)
         └──► 3. Escalation Decision (Auto-handle vs. Human Review + Stated Reason)
```

---

## 📊 Key Deliverables Summary

| Deliverable | Description | Key Artifact / Script |
| :--- | :--- | :--- |
| **1. Runnable Pipeline** | Complete runnable code + reproduction in <15 minutes | [`scripts/reproduce_headline_results.py`](file:///d:/aiml%20related%20projects/hiver%20assignment/scripts/reproduce_headline_results.py)<br>[`scripts/test_3_cases.py`](file:///d:/aiml%20related%20projects/hiver%20assignment/scripts/test_3_cases.py) |
| **2. Golden Evaluation Set** | 200 hand-labelled, stratified test cases across 17 classes | [`data/golden/golden_eval_draft.jsonl`](file:///d:/aiml%20related%20projects/hiver%20assignment/data/golden/golden_eval_draft.jsonl)<br>[`data/golden/golden_review.md`](file:///d:/aiml%20related%20projects/hiver%20assignment/data/golden/golden_review.md) |
| **3. Evaluation Harness** | Automated classification metrics + LLM Judge + Human Agreement | [`evaluation/gemini_judge.py`](file:///d:/aiml%20related%20projects/hiver%20assignment/evaluation/gemini_judge.py)<br>[`scripts/evaluate_reply_quality.py`](file:///d:/aiml%20related%20projects/hiver%20assignment/scripts/evaluate_reply_quality.py)<br>[`experiments/results/judge_evaluation_report.md`](file:///d:/aiml%20related%20projects/hiver%20assignment/experiments/results/judge_evaluation_report.md) |
| **4. Technical Report** | 6-page comprehensive report covering framing, failure modes & blindspots | [`report/report.md`](file:///d:/aiml%20related%20projects/hiver%20assignment/report/report.md) |
| **5. Decision Log** | 15 non-obvious engineering decisions and technical rationales | [Section 9 in `report/report.md`](file:///d:/aiml%20related%20projects/hiver%20assignment/report/report.md#9-decision-log-15-non-obvious-engineering-decisions) |

---

## 🎯 Response Quality & Human-Judge Agreement

Evaluated on 30 representative test replies across 3 core dimensions on a 1–5 scale:

| Dimension | Human Mean | Judge Mean | Pearson Correlation ($r$) | Cohen's Kappa ($\kappa$) | Mean Absolute Error (MAE) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Correctness & Policy Grounding** | 3.70 / 5.0 | 3.93 / 5.0 | 0.5210 | 0.4280 | 0.433 |
| **Empathy & Professional Tone** | 4.37 / 5.0 | 4.70 / 5.0 | **0.4981** | **0.3976** | **0.333** |
| **Actionability & Policy Safety** | 3.87 / 5.0 | 4.53 / 5.0 | **0.5917** | 0.3120 | 0.667 |
| **Overall Composite Score** | **3.98 / 5.0** | **4.39 / 5.0** | **0.5640** | **0.3850** | **0.410** |

*Run agreement evaluation yourself:*
```powershell
python scripts/evaluate_reply_quality.py
```

---

## 🔍 Top 5 Failure Modes & Hypotheses

Detailed drill-down on the 71 misclassifications in [`data/golden/rag_failures_v2_clean.txt`](file:///d:/aiml%20related%20projects/hiver%20assignment/data/golden/rag_failures_v2_clean.txt):

1. **Courier Mention vs. Delivery Delay (`delivery_carrier_issue` $\rightarrow$ `delivery_status_delay`)**: Mention of courier names (UPS, USPS) alongside lateness causes delay semantics to drown out specific carrier-fault allegations.
2. **Feature Inquiry vs. Glitch (`product_service_information` $\rightarrow$ `technical_or_system_issue`)**: Unsupported formats (e.g. non-English fonts on Kindle) misdiagnosed as software bugs rather than inherent device limitations.
3. **Sentiment Masking Root Cause (`customer_support_experience` vs. `refund_issue`)**: Frustrated complaints about prior rep rudeness obscure the underlying transactional refund request.
4. **Delivery Not Received vs. Immediate Refund Demands (`delivery_not_received` vs. `refund_issue`)**: Aggressive customer demands for money override the misdelivery investigation intent.
5. **Long-Tail Intent Ambiguity (`other_support` / `non_support_social`)**: Greetings combined with operational questions confuse single-label boundary rules.

---

## ⚠️ "What is Misleading About My Headline Number?"

*(Mandatory Section from Assignment)*

- **Single-Label Ground Truth Penalizes Valid Multi-Intent Replies**: Customer tweets often combine multiple complaints (e.g. late delivery + rude driver + refund demand). If the model addresses the refund or carrier issue instead of delay, automated metrics score it as a 0% failure, even when the generated reply is accurate and helpful.
- **Stratified vs. Real Production Distribution**: The 200-example golden set intentionally balances rare intents (e.g. account security) equally. On live Amazon Twitter feeds, ~45% of traffic is delivery delays, which would artificially inflate accuracy on common intents while masking vulnerabilities on rare security tickets.
- **Retrieval Similarity Does Not Correlate with Classification Ease**: Average retrieval similarity for incorrect cases was 0.5855 vs 0.5431 for correct cases, demonstrating that high vector similarity does not imply clean classification.

Read the full technical analysis in [**`report/report.md`**](file:///d:/aiml%20related%20projects/hiver%20assignment/report/report.md).

---

## 🧪 Running Unit Tests

Verify agent orchestration, retrieval, and classification modules:

```powershell
python -m pytest tests/
```
All 6 integration and unit tests pass in ~6 seconds.

---

## 📁 Repository Map

```
hiver-ai-support-agent/
│
├── README.md                                # Quickstart, headline results, and system guide
├── requirements.txt                         # Python dependencies
├── .env.example                             # Environment variable template
│
├── data/
│   ├── golden/                              # 200-example golden test benchmark & review logs
│   │   ├── golden_eval_draft.jsonl          # 200 hand-labelled evaluation cases
│   │   ├── golden_review.md                 # Sampling & annotation log
│   │   ├── human_reply_ratings.json         # 30 human quality annotations
│   │   ├── baseline_keyword_predictions.jsonl # Baseline 1 predictions
│   │   ├── baseline_llm_predictions.jsonl   # Baseline 2 predictions
│   │   ├── rag_predictions.jsonl            # RAG Agent V1 predictions
│   │   └── rag_predictions_v2.jsonl         # RAG Agent V2 predictions
│   └── knowledge/                           # 10 domain knowledge guides (markdown)
│
├── scripts/
│   ├── reproduce_headline_results.py        # <10s headline reproduction script
│   ├── rag_agent.py                         # RAG Agent V1 (Frozen)
│   ├── rag_agent_v2.py                      # RAG Agent V2 (Optimized Decision Policy)
│   ├── evaluate_rag_agent.py                # V1 200-example evaluation runner
│   ├── evaluate_rag_agent_v2.py             # V2 200-example evaluation runner
│   ├── evaluate_reply_quality.py            # LLM Judge & Human Agreement harness
│   ├── analyze_rag_v2_failures.py           # V2 failure categorization & confusion analysis
│   └── test_3_cases.py                      # Interactive 3-case smoke test
│
├── evaluation/
│   ├── gemini_judge.py                      # LLM-as-a-judge implementation
│   ├── human_judge_agreement.py             # Cohen's Kappa, Pearson r, MAE calculators
│   └── failure_analysis.py                  # Error categorization utilities
│
├── experiments/results/
│   ├── human_judge_agreement.json           # Machine-readable agreement metrics
│   └── judge_evaluation_report.md           # Markdown judge evaluation summary
│
├── report/
│   └── report.md                            # Comprehensive 6-page technical report & decision log
│
└── tests/                                   # Pytest unit & integration tests
```
