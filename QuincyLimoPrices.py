import streamlit as st
import pandas as pd
import re

# 1. 網頁基本設定
st.set_page_config(page_title="Quincy Limo Prices", layout="centered")
st.title("🚗 Quincy Limo 預約系統")

# 2. 你的 Google Sheets CSV 連結
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTUroRgmX-R1wQx5ndR5B8plTm7uajQg4OdpdxV8UK21exlpKhmix-wjLKGgG2HrLqWLhHQpQn-Gmfv/pub?gid=0&single=true&output=csv"

@st.cache_data(ttl=60)
def load_data():
    data = pd.read_csv(sheet_url)
    data.columns = data.columns.str.strip()
    return data

try:
    df = load_data()
    
    # --- 第一部分：基本篩選 ---
    st.subheader("第一步：選擇路線與車型")
    col1, col2 = st.columns(2)
    with col1:
        models = sorted(df['Model'].dropna().unique())
        selected_model = st.selectbox("選擇車型 (Model):", models)
    with col2:
        available_regions = sorted(df[df['Model'] == selected_model]['Region'].dropna().unique())
        selected_region = st.selectbox("選擇地區 (Region):", available_regions)

    st.divider()

    # --- 第二部分：附加選項 ---
    st.subheader("第二步：附加選項與時間")
    col3, col4 = st.columns(2)

    with col3:
        seat_count = st.number_input("兒童安全座椅 (Child Seats):", min_value=0, max_value=4, value=0)
        seat_total = seat_count * 120

    with col4:
        # 3. 手動輸入時間 (不限制選盤，改用文字框)
        pickup_time = st.text_input("預約上車時間 (Pick-up Time):", placeholder="例如: 08:30 或 2:00 PM")
        
        # 簡單的防錯提示 (如果使用者輸入了非時間內容)
        if pickup_time and not re.search(r'\d', pickup_time):
            st.warning("⚠️ 請輸入正確的時間格式。")

    st.divider()

    # --- 第三部分：結果顯示 ---
    final_result = df[(df['Model'] == selected_model) & (df['Region'] == selected_region)]

    if not final_result.empty:
        base_price = final_result.iloc[0]['Result']
        
        st.subheader("📍 預約明細 (Summary):")
        
        # 顯示清單
        st.write(f"🔹 **車型**: {selected_model}")
        st.write(f"🔹 **地區**: {selected_region}")
        st.write(f"🔹 **上車時間**: {pickup_time if pickup_time else '未輸入'}")
        st.write(f"🔹 **安全座椅**: {seat_count} 張 (共 {seat_total} 元)")
        
        st.success(f"💰 **基本報價：{base_price}**")
        
        if seat_count > 0:
            st.info(f"備註：總費用為基本報價加安全座椅費用 {seat_total} 元。")
    else:
        st.warning("查無此組合資料。")

except Exception as e:
    st.error("資料載入失敗。")
