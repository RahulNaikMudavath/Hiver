# Amazon Customer Support Knowledge Base: Seller Support & Marketplace

## 1. Scope & Associated Intents
- `seller_support_issue`: Inquiries involving third-party marketplace sellers, orders "Sold and Shipped by Third-Party Sellers" (FBM), Fulfilled by Amazon (FBA) seller distinction, contacting marketplace sellers, filing A-to-z Guarantee claims, reporting rogue sellers, and redirecting third-party merchants requesting Seller Central seller-side assistance.

---

## 2. Core Policies & Marketplace Governance

### Marketplace Fulfillment Models
- **Sold and Shipped by Amazon**: Amazon handles shipping, inventory, returns, and direct customer support.
- **Fulfilled by Amazon (FBA)**: Sold by a third-party merchant, but packed and shipped from Amazon fulfillment centers. Amazon handles all delivery, return, and customer service inquiries.
- **Sold and Shipped by Seller (FBM)**: The third-party merchant stores, packs, ships, and handles frontline customer service and return authorisations directly.

### The A-to-z Guarantee
- **Protection Scope**: Protects buyers when purchasing physical items sold and shipped by a third-party seller. Covers both timely delivery and the condition of the item.
- **Claim Process**:
  1. Customer must first contact the seller via "Contact Seller" in "Your Orders".
  2. The seller has **48 hours** to respond and provide a resolution.
  3. If the seller does not respond within 48 hours, or cannot resolve the issue (e.g., refuses valid return/refund for a defective or missing item), the customer can file an **A-to-z Guarantee Claim**.
  4. Amazon investigates and reimburses the customer directly if the claim is approved.

### Seller Inquiries on Social Media (Merchant Redirection)
- **Support Boundary**: The `@AmazonHelp` social team provides **customer/buyer support only**.
- **Merchant Routing**: Third-party merchants asking about Seller Central login, seller disbursements, listing suspensions, seller performance metrics, or FBA inbound inventory must be routed to **Seller Central Help** (`sellercentral.amazon.com`) or dedicated seller channels (`@AmazonSeller`).

### Off-Amazon Payment Fraud Alert
- Amazon strictly prohibits sellers from asking customers to pay via wire transfer, Western Union, direct bank transfer, or external payment links. Any off-Amazon payment request must be flagged immediately as potential fraud.

---

## 3. Communication Guidelines & Tone on Twitter/Social Media
- **Tone**: Professional, clear, objective, protective of buyer rights.
- **Clarify FBM vs FBA**: Always check whether the order was fulfilled by Amazon or the seller so the customer knows who has physical custody of the package.
- **Merchant Separation**: Politely clarify the boundary between consumer support and merchant Seller Support.

---

## 4. Decision Matrix: Auto-Handle vs. Human Escalation

| Scenario | Recommendation | Reason / Escalation Trigger |
| :--- | :--- | :--- |
| Buyer asks how to message a third-party seller about an order | **Auto-Handle** | Navigation guidance; direct to "Your Orders" -> "Problem with Order" -> "Contact Seller". |
| Third-party seller asks for help with Seller Central account suspension or inventory | **Auto-Handle** | Domain routing; inform user that this channel is for consumer support and direct to `sellercentral.amazon.com`. |
| Customer asks how the A-to-z Guarantee works and eligibility rules | **Auto-Handle** | Informational; provide A-to-z Guarantee overview and link (`amazon.com/help/atoz`). |
| Seller has not responded to buyer message after >48 hours and package is missing | **Escalate to Human** | A-to-z Claim filing; agent can file claim on customer's behalf or expedite refund. |
| Marketplace seller sent abusive, threatening messages, or asked for off-platform payment | **Escalate to Human** | Trust & Safety violation; immediate seller investigation and account shielding required. |
| Customer's A-to-z Claim was denied but customer has proof of timely delivery failure | **Escalate to Human** | Claim appeal; requires senior specialist review of tracking and courier records. |

---

## 5. Canonical Response Templates

### Template: Contacting a Third-Party Seller (Self-Serve)
> "For orders sold and shipped directly by a marketplace seller, you can contact them directly through your account! Head over to 'Your Orders', find the order, and select 'Problem with Order' or 'Contact Seller' here: [LINK]. Sellers typically reply within 48 hours! ^CS"

### Template: Seller Central Inquiry Routing (Seller Redirection)
> "Hi there! Our team here assists with Amazon customer and buyer purchases. For assistance with your Seller Central account, inventory, or seller performance, please visit Seller Central Help at https://sellercentral.amazon.com/cu/contact-us or reach out to our dedicated seller support teams! ^CS"

### Template: Unresponsive Seller / A-to-z Escalation (Human Escalation)
> "If a marketplace seller hasn't responded within 48 hours to resolve your order issue, our A-to-z Guarantee is here to protect you. We'd like to help you submit or review your claim directly. Please send us a secure DM here: [DM_LINK] so we can get this resolved! ^CS"
