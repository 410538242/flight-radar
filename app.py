import streamlit as st
import requests

# 填入你的 Duffel Test Access Token
#ACCESS_TOKEN = "duffel_test_lh-dE4-7YbhzkIBCpiGlusHzDrj6ytnlwJxsvv34-4n"

# 從 Streamlit 雲端的安全設定中讀取 Token
ACCESS_TOKEN = st.secrets["DUFFEL_TOKEN"]

st.title("✈️ 我的專屬便宜機票雷達")
st.write("透過 Duffel API 即時搜尋測試環境中的航班報價！")

# 網頁輸入介面
col1, col2 = st.columns(2)
with col1:
    origin = st.text_input("出發地機場代碼 (例如 LHR)", value="LHR")
with col2:
    destination = st.text_input("目的地機場代碼 (例如 JFK)", value="JFK")

departure_date = st.date_input("出發日期")

# 搜尋按鈕
if st.button("開始搜尋機票"):
    if not ACCESS_TOKEN or ACCESS_TOKEN == "你的_duffel_test_token":
        st.error("請先在程式碼中填入你的 Duffel Access Token！")
    else:
        with st.spinner("正在向全球航班系統查詢中..."):
            headers = {
                "Authorization": f"Bearer {ACCESS_TOKEN}",
                "Duffel-Version": "v2",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            # 1. 建立 Offer Request
            request_url = "https://api.duffel.com/air/offer_requests"
            payload = {
                "data": {
                    "slices": [
                        {
                            "origin": origin,
                            "destination": destination,
                            "departure_date": str(departure_date)
                        }
                    ],
                    "passengers": [{"type": "adult"}],
                    "cabin_class": "economy"
                }
            }
            
            res = requests.post(request_url, json=payload, headers=headers)
            
            if res.status_code == 201:
                request_data = res.json()["data"]
                offer_request_id = request_data["id"]
                
                # 2. 取得 Offers 清單
                offers_url = f"https://api.duffel.com/air/offers?offer_request_id={offer_request_id}"
                offers_res = requests.get(offers_url, headers=headers)
                
                if offers_res.status_code == 200:
                    offers_data = offers_res.json()["data"]
                    st.success(f"成功找到 {len(offers_data)} 個航班選項！")
                    
                    # 3. 在網頁上漂亮地列出前幾筆結果
                    for i, offer in enumerate(offers_data[:10]):
                        with st.expander(f"選項 {i+1}: {offer['owner']['name']} - 總價: {offer['total_currency']} {offer['total_amount']}"):
                            st.write(f"**機票 ID**: `{offer['id']}`")
                            st.write(f"**航空公司**: {offer['owner']['name']}")
                            st.write(f"**總價**: {offer['total_currency']} {offer['total_amount']}")
                else:
                    st.error("抓取報價失敗：" + offers_res.text)
            else:
                st.error("建立查詢請求失敗：" + res.text)