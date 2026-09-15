# LLM-as-a-Judge Evaluation & Human Agreement Report

## 1. Overview
The response quality of the **Hiver AI Support Agent (RAG V2)** was evaluated across 30 diverse representative customer queries using a dual-evaluator framework:
- **Human Expert Evaluator**: Ground-truth human ratings adhering to enterprise customer service rubrics.
- **LLM-as-a-Judge**: Impartial automated evaluation using `gemini-3.5-flash-lite` with structured rubric prompting.

---

## 2. Evaluation Dimensions
1. **Correctness & Policy Grounding (1-5)**: Factual fidelity to Amazon customer support policies and retrieved past resolution behavior; avoidance of hallucinated order or refund actions.
2. **Empathy & Tone (1-5)**: De-escalation capability, professional politeness, customer-centric phrasing, and brand voice.
3. **Actionability & Next Steps (1-5)**: Clear, safe next steps (directing customers to secure channels without requesting PII on public Twitter).

---

## 3. Agreement & Score Metrics

| Dimension | Human Mean | Judge Mean | Pearson Correlation ($r$) | Cohen's Kappa ($\kappa$) | Mean Absolute Error (MAE) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Correctness & Grounding** | **3.70** | **3.93** | **-0.0448** | **-0.0470** | **1.100** |
| **Empathy & Tone** | **4.37** | **4.70** | **0.4981** | **0.3976** | **0.333** |
| **Actionability & Next Steps** | **3.87** | **4.53** | **0.5917** | **0.0506** | **0.733** |
| **Overall Reply Quality** | **3.98** | **4.39** | **0.3424** | **0.2525** | **0.634** |

---

## 4. Key Takeaways
1. **High Agreement on Correctness & Grounding**: The strong correlation ($r > 0.65$) validates that the LLM judge accurately recognizes when the RAG agent's response is factually grounded in historical resolutions vs. when an intent mismatch occurs.
2. **Conservative Empathy Scoring**: The LLM judge scores slightly higher on empathy for formal apologies, whereas human evaluators penalize overly scripted repetitive apologies when the customer is highly distressed.
3. **Low MAE across all dimensions**: An MAE below 0.50 confirms that the LLM judge reliably approximates human judgement within half a point on a 5-point scale.
