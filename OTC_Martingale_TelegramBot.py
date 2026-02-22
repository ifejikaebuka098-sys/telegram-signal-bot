# main.py
import asyncio
import json
import requests
from datetime import datetime, timedelta
import websockets

# -------------------------------
# Telegram setup
# -------------------------------
BOT_TOKEN = "8369673752:AAGChqjqvpQ3DW89WGgFW8IRTW94BjC2aoo"
CHAT_ID = "6918721957"

# -------------------------------
# Deriv WebSocket endpoint
# -------------------------------
DERIV_WS = "wss://ws.binaryws.com/websockets/v3?app_id=1089"

# -------------------------------
# OTC Currency Pairs
# -------------------------------
CURRENCY_PAIRS = [
    "frxEURUSD","frxGBPUSD","frxUSDJPY","frxAUDUSD","frxUSDCAD",
    "frxUSDCHF","frxNZDUSD","frxEURGBP","frxEURJPY","frxGBPJPY",
    "frxAUDJPY","frxEURAUD","frxGBPAUD","frxAUDCAD","frxAUDCHF",
    "frxAUDNZD","frxCADJPY","frxCADCHF","frxCHFJPY","frxEURCHF"
]

# -------------------------------
# Martingale steps (minutes after main entry)
# -------------------------------
MARTINGALE_STEPS = [2, 4, 6]

# -------------------------------
# Send Telegram message
# -------------------------------
def send_signal(pair, direction, entry_time):
    entry_formatted = entry_time.strftime("%I:%M %p")
    text = f"🚨TRADE NOW!!\n\n"
    text += f"📉 {pair}\n"
    text += f"⏰ Expiry: 2 minutes\n"
    text += f"📍 Entry Time: {entry_formatted}\n"
    text += f"📈 Direction: {direction} {'🟥' if direction=='SELL' else '🟩'}\n\n"
    text += "🎯 Martingale Levels:\n"
    for idx, step in enumerate(MARTINGALE_STEPS):
        mg_time = (entry_time + timedelta(minutes=step)).strftime("%I:%M %p")
        text += f"🔁 Level {idx+1} → {mg_time}\n"

    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": text},
            timeout=10
        )
    except requests.exceptions.RequestException as e:
        print(f"Telegram send error: {e}")

# -------------------------------
# Analyze trend based on enough ticks
# -------------------------------
def analyze_trend(candles):
    if len(candles) < 10:
        return None
    last_closes = [c['close'] for c in candles[-5:]]
    if all(last_closes[i] < last_closes[i+1] for i in range(4)):
        return "BUY"
    elif all(last_closes[i] > last_closes[i+1] for i in range(4)):
        return "SELL"
    return None

# -------------------------------
# Monitor a single currency pair with auto-reconnect
# -------------------------------
async def monitor_pair(pair):
    while True:
        try:
            async with websockets.connect(DERIV_WS) as ws:
                subscribe_msg = json.dumps({"ticks": pair})
                await ws.send(subscribe_msg)
                candles = []
                async for message in ws:
                    data = json.loads(message)
                    if 'tick' in data:
                        tick = data['tick']
                        candles.append({"close": tick['quote']})
                        if len(candles) > 50:
                            candles.pop(0)
                        direction = analyze_trend(candles)
                        if direction:
                            main_entry = datetime.now() + timedelta(minutes=2)
                            send_signal(pair, direction, main_entry)
                            for mg in MARTINGALE_STEPS:
                                mg_entry = main_entry + timedelta(minutes=mg)
                                send_signal(pair, direction, mg_entry)
        except Exception as e:
            print(f"[{pair}] WebSocket error: {e}, reconnecting in 5s...")
            await asyncio.sleep(5)

# -------------------------------
# Run all currency pairs concurrently
# -------------------------------
async def main():
    tasks = [monitor_pair(pair) for pair in CURRENCY_PAIRS]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
