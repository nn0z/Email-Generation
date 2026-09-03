# Email-Generation

A lightweight and fast Python tool designed to create and manage temporary email addresses directly, featuring automated inbox monitoring and instant OTP (One-Time Password) code extraction.

---

## 🚀 Key Features

* **Bulk Generation:** Create a single temporary email or multiple inboxes simultaneously based on your requirements.
* **Live Monitoring:** Automatically refreshes and checks inboxes every few seconds to detect new messages without manual intervention.
* **Smart OTP Extractor:** An intelligent regex-based system that scans incoming message contents to locate and highlight verification codes, PINs, or OTPs (4 to 6 digits).
* **Session Management:** Maintains isolated sessions and cookies for each generated email address to ensure stable connectivity.

---

## ⚙️ Prerequisites

The tool requires Python and a couple of external libraries. You can install them using pip:

```
pip install requests beautifulsoup4
```
## ⚠️ Disclaimer

This tool (`Email-Generation.py`) is developed for **educational, testing, and personal automation purposes only**. 

* **No Abuse:** Do not use this tool for spamming, bypassing security controls, engaging in malicious activities, or registering accounts on platforms where temporary or disposable emails are strictly prohibited.
* **Service Availability:** The script interacts directly with third-party disposable email providers (such as Mohmal). Any changes to their website structure, APIs, or terms of service may break the functionality of this tool.
* **Liability:** The author/developer assumes **no responsibility or liability** for any misuse, suspension of accounts, data loss, or any other direct or indirect damage resulting from the use of this software. Use it at your own risk.
