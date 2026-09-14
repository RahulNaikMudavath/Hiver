# Amazon Customer Support Knowledge Base: Payments & Cashback

## 1. Scope & Associated Intents
- `payment_or_cashback`: Issues involving credit/debit card charges, temporary authorization holds, split charges, declined payments, gift card redemptions, Amazon Pay transactions, promotional cashback, reward point redemptions, and billing statement inquiries.

---

## 2. Core Policies & Billing Mechanics

### Authorization Holds vs. Actual Charges
- **Dispatch Billing Rule**: Amazon **does not charge** a payment method until an item is dispatched from the fulfillment center.
- **Pending Authorization**: When an order is placed, an authorization hold for the estimated total is placed to verify funds. This hold drops off according to the customer's bank policy (usually within 3–7 business days).
- **Split Shipments / Multiple Charges**: If an order contains multiple items that ship separately or from different warehouses, the customer will see multiple partial charges on their bank statement. The sum of these charges will always equal the original order total.

### Declined Payments & Payment Updates
- When a payment is declined, the order is paused for up to 48 hours rather than immediately cancelled.
- Customers can update payment details by visiting "Your Orders" -> "Revise Payment Method" or "Your Payments" (`amazon.com/cpe/yourpayments/wallet`).
- Agents should advise customers to verify:
  1. Card expiration date and CVV.
  2. Billing address matching bank records.
  3. Daily spending limits or bank fraud alerts on online e-commerce transactions.

### Gift Cards & Cashback Promotions
- **Gift Card Redemption**: Once a gift card claim code is redeemed to an account, it cannot be transferred to another account or redeemed for cash (unless required by law).
- **Cashback Promotions**: Promotional credits and partner cashbacks (e.g., Prime Visa 5% cashback or Amazon Pay promotional cashback) may take 1–2 billing cycles or 24–48 hours post-dispatch to reflect on statement or balance.

---

## 3. Communication Guidelines & Tone on Twitter/Social Media
- **Tone**: Professional, discreet, precise, reassuring.
- **CRITICAL SECURITY RULE**: **Never** ask for full credit card numbers, CVV, or bank account credentials. Under PCI-DSS compliance, any message containing sensitive payment information must be directed to authenticated secure channels.
- **Clarify Authorizations**: Proactively explain pending vs settled charges when customers report "double charges" on recent orders.

---

## 4. Decision Matrix: Auto-Handle vs. Human Escalation

| Scenario | Recommendation | Reason / Escalation Trigger |
| :--- | :--- | :--- |
| Customer confused by multiple charges from one order (split shipment) | **Auto-Handle** | Informational; explain Amazon charges upon item dispatch and ask them to compare invoice breakdown in "Your Orders". |
| Customer reports card declined on a pending order | **Auto-Handle** | Self-serve guidance; direct to "Your Orders" -> "Revise Payment Method" and bank verification checklist. |
| Customer asks how to redeem an Amazon Gift Card or check balance | **Auto-Handle** | Standard navigation guidance (`amazon.com/gc/redeem`). |
| Customer has two identical *posted* (settled) charges on bank statement for the same order | **Escalate to Human** | Financial discrepancy; requires billing team transaction audit and duplicate charge refund. |
| Unrecognized charge appearing on customer's credit card statement from Amazon | **Escalate to Human** | Security/Fraud inquiry; requires charge lookup by billing specialist or fraud intake. |
| Promotional cashback / gift card credit promised during sale did not credit | **Escalate to Human** | Account concession review; agent must verify promotional eligibility and manually apply credit. |
| Customer states they have filed or intend to file a bank chargeback | **Escalate to Human** | Legal/Financial risk; requires account specialist handling to prevent account closure/suspension. |

---

## 5. Canonical Response Templates

### Template: Multiple / Split Charges Explanation (Informational)
> "Thanks for reaching out! When items in an order ship separately from different fulfillment centers, you may see separate charges that add up to your order total. We also only charge your card as each item dispatches. You can review the exact invoice breakdown in 'Your Orders' here: [LINK]! ^CS"

### Template: Revise Declined Payment (Self-Serve)
> "I'm sorry for any trouble with your payment! You can easily update your card or select a new payment method without placing a new order by visiting 'Your Orders' and selecting 'Revise Payment Method' here: [LINK]. Please also check that your billing address matches your bank records! ^CS"

### Template: Billing Discrepancy Escalation (Human Escalation)
> "We take any billing concerns very seriously and want to review this charge immediately. Because your payment privacy is paramount, please connect with our secure support team via DM here: [DM_LINK] so we can investigate this directly on your account. ^CS"
