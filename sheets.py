import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pytz
from config import SPREADSHEET_ID, SHEET_NAME, CREDENTIALS_FILE, TIMEZONE

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

HEADERS = ["User ID", "Username", "Entrata", "Uscita", "Durata"]


def get_sheet():
    """Authenticate and return the worksheet."""
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(SPREADSHEET_ID)
    try:
        sheet = spreadsheet.worksheet(SHEET_NAME)
    except gspread.exceptions.WorksheetNotFound:
        sheet = spreadsheet.add_worksheet(title=SHEET_NAME, rows=1000, cols=5)
        sheet.append_row(HEADERS)
    return sheet


def now_rome() -> datetime:
    """Return current datetime in Europe/Rome timezone."""
    tz = pytz.timezone(TIMEZONE)
    return datetime.now(tz)


def format_ts(dt: datetime) -> str:
    """Format datetime to readable string."""
    return dt.strftime("%d/%m/%Y %H:%M:%S")


def format_duration(seconds: int) -> str:
    """Format seconds into Xh Ym Zs string."""
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    parts = []
    if h:
        parts.append(f"{h}h")
    if m:
        parts.append(f"{m}m")
    if s or not parts:
        parts.append(f"{s}s")
    return " ".join(parts)


def record_entrata(user_id: int, username: str) -> dict:
    """
    Record a check-in for the user.
    Returns: {"status": "ok"|"already_open", "timestamp": str}
    """
    sheet = get_sheet()
    all_rows = sheet.get_all_values()
    ts = now_rome()

    # Check for open session (entrata with no uscita)
    for i, row in enumerate(all_rows[1:], start=2):  # skip header
        if len(row) >= 1 and row[0] == str(user_id):
            entrata_filled = len(row) >= 3 and row[2].strip()
            uscita_filled = len(row) >= 4 and row[3].strip()
            if entrata_filled and not uscita_filled:
                return {"status": "already_open", "timestamp": row[2]}

    # Append new row
    sheet.append_row([str(user_id), username or "N/A", format_ts(ts), "", ""])
    return {"status": "ok", "timestamp": format_ts(ts)}


def record_uscita(user_id: int) -> dict:
    """
    Record a check-out for the user.
    Returns: {"status": "ok"|"no_entrata", "entrata": str, "uscita": str, "durata": str}
    """
    sheet = get_sheet()
    all_rows = sheet.get_all_values()
    ts = now_rome()

    # Find last open session for this user
    open_row_index = None
    open_entrata_str = None
    for i, row in enumerate(all_rows[1:], start=2):
        if len(row) >= 1 and row[0] == str(user_id):
            entrata_filled = len(row) >= 3 and row[2].strip()
            uscita_filled = len(row) >= 4 and row[3].strip()
            if entrata_filled and not uscita_filled:
                open_row_index = i
                open_entrata_str = row[2]

    if open_row_index is None:
        return {"status": "no_entrata"}

    # Parse entrata timestamp
    tz = pytz.timezone(TIMEZONE)
    entrata_dt = tz.localize(datetime.strptime(open_entrata_str, "%d/%m/%Y %H:%M:%S"))
    duration_secs = int((ts - entrata_dt).total_seconds())
    durata_str = format_duration(duration_secs)
    uscita_str = format_ts(ts)

    # Update the row: columns D (uscita) and E (durata)
    sheet.update_cell(open_row_index, 4, uscita_str)   # col D
    sheet.update_cell(open_row_index, 5, durata_str)   # col E

    return {
        "status": "ok",
        "entrata": open_entrata_str,
        "uscita": uscita_str,
        "durata": durata_str,
    }
