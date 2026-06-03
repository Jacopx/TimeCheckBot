# Bot Presenze Telegram

Registra entrate e uscite su Google Sheets tramite Telegram.

## Setup

### 1. Token Telegram
1. Parla con [@BotFather](https://t.me/BotFather) su Telegram
2. Invia `/newbot` e segui le istruzioni
3. Copia il token ricevuto

### 2. Google Service Account
1. Vai su [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuovo progetto (o usa uno esistente)
3. Attiva le API: **Google Sheets API** e **Google Drive API**
4. Vai su *IAM & Admin → Service Accounts → Crea account di servizio*
5. Scarica la chiave JSON e salvala come `credentials.json` nella cartella del bot
6. Copia l'email del service account (es. `bot@progetto.iam.gserviceaccount.com`)

### 3. Google Sheet
1. Crea un nuovo Google Sheet
2. Condividilo con l'email del service account (ruolo: Editor)
3. Copia l'ID del foglio dall'URL:
   `https://docs.google.com/spreadsheets/d/**SPREADSHEET_ID**/edit`

### 4. Configurazione
Imposta le variabili d'ambiente oppure modifica `config.py`:

```bash
export TELEGRAM_TOKEN="il_tuo_token"
export SPREADSHEET_ID="id_del_foglio"
```

Oppure direttamente in `config.py`:
```python
TELEGRAM_TOKEN = "il_tuo_token"
SPREADSHEET_ID = "id_del_foglio"
```

### 5. Installazione e avvio
```bash
pip install -r requirements.txt
python bot.py
```

## Struttura del foglio (auto-creata)

| User ID | Username | Entrata | Uscita | Durata |
|---------|----------|---------|--------|--------|
| 123456  | mario    | 03/06/2026 09:00:00 | 03/06/2026 17:30:00 | 8h 30m |

## Comandi disponibili
- `/start` — mostra la tastiera con i pulsanti
- `/entrata` — registra l'entrata
- `/uscita` — registra l'uscita e mostra la durata della sessione
