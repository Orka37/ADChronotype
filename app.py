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

    .stNumberInput button:hover {
        background-color: rgba(168, 85, 247, 0.4) !important;
    }

    div[data-testid="column"]:first-child [data-testid="stMetricValue"] {
        font-size: 80px !important;
        font-weight: bold !important;
        color: #A855F7 !important;
    }
    
    div[data-testid="column"]:not(:first-child) [data-testid="stMetricValue"] {
        font-size: 28px !important; 
        font-weight: 600 !important;
        color: #F8FAF8 !important;
    }
    
    [data-testid="stMetricLabel"] p {
        font-size: 16px !important;
        color: #cbd5e1 !important;
    }
    
    div[data-testid="InputInstructions"] { display: none !important; }

    div.stButton > button {
        background: linear-gradient(45deg, #6366F1, #A855F7); color: white;
        border: none; padding: 6px 20px !important; min-height: 35px !important;
        border-radius: 8px !important; font-weight: 500 !important;
        transition: all 0.3s ease !important; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3) !important;
    }
    div.stButton > button:hover { transform: scale(1.02); box-shadow: 0 0 15px rgba(99, 102, 241, 0.5) !important; }
    div.stButton > button:active { transform: scale(0.95) !important; }

    .stMarkdown h4 a {
        display: none !important;
    }

    .stMarkdown h4 {
        margin-right: 0px !important;
    }

    div[data-testid="stNotification"] {
        background-color: rgba(99, 102, 241, 0.2) !important; color: #F8FAF8 !important;
        border: 1px solid #6366F1 !important; border-radius: 10px !important;
    }
    div[data-testid="stNotification"] svg { fill: #A855F7 !important; }
    </style>
    """, unsafe_allow_html=True)

#---Member Portal---#

if not st.session_state.logged_in:
    st.markdown("<div class='main-title'><h1>Member Portal</h1></div>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Log In", "Create Account"])
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
                    if not str(row['Chronotype']).strip() == "":
                        st.session_state.chronotype = str(row['Chronotype']).strip()
                        st.session_state.sleeptime = int(row['Sleeptime (hrs)'])
                        st.session_state.sleepquality = int(row['Sleepquality'])
                        st.session_state.age = int(row['Age'])
                        st.session_state.bmi = float(row['BMI'])
                        st.session_state.ethnicity = str(row['Ethnicity']).strip()
                        consent_val = str(row['Consent']).strip().upper()
                        if consent_val == "TRUE":
                            st.session_state.consent=True
                        else:
                            st.session_state.consent=False
                        help_val = str(row['Help']).strip().upper()
                        if help_val == "TRUE":
                            st.session_state.help=True
                        else:
                            st.session_state.help=False
                        predict_val = str(row['Predict']).strip().upper()
                        if predict_val == "TRUE":
                            st.session_state.predict=True
                        else:
                            st.session_state.predict=False
                        predict_normal_val = str(row['Predict_Normal']).strip().upper()
                        if predict_normal_val == "TRUE":
                            st.session_state.predict_normal=True
                        else:
                            st.session_state.predict_normal=False
                st.rerun()
            else:
                st.error("Wrong username or password.") 
    with tab2:
        new_u = st.text_input("New Username")
        new_p = st.text_input("New Password", type="password")
        if st.button("Register"):
            users_df = get_data("Users")
            if new_u in users_df['Username'].values:
                st.warning("Username taken!")
            else:
                SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzkeLxtNljg5hbFDUOIvUmR54SSJshzvNgV_nsx8xDlwjO4KoneHotJv7thLc47n40SCA/exec"
                payload = [new_u, new_p]
                response = requests.post(f"{SCRIPT_URL}?sheet=Users", json=payload)
                if "Success" in response.text:
                    st.success("Account created! You can now Log In.")
                    st.cache_data.clear()
    st.stop()

#---Consent---#

if not st.session_state.consent:
    st.markdown("<h1 style='text-align: center;'>ADChronotype</h1>", unsafe_allow_html=True)
    st.error("***You must consent, if you want to use the app!***")
    st.write("*Enter consent info!*")
    if st.button("I Consent!"):
        st.session_state.consent=True
        st.rerun()
    st.stop()

#---Navigation---#

def go(page):
    st.session_state.page = page
    st.rerun()

#---Pop-ups---#

@st.dialog("Project details!")
def project_details():
    st.write("*Enter information regarding our app!*")
    if st.button("Close"):
        st.rerun()

@st.dialog("Factor Details")
def factor_details():
    st.write("Chronotype → Your body's sleep wake preference.")
    st.write("To find your chronotype: https://qxmd.com/calculate/calculator_829/morningness-eveningness-questionnaire-meq#")
    st.write("To find your sleep quality: https://qxmd.com/calculate/calculator_603/pittsburgh-sleep-quality-index-psqi")
    if st.button("Thanks!"):
        st.rerun()

@st.dialog("Please Check Your Answers!")
def predict_normal():
    st.write("The values you submitted are the exact same as the default values. Are you sure, the values accurately represent you?")
    if st.button("No, I need to change my answers!"):
        st.rerun()
    if st.button("Yes, predict my likeness score!"):
        st.session_state.predict_normal=True
        st.session_state.predict=True
        save()
        go("prediction")

#---Home---#

if st.session_state.page=="home":
    st.markdown("<h1 style='text-align: center;'>ADChronotype</h1>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns([0.7,9,4,1])
    with col2:
        st.markdown("<h4 style='text-align: right;'>Alzheimer's Risk Prediction Platform&nbsp;&nbsp;&nbsp; →</h4>", unsafe_allow_html=True)
    with col3:
        if st.button("Click for more info!"):
            project_details()
    if st.session_state.predict:
        st.write("**Based on the most recent data you provided, you are**", "**[*input value*]**", "**likely to get Alzheimer's Disease!**")
    if st.button("Input Details", use_container_width=True):
        go("input")

#---Input---#

if st.session_state.page == "input":
    st.markdown("<h1 style='text-align: center;'>Input Info</h1>", unsafe_allow_html=True)
    with st.form("user_input_form"): # Give the form a clear name
        chronotype_options = ["Definite Morning","Moderate Morning","Intermediate","Moderate Evening","Definite Evening"]
        ethnicity_options = ["Caucasian", "South Asian", "East Asian", "Hispanic", "African American", "Native American", "Other"]
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🌙 Sleep Data")
            chronotype = st.selectbox("**Sleep Chronotype**", chronotype_options, index=chronotype_options.index(st.session_state.chronotype))
            sleeptime = st.number_input("**Sleep Duration (hrs)**", min_value=0, max_value=24, step=1, value=int(st.session_state.sleeptime))
            sleepquality = st.number_input("**Sleep Quality**", min_value=0, max_value=21, step=1, value=int(st.session_state.sleepquality))
        with col2:
            st.subheader("👤 Personal Info")
            age = st.number_input("**Age (40-60 years)**", min_value=40, max_value=60, step=1, value=int(st.session_state.age))
            BMI = round(st.number_input("**BMI**", min_value=6.7, max_value=100.0, step=0.1, value=float(st.session_state.bmi)), 2)
            ethnicity = st.selectbox("**Ethnicity**", ethnicity_options, index=ethnicity_options.index(st.session_state.ethnicity))
        col1, col2, col3 = st.columns([3,5,1])
        with col1:
            submit = st.form_submit_button("Save & Generate Prediction")
        with col3:
            help = st.form_submit_button("Help!")
    if st.session_state.help==False:
        st.session_state.help=True
        factor_details()
    if submit:
        st.session_state.chronotype = chronotype
        st.session_state.sleeptime = sleeptime
        st.session_state.sleepquality = sleepquality
        st.session_state.age = age
        st.session_state.bmi = BMI
        st.session_state.ethnicity = ethnicity
        default = (chronotype == "Intermediate" and sleeptime == 8 and sleepquality == 5 and age == 40 and BMI == 22.00 and ethnicity == "South Asian")
        if default and not st.session_state.predict_normal:
            predict_normal()
        else:
            st.session_state.predict=True
            save()
            go("prediction")
    if help:
        factor_details()
    if st.button("**Exit**"):
        go("home")

#---Prediction---#

if st.session_state.page == "prediction":
    st.toast("Success!", icon="✅")
    st.markdown("<h1 style='text-align: center;'>Analysis Results</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Score")
        st.metric(label="Alzheimer's Likelihood Score", value="67%", delta="Moderate Risk", delta_color="inverse")
        st.warning("Note: This is an statistical assessment of your cogntive similarity to Alzheimer's Disease Patients; NOT a clinical diagnosis.")
        if st.button("← Return Home", use_container_width=True):
            go("home")
    with col2:
        st.markdown("### Score Breakdown")
        st.markdown("#### Below are the contribution values of each factor towards your overall score")
        col3, col4 = st.columns(2)
        with col3:
            st.metric(label="Chronotype's Likelihood Score", value="67%", delta="Moderate Risk", delta_color="inverse")








