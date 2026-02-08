import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import requests

#---Setup---#
SHEET_URL = "https://script.google.com/macros/s/AKfycbzkeLxtNljg5hbFDUOIvUmR54SSJshzvNgV_nsx8xDlwjO4KoneHotJv7thLc47n40SCA/exec"
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data(worksheet_name):
    base_url = "https://docs.google.com/spreadsheets/d/153ts_XfAGqCCabIyj_hSMu6H4Vmr5ZWeH2S2lULU__0/gviz/tq?tqx=out:csv&sheet="
    final_url = f"{base_url}{worksheet_name}"
    return pd.read_csv(final_url)

def norm_state():
    defaults = {
        "consent": False,
        "logged_in": False,
        "current_user": None,
        "page": "home",
        "chronotype": "Intermediate",
        "sleeptime": 8,
        "sleepquality": 5,
        "age": 40,
        "bmi": 22.00,
        "ethnicity": "South Asian",
        "help": False,
        "predict": False,
        "predict_normal": False
    }
    for a, b in defaults.items():
        if a not in st.session_state:
            st.session_state[a] = b

norm_state()

def save():
    st.toast("Predicting...", icon="🔄")
    SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzkeLxtNljg5hbFDUOIvUmR54SSJshzvNgV_nsx8xDlwjO4KoneHotJv7thLc47n40SCA/exec"
    payload = [
        st.session_state.current_user,
        st.session_state.consent,
        st.session_state.chronotype,
        st.session_state.sleeptime,
        st.session_state.sleepquality,
        st.session_state.age,
        st.session_state.bmi,
        st.session_state.ethnicity,
        st.session_state.help,
        st.session_state.predict,
        st.session_state.predict_normal
    ]
    requests.post(f"{SCRIPT_URL}?sheet=Info&action=update", json=payload)
    st.cache_data.clear()

st.set_page_config(page_title="ADChronotype")

