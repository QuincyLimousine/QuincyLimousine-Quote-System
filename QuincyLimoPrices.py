import streamlit as st
import pandas as pd
from dateutil import parser
from datetime import date, datetime

# --- 1. 初始化語言與步驟設定 ---
if 'lang' not in st.session_state:
    st.session_state.lang = 'CH'
if 'step' not in st.session_state:
    st.session_state.step = 1

def toggle_language():
    st.session_state.lang = 'EN' if st.session_state.lang == 'CH' else 'CH'

def next_step():
    st.session_state.step += 1

def prev_step():
    st.session_state.step -= 1

# --- 2. 翻譯字典 ---
texts = {
    'CH': {
        'title': 'Quincy Limousine 報價系統',
        'step1': '步驟 1: 客戶聯絡資料',
        'step2': '步驟 2: 接送日期與時間',
        'step3': '步驟 3: 接送行程與車型',
        'step4': '步驟 4: 附加選項與報價',
        'next': '下一步',
        'prev': '返回上一步',
        'name_label': '姓名 (Full Name):',
        'phone_label': '電話號碼 (Phone Number):',
        'email_label': 'Gmail 地址:',
        'email_error': '⚠️ 請輸入有效的 Gmail 地址 (需包含 @gmail.com)',
        'date_label': '使用日期:',
        'time_label': '使用時間:',
        'time_placeholder': '例如: 22:30',
        'night_warning': '🌙 已計入夜間服務費 $100 (22:00-07:00)',
        'type_label': '接送類型:',
        'region_label': '地區:',
        'model_label': '車型:',
        'district_label': '區域:',
        'select_op': '請選擇',
        'select_reg_first': '請先選擇地區',
        'seat_label': '兒童安全座椅 ($120/張):',
        'mg_label': '機場接機服務 ($80)',
        'mg_pickup': '需要接機服務 (接機大堂 A)',
        'summary_title': '📍 預約彙總與報價',
        'items_list': ["客戶姓名", "聯絡電話", "Gmail", "日期", "時間", "行程", "安全座椅", "接機服務", "基本車資", "總費用"],
        'item': '項目', 'details': '內容',
        'total_metric': '預計總費用',
        'no_price': '查無此組合價格，請重新檢查行程。',
        'seat_unit': '張'
    },
    'EN': {
        'title': 'Quincy Limousine Quote System',
        'step1': 'Step 1: Contact Info',
        'step2': 'Step 2: Date & Time',
        'step3': 'Step 3: Route & Vehicle',
        'step4': 'Step 4: Extras & Quote',
        'next': 'Next',
        'prev': 'Back',
        'name_label': 'Full Name:',
        'phone_label': 'Phone Number:',
        'email_label': 'Gmail:',
        'email_error': '⚠️ Valid Gmail required (@gmail.com)',
        'date_label': 'Date:',
        'time_label': 'Pick-up Time:',
        'time_placeholder': 'e.g. 22:30',
        'night_warning': '🌙 Night surcharge $100 included',
        'type_label': 'Transfer Type:',
        'region_label': 'Region:',
        'model_label': 'Vehicle Type:',
        'district_label': 'District:',
        'select_op': 'Select',
        'select_reg_first': 'Select region first',
        'seat_label': 'Child Seat ($120/each):',
        'mg_label': 'Meet & Greet ($80)',
        'mg_pickup': 'Meet & Greet (Arrival Hall A)',
        'summary_title': '📍 Summary & Quote',
        'items_list': ["Name", "Phone", "Gmail", "Date", "Time", "Route", "Child Seat", "Meet & Greet", "Base Fare", "Total"],
        'item': 'Item', 'details': 'Details',
        'total_metric': 'Total Price',
        'no_price': 'Price not found.',
        'seat_unit': 'Seat(s)'
    }
}

L = texts[st.session_state.lang]

# --- 3. 網頁基本設定 ---
st.set_page_config(page_title="Quincy Limo Prices", layout="centered")

col_t, col_l = st.columns([0.8, 0.2])
with col_t:
    st.title(f"🚗 {L['title']}")
with col_l:
    st.button("🌐 EN/中文", on_click=toggle_language)

# 進度條
st.progress(st.session_state.step / 4)

# --- 4. 資料載入 ---
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTUroRgmX-R1wQx5ndR5B8plTm7uajQg4OdpdxV8UK21exlpKhmix-wjLKGgG2HrLqWLhHQpQn-Gmfv/pub?gid=0&single=true&output=csv"

@st.cache_data(ttl=60)
def load_data():
    try:
        data = pd.read_csv(sheet_url)
        data.columns = data.columns.str.strip()
        return data
    except: return pd.DataFrame()

df = load_data()

# --- 步驟分頁邏輯 ---

