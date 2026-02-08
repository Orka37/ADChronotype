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
        "predict_normal": False,
        "score": "N/A",
        "score_chronotype": "N/A",
        "score_sleeptime": "N/A",
        "score_sleepquality": "N/A",
        "score_age": "N/A",
        "score_bmi": "N/A",
        "score_ethnicity": "N/A"
    }
    for a, b in defaults.items():
        if a not in st.session_state:
            st.session_state[a] = b

norm_state()

def ML():
    st.session_state.score = 67
    st.session_state.score_chronotype = 13
    st.session_state.score_sleeptime = 17
    st.session_state.score_sleepquality = 7
    st.session_state.score_age = 1
    st.session_state.score_bmi = 21
    st.session_state.score_ethnicity = 8

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
        st.session_state.predict_normal,
        st.session_state.score,
        st.session_state.score_chronotype,
        st.session_state.score_sleeptime,
        st.session_state.score_sleepquality,
        st.session_state.score_age,
        st.session_state.score_bmi,
        st.session_state.score_ethnicity
    ]
    requests.post(f"{SCRIPT_URL}?sheet=Info&action=update", json=payload)
    st.cache_data.clear()
    go("home")

def score_metric(label, value):
    if value=="N/A":
        st.metric(label=label,value=value,delta=None)
        return
    if value > 90:
        delta_text = "⚡ EXTREME RISK"
        delta_color = "inverse"
    elif value > 60:
        delta_text = "🔥 High Risk"
        delta_color = "inverse"
    elif value > 30:
        delta_text = "⚠️ Moderate Risk"
        delta_color = "off"
    else:
        delta_text = "✅ Low Risk"
        delta_color = "normal"
    st.metric(label=label, value=f"{value}%", delta=delta_text, delta_color=delta_color)

def factor_metric(label, value):
    if value=="N/A":
        st.metric(label=label,value=value,delta=None)
        return
    if value > 15:
        delta_text = "🔥 High Impact"
        delta_color = "inverse"
    elif value > 10:
        delta_text = "⚠️ Moderate Impact"
        delta_color = "off"
    elif value > 0:
        delta_text = "✅ Low Impact"
        delta_color = "normal"
    st.metric(label=label, value=f"{value}%", delta=delta_text, delta_color=delta_color)
    
st.set_page_config(page_title="ADChronotype")

#---Navigation---#

def go(page):
    st.session_state.page = page
    st.rerun()

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
    
    div[data-testid="InputInstructions"] { display: none !important; }

    div.stButton > button {
        background: linear-gradient(45deg, #6366F1, #A855F7); color: white;
        border: none; padding: 6px 20px !important; min-height: 35px !important;
        border-radius: 8px !important; font-weight: 500 !important;
        transition: all 0.3s ease !important; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3) !important;
    }

    header {visibility: hidden;}
    footer {visibility: hidden;}
    .viewerBadge_container__1QSob {display: none !important;}
    button[title="View source"] {display: none !important;}
    [data-testid="stHeaderActionElements"] {display: none;}
    a.header-anchor {display: none !important;}
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
    }
    
    .title-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        margin-bottom: 20px;
    }
    .info-icon {
        cursor: pointer;
        color: #7c4dff;
        font-size: 1.2rem;
        font-weight: bold;
        border: 1px solid #7c4dff;
        border-radius: 50%;
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: 0.3s;
    }
    .info-icon:hover {
        background-color: #7c4dff;
        color: white;
    }

    [data-testid="stMetricDeltaIcon"], 
    [data-testid="stMetricDelta"] svg {
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
        height: 0 !important;
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
                    st.info("Logging In...")
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
                        predict_normal_val = str(row['Predict_Normal']).strip().upper()
                        if predict_normal_val == "TRUE":
                            st.session_state.predict_normal=True
                        else:
                            st.session_state.predict_normal=False
                        st.session_state.score = int(row['Score'])
                        st.session_state.score_chronotype = int(row['Chronotype Score'])
                        st.session_state.score_sleeptime = int(row['Sleeptime Score'])
                        st.session_state.score_sleepquality = int(row['Sleepquality Score'])
                        st.session_state.score_age = int(row['Age Score'])
                        st.session_state.score_bmi = int(row['BMI Score'])
                        st.session_state.score_ethnicity = int(row['Ethnicity Score'])
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
            elif new_p = "":
                st.warning("Please enter a valid password!")
            else:
                SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzkeLxtNljg5hbFDUOIvUmR54SSJshzvNgV_nsx8xDlwjO4KoneHotJv7thLc47n40SCA/exec"
                payload = [new_u, new_p]
                response = requests.post(f"{SCRIPT_URL}?sheet=Users", json=payload)
                if "Success" in response.text:
                    st.success("Account created! You can now log in.")
                    st.cache_data.clear()
    st.stop()

#---Consent---#

if not st.session_state.consent:
    st.markdown("<h1 style='text-align: center;'>ADChronotype</h1>", unsafe_allow_html=True)
    st.info("***You must consent, if you want to use the app!***")
    st.write("*Enter consent info!*")
    if st.button("I Consent!"):
        st.session_state.consent=True
        st.rerun()
    st.stop()

#---Pop-ups---#

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
        ML()
        save()

#---Home---#

if st.session_state.page=="home":
    col1, col2 = st.columns([0.7, 0.3], gap="small")
    with col1:
        st.markdown("<h1 style='text-align: right; margin: 0;'>ADChronotype</h1>", unsafe_allow_html=True)
    with col2:
        with st.popover("?", help="Click for project details"):
            st.markdown("### Project Details")
            st.write("This app estimates your cognitive similarity to a person w/ AD, based off ur features by using ML.")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Score")
        score_metric("Alzheimer's Likeness Score", st.session_state.score)
        st.warning("""
            Note: THIS IS NOT A CLINICAL DIAGNOSIS!
            
            This is simply a statistical assessment of how similar your cognitive profile is to Alzheimer's Disease Patients.
        """)
        if st.button("Input Details", use_container_width=True):
            go("input")
        if st.button("View Tips to Decrease Score", use_container_width=True):
            go("tips")
        with col2:
            st.markdown("### Factor Contribution")
            col3, col4 = st.columns(2)
            with col3:
                factor_metric("Chronotype", st.session_state.score_chronotype)
                factor_metric("Sleep Duration", st.session_state.score_sleeptime)
                factor_metric("Sleep Quality", st.session_state.score_sleepquality)
            with col4:
                factor_metric("Age", st.session_state.score_age)
                factor_metric("BMI", st.session_state.score_bmi)
                factor_metric("Ethnicity", st.session_state.score_ethnicity)

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
            sleepquality = st.number_input("**Sleep Quality (0-21)**", min_value=0, max_value=21, step=1, value=int(st.session_state.sleepquality))
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
            ML()
            save()
    if help:
        factor_details()
    if st.button("**Exit**"):
        go("home")

#---Tips---#

if st.session_state.page=="tips":
    st.markdown("<h1 style='text-align: center;'>Tips to Lower Your Score</h1>", unsafe_allow_html=True)
    st.info("WORK IN PROGRESS!")
