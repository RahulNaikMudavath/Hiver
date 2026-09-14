# Amazon Customer Support Knowledge Base: Account Access & Security

## 1. Scope & Associated Intents
- `account_access_security`: Inability to log in, password reset loops, Two-Step Verification (2SV / OTP) issues, locked or suspended accounts, suspected unauthorized access/hacks, unfamiliar orders placed on account, phishing/spoofing reports, and account recovery procedures.

---

## 2. Core Policies & Security Protocols

### Account Authentication & Password Resets
- **Self-Service Password Reset**: Direct customers to `amazon.com/passwordreset`. Verification code sent to primary email or verified mobile number.
- **Two-Step Verification (2SV)**: Provides enhanced security via SMS OTP or Authenticator Apps (Google Authenticator, Microsoft Authenticator).
- **Lost 2SV Device / Recovery**: If the customer no longer has access to their phone/device, they must complete Account Recovery by uploading a government-issued ID via the secure Amazon portal (`amazon.com/a/ayh`). Verification typically takes 24–48 hours.

### Compromised Account & Unauthorized Activity Protocol
- **Signs of Compromise**:
  1. Confirmation emails for orders the customer never placed.
  2. Notification of password, phone number, or email changes.
  3. Gift card balance depleted unexpectedly.
  4. Archived orders appearing in "Archived Orders".
- **Immediate Action Steps**:
  1. Immediately change Amazon password.
  2. Cancel any unauthorized pending orders in "Your Orders" if accessible.
  3. Turn on Two-Step Verification.
  4. Revoke unauthorized app sessions in "Login & Security".
  5. If locked out, report immediately to Amazon Account Security specialists.

### Phishing & Spoofing Defense
- Amazon will **NEVER** ask for passwords, full credit card numbers, or security codes over social media, email, or phone.
- Customers encountering fake customer service numbers or phishing links should report them directly to `stop-spoofing@amazon.com`.

---

## 3. Communication Guidelines & Tone on Twitter/Social Media
- **Tone**: Calm, urgent, vigilant, highly empathetic, reassuring.
- **STRICT COMPLIANCE**: Never solicit or publish customer login email addresses, passwords, phone numbers, or OTP codes on social media channels.
- **Immediate Quarantine**: If a customer posts personal login details publicly on Twitter/X, urgently instruct them to delete the tweet and reset their password immediately.

---

## 4. Decision Matrix: Auto-Handle vs. Human Escalation

| Scenario | Recommendation | Reason / Escalation Trigger |
| :--- | :--- | :--- |
| Customer forgot password and needs reset instructions | **Auto-Handle** | Standard self-service workflow; provide official password assistance link (`amazon.com/passwordreset`). |
| Customer asks how to enable Two-Step Verification (2SV) | **Auto-Handle** | Informational guidance to Account Settings -> "Login & Security". |
| Customer suspects received email is a phishing attempt | **Auto-Handle** | Provide guidance on identifying genuine Amazon emails (`@amazon.com` domain) and forwarding to `stop-spoofing@amazon.com`. |
| Customer reports unauthorized orders placed or suspected account hack | **Escalate to Human** | Immediate account security incident; requires account hold, unauthorized order cancellation, and referral to Account Security Team. |
| Customer locked out of account due to Two-Step Verification device loss | **Escalate to Human** | Sensitive identity verification; customer must be guided into official Two-Step Verification Recovery pipeline. |
| Account suspended or put on hold by Account Verification / Fraud team | **Escalate to Human** | Specialist team action required; frontline bots cannot alter account hold statuses. |

---

## 5. Canonical Response Templates

### Template: Password Reset Guidance (Self-Serve)
> "We're here to help get you back into your account! You can safely reset your password anytime by visiting our Password Assistance page here: [LINK]. Make sure to check your spam/junk folder for the verification code! Let us know if you encounter any errors along the way. ^CS"

### Template: Suspicious Email / Phishing (Informational)
> "Thanks for bringing this to our attention! Amazon will never ask for sensitive account information or passwords via email or social media. You can forward suspicious emails directly to our security team at stop-spoofing@amazon.com and review how to identify authentic emails here: [LINK]. ^CS"

### Template: Unauthorized Activity / Hack Escalation (Human Escalation)
> "We treat account security with the utmost urgency. If you suspect unauthorized access or see unfamiliar activity on your account, please connect with our Account Security specialists immediately via secure DM here: [DM_LINK] so we can secure your account right away. ^CS"
