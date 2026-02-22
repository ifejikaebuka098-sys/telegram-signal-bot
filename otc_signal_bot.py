import time
import requests
from datetime import datetime, timedelta
import random  # for demo trend simulation

# -------------------------------
# Telegram setup (direct token & chat ID)
# -------------------------------
BOT_TOKEN = "8369673752:AAGChqjqvpQ3DW89WGgFW8IRTW94BjC2aoo"  # your bot token
CHAT_ID = "6918721957"  # your chat ID

# -------------------------------
# OTC Currency Pairs & flags
# -------------------------------
CURRENCY_PAIRS = {
    "EURUSD-OTC": "🇪🇺/🇺🇸",
    "AUDUSD-OTC": "🇦🇺/🇺🇸",
    "GBPUSD-OTC": "🇬🇧/🇺🇸",
    "USDJPY-OTC": "🇺🇸/🇯🇵",
    "USDCAD-OTC": "🇺🇸/🇨🇦",
    "USDCHF-OTC": "🇺🇸/🇨🇭",
    "NZDUSD-OTC": "🇳🇿/🇺🇸",
    "EURGBP-OTC": "🇪🇺/🇬🇧",
    "EURJPY-OTC": "🇪🇺/🇯🇵",
    "AUDJPY-OTC": "🇦🇺/🇯🇵",
    "GBPJPY-OTC": "🇬🇧/🇯🇵",
    "EURCHF-OTC": "🇪🇺/🇨🇭",
    "AUDCAD-OTC": "🇦🇺/🇨🇦",
    "AUDCHF-OTC": "🇦🇺/🇨🇭",
    "AUDNZD-OTC": "🇦🇺/🇳🇿",
    "CADCHF-OTC": "🇨🇦/🇨🇭",
    "CADJPY-OTC": "🇨🇦/🇯🇵",
    "CHFJPY-OTC": "🇨🇭/🇯🇵",
    "EURAUD-OTC": "🇪🇺/🇦🇺",
    "GBPAUD-OTC": "🇬🇧/🇦🇺"
}

# -------------------------------
# Martingale timings (minutes after main signal)
# -------------------------------
MARTINGALE_STEPS = [2, 4, 6]  # MG1, MG2, MG3 (minutes)

# -------------------------------
# Send Telegram message
# -------------------------------
def send_signal_message(pair, signal_type, entry_time, mg_step=None):
    flag = CURRENCY_PAIRS[pair]
    expiry_time = (entry_time + timedelta(minutes=2)).strftime("%I:%M %p")
    entry_formatted = entry_time.strftime("%I:%M %p")
    
    text = f"🚨TRADE NOW!!\n\n"
    text += f"📉{flag} ({pair})\n"
    text += f"⏰ Expiry: 2 minutes\n"
    text += f"📍 Entry Time: {entry_formatted}\n"
    text += f"📈 Direction: {signal_type} {'🟥' if signal_type=='SELL' else '🟩'}\n\n"
    
    if mg_step is None:
        # Main signal, include martingale levels
        text += "🎯 Martingale Levels:\n"
        for idx, step in enumerate(MARTINGALE_STEPS):
            mg_entry = (entry_time + timedelta(minutes=step)).strftime("%I:%M %p")
            text += f"🔁 Level {idx+1} → {mg_entry}\n"
    
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": text}
    )

# -------------------------------
# Simulate trend detection (demo)
# Replace this with real OTC logic / API later
# -------------------------------
def detect_trend(pair):
    # 30% chance to trigger a signal (demo)
    if random.random() < 0.3:
        return random.choice(["BUY", "SELL"])
    return None

# -------------------------------
# Determine session for adaptation
# -------------------------------
def current_session():
    hour = datetime.now().hour
    if 6 <= hour < 12:
        return "Morning"
    elif 12 <= hour < 18:
        return "Afternoon"
    else:
        return "Night"

# -------------------------------
# Main signal loop
# -------------------------------
def run_signal_bot():
    print("🚀 Signal bot started...")
    while True:
        session = current_session()
        for pair in CURRENCY_PAIRS.keys():
            signal = detect_trend(pair)
            if signal:
                main_entry = datetime.now() + timedelta(minutes=2)  # main entry 2 min ahead
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Detected {signal} on {pair} during {session}")
                
                # Send main signal with Martingale levels
                send_signal_message(pair, signal, main_entry)
                
                # Schedule Martingale signals
                for mg_index, mg_delay in enumerate(MARTINGALE_STEPS):
                    time_to_wait = (main_entry + timedelta(minutes=mg_delay) - datetime.now()).total_seconds()
                    if time_to_wait > 0:
                        time.sleep(time_to_wait)
                    send_signal_message(pair, signal, main_entry + timedelta(minutes=mg_delay), mg_step=mg_index)
        time.sleep(30)  # check every 30 seconds

# -------------------------------
# Run bot
# -------------------------------
if __name__ == "__main__":
    run_signal_bot()
