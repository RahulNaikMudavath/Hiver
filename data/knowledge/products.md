# Amazon Customer Support Knowledge Base: Product Issues & Information

## 1. Scope & Associated Intents
- `product_issue`: Physical damage upon arrival, defective or malfunctioning merchandise, missing components/accessories, incorrect item received, expired consumables, counterfeit concerns, and product quality complaints.
- `product_service_information`: Questions regarding item specifications, dimensions, compatibility, availability/restock dates, manufacturer warranties, user manuals, and pre-purchase inquiries.

---

## 2. Core Policies & Resolution Workflows

### Damaged, Defective, or Incorrect Items Received
- **Immediate Replacement**: For items fulfilled by Amazon (FBA) or Sold by Amazon (Retail), customers can request a free replacement immediately via the Returns Center (`amazon.com/returns`).
- **30-Day Return Buffer**: When a replacement is created, the customer has 30 days to send back the original damaged or incorrect item using a prepaid return label/QR code. If the original item is not received within 30 days, the customer's payment method is charged for the replacement.
- **Out of Stock Replacements**: If the identical item is sold out or unavailable for replacement, a full refund is processed upon return.
- **Wrong Item Received**: If the customer received an entirely different product, Amazon provides a prepaid return label and dispatches the correct item. If the item received is a hazardous/perishable item, return may be waived.

### Product Safety & Counterfeits
- **Safety Hazards**: Any report of fire, smoke, electric shock, battery swelling, chemical burns, or personal injury caused by a product triggers an immediate critical escalation to the Product Safety and Legal teams. The ASIN is placed under review.
- **Anti-Counterfeiting Policy**: Amazon has a zero-tolerance counterfeit policy. Items reported as counterfeit are referred to the Customer Trust & Partner Support (CTPS) team for authenticity investigation and full refund issuance.

### Warranties & Product Information
- **Within 30 Days**: Fully covered by Amazon's 30-day return and replacement policy.
- **Beyond 30 Days**: For technical consumer electronics, manufacturer warranties apply. Amazon helps customers obtain proof of purchase (VAT invoice) and manufacturer contact information from the order summary page.

---

## 3. Communication Guidelines & Tone on Twitter/Social Media
- **Tone**: Attentive, apologetic, helpful, thorough.
- **Empathy for Damaged Deliveries**: Acknowledge the disappointment of opening a damaged or incorrect package right away.
- **Never Promise Unreleased Specs**: Direct customers to verified product detail pages for technical specifications rather than guessing.

---

## 4. Decision Matrix: Auto-Handle vs. Human Escalation

| Scenario | Recommendation | Reason / Escalation Trigger |
| :--- | :--- | :--- |
| Customer asks if an item is compatible with their device or asks for restock date | **Auto-Handle** | Informational; direct customer to product detail page Q&A section and "Notify Me when available" button. |
| Customer received a slightly damaged non-hazardous item and wants replacement | **Auto-Handle** | Standard self-service workflow; guide to "Your Orders" -> "Return or Replace items". |
| Customer needs a VAT invoice or proof of purchase for manufacturer warranty claim | **Auto-Handle** | Navigation guidance; direct to "Your Orders" -> "Invoice / Order Summary". |
| Product caused property damage, fire, electrical hazard, or personal injury | **Escalate to Human** | Critical safety incident; immediate intake by Executive/Product Safety Escalations team. |
| Customer reports receiving an obvious counterfeit or opened used item sold as new | **Escalate to Human** | Trust & safety violation; requires investigation, seller review, and concession approval. |
| Heavy bulky item (furniture/appliance) delivered damaged and customer cannot transport for return | **Escalate to Human** | Requires carrier special freight pick-up arrangement by a logistics agent. |

---

## 5. Canonical Response Templates

### Template: Request a Replacement (Self-Serve)
> "We're so sorry your item arrived damaged! We want to get a replacement into your hands as quickly as possible. You can request a free replacement with just a few clicks under 'Your Orders' by selecting 'Return or replace items' here: [LINK]. We'll ship out a new one right away! ^CS"

### Template: Product Specifications / Restock (Informational)
> "Thanks for asking! For the most accurate and up-to-date specifications, features, and compatibility details, please check the 'Product Details' and 'Customer Questions & Answers' section on the product page here: [LINK]. If an item is out of stock, clicking 'Email Me' will alert you the moment it returns! ^CS"

### Template: Product Safety / Counterfeit Escalation (Human Escalation)
> "We take product quality and customer safety extremely seriously. We want to investigate this immediately for you. Please connect with our support specialists via secure DM here: [DM_LINK] so we can collect the order details and take urgent action. ^CS"
