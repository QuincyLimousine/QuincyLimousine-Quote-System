import streamlit as st
import pandas as pd
from dateutil import parser
from datetime import date, datetime

# --- 1. 初始化設定 ---
if 'lang' not in st.session_state:
    st.session_state.lang = 'CH'
if 'step' not in st.session_state:
    st.session_state.step = 1

def toggle_language():
    st.session_state.lang = 'EN' if st.session_state.lang == 'CH' else 'CH'

# --- 2. 翻譯字典 (新增警告訊息) ---
texts = {
    'CH': {
        'title': 'Quincy Limousine 報價系統',
        'step1': '步驟 1: 客戶聯絡資料',
        'step2': '步驟 2: 接送日期與時間',
        'step3': '步驟 3: 接送行程與車型',
        'step4': '步驟 4: 附加選項與報價',
        'next': '下一步',
        'prev': '返回上一步',
        'fill_all': '⚠️ 請完整填寫所有必填資料後再按下一步。',
        'email_error': '❌ 請輸入有效的 Gmail 地址 (@gmail.com)',
        'time_error': '❌ 時間格式錯誤 (例如 22:30)',
        'name_label': '姓名 (Full Name):',
        'phone_label': '電話號碼 (Phone Number):',
        'email_label': 'Gmail 地址:',
        'date_label': '使用日期:',
        'time_label': '使用時間:',
        'time_placeholder': '例如: 22:30',
        'type_label': '接送類型:',
        'region_label': '地區:',
        'model_label': '車型:',
        'district_label': '區域:',
        'select_op': '請選擇',
        'items_list': ["客戶姓名", "聯絡電話", "Gmail", "日期", "時間", "行程", "安全座椅", "接機服務", "基本車資", "總費用"],
        'total_metric': '預計總費用',
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
        'fill_all': '⚠️ Please fill in all required fields first.',
        'email_error': '❌ Invalid Gmail (@gmail.com)',
        'time_error': '❌ Time format error (e.g. 22:30)',
        'name_label': 'Full Name:',
        'phone_label': 'Phone Number:',
        'email_label': 'Gmail:',
        'date_label': 'Date:',
        'time_label': 'Pick-up Time:',
        'time_placeholder': 'e.g. 22:30',
        'type_label': 'Transfer Type:',
        'region_label': 'Region:',
        'model_label': 'Vehicle Type:',
        'district_label': 'District:',
        'select_op': 'Select',
        'items_list': ["Name", "Phone", "Gmail", "Date", "Time", "Route", "Child Seat", "Meet & Greet", "Base Fare", "Total"],
        'total_metric': 'Total Price',
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

st.progress(st.session_state.step / 4)

# 載入資料
@st.cache_data(ttl=60)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTUroRgmX-R1wQx5ndR5B8plTm7uajQg4OdpdxV8UK21exlpKhmix-wjLKGgG2HrLqWLhHQpQn-Gmfv/pub?gid=0&single=true&output=csv"
    try:
        data = pd.read_csv(url)
        data.columns = data.columns.str.strip()
        return data
    except: return pd.DataFrame()

df = load_data()

# --- 步驟邏輯 ---

# Step 1
if st.session_state.step == 1:
    st.subheader(L['step1'])
    u_name = st.text_input(L['name_label'], value=st.session_state.get('u_name', '')).strip()
    u_phone = st.text_input(L['phone_label'], value=st.session_state.get('u_phone', '')).strip()
    u_email = st.text_input(L['email_label'], value=st.session_state.get('u_email', '')).strip()
    
    if st.button(L['next']):
        if u_name and u_phone and "@gmail.com" in u_email.lower():
            st.session_state.u_name = u_name
            st.session_state.u_phone = u_phone
            st.session_state.u_email = u_email
            st.session_state.step = 2
            st.rerun()
        else:
            st.error(L['fill_all'] if not (u_name and u_phone) else L['email_error'])

# Step 2
elif st.session_state.step == 2:
    st.subheader(L['step2'])
    s_date = st.date_input(L['date_label'], value=st.session_state.get('s_date', date.today()), min_value=date.today())
    p_time = st.text_input(L['time_label'], value=st.session_state.get('p_time', ''), placeholder=L['time_placeholder']).strip()
    
    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        if st.button(L['prev']):
            st.session_state.step = 1
            st.rerun()
    with col_nav2:
        if st.button(L['next']):
            try:
                parser.parse(p_time)
                st.session_state.s_date = s_date
                st.session_state.p_time = p_time
                st.session_state.step = 3
                st.rerun()
            except:
                st.error(L['time_error'] if p_time else L['fill_all'])

# Step 3
elif st.session_state.step == 3:
    st.subheader(L['step3'])
    
    # 這裡加入預設 index 處理
    t_types = [L['select_op']] + sorted(df['Transfer Type'].unique().tolist())
    s_type = st.selectbox(L['type_label'], t_types)
    
    mods = [L['select_op']] + sorted(df['Model'].unique().tolist())
    s_model = st.selectbox(L['model_label'], mods)
    
    regs = [L['select_op']] + sorted(df['Region'].unique().tolist())
    s_region = st.selectbox(L['region_label'], regs)
    
    s_district = L['select_op']
    if s_region != L['select_op']:
        dists = [L['select_op']] + sorted(df[df['Region'] == s_region]['District'].unique().tolist())
        s_district = st.selectbox(L['district_label'], dists)

    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        if st.button(L['prev']):
            st.session_state.step = 2
            st.rerun()
    with col_nav2:
        if st.button(L['next']):
            if all(x != L['select_op'] for x in [s_type, s_model, s_region, s_district]):
                st.session_state.s_type = s_type
                st.session_state.s_model = s_model
                st.session_state.s_region = s_region
                st.session_state.s_district = s_district
                st.session_state.step = 4
                st.rerun()
            else:
                st.error(L['fill_all'])

# Step 4
elif st.session_state.step == 4:
    st.subheader(L['step4'])
    seat_count = st.number_input(L['seat_label'], 0, 4, 0)
    mg_fee = 0
    if "Arrival" in st.session_state.s_type:
        if st.checkbox(L['mg_pickup']): mg_fee = 80

    # 報價表格生成... (代碼邏輯同前，計算總價)
    res = df[(df['Transfer Type'] == st.session_state.s_type) & (df['Model'] == st.session_state.s_model) & (df['District'] == st.session_state.s_district)]
    
    if not res.empty:
        base = int(''.join(filter(str.isdigit, str(res.iloc[0]['Result']))))
        # 夜間費計算
        night = 100 if (parser.parse(st.session_state.p_time).time() >= pd.to_datetime("22:00").time() or parser.parse(st.session_state.p_time).time() <= pd.to_datetime("07:00").time()) else 0
        total = base + (seat_count * 120) + mg_fee + night
        
        st.table(pd.DataFrame({"項目": L['items_list'], "內容": [st.session_state.u_name, st.session_state.u_phone, st.session_state.u_email, str(st.session_state.s_date), st.session_state.p_time, st.session_state.s_district, seat_count, mg_fee, base, total]}))
        st.metric(L['total_metric'], f"HKD ${total}")
    
    if st.button(L['prev']):
        st.session_state.step = 3
        st.rerun()
