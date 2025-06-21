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
- Download the LLM model you wish to use (default: llama3):

```bash
ollama pull llama3


