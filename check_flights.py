import os
import requests

# 從 GitHub Secrets 讀取敏感金鑰
DUFFEL_TOKEN = os.environ.get("DUFFEL_TOKEN")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

def check_flights():
    headers = {
        "Authorization": f"Bearer {DUFFEL_TOKEN}",
        "Duffel-Version": "v2",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # 預設幫你查一個測試航線 (例如 LHR 飛 JFK，你可以之後自行更改)
    payload = {
        "data": {
            "slices": [
                {
                    "origin": "KHH",
                    "destination": "HKG",
                    "departure_date": "2026-12-25"
                }
            ],
            "passengers": [{"type": "adult"}],
            "cabin_class": "economy"
        }
    }
    
    res = requests.post("https://api.duffel.com/air/offer_requests", json=payload, headers=headers)
    
    if res.status_code == 201:
        offer_request_id = res.json()["data"]["id"]
        offers_res = requests.get(f"https://api.duffel.com/air/offers?offer_request_id={offer_request_id}", headers=headers)
        
        if offers_res.status_code == 200:
            offers = offers_res.json()["data"]
            if offers:
                cheapest = offers[0] # 取出最便宜的第一筆
                price = cheapest["total_amount"]
                currency = cheapest["total_currency"]
                airline = cheapest["owner"]["name"]
                
                msg = f"✈️ **機票雷達自動通知**\n\n找到由 **{airline}** 執飛的航班！\n💰 價格：`{currency} {price}`\n\n快打開 App 看看吧！"
                send_telegram_message(msg)
                print("已成功發送 Telegram 通知！")

if __name__ == "__main__":
    check_flights()