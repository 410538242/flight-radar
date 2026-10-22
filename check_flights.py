import os
import requests

DUFFEL_TOKEN = os.environ.get("DUFFEL_TOKEN")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# 檢查有沒有成功讀到變數
print(f"DEBUG - DUFFEL_TOKEN 是否存在: {bool(DUFFEL_TOKEN)}")
print(f"DEBUG - TELEGRAM_BOT_TOKEN 是否存在: {bool(TELEGRAM_BOT_TOKEN)}")
print(f"DEBUG - CHAT_ID 是否存在: {bool(CHAT_ID)}")
print(f"DEBUG - 實際收到的 CHAT_ID 值: {CHAT_ID}")

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    res = requests.post(url, json=payload)
    # 印出 Telegram 官方的回應
    print(f"Telegram API 狀態碼: {res.status_code}")
    print(f"Telegram API 完整回應: {res.text}")
    
def check_flights():
    headers = {
        "Authorization": f"Bearer {DUFFEL_TOKEN}",
        "Duffel-Version": "v2",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # 測試航線 (LHR 飛 JFK)
    payload = {
        "data": {
            "slices": [
                {
                    "origin": "LHR",
                    "destination": "JFK",
                    "departure_date": "2026-12-25"
                }
            ],
            "passengers": [{"type": "adult"}],
            "cabin_class": "economy"
        }
    }
    
    try:
        res = requests.post("https://api.duffel.com/air/offer_requests", json=payload, headers=headers)
        
        if res.status_code == 201:
            offer_request_id = res.json()["data"]["id"]
            offers_res = requests.get(f"https://api.duffel.com/air/offers?offer_request_id={offer_request_id}", headers=headers)
            
            if offers_res.status_code == 200:
                offers = offers_res.json()["data"]
                if offers:
                    cheapest = offers[0]
                    price = cheapest["total_amount"]
                    currency = cheapest["total_currency"]
                    airline = cheapest["owner"]["name"]
                    
                    msg = f"🟢 **機票雷達定時回報**\n\n查詢成功！找到由 **{airline}** 執飛的航班。\n💰 最低價格：`{currency} {price}`"
                else:
                    msg = "🟡 **機票雷達定時回報**\n\n本次檢查完成：目前沒有找到符合條件的航班。"
            else:
                msg = f"🔴 **機票雷達回報**\n\n取得報價清單失敗，狀態碼: {offers_res.status_code}"
        else:
            msg = f"🔴 **機票雷達回報**\n\n建立查詢請求失敗，狀態碼: {res.status_code}"
            
        # 每次執行完都發送 Telegram 通知
        send_telegram_message(msg)
        print("已發送本次執行狀態至 Telegram！")
        
    except Exception as e:
        error_msg = f"❌ **機票雷達發生錯誤**\n\n錯誤訊息: `{e}`"
        send_telegram_message(error_msg)
        print(f"發生錯誤: {e}")

if __name__ == "__main__":
    check_flights()