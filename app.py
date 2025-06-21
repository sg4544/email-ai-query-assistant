import streamlit as st
import imaplib
import email
from email.header import decode_header
import os
import json
import time
from tqdm import tqdm
import chromadb
from sentence_transformers import SentenceTransformer
import ollama
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError

# ----- CONFIG -----
CHROMA_DB_DIR = "chroma_db"
EMBEDDING_MODEL = 'all-MiniLM-L6-v2'
LLM_MODEL = 'llama3'
IMAP_SERVER_YAHOO = "imap.mail.yahoo.com"
IMAP_PORT = 993
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# ----- INITIALIZE CHROMA COLLECTION -----
def get_chroma_collection():
    os.makedirs(CHROMA_DB_DIR, exist_ok=True)
    chroma_client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
    collection = chroma_client.get_or_create_collection("emails")
    return collection

# ----- IMAP CONNECT FOR YAHOO -----
def connect_to_yahoo(username, app_password):
    mail = imaplib.IMAP4_SSL(IMAP_SERVER_YAHOO)
    mail.login(username, app_password)
    return mail

# ----- FETCH EMAILS FROM YAHOO (INCREMENTAL) -----
def fetch_emails_yahoo(mail, collection, account_label):
    mail.select("inbox")
    status, messages = mail.search(None, "ALL")
    email_ids = messages[0].split()
    embedder = SentenceTransformer(EMBEDDING_MODEL)

    for eid in tqdm(email_ids, desc="Fetching Yahoo emails"):
        email_id_str = account_label + ":" + eid.decode()
        if collection.count(ids=[email_id_str]) > 0:
            continue
        status, msg_data = mail.fetch(eid, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding or "utf-8", errors="ignore")
                date = msg["Date"]

                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            charset = part.get_content_charset() or "utf-8"
                            body += part.get_payload(decode=True).decode(charset, errors="ignore")
                else:
                    charset = msg.get_content_charset() or "utf-8"
                    body += msg.get_payload(decode=True).decode(charset, errors="ignore")

                content = f"[Yahoo] Subject: {subject}\nDate: {date}\nBody: {body}"
                embedding = embedder.encode(content).tolist()
                collection.add(documents=[content], ids=[email_id_str], embeddings=[embedding])

# ----- GMAIL AUTH -----
def gmail_authenticate(credentials_json):
    flow = InstalledAppFlow.from_client_secrets_file(credentials_json, SCOPES)
    creds = flow.run_local_server(port=0)
    service = build('gmail', 'v1', credentials=creds)
    return service

# ----- FETCH EMAILS FROM GMAIL (INCREMENTAL) -----
def fetch_emails_gmail(service, collection, account_label):
    embedder = SentenceTransformer(EMBEDDING_MODEL)
    next_page_token = None
    while True:
        response = service.users().messages().list(userId='me', maxResults=500, pageToken=next_page_token).execute()
        messages = response.get('messages', [])
        for message in messages:
            email_id_str = account_label + ":" + message['id']
            if collection.count(ids=[email_id_str]) > 0:
                continue
            try:
                msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
                headers = msg['payload'].get('headers', [])
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
                snippet = msg.get('snippet', '')
                content = f"[Gmail] Subject: {subject}\nDate: {date}\nBody: {snippet}"
                embedding = embedder.encode(content).tolist()
                collection.add(documents=[content], ids=[email_id_str], embeddings=[embedding])
            except HttpError:
                continue
        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

# ----- QUERY FUNCTION -----
def query_emails_with_local_llm(collection, query, chat_history):
    embedder = SentenceTransformer(EMBEDDING_MODEL)
    query_embedding = embedder.encode(query).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=5,
        include=['documents']
    )

    context = "\n\n".join(results['documents'][0])
    prompt = f"""
You are an intelligent assistant answering questions based on personal emails.
Relevant emails:

{context}

Chat History:
{chat_history}

Now answer the current user question:
{query}
"""

    response = ollama.chat(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": "You analyze personal emails."},
            {"role": "user", "content": prompt}
        ]
    )
    answer = response['message']['content']
    return answer

# ----- STREAMLIT APP -----
st.title("📧 Fully Local Multi-Mailbox AI Email Assistant")

collection = get_chroma_collection()

# --- SYNC BUTTON ---
if st.button("🔄 Sync Emails"):
    provider = st.selectbox("Select provider to sync:", ["Yahoo", "Gmail"], key="sync_provider")
    if provider == "Yahoo":
        username = st.text_input("Yahoo Email Address:", key="yahoo_user")
        app_password = st.text_input("Yahoo App Password:", type="password", key="yahoo_pass")
        if st.button("Start Yahoo Sync") and username and app_password:
            with st.spinner("Connecting to Yahoo and syncing emails..."):
                mail = connect_to_yahoo(username, app_password)
                fetch_emails_yahoo(mail, collection, account_label=username)
                mail.logout()
                st.success("Yahoo sync complete.")
    elif provider == "Gmail":
        credentials_file = st.file_uploader("Upload your Gmail credentials.json file", key="gmail_creds")
        gmail_account = st.text_input("Gmail Account Label:", key="gmail_label")
        if st.button("Start Gmail Sync") and credentials_file and gmail_account:
            with open("temp_credentials.json", "wb") as f:
                f.write(credentials_file.getvalue())
            with st.spinner("Authenticating with Gmail and syncing emails..."):
                service = gmail_authenticate("temp_credentials.json")
                fetch_emails_gmail(service, collection, account_label=gmail_account)
                st.success("Gmail sync complete.")

if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

st.write("---")
query = st.text_input("Ask a question about your emails:")
if query:
    chat_log = "\n".join([f"Q: {q}\nA: {a}" for q,a in st.session_state['chat_history']])
    with st.spinner("Thinking..."):
        answer = query_emails_with_local_llm(collection, query, chat_log)
        st.session_state['chat_history'].append((query, answer))
        st.write("### Answer:")
        st.write(answer)

if st.button("🗑 Clear Chat History"):
    st.session_state['chat_history'] = []
    st.success("Chat history cleared.")
