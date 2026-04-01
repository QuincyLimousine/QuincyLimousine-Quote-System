import streamlit as st
import pandas as pd
from dateutil import parser

# 1. 網頁基本設定
st.set_page_config(page_title="Quincy Limo Prices", layout="centered")
st.title("🚗 Quincy Limo 預約報價系統")

# 2. 資料來源 (Google Sheets CSV)
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTUroRgmX-R1wQx5ndR5B8plTm7uajQg4OdpdxV8UK21exlpKhmix-wjLKGgG2HrLqWLhHQpQn-Gmfv/pub?gid=0&single=true&output=csv"

@st.cache_data(ttl=60)
def load_data():
    try:
        data = pd.read_csv(sheet_url)
        data.columns = data.columns.str.strip()
        return data
    except:
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.error("無法載入資料庫，請檢查 Google Sheet 連結。")
else:
    # --- 第一部分：行程篩選 (加入「請選擇」) ---
    st.subheader("第一步：行程詳細資料")
    
    col1, col2 = st.columns(2)
    with col1:
        # 接送類型
        transfer_types = ["請選擇"] + sorted(df['Transfer Type'].dropna().unique().tolist())
        selected_type = st.selectbox("接送類型 (Transfer Type):", transfer_types)

    with col2:
        # 車型
        models = ["請選擇"] + sorted(df['Model'].dropna().unique().tolist())
        selected_model = st.selectbox("選擇車型 (Model):", models)

    col_d1, col_d2 = st.columns(2)
    
    with col_d1:
        # 地區 (Region)
        regions = ["請選擇"] + sorted(df['Region'].dropna().unique().tolist())
        selected_region = st.selectbox("地區 (Region):", regions)

    with col_d2:
        # 區域 (District)
        districts = ["請選擇"] + sorted(df['District'].dropna().unique().tolist())
        selected_district = st.selectbox("分區 (District):", districts)

    st.divider()

    # --- 第二部分：附加選項 ---
    st.subheader("第二步：附加選項與時間")
    col3, col4 = st.columns(2)
    with col3:
        seat_count = st.number_input("兒童安全座椅 ($120/張):", min_value=0, max_value=4, value=0)
        seat_fee = seat_count * 120

    with col4:
        pickup_input = st.text_input("預約上車時間 (Pick-up Time):", placeholder="例如: 23:30")
        
        night_fee = 0
        if pickup_input:
            try:
                parsed_time = parser.parse(pickup_input).time()
                if parsed_time >= pd.to_datetime("22:00").time() or parsed_time <= pd.to_datetime("07:00").time():
                    night_fee = 100
            except:
                st.caption("⚠️ 格式參考: 22:30 或 10:30 PM")

    st.divider()

    # --- 第三部分：結果判斷 ---
    # 只有當所有必選項目都不是「請選擇」時，才執行搜尋與顯示
    if "請選擇" not in [selected_type, selected_model, selected_district, selected_region]:
        
        final_result = df[
            (df['Transfer Type'] == selected_type) & 
            (df['Model'] == selected_model) & 
            (df['District'] == selected_district) & 
            (df['Region'] == selected_region)
        ]

        if not final_result.empty:
            base_price_raw = final_result.iloc[0]['Result']
            try:
                base_price = int(''.join(filter(str.isdigit, str(base_price_raw))))
            except:
                base_price = 0
            
            total_price = base_price + seat_fee + night_fee
            
            st.subheader("📍 預算總覽 (Estimated Quote):")
            
            # 費用明細表格
            detail_df = pd.DataFrame({
                "項目 (Item)": ["基本行程費用", "安全座椅費用", "夜間服務費"],
                "金額 (Amount)": [f"${base_price}", f"${seat_fee}", f"${night_fee}"]
            })
            st.table(detail_df)
            
            st.metric(label="總計金額 (Total Price)", value=f"HKD ${total_price}")
            
            if night_fee > 0:
                st.warning("🌙 已計入夜間服務費 $100 (22:00-07:00)")
        else:
            st.warning("查無此特定組合的價格，請與客服聯絡或調整選擇。")
    else:
        # 使用者尚未完成所有選擇時顯示提示
        st.info("💡 請完成上方所有選項以獲取報價。")