# 步驟 1: 聯絡資料
if st.session_state.step == 1:
    st.subheader(L['step1'])
    st.session_state.user_name = st.text_input(L['name_label'], value=st.session_state.get('user_name', '')).strip()
    
    col_c, col_p = st.columns([0.4, 0.6])
    raw_codes = [("🇭🇰 HK +852", "+852"), ("🇨🇳 CN +86", "+86"), ("🇲🇴 MO +853", "+853"), ("🇹🇼 TW +886", "+886"), ("🇬🇧 UK +44", "+44"), ("🇺🇸 US +1", "+1")]
    with col_c:
        code_choice = st.selectbox("Code", [c[0] for c in raw_codes])
        selected_code = next(c[1] for c in raw_codes if c[0] == code_choice)
    with col_p:
        st.session_state.phone_only = st.text_input(L['phone_label'], value=st.session_state.get('phone_only', '')).strip()
    
    st.session_state.user_email = st.text_input(L['email_label'], value=st.session_state.get('user_email', '')).strip()
    
    email_valid = "@gmail.com" in st.session_state.user_email.lower()
    if st.session_state.user_email and not email_valid:
        st.error(L['email_error'])

    if st.session_state.user_name and st.session_state.phone_only and email_valid:
        st.button(L['next'], on_click=next_step)

# 步驟 2: 時間日期
elif st.session_state.step == 2:
    st.subheader(L['step2'])
    st.session_state.sel_date = st.date_input(L['date_label'], value=st.session_state.get('sel_date', date.today()), min_value=date.today())
    st.session_state.pickup_time = st.text_input(L['time_label'], value=st.session_state.get('pickup_time', ''), placeholder=L['time_placeholder']).strip()
    
    if st.session_state.pickup_time:
        try:
            parser.parse(st.session_state.pickup_time)
            col_nav1, col_nav2 = st.columns(2)
            with col_nav1: st.button(L['prev'], on_click=prev_step)
            with col_nav2: st.button(L['next'], on_click=next_step)
        except:
            st.error("Format error (e.g. 22:30)")
    else:
        st.button(L['prev'], on_click=prev_step)

# 步驟 3: 行程選擇
elif st.session_state.step == 3:
    st.subheader(L['step3'])
    
    t_types = [L['select_op']] + sorted(df['Transfer Type'].unique().tolist())
    st.session_state.sel_type = st.selectbox(L['type_label'], t_types, index=0)
    
    mods = [L['select_op']] + sorted(df['Model'].unique().tolist())
    st.session_state.sel_model = st.selectbox(L['model_label'], mods, index=0)
    
    regs = [L['select_op']] + sorted(df['Region'].unique().tolist())
    st.session_state.sel_region = st.selectbox(L['region_label'], regs, index=0)
    
    if st.session_state.sel_region != L['select_op']:
        dists = [L['select_op']] + sorted(df[df['Region'] == st.session_state.sel_region]['District'].unique().tolist())
        st.session_state.sel_district = st.selectbox(L['district_label'], dists)
    else:
        st.session_state.sel_district = L['select_op']

    # 檢查是否都選了
    if all(x != L['select_op'] for x in [st.session_state.sel_type, st.session_state.sel_model, st.session_state.sel_region, st.session_state.sel_district]):
        col_nav1, col_nav2 = st.columns(2)
        with col_nav1: st.button(L['prev'], on_click=prev_step)
        with col_nav2: st.button(L['next'], on_click=next_step)
    else:
        st.button(L['prev'], on_click=prev_step)

# 步驟 4: 附加選項與報價
elif st.session_state.step == 4:
    st.subheader(L['step4'])
    
    col_a, col_b = st.columns(2)
    with col_a:
        seat_count = st.number_input(L['seat_label'], 0, 4, 0)
    
    mg_fee = 0
    if "Arrival" in st.session_state.sel_type:
        with col_b:
            if st.checkbox(L['mg_pickup']): mg_fee = 80

    # 計算報價
    res = df[
        (df['Transfer Type'].str.strip() == st.session_state.sel_type) &
        (df['Model'].str.strip() == st.session_state.sel_model) &
        (df['Region'].str.strip() == st.session_state.sel_region) &
        (df['District'].str.strip() == st.session_state.sel_district)
    ]

    if not res.empty:
        base_price = int(''.join(filter(str.isdigit, str(res.iloc[0]['Result']))))
        # 夜間費
        night_fee = 0
        p_time = parser.parse(st.session_state.pickup_time).time()
        if p_time >= pd.to_datetime("22:00").time() or p_time <= pd.to_datetime("07:00").time():
            night_fee = 100
            st.warning(L['night_warning'])
        
        total = base_price + (seat_count * 120) + mg_fee + night_fee
        
        st.divider()
        st.subheader(L['summary_title'])
        
        route_str = f"{st.session_state.sel_district} ↔ Airport"
        summary_data = [
            st.session_state.user_name, f"{st.session_state.phone_only}", st.session_state.user_email,
            str(st.session_state.sel_date), st.session_state.pickup_time, route_str,
            f"{seat_count} {L['seat_unit']}", f"${mg_fee}", f"${base_price}", f"HKD ${total}"
        ]
        
        st.table(pd.DataFrame({L['item']: L['items_list'], L['details']: summary_data}))
        st.metric(L['total_metric'], f"HKD ${total}")
    else:
        st.error(L['no_price'])
    
    st.button(L['prev'], on_click=prev_step)
