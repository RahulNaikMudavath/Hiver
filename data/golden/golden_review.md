# Golden Evaluation Set Review & Annotation Log

> [!IMPORTANT]
> **Dataset Status:** LLM-Assisted Draft  
> **Annotation Status:** `llm_assisted_needs_human_verification`  
> These annotations were produced via context-aware LLM evaluation following strict taxonomy priority rules. They require manual human review and verification before being designated as the final ground-truth gold set.

---

## 1. Dataset Summary

The Golden Evaluation Set serves as the high-fidelity benchmark for evaluating AI Customer Support Agents on Amazon customer service interactions from Twitter (`AmazonHelp`).
To guarantee balanced multi-class evaluation and prevent popular intents (like delivery status delays) from overwhelming rare but critical issues (like account security or system errors), the dataset was created via stratified sampling across 17 locked taxonomy classes.

| Metric | Value |
| :--- | :--- |
| **Source Candidate Pool** | `data/golden/golden_candidates_v2.jsonl` (250 candidates) |
| **Final Draft Size** | **200 evaluation examples** |
| **Unique Candidate IDs** | 200 |
| **Unique Target Tweet IDs** | 200 |
| **Taxonomy Scope** | 17 locked intent classes |
| **Null Gold Labels** | 0 |
| **Invalid Labels** | 0 |
| **Suggested vs. Gold Disagreements** | 5 |
| **Ambiguous Cases Documented** | 1 |

---

## 2. Validation Checks

All automated sanity and schema checks passed successfully:

- [x] **Exact Count:** Exactly 200 records generated.
- [x] **Candidate ID Uniqueness:** 200 unique `candidate_id` values.
- [x] **Tweet ID Uniqueness:** 200 unique `target_tweet_id` values.
- [x] **Label Validity:** All 200 records belong to the 17 locked taxonomy labels.
- [x] **Zero Nulls:** No null or blank `gold_intent` entries.
- [x] **PII Protection:** Strict regex masking applied to phone numbers, emails, order IDs, tracking codes, and handles.
- [x] **Context Preservation:** Full conversation thread preserved with inbound/outbound speaker demarcation.

---

## 3. Gold-Label Target Allocation & Distribution

The 200 selected examples strictly follow the target stratification specified for the benchmark:

| Intent Class | Target Allocation | Actual Selected | % of Golden Set |
| :--- | :---: | :---: | :---: |
| `delivery_status_delay` | 35 | 35 | 17.5% |
| `delivery_not_received` | 13 | 13 | 6.5% |
| `delivery_carrier_issue` | 20 | 20 | 10.0% |
| `order_cancellation` | 6 | 6 | 3.0% |
| `return_issue` | 8 | 8 | 4.0% |
| `refund_issue` | 10 | 10 | 5.0% |
| `product_issue` | 14 | 14 | 7.0% |
| `payment_or_cashback` | 10 | 10 | 5.0% |
| `pricing_or_promotion` | 10 | 10 | 5.0% |
| `account_access_security` | 8 | 8 | 4.0% |
| `prime_or_subscription` | 8 | 8 | 4.0% |
| `product_service_information` | 22 | 22 | 11.0% |
| `customer_support_experience` | 20 | 20 | 10.0% |
| `seller_support_issue` | 5 | 5 | 2.5% |
| `technical_or_system_issue` | 5 | 5 | 2.5% |
| `other_support` | 4 | 4 | 2.0% |
| `non_support_social` | 2 | 2 | 1.0% |
| **TOTAL** | **200** | **200** | **100.0%** |

---

## 4. Disagreements: Suggested Intent vs. Gold Intent

In 5 instances, the candidate's initial `suggested_intent` was overridden based on the full conversation context and the priority rules:

| Candidate ID | Target Tweet ID | Suggested Intent | Verified Gold Intent | Rationale & Context Signals |
| :---: | :---: | :--- | :--- | :--- |
| **73** | `2139755` | `prime_or_subscription` | `delivery_status_delay` | Priority Rule A: Late delivery of an order placed with Prime is classified as delivery_status_delay. |
| **76** | `2981609` | `delivery_status_delay` | `delivery_carrier_issue` | Priority Rule G: Courier falsely claimed delivery was attempted when customer was home; driver behavior issue. |
| **86** | `726786` | `delivery_carrier_issue` | `delivery_not_received` | Priority Rule H: Customer reports phone order was marked 'undelivered' without notice or receipt. |
| **90** | `2625949` | `refund_issue` | `prime_or_subscription` | Customer inquiring about unauthorized Amazon Prime subscription fee and membership cancellation. |
| **205** | `1827355` | `delivery_status_delay` | `delivery_not_received` | Priority Rule H: Order was lost by courier and never received by customer. |

---

## 5. Ambiguous & Borderline Cases Requiring Human Review

The following 1 borderline examples were identified and documented for explicit human verification:

### Candidate 22 (Tweet ID: `1558035`)
- **Target Message:** > @AmazonHelp Oui oui c'est déjà fait! Ils ne peuvent rien faire tant que l'enquête n'est pas ouverte apparement ....
- **Suggested Intent:** `delivery_not_received`
- **Assigned Gold Intent:** `delivery_not_received`
- **Annotation Note:** Customer received an empty package with the ordered phone missing; treated as delivery not received.
- **Reviewer Action:** Verify if context sufficiently justifies the boundary assignment.

---

## 6. PII Masking Summary

To comply with data privacy standards and prevent data contamination:
1. **Order IDs:** Amazon order format strings (`\d{3}-\d{7}-\d{7}`) replaced with `[ORDER_ID]`.
2. **Phone Numbers:** International, 10-digit mobile numbers, and UK toll-free numbers replaced with `[PHONE]`.
3. **Email Addresses:** Standard email regex patterns replaced with `[EMAIL]`.
4. **Tracking Numbers:** Multi-digit courier tracking identifiers replaced with `[TRACKING_ID]`.
5. **Usernames & Handles:** All customer and third-party handles (`@\w+`) replaced with `[USERNAME]`. The official brand handle `@AmazonHelp` is retained to preserve conversation turn semantics.

---

## 7. Next Steps for Human Verification

1. Open `data/golden/golden_review.md` and inspect the flagged disagreements and borderline cases.
2. Review sample rows in `data/golden/golden_eval_draft.jsonl`.
3. Update `annotation_status` from `llm_assisted_needs_human_verification` to `human_verified_gold` once manual sign-off is completed.
4. Promote the verified file to `data/golden/test_set.jsonl` for final model evaluation and benchmark reporting.
