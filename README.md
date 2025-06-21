# email-ai-query-assistant
App to query your Gmail/Yahoo emails - Which date did I start a new job in 2023?

# 📧 Fully Local Multi-Mailbox AI Email Assistant

This application allows you to connect to your personal email accounts (Yahoo & Gmail), fetch emails locally, index them into a private local database, and query them using an AI-powered assistant — fully private and fully local.
No Email snippets are sent to any 3rd party LLM. 100% Privacy Assured

## 🔐 Key Features

- Multi-Mailbox support: Gmail + Yahoo
- Fully local embeddings (no cloud APIs)
- Fully local Large Language Model (via Ollama)
- Incremental sync: fetches only new emails after initial indexing
- Multi-turn chat interface
- Fully private: no personal data leaves your machine

---

## ⚙️ Pre-requisites

### 1️⃣ Install Python (recommended version 3.10+)

Make sure `python` and `pip` are installed and available.

### 2️⃣ Install Ollama (for local LLM)

- Download and install Ollama: https://ollama.com/download

3️⃣ Install Git (optional, for cloning project)
If not already installed, download from: https://git-scm.com/

🔑 Authentication Requirements
Gmail Setup
Go to: https://console.cloud.google.com/apis/credentials

Create OAuth Consent Screen (External or Internal for personal use)

Create OAuth Client ID (Desktop App)

Download credentials.json

You will upload this file when syncing Gmail via the app interface

Yahoo Setup
Go to: https://login.yahoo.com/account/security

Enable App Passwords

Generate a new App Password for IMAP access

Use this app-password when syncing Yahoo

📦 Installation Steps
1️⃣ Clone Repository (or download code manually)
bash
Copy
Edit
git clone <your-repo-url>
cd <your-repo-directory>

2️⃣ Create Python Virtual Environment
python -m venv venv

Activate:

Windows:
venv\Scripts\activate

Mac/Linux:
source venv/bin/activate


3️⃣ Install Required Packages
Create a file named requirements.txt (already provided) and install:

bash
Copy
Edit
pip install -r requirements.txt


🚀 Running The App
Start the application with:

bash
Copy
Edit
streamlit run your_script_name.py

🧠 Using the App
1️⃣ Choose provider (Yahoo or Gmail)

2️⃣ Enter credentials (Yahoo app password or Gmail credentials.json)

3️⃣ Click Sync to download and index your emails (only new emails will be fetched on re-sync)

4️⃣ Start asking questions — enjoy your private AI email assistant!

5️⃣ Multi-turn chat supported.

- Download the LLM model you wish to use (default: llama3):

```bash
ollama pull llama3


