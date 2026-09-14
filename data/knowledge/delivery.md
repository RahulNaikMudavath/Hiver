# Amazon Customer Support Knowledge Base: Delivery & Shipping

## 1. Scope & Associated Intents
- `delivery_status_delay`: Delayed dispatch, transit delays, inquiries on tracking updates, missed guaranteed delivery dates.
- `delivery_not_received`: Order marked as "Delivered" on tracking but package is not found by customer.
- `delivery_carrier_issue`: Carrier misconduct, courier access issues, safe place discrepancies, damaged packaging during transit, delivery driver complaints.

---

## 2. Core Policies & Timelines

### Tracking & Guaranteed Delivery
- **Tracking Updates**: Tracking updates typically reflect within 24–48 hours of dispatch. Standard domestic carriers include Amazon Logistics (AMZL), UPS, USPS, FedEx, Royal Mail, Hermes/Evri, and local postal carriers.
- **Prime Delivery Guarantee**: Prime eligible items have guaranteed delivery dates. If a guaranteed date is missed, customers are entitled to report it; Amazon historically offers compensation (e.g., promotional credit or 1 month Prime extension where applicable).
- **Delayed in Transit**: If tracking shows no movement for more than 48 hours past the estimated delivery date, the package is considered lost in transit.

### Delivered But Not Received Protocol
- **48-Hour Buffer Rule**: Carriers sometimes scan packages as "Delivered" up to 24–48 hours prior to physical drop-off (due to premature route completion scans).
- **Initial Verification Checklist**:
  1. Check around delivery location (porch, garage, bushes, side door, apartment mail room, leasing office).
  2. Inquire with neighbors or household members.
  3. Verify the shipping address in "Your Orders" to confirm no typo or old address was selected.
  4. Check for carrier "Attempted Delivery" notice slip.
- **Resolution Horizon**: If 48 hours have passed since the "Delivered" scan and the package is still missing, Amazon initiates an immediate replacement or full refund.

### Carrier & Driver Protocols
- **Delivery Instructions / Safe Place**: Customers can set permanent or order-specific delivery instructions (gate codes, leave behind pillar, front desk).
- **Driver Misconduct / Property Damage**: Handled with immediate supervisor escalation. Photos of damage requested, carrier ticket logged internally.

---

## 3. Communication Guidelines & Tone on Twitter/Social Media
- **Tone**: Empathetic, reassuring, action-oriented, professional.
- **Privacy Policy**: **Never** ask for customer tracking numbers, phone numbers, or email addresses publicly on Twitter/X.
- **Link Standard**: Use authenticated customer service links: `https://www.amazon.com/gp/help/customer/contact-us` or verified Direct Message (DM) links with secure sign-in tokens.
- **Sign-off**: Include agent initials (e.g., `^AB`) as customary for `@AmazonHelp`.

---

## 4. Decision Matrix: Auto-Handle vs. Human Escalation

| Scenario | Recommendation | Reason / Escalation Trigger |
| :--- | :--- | :--- |
| Customer asks where package is, within estimated delivery window | **Auto-Handle** | Self-serve tracking query; provide tracking link and explain expected delivery timeframe. |
| Tracking shows delayed by 1 day, still within 48h carrier transit buffer | **Auto-Handle** | Provide standard tracking advice, advise checking tracking link and waiting until the end of the day. |
| Package marked "Delivered" today, customer cannot locate | **Auto-Handle** | Share the 48-hour buffer checklist (check safe place, neighbors, leasing office). |
| Package marked "Delivered" >48 hours ago and still missing | **Escalate to Human** | Financial action required (agent must issue replacement order or process refund). |
| Carrier driver property damage, physical confrontation, or safety hazard | **Escalate to Human** | Safety, liability, and carrier investigation requirement. |
| High-value package ($500+) lost with OTP (One-Time Password) dispute | **Escalate to Human** | Requires logistics investigation and loss prevention authorization. |
| Customer demands compensation/refund for missed Prime guaranteed date | **Escalate to Human** | Discretionary concession/credit application requires agent account access. |

---

## 5. Canonical Response Templates

### Template: Tracking Delay (Self-Serve)
> "I'm sorry to hear your delivery is running behind schedule! You can view the most up-to-date tracking details and estimated arrival time directly in 'Your Orders' here: [LINK]. If your item hasn't arrived within 48 hours of the expected date, please let us know via DM so we can assist further! ^CS"

### Template: Marked Delivered but Missing (Initial Check)
> "We're sorry your package hasn't turned up yet! Occasionally carriers scan packages slightly early. We recommend checking safe places around your property, with neighbors, or your building office. If it hasn't appeared within 48 hours of the delivery scan, reach out to us here: [LINK] and we'll be happy to make this right! ^CS"

### Template: Escalation to Human / DM
> "We understand how frustrating this delay is, especially when you were expecting this on time. Because we'll need to look into your specific order details securely to arrange a replacement or refund, please send us a DM with your details here: [DM_LINK]. We're ready to help! ^CS"
