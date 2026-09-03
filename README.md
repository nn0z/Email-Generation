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
