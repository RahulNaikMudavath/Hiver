# Amazon Customer Support Knowledge Base: Prime & Subscriptions

## 1. Scope & Associated Intents
- `prime_or_subscription`: Inquiries regarding Amazon Prime membership, membership fee billing, auto-renewal settings, cancellations and refunds, Prime Video/Music/Gaming access, Prime Student, Prime Access, Amazon Household sharing, and digital add-on channels (e.g., Kindle Unlimited, Audible, Paramount+).

---

## 2. Core Policies & Membership Rules

### Prime Membership Benefits & Pricing
- **Core Benefits**: Fast, free delivery (Same-Day, One-Day, Two-Day), Prime Video streaming, Amazon Music Prime, Prime Gaming, Prime Reading, unlimited Amazon Photos storage, and exclusive early access to Lightning Deals.
- **Plans**: Monthly and Annual plans. Discounted tiers available for verified students (Prime Student) and qualifying government assistance recipients (Prime Access).
- **Amazon Household**: Allows 2 adults in a household to share Prime delivery benefits, Prime Video streaming, and digital content libraries without sharing account logins or payment details.

### Cancellation & Refund Policy
- **Self-Service Cancellation**: Customers can manage or end their membership anytime at `amazon.com/mc` (Manage My Prime Membership).
- **Refund Eligibility**:
  - **Full Refund**: If a customer is charged for a new period or auto-renewal but **has not used any Prime benefits** (no Prime orders placed, no Prime Video streamed, no Prime Music played) during that cycle, they receive an automated full refund upon cancellation.
  - **Partial / End-of-Cycle**: If benefits have been used, the membership remains active until the end of the paid billing period and will not renew.

### Digital Add-on Channels & Subscriptions
- Subscriptions to third-party channels via Prime Video (e.g., Paramount+, Max, Starz) and standalone services (Kindle Unlimited, Audible) are billed independently from the main Prime membership.
- Managed under "Your Memberships & Subscriptions" (`amazon.com/yourmembershipsandsubscriptions`).

---

## 3. Communication Guidelines & Tone on Twitter/Social Media
- **Tone**: Courteous, appreciative, transparent, helpful.
- **Value Highlighting**: When addressing questions about Prime pricing or benefits, briefly mention the key benefits included while respecting the customer's decision to cancel or modify.
- **Direct Navigation**: Provide clear direct URLs for membership management so customers can self-cancel without waiting for an agent.

---

## 4. Decision Matrix: Auto-Handle vs. Human Escalation

| Scenario | Recommendation | Reason / Escalation Trigger |
| :--- | :--- | :--- |
| Customer asks how to cancel Prime or turn off auto-renewal | **Auto-Handle** | Standard self-serve navigation; provide Manage Prime link (`amazon.com/mc`). |
| Customer asks why they were charged a subscription fee (e.g., channel add-on) | **Auto-Handle** | Informational; guide customer to "Your Memberships & Subscriptions" to review active channel subscriptions and trial dates. |
| Customer inquires about student discount eligibility or verification process | **Auto-Handle** | Informational; share Prime Student registration and SheerID verification instructions. |
| Unintended auto-renewal fee charged, customer used a minor benefit but requests refund exception | **Escalate to Human** | Billing discretion; requires customer service agent review to evaluate prorated or courtesy refund. |
| Active Prime member is consistently charged shipping fees on Prime-eligible items | **Escalate to Human** | Technical account issue or seller cart error requiring account audit and shipping fee waiver. |
| Customer unable to cancel an external channel subscription or reports unauthorized recurring charge | **Escalate to Human** | Billing dispute requiring backend subscription termination and charge review. |

---

## 5. Canonical Response Templates

### Template: How to Cancel / Manage Prime (Self-Serve)
> "We're sorry to see you consider leaving Prime! You can easily view your membership details, turn off auto-renew, or cancel anytime by visiting 'Manage My Prime Membership' here: [LINK]. If you haven't used any benefits this billing cycle, you'll be eligible for a full refund upon cancellation. ^CS"

### Template: Review Subscriptions (Informational)
> "To view and manage all your active subscriptions and channel add-ons, simply head over to 'Your Memberships & Subscriptions' here: [LINK]. From there, you can view renewal dates, update billing, or cancel any services with a single click! Let us know if you need anything else. ^CS"

### Template: Membership Billing Dispute (Human Escalation)
> "We want to make sure your membership billing is completely accurate and assist with this charge right away. Because we'll need to review your private account details safely, please connect with our team via secure DM here: [DM_LINK]. We're on standby to help! ^CS"
