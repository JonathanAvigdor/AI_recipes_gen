# AI Recipes Generator (ICA Offers) 🍝

Generate **3 smart recipes** and a **compiled shopping list** from your nearest **ICA** store’s weekly offers — right in a Streamlit app. Optionally email the results (local only).

**Live demo:** https://jonathanavigdor-ai-recipes-gen-app-fggsd2.streamlit.app/

---

## ✨ Features
- **Paste ICA offers URL** → scrapes weekly deals
- **AI generation** (OpenAI via LangChain): 3 recipes + combined shopping list
- **Clean UI** with tabs (“Recipes”, “Shopping List”)
- **Email results** (works on local runs via Gmail API OAuth)
- **Cloud-safe scraping**: requests+BeautifulSoup on Streamlit Cloud; Selenium locally

---

## 🧱 Project Structure
```text
AI_recipes_gen/
├─ app.py                         # Streamlit app
├─ requirements.txt
├─ recipe_chain_module/
│  └─ recipe_chain.py             # LangChain chain (OpenAI)
├─ web_scraper/
│  └─ scraper.py                  # Hybrid scraper (requests/bs4 on cloud, Selenium locally)
├─ gmail_api/
│  └─ gmail_sender.py             # Gmail API helper (local-only)
├─ .env                           # Local only (OPENAI_API_KEY) – do not commit
└─ .streamlit/
   └─ secrets.toml                # Cloud secrets (OPENAI_API_KEY, RUN_ENV) – set in Streamlit Cloud UI
```

---

## ⚙️ Setup (Local)

### 1) Create & activate a virtual environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 2) Install dependencies
```bash
pip install -r requirements.txt
```

### 3) Environment variables
Create a **.env** file in the project root:
```env
OPENAI_API_KEY=sk-xxxx...
# optional
# RUN_ENV=local
```

### 4) (Optional) Gmail API for email (local only)
- Enable **Gmail API** in Google Cloud Console
- Create **OAuth Client ID → Desktop App**
- Download **credentials.json** to the project root
- First send will open a browser consent and create **token.json** (gitignored)

### 5) Run the app
```bash
python -m streamlit run app.py
```
- Paste your ICA **offers URL**
- Click **Fetch Offers**
- Click **🤖 Generate Recipes & Shopping List**
- (Local only) Click **📧 Send to my email**

---

## ☁️ Deploy on Streamlit Cloud

1. Push this repo to GitHub (secrets & creds are gitignored).
2. In **Streamlit Cloud** → **New app** → pick repo → **main** → `app.py`.
3. In **App → Settings → Secrets**, add:
   ```toml
   OPENAI_API_KEY = "sk-xxxx..."
   RUN_ENV = "cloud"
   ```
4. Deploy.

**Notes:**
- On Cloud, the app **uses requests+BeautifulSoup** automatically (no Selenium/Chrome).
- Gmail OAuth (credentials/token) **does not work** on Cloud; email button is hidden there.

---

## 🧠 How it Works

- **Scraper** (`web_scraper/scraper.py`)
  - `RUN_ENV=cloud` → **requests + BeautifulSoup** (safe on Streamlit Cloud)
  - Local → try **Selenium** for JS-heavy pages, fallback to requests+bs4
- **AI Chain** (`recipe_chain_module/recipe_chain.py`)
  - LangChain + OpenAI (`ChatOpenAI`) generate:
    - 3 recipes (name, ingredients with units, step-by-step)
    - A **compiled** shopping list (quantities summed across recipes)
- **Email** (`gmail_api/gmail_sender.py`)
  - Gmail API OAuth (local only): `credentials.json` → consent → `token.json` → `send_message`

---

## 🔐 Security

- **Never commit secrets** (`.env`, `.streamlit/secrets.toml`, `credentials.json`, `token.json` are gitignored).
- **Rotate keys** immediately if exposed.
- On Cloud, use only **Secrets** (no local `.env`).

---

## ✅ Requirements (excerpt)

See `requirements.txt` for exact pins:
- streamlit, python-dotenv
- langchain, langchain-openai, openai
- requests, beautifulsoup4, lxml
- selenium, webdriver-manager (local only)
- google-auth, google-auth-oauthlib, google-api-python-client

---

## 🪛 Troubleshooting

- **Selenium/chromedriver error on Cloud**  
  Ensure secrets contain `RUN_ENV="cloud"`.

- **`ModuleNotFoundError: selenium` locally**  
  Install inside your venv:  
  ```bash
  pip install selenium webdriver-manager
  python -m streamlit run app.py
  ```

- **No offers found**  
  Try another ICA offers URL or adjust selectors in `scraper.py`.

- **OpenAI key not picked up**  
  Local: ensure `.env` has `OPENAI_API_KEY` and the correct venv is active.  
  Cloud: set `OPENAI_API_KEY` in **Secrets**.

- **Email fails on Cloud**  
  Expected. Gmail OAuth isn’t supported on Streamlit Cloud. Use local runs to email, or switch to a server-to-server provider later (e.g., SendGrid).

---

## 🗺️ Roadmap

- UI polish (cards for offers & recipes, copy buttons)
- Export to **PDF/Markdown**; “Send to self” via SendGrid (cloud-friendly)
- Store picker (pre-populated ICA stores)
- Caching & cost controls
- Multilingual (SV/EN/HE)

---

## 🤝 Contributing

Issues and PRs are welcome. Keep commits small and focused.

---

## 📝 License

MIT
