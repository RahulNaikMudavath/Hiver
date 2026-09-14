# Amazon Customer Support Knowledge Base: Technical & System Issues

## 1. Scope & Associated Intents
- `technical_or_system_issue`: Website glitches, checkout button errors, app crashes (iOS/Android), page loading failures, digital content playback errors (Prime Video, Amazon Music, Audible), Kindle eBook download/sync issues, Echo/Alexa connectivity issues, and Amazon device hardware errors.

---

## 2. Core Policies & Troubleshooting Playbooks

### First-Line Web & Mobile App Troubleshooting
When a customer reports an issue loading pages, submitting forms, or completing checkout:
1. **Browser**:
   - Clear browser cache, history, and cookies.
   - Try an incognito/private browsing window.
   - Disable active browser extensions (especially ad-blockers or script-blockers).
   - Test on an alternative modern browser (Chrome, Edge, Firefox, Safari).
2. **Mobile App (iOS / Android)**:
   - Force close and re-open the Amazon Shopping app.
   - Check the Apple App Store or Google Play Store for pending app updates.
   - Clear app cache (Android: Settings -> Apps -> Amazon -> Storage -> Clear Cache).
   - Uninstall and reinstall the Amazon Shopping app.

### Digital Content & Streaming Errors (Prime Video / Kindle / Music)
- **Prime Video Error Codes**:
  - `Error 1060` / `5004`: Connection / bandwidth timeout. Advise restarting home router and streaming device.
  - `Error 7031` / `HDMI / HDCP Error`: Digital Rights Management (DRM) handshake failure. Advise checking HDMI cable and HDCP 2.2 port compatibility.
- **Kindle Book Syncing / Download Failures**:
  - Verify device is connected to Wi-Fi.
  - Check "Manage Your Content and Devices" (`amazon.com/mycd`) to ensure purchase succeeded and send book to default device.
  - Sync device manually (Settings -> Sync My Kindle).

### Amazon Devices (Echo, Fire TV, Kindle E-Reader)
- **Standard Power Cycle**: Unplug the device power adapter for 30 seconds, then plug back in.
- **Deregistration / Re-registration**: If an Amazon device is having cloud sync or account credential errors, go to `amazon.com/mycd` -> Devices -> Deregister, then log back in on the device.

---

## 3. Communication Guidelines & Tone on Twitter/Social Media
- **Tone**: Patient, structured, technically clear, approachable.
- **Avoid Overly Complex Jargon**: Provide numbered, simple step-by-step instructions.
- **Identify Environment**: When replying on social media, proactively ask what device/browser the customer is using (e.g., "Are you experiencing this on the mobile app or a web browser?").

---

## 4. Decision Matrix: Auto-Handle vs. Human Escalation

| Scenario | Recommendation | Reason / Escalation Trigger |
| :--- | :--- | :--- |
| Customer unable to click checkout or encountering form validation errors | **Auto-Handle** | First-line troubleshooting; suggest browser cache clear, incognito mode, or app update. |
| Prime Video streaming stuttering or showing standard error code | **Auto-Handle** | Informational; share connection test steps, restart router, check device HDMI/app version. |
| Kindle eBook bought but not showing on device | **Auto-Handle** | Self-serve guidance; direct to `amazon.com/mycd` and advise manual device sync over Wi-Fi. |
| Purchased digital content (movies/books) permanently missing or licensing error blocks playback | **Escalate to Human** | Digital Rights / Order issue; requires digital support specialist to re-push licenses or refund digital order. |
| Device (Echo/Fire TV) won't power on or is stuck in an endless boot loop after update | **Escalate to Human** | Hardware warranty/RMA evaluation; requires hardware diagnostic and possible warranty replacement. |
| Widespread payment gateway 500/503 server error affecting multiple users | **Escalate to Human** | Sev-1 / Sev-2 site incident; must be escalated to On-Call Technical Operations / NOC. |

---

## 5. Canonical Response Templates

### Template: Website / Checkout Glitch (Troubleshooting)
> "I'm sorry for the trouble checking out! To help resolve this, please try clearing your browser's cache and cookies, or try opening an incognito/private window. If you're on the mobile app, checking for the latest app update or restarting the app often does the trick! Let us know if the issue persists. ^CS"

### Template: Prime Video Streaming Error (Troubleshooting)
> "We're sorry for the interruption in your streaming! Please try restarting your device and power-cycling your home Wi-Fi router for 30 seconds. Also check that your Prime Video app is fully updated to the latest version. You can find more streaming tips here: [LINK]! ^CS"

### Template: Device / Digital Failure Escalation (Human Escalation)
> "We want to make sure your device and digital content are working seamlessly. Because we may need to review your registered devices and run live diagnostics, please connect with our specialized technical support team via secure DM here: [DM_LINK]. ^CS"
