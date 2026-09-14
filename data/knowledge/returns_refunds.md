# Amazon Customer Support Knowledge Base: Returns & Refunds

## 1. Scope & Associated Intents
- `return_issue`: Inquiries regarding initiating returns, return policy windows, return labels, drop-off locations (UPS, Kohl's, Lockers), return shipping costs, and item eligibility.
- `refund_issue`: Inquiries regarding refund status, missing refunds, refund processing timelines, discrepancies in refunded amounts, and restocking fees.

---

## 2. Core Policies & Timelines

### Return Windows & Eligibility
- **Standard Policy**: Most physical items fulfilled by Amazon can be returned within **30 days of receipt** in new and unopened or gently tested condition.
- **Holiday Extension**: Items purchased between November 1 and December 31 can typically be returned until January 31 of the following year.
- **Non-Returnable Items**: Opened software, hazardous materials (flammable liquids/gases), downloadable products, gift cards, grocery items, and items with missing serial numbers. For damaged/defective non-returnable items, Amazon typically issues a refund without requiring a return.

### Return Drop-Off Options & QR Codes
- **Label-Free / Box-Free Drop-Off**: Available at participating UPS Stores, Kohl's, and Whole Foods locations. Customers show a mobile QR code generated in the "Returns Center"; no boxing or printing required.
- **Amazon Locker / Hub**: Packages within size limits can be dropped off at designated automated lockers.
- **Return Shipping Fees**: Free returns apply to Prime-eligible items and any order where the return is due to Amazon error, transit damage, or defect. Customer remorse returns on non-qualifying 3P items may incur return postage deducted from the refund.

### Refund Timelines by Payment Method
- **Amazon Gift Card Balance**: 2–4 hours after the return is scanned at the drop-off carrier.
- **Credit / Debit Card**: 3–5 business days after warehouse processing (can take up to 10 business days depending on issuing financial institution).
- **Direct Debit / Bank Account**: Up to 10 business days.
- **Instant Refunds**: On select items, refund is issued immediately upon first carrier drop-off scan, subject to later inspection.

---

## 3. Communication Guidelines & Tone on Twitter/Social Media
- **Tone**: Transparent, polite, supportive, reassuring.
- **Clarity on Timelines**: Always specify that card refunds depend on the customer's bank statement cycle after Amazon releases funds.
- **Privacy Policy**: Do not ask for order numbers or bank card digits publicly. Direct to authenticated account portals.

---

## 4. Decision Matrix: Auto-Handle vs. Human Escalation

| Scenario | Recommendation | Reason / Escalation Trigger |
| :--- | :--- | :--- |
| Customer asks how to return an item within 30-day window | **Auto-Handle** | Standard self-serve guidance; provide Online Returns Center link (`amazon.com/returns`). |
| Customer asks where their refund is within the 3–5 business day processing window | **Auto-Handle** | Informational; explain standard banking processing timelines and how to view refund status under "Your Orders". |
| Customer needs return label reprinted or QR code re-sent | **Auto-Handle** | Guide to "Your Orders" -> "View Return/Refund Status" to access QR code/label. |
| Refund shows completed on Amazon over 10 business days ago, but bank has no record | **Escalate to Human** | Financial discrepancy; requires Acquirer Reference Number (ARN) retrieval by a billing agent. |
| Customer received defective/damaged item that is hazardous or non-returnable | **Escalate to Human** | Manual override required to grant refund without requiring physical return. |
| Warehouse claims returned package was empty or wrong item returned | **Escalate to Human** | Concession dispute; requires warehouse review and incident report filing. |
| Item returned >14 days ago, tracking shows delivered to warehouse, but no refund scan | **Escalate to Human** | Warehouse intake delay requiring agent manual refund push. |

---

## 5. Canonical Response Templates

### Template: How to Return (Self-Serve)
> "Returning an item is quick and easy! You can generate a return QR code or shipping label by going to 'Your Orders', selecting the item, and clicking 'Return or replace items' here: [LINK]. Most locations like The UPS Store or Kohl's don't even require a box or label! Let us know if you need any assistance. ^CS"

### Template: Refund Status / Timelines (Informational)
> "Once your return is processed, card refunds typically reflect within 3-5 business days depending on your bank's processing times. You can track your refund progress anytime under 'View Return/Refund Status' in 'Your Orders' here: [LINK]. Thanks for your patience! ^CS"

### Template: Delayed Refund Escalation (Human Escalation)
> "We want to make sure your refund is settled right away since it's past the usual timeframe. Because we need to safely check your account and order details, please connect with our team securely via DM here: [DM_LINK]. We'll get this investigated immediately! ^CS"
