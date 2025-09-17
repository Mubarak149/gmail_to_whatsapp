# gmail\_to\_whatsapp

**Description**

* Connects to Gmail via the Gmail API
* Fetches emails that match a filter you choose
* Forwards email summaries to your WhatsApp using the WhatsApp Cloud API

> This README is written for a script-kiddie: short, direct commands, and copy-paste ready.

---

## Quick TL;DR (run this now)

```bash
# inside project folder
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# create .env and credentials.json as explained below
python gmail_to_whatsapp.py
```

---

## Files you should have

* `gmail_to_whatsapp.py` — the main script
* `credentials.json` — Google OAuth client (download from Google Cloud)
* `.env` — your secret tokens (not checked into git)
* `requirements.txt` — Python packages
* `token.json` — created automatically after first run (stores Google tokens)

---

## Quick setup (step-by-step, copy-paste)

1. Create and activate a Python venv:

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2 requests python-dotenv
   ```

3. Download `credentials.json` from Google Cloud (OAuth client). Put it in the project folder.

   * Enable **Gmail API** for your Google project.
   * In OAuth client settings add an **Authorized redirect URI**: `http://localhost:8080/`.
   * Add your Gmail address as a **Test user** on the OAuth consent screen while testing.

4. Create a `.env` file in the project folder with these entries (DO NOT paste your real tokens publicly):

   ```env
   WHATSAPP_TOKEN=EAAX...your_meta_token_here...
   PHONE_NUMBER_ID=800172286511386
   TO_PHONE_NUMBER=2347045...
   ```

5. Run the script:

   ```bash
   python gmail_to_whatsapp.py
   ```

   * On first run a browser will open. Log in to your Google account and accept permissions.
   * A `token.json` file will be created automatically (stores tokens + refresh token).

---

## What each part does (short)

* `load_dotenv()` — loads your `.env` file so `os.getenv()` can read tokens.
* `gmail_authenticate()` — handles Google OAuth: reads `token.json`, refreshes token if possible, or opens browser to get new tokens. Uses `prompt='consent'` to force a refresh token.
* `fetch_emails(service, query)` — searches Gmail for messages that match your query (eg `subject:Scholarship is:unread`) and returns subject/from/body.
* `send_whatsapp_message(text)` — calls the WhatsApp Cloud API to forward the text message.

---

## Example `.env` (again: keep it secret)

```
WHATSAPP_TOKEN=EAAXXXXXXXXXXXXXXXXXXXXX
PHONE_NUMBER_ID=800172286511386
TO_PHONE_NUMBER=2347012345678
```

---

## Common problems & fixes (copy-paste friendly)

* **redirect\_uri\_mismatch**

  * Fix: In Google Cloud Console → OAuth client → add `http://localhost:8080/` as an authorized redirect URI. Make sure your script uses `port=8080`.

* **missing refresh\_token**

  * Fix: Delete `token.json`, run the script again. When consenting in the browser, ensure the flow requests `access_type=offline` and `prompt='consent'`. The script already does this if you used the included version.

* **Gmail API not enabled**

  * Fix: Visit: `https://console.developers.google.com/apis/api/gmail.googleapis.com/overview?project=YOUR_PROJECT_ID` and click **Enable**.

* **Invalid/expired WhatsApp access token**

  * Fix: Get a permanent/system user token from Meta Developer dashboard (WhatsApp Cloud API) and replace `WHATSAPP_TOKEN` in `.env`.

* **.env not loaded (WHATSAPP\_TOKEN is None)**

  * Fix: Ensure `.env` is in the same folder as the script and `python-dotenv` is installed. The script calls `load_dotenv()`.

---

## Nice-to-have improvements (if you want to level up)

* Mark emails as **read** after forwarding (use `https://www.googleapis.com/auth/gmail.modify` scope and `service.users().messages().modify(...)`).
* Split long email bodies into smaller chunks before sending to WhatsApp (WhatsApp has message size limits).
* Run script periodically with `cron` or systemd timer to check mail every X minutes.
* Store tokens securely (use an encrypted store or secret manager for production).

Example cron entry (run every 5 minutes):

```
*/5 * * * * /home/you/venv/bin/python /path/to/gmail_to_whatsapp.py >> /path/to/logfile.log 2>&1
```

---

## Minimal `requirements.txt` (copy-paste)

```
google-api-python-client
google-auth
google-auth-oauthlib
google-auth-httplib2
requests
python-dotenv
```

---

## Security tips (DON'T BE STUPID)

* Never push `.env`, `token.json`, or `credentials.json` to public GitHub.
* Use `.gitignore` to skip them.
* Prefer long-lived system tokens for WhatsApp (from Meta) instead of short-lived user tokens.

---

## If things still break

* Copy the last error message and paste it into Google — chances are someone already solved it.
* If stuck, drop an exact error here and I can help troubleshoot.

---

## License

Use it, modify it, break it. No warranty. MIT-style vibes.

---

Happy forwarding. Break stuff. Learn fast. 🚀
