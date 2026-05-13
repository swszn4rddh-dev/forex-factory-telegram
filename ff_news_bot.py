import requests
from datetime import datetime
import pytz
import os

# ================== EINSTELLUNGEN ==================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHANNEL = os.getenv("TELEGRAM_CHANNEL")
# ===================================================

url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
berlin_tz = pytz.timezone("Europe/Berlin")
now = datetime.now(berlin_tz)

print(f"🕒 Skript läuft um: {now.strftime('%d.%m.%Y %H:%M')} Berlin-Zeit")
print(f"📅 Sende Kalender für heute: {now.strftime('%d.%m.%Y')}")

try:
    data = requests.get(url, timeout=15).json()
except:
    print("Fehler beim Laden der Daten")
    exit()

messages = []

for event in data:
    # Impact filtern
    impact = event.get("impact", "")
    if impact not in ["High", "Medium", "Holiday"]:
        continue

    # Zeit konvertieren nach Berlin
    try:
        dt_utc = datetime.fromisoformat(event["date"].replace("Z", "+00:00"))
        dt_berlin = dt_utc.astimezone(berlin_tz)
       
        # Nur heutige Events
        if dt_berlin.date() != now.date():
            continue
           
        time_str = dt_berlin.strftime("%H:%M")
    except:
        time_str = "Ganztägig"

    country = event["country"]
    title = event["title"]
   
    # Emojis
    if impact == "High":
        emoji = "🔴"
        impact_text = "High Impact"
    elif impact == "Medium":
        emoji = "🟠"
        impact_text = "Medium Impact"
    else:  # Holiday
        emoji = "🏖️"
        impact_text = "Bank Holiday"
        time_str = "Ganztägig"

    # Nachricht zusammenbauen
    msg = f"{emoji} <b>{country} — {title}</b>\n"
    msg += f"🕒 {time_str} | {impact_text}\n"
   
    if event.get("forecast"):
        msg += f"Prognose: {event['forecast']}\n"
    if event.get("previous"):
        msg += f"Vorher: {event['previous']}\n"
   
    messages.append(msg)

# Nachricht senden
if messages:
    header = f"📅 <b>Wirtschaftskalender Heute • {now.strftime('%d.%m.%Y')}</b>\n\n"
    full_message = header + "\n".join(messages)
   
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHANNEL,
        "text": full_message,
        "parse_mode": "HTML"
    }
   
    response = requests.post(telegram_url, json=payload)
    print(f"✅ Nachricht gesendet! Status: {response.status_code}")
    print(f"{len(messages)} Events für heute gepostet.")
else:
    print("Heute keine relevanten High/Medium Events.")