#---Theme---#
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at top right, #1E293B, #0F172A); }

    .main-title {
        font-family: 'sans serif'; color: #F8FAF8; text-align: center;
        padding: 15px; background: rgba(255, 255, 255, 0.05);
        border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }

    /* Glass Card Container */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        padding: 30px;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
    }

    .stNumberInput button:hover { background-color: rgba(168, 85, 247, 0.4) !important; }
    div[data-testid="InputInstructions"] { display: none !important; }

    div.stButton > button {
        background: linear-gradient(45deg, #6366F1, #A855F7); color: white;
        border: none; padding: 6px 20px !important; min-height: 35px !important;
        border-radius: 8px !important; font-weight: 500 !important;
        transition: all 0.3s ease !important; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3) !important;
    }
    div.stButton > button:hover { transform: scale(1.02); box-shadow: 0 0 15px rgba(99, 102, 241, 0.5) !important; }
    div.stButton > button:active { transform: scale(0.95) !important; }

    /* Fix Metric Alignment for Results */
    [data-testid="stMetricValue"] { font-size: 56px !important; color: #F8FAF8 !important; }
    </style>
    """, unsafe_allow_html=True)

#---Member Portal (The Gate)---#
if not st.session_state.logged_in:
    st.markdown("<div class='main-title'><h1>Member Portal</h1></div>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Log In", "Create Account"])
    # ... (Login/Registration logic remains identical to your code)
    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Log In"):
            users_df = get_data("Users")
            info_df = get_data("Info")
            user_match = users_df[(users_df['Username'].astype(str) == str(u)) & (users_df['Password'].astype(str) == str(p))]
            if not user_match.empty:
                st.session_state.logged_in = True
                st.session_state.current_user = u
                user_info = info_df[info_df["Username"].astype(str) == str(u)]
                if not user_info.empty:
                    row = user_info.iloc[0]
                    # Map your variables correctly
                    st.session_state.chronotype = str(row['Chronotype']).strip()
                    st.session_state.sleeptime = int(row['Sleeptime (hrs)'])
                    st.session_state.sleepquality = int(row['Sleepquality'])
                    st.session_state.age = int(row['Age'])
                    st.session_state.bmi = float(row['BMI'])
                    st.session_state.ethnicity = str(row['Ethnicity']).strip()
                    st.session_state.consent = str(row['Consent']).strip().upper() == "TRUE"
                    st.session_state.help = str(row['Help']).strip().upper() == "TRUE"
                    st.session_state.predict = str(row['Predict']).strip().upper() == "TRUE"
                    st.session_state.predict_normal = str(row['Predict_Normal']).strip().upper() == "TRUE"
                st.rerun()
            else: st.error("Wrong username or password.") 
    with tab2:
        new_u = st.text_input("New Username")
        new_p = st.text_input("New Password", type="password")
        if st.button("Register"):
            users_df = get_data("Users")
            if new_u in users_df['Username'].values: st.warning("Username taken!")
            else:
                payload = [new_u, new_p]
                response = requests.post(f"{SHEET_URL}?sheet=Users", json=payload)
                if "Success" in response.text: st.success("Account created! Log In."); st.cache_data.clear()
    st.stop()

#---Consent (Second Gate)---#
if not st.session_state.consent:
    st.markdown("<h1 style='text-align: center;'>ADChronotype</h1>", unsafe_allow_html=True)
    st.error("***You must consent to use the app!***")
    if st.button("I Consent!"):
        st.session_state.consent=True
        st.rerun()
    st.stop()

#---Navigation Helpers---#
def go(page):
    st.session_state.page = page
    st.rerun()

@st.dialog("Project details!")
def project_details():
    st.write("ADChronotype is an Alzheimer's Risk Prediction Platform using Sleep Chronotypes and biometric data.")
    if st.button("Close"): st.rerun()

#---Home Screen (Improved Layout)---#
if st.session_state.page == "home":
    st.markdown("<h1 style='text-align: center;'>ADChronotype</h1>", unsafe_allow_html=True)
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    h_col1, h_col2 = st.columns([3, 1])
    with h_col1:
        st.markdown("### Alzheimer's Risk Prediction Platform →")
    with h_col2:
        if st.button("More Info", use_container_width=True): project_details()
    
    if st.session_state.predict:
        st.info(f"Welcome back, **{st.session_state.current_user}**. Based on your last session, a prediction is available.")
    else:
        st.write("Welcome! Please input your details to generate a likeness score.")
    
    if st.button("Input Details", use_container_width=True): go("input")
    st.markdown('</div>', unsafe_allow_html=True)

#---Input Screen (Your code remains the same, just inside a container)---#
if st.session_state.page == "input":
    st.markdown("<h1 style='text-align: center;'>Input Info</h1>", unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    with st.form("user_input_form"):
        chronotype_options = ["Definite Morning","Moderate Morning","Intermediate","Moderate Evening","Definite Evening"]
        ethnicity_options = ["Caucasian", "South Asian", "East Asian", "Hispanic", "African American", "Native American", "Other"]
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🌙 Sleep Data")
            chronotype = st.selectbox("**Sleep Chronotype?**", chronotype_options, index=chronotype_options.index(st.session_state.chronotype))
            sleeptime = st.number_input("**Sleep Duration (hrs)**", 0, 24, int(st.session_state.sleeptime))
            sleepquality = st.number_input("**Sleep Quality (0-21)**", 0, 21, int(st.session_state.sleepquality))
        with col2:
            st.subheader("👤 Personal Info")
            age = st.number_input("**Age (40-60)**", 40, 60, int(st.session_state.age))
            BMI = st.number_input("**BMI**", 6.7, 100.0, float(st.session_state.bmi))
            ethnicity = st.selectbox("**Ethnicity**", ethnicity_options, index=ethnicity_options.index(st.session_state.ethnicity))
        
        c1, c2, c3 = st.columns([3,5,1])
        with c1: submit = st.form_submit_button("Generate Prediction")
        with c3: help_btn = st.form_submit_button("Help!")
    st.markdown('</div>', unsafe_allow_html=True)

    if submit:
        st.session_state.chronotype, st.session_state.sleeptime = chronotype, sleeptime
        st.session_state.sleepquality, st.session_state.age = sleepquality, age
        st.session_state.bmi, st.session_state.ethnicity = BMI, ethnicity
        st.session_state.predict = True
        save()
        go("prediction")
    if help_btn: factor_details()
    if st.button("Exit"): go("home")

#---Prediction Screen (Improved Layout)---#
if st.session_state.page == "prediction":
    st.toast("Success!", icon="✅")
    st.markdown("<h1 style='text-align: center;'>Analysis Results</h1>", unsafe_allow_html=True)
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    p_col1, p_col2 = st.columns(2)
    with p_col1:
        # Static example based on your code
        st.metric(label="Likelihood Score", value="67%", delta="Moderate Risk", delta_color="inverse")
        if st.button("← Return Home", use_container_width=True): go("home")
    with p_col2:
        st.markdown("#### About your score")
        st.info("This prediction utilizes your Sleep Chronotype, Sleep Quality, BMI, and age to determine statistical likelihood.")
        st.warning("Note: This is an AI assessment, not a clinical diagnosis.")
    st.markdown('</div>', unsafe_allow_html=True)
