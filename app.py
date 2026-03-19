import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import requests
import hashlib
import datetime
import joblib
import numpy as np
import shap
import streamlit.components.v1 as components

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
        "sleeptime": 20,
        "waketime": 7,
        "age": 40,
        "weight": 200,
        "height_ft": 6,
        "height_inch": 0,
        "bmi": 27.1,
        "ethnicity": "South Asian",
        "help": False,
        "predict": 0,
        "predict_normal": False,
        "score_baseline": "N/A",
        "score": "N/A",
        "score_chronotype": "N/A",
        "score_sleeptime": "N/A",
        "score_waketime": "N/A",
        "score_age": "N/A",
        "score_bmi": "N/A",
        "score_ethnicity": "N/A"
    }
    for a, b in defaults.items():
        if a not in st.session_state:
            st.session_state[a] = b

norm_state()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

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
    st.metric(label=label, value=f"{value:.1f}%", delta=delta_text, delta_color=delta_color)

def factor_metric(label, value):
    if value == "N/A":
        st.metric(label=label, value=value, delta=None)
        return
    sign = "+" if value > 0 else ""
    if abs(value) > 15:
        delta_text = "🔥 High Impact"
        delta_color = "inverse"
    elif abs(value) > 10:
        delta_text = "⚠️ Moderate Impact"
        delta_color = "off"
    elif abs(value) > 0:
        delta_text = "✅ Low Impact"
        delta_color = "normal"
    else:
        delta_text = ""
        delta_color = "off"
    st.metric(label=label, value=f"{sign}{value:.1f}%", delta=delta_text, delta_color=delta_color)

def ML():
    model = joblib.load("ml_model.pkl")
    max_score = 67.37

    chronotype = st.session_state.chronotype
    ethnicity  = st.session_state.ethnicity
    age = st.session_state.age
    bmi = st.session_state.bmi
    sleep_numeric = float(st.session_state.sleeptime)
    wake_numeric = float(st.session_state.waketime)
    sleep_hrs = (wake_numeric - sleep_numeric) % 24

    sleep_sin = np.sin(2 * np.pi * sleep_numeric / 24)
    sleep_cos = np.cos(2 * np.pi * sleep_numeric / 24)
    wake_sin = np.sin(2 * np.pi * wake_numeric  / 24)
    wake_cos = np.cos(2 * np.pi * wake_numeric  / 24)

    row = {
        "Age": age, "BMI": bmi,
        "SleepTime_sin": sleep_sin, "SleepTime_cos": sleep_cos,
        "WakeTime_sin":  wake_sin,  "WakeTime_cos":  wake_cos,
        "SleepDuration": sleep_hrs,
        "Chronotype_Definite Evening":  1 if chronotype == "Definite Evening"  else 0,
        "Chronotype_Definite Morning":  1 if chronotype == "Definite Morning"  else 0,
        "Chronotype_Intermediate":      1 if chronotype == "Intermediate"      else 0,
        "Chronotype_Moderate Evening":  1 if chronotype == "Moderate Evening"  else 0,
        "Chronotype_Moderate Morning":  1 if chronotype == "Moderate Morning"  else 0,
        "Ethnicity_African American":   1 if ethnicity  == "African American"  else 0,
        "Ethnicity_Caucasian":          1 if ethnicity  == "Caucasian"         else 0,
        "Ethnicity_East Asian":         1 if ethnicity  == "East Asian"        else 0,
        "Ethnicity_Hispanic":           1 if ethnicity  == "Hispanic"          else 0,
        "Ethnicity_Other":              1 if ethnicity  == "Other"             else 0,
        "Ethnicity_South Asian":        1 if ethnicity  == "South Asian"       else 0,
        "FamilyHistory_No":  1,
        "FamilyHistory_Yes": 0,
    }

    model_cols = ['Age', 'BMI', 'SleepTime_sin', 'SleepTime_cos', 'WakeTime_sin', 'WakeTime_cos', 'SleepDuration', 'Chronotype_Definite Evening', 'Chronotype_Definite Morning', 'Chronotype_Intermediate', 'Chronotype_Moderate Evening', 'Chronotype_Moderate Morning', 'Ethnicity_African American', 'Ethnicity_Caucasian', 'Ethnicity_East Asian', 'Ethnicity_Hispanic', 'Ethnicity_Other', 'Ethnicity_South Asian', 'FamilyHistory_No', 'FamilyHistory_Yes']
    input_df = pd.DataFrame([row])[model_cols]

    prediction = float(model.predict(input_df)[0])
    overall_pct = round(min(max(prediction / max_score * 100, 0), 100), 1)

    explainer = shap.TreeExplainer(model)
    shap_vals = explainer(input_df).values[0]
    feature_map = dict(zip(model_cols, shap_vals))

    def factor_pct(keys):
        return float(round(sum(feature_map.get(k, 0) for k in keys) / max_score * 100, 1))
    
    all_chrono_keys = ["Chronotype_Definite Evening", "Chronotype_Definite Morning", "Chronotype_Intermediate", "Chronotype_Moderate Evening", "Chronotype_Moderate Morning"]
    all_eth_keys = ["Ethnicity_African American", "Ethnicity_Caucasian", "Ethnicity_East Asian", "Ethnicity_Hispanic", "Ethnicity_Other", "Ethnicity_South Asian"]
    
    inactive_shap = sum(feature_map.get(k, 0) for k in all_chrono_keys if k != f"Chronotype_{chronotype}")
    inactive_shap += sum(feature_map.get(k, 0) for k in all_eth_keys if k != f"Ethnicity_{ethnicity}")
    
    family_shap = feature_map.get("FamilyHistory_No", 0) + feature_map.get("FamilyHistory_Yes", 0)
    duration_shap = feature_map.get("SleepDuration", 0)
    baseline = float(round(explainer.expected_value,1))
    st.session_state.score_baseline = float(round((baseline + family_shap + duration_shap + inactive_shap) / max_score * 100, 1))

    st.session_state.score = overall_pct
    st.session_state.score_chronotype = factor_pct([f"Chronotype_{chronotype}"])
    st.session_state.score_sleeptime = factor_pct(["SleepTime_sin", "SleepTime_cos"])
    st.session_state.score_waketime = factor_pct(["WakeTime_sin", "WakeTime_cos"])
    st.session_state.score_age = factor_pct(["Age"])
    st.session_state.score_bmi = factor_pct(["BMI"])
    st.session_state.score_ethnicity = factor_pct([f"Ethnicity_{ethnicity}"])

def save():
    st.session_state.predict=2
    st.toast("Predicting...", icon="🔄")
    payload = [
        str(st.session_state.current_user),
        bool(st.session_state.consent),
        str(st.session_state.chronotype),
        int(st.session_state.sleeptime),
        int(st.session_state.waketime),
        int(st.session_state.age),
        float(st.session_state.bmi),
        str(st.session_state.ethnicity),
        bool(st.session_state.help),
        int(st.session_state.predict),
        bool(st.session_state.predict_normal),
        float(round(st.session_state.score_baseline,1)),
        float(st.session_state.score),
        float(round(st.session_state.score_chronotype,1)),
        float(round(st.session_state.score_sleeptime,1)),
        float(round(st.session_state.score_waketime,1)),
        float(round(st.session_state.score_age,1)),
        float(round(st.session_state.score_bmi,1)),
        float(round(st.session_state.score_ethnicity,1)),
    ]
    requests.post(f"{SHEET_URL}?sheet=Info&action=update", json=payload)
    st.cache_data.clear()
    go("home")
    
st.set_page_config(
    page_title="ADChronotype",
    page_icon="🧠",
    initial_sidebar_state="expanded"
)

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
    footer {visibility: hidden;}
    .viewerBadge_container__1QSob {display: none !important;}
    button[title="View source"] {display: none !important;}
    [data-testid="stHeaderActionElements"] {display: none;}
    a.header-anchor {display: none !important;}
    .block-container {
        padding-top: 3.5rem;
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
        width: 18px;
        height: 18px;
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
            st.toast("Logging In...", icon="🔄")
            users_df = get_data("Users")
            info_df = get_data("Info")
            hashed_input = hash_password(p)
            user_match = users_df[(users_df['Username'].astype(str) == str(u)) & (users_df['Password'].astype(str) == hashed_input)]
            if not user_match.empty:
                st.session_state.logged_in = True
                st.session_state.current_user = u
                user_info = info_df[info_df["Username"].astype(str) == str(u)]
                if not user_info.empty:
                    row = user_info.iloc[0]
                    if not str(row['Chronotype']).strip() == "":
                        consent_val = str(row['Consent']).strip().upper()
                        if consent_val == "TRUE":
                            st.session_state.consent=True
                        else:
                            st.session_state.consent=False
                        st.session_state.chronotype = str(row['Chronotype']).strip()
                        st.session_state.sleeptime = int(row['Sleeptime (hrs)'])
                        st.session_state.waketime = int(row['Waketime (hrs)'])
                        st.session_state.age = int(row['Age'])
                        st.session_state.bmi = float(row['BMI'])
                        st.session_state.ethnicity = str(row['Ethnicity']).strip()
                        help_val = str(row['Help']).strip().upper()
                        if help_val == "TRUE":
                            st.session_state.help=True
                        else:
                            st.session_state.help=False
                        st.session_state.predict = int(row['Predict'])
                        predict_normal_val = str(row['Predict_Normal']).strip().upper()
                        if predict_normal_val == "TRUE":
                            st.session_state.predict_normal=True
                        else:
                            st.session_state.predict_normal=False
                        st.session_state.score_baseline = float(round(row['Baseline Score'],1))
                        st.session_state.score = float(row['Score'])
                        st.session_state.score_chronotype = float(row['Chronotype Score'])
                        st.session_state.score_sleeptime = float(row['Sleeptime Score'])
                        st.session_state.score_waketime = float(row['Waketime Score'])
                        st.session_state.score_age = float(row['Age Score'])
                        st.session_state.score_bmi = float(row['BMI Score'])
                        st.session_state.score_ethnicity = float(row['Ethnicity Score'])
                if not st.session_state.consent:
                    go("consent")
                st.rerun()
            else:
                st.error("Wrong username or password.") 
                st.toast("Log In Failed", icon="❌")
    with tab2:
        new_u = st.text_input("New Username")
        new_p = st.text_input("New Password", type="password")
        if st.button("Register"):
            users_df = get_data("Users")
            if new_u in users_df['Username'].values:
                st.warning("Username taken!")
            elif new_p == "":
                st.warning("Please enter a valid password!")
            elif new_u == "":
                st.warning("Please enter a valid username!")
            else:
                st.toast("Creating Account...", icon="🔄")
                SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzkeLxtNljg5hbFDUOIvUmR54SSJshzvNgV_nsx8xDlwjO4KoneHotJv7thLc47n40SCA/exec"
                hashed_new_p = hash_password(new_p)
                payload = [new_u, hashed_new_p]
                response = requests.post(f"{SCRIPT_URL}?sheet=Users", json=payload)
                if "Success" in response.text:
                    st.toast("Account Created!", icon="✅")
                    st.success("Account created! You can now log in.")
                    st.cache_data.clear()
    st.stop()

#---Consent---#

if st.session_state.page=="consent":
    st.markdown("<h1 style='text-align: center;'>ADChronotype</h1>", unsafe_allow_html=True)
    if not st.session_state.consent:
        st.toast("Logged In!", icon="✅")
        st.info("***You must consent, if you want to use the app!***")
        st.markdown("<h2 style='text-align: center;'>Project Information</h2>", unsafe_allow_html=True)
        st.markdown("This project was built by high schoolers in an attempt to educate the community regarding the effects of lifestyle factors on cognition in relation to Alzheimer's Disease.")
        st.markdown("<h4 style=''><b><i>Procedure:</i></b></h4>", unsafe_allow_html=True)
        st.markdown("- This streamlit-based GitHub-launched website app utilizes an eXtreme Gradient Boosting Regression Machine Learning Model to create an Alzheimer's Disease Cognitive Similarity Score.")
        st.markdown("- The AD Cognitive Similarity Score was derived via statistical analysis that utilizes z-scores, Euclidean distance, and normalization, to compare the results of 101 gathered individuals in 4 self-coded cognitive tests (Mindcrowd Memory & Attention, Stroop Task, Digit Span) to the AD population.")
        st.markdown("<h4 style=''><b><i>Research Question & Hypothesis:</i></b></h4>", unsafe_allow_html=True)
        st.markdown("<h5 style=''><b><i>Research Question: How does a 40-60-year-old’s sleep chronotype affect their likeness score of getting Alzheimer’s disease?</i></b></h4>", unsafe_allow_html=True)
        st.markdown("""The age range of 40–60 is considered the preclinical stage of
                    Alzheimer’s Disease and is the period when the onset of
                    neurological changes begins to occur. The only way to create a
                    full prediction is to analyze the biology of the brain during AD, a
                    process for which no predictable pattern is currently known.
                    Pioneer scientists have been researching prediction methods
                    and have struggled to do so. Hence, the research team derived
                    a likeness score by using statistical analysis to compare an
                    individual’s cognitive profile to that of an average AD patient.
                    """)
        st.markdown("<h5 style=''><b><i>Hypothesis: Evening chronotypes will have the most influence on cognitive likeness for Alzheimer's Disease in middle-aged to older people.</i></b></h4>", unsafe_allow_html=True)
        st.markdown("""Evening chronotypes experience REM maxprop later in their
                    sleep schedules, and due to social constructs, many evening
                    chronotype individuals may be forced to wake up early,
                    increasing the likelihood that they wake before reaching REM
                    maxprop. This can result in reduced memory consolidation,
                    impaired glymphatic clearance, and lower cognitive
                    performance. Long-term failure to reach REM maxprop may
                    lead to a buildup of beta-amyloid plaques and tau tangles, both
                    of which are key markers of Alzheimer’s Disease. The lack of
                    cognitive maintenance also makes the individual's cognitive
                    profile more similar to that of Alzheimer’s Disease patients,
                    resulting in a higher likeness score and a greater influence of
                    chronotype on that score.
                    """)
        with open("rem_chronotype_diagram.html", "r") as f:
            html_content = f.read()
        components.html(html_content, height=800, width=1200, scrolling=True)
        st.markdown("<h2 style=''><b><i>---------------------------------------------------------------</i></b></h2>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center;'><b><i>Consent</i></b></h2>", unsafe_allow_html=True)
        st.markdown("<h5 style=''><b><i>By using this app you fully consent to/acknowledge the following:</i></b></h5>", unsafe_allow_html=True)
        st.markdown("- You are conscience of all terms and conditions mentioned on this page.")
        st.markdown("- The owners of the app will have access to all of your lifestyle factors as well as your score and its breakdown.")
        st.markdown("- Your account is confidential to the extent where only your password is encrypted by SHA-256 encryption.")
        st.markdown("- The owners of the app will NOT utilize any of your data without your full consent.")
        if st.button("I Consent!"):
            st.session_state.consent=True
            go("home")
            st.rerun()
        st.stop()
    else:
        st.markdown("<h2 style='text-align: center;'>Project Information</h2>", unsafe_allow_html=True)
        st.markdown("This project was built by high schoolers in an attempt to educate the community regarding the effects of lifestyle factors on cognition in relation to Alzheimer's Disease.")
        st.markdown("<h4 style=''><b><i>Procedure:</i></b></h4>", unsafe_allow_html=True)
        st.markdown("- This streamlit-based GitHub-launched website app utilizes an eXtreme Gradient Boosting Regression Machine Learning Model to create an Alzheimer's Disease Cognitive Similarity Score.")
        st.markdown("- The AD Cognitive Similarity Score was derived via statistical analysis that utilizes z-scores, Euclidean distance, and normalization, to compare the results of 101 gathered individuals in 4 self-coded cognitive tests (Mindcrowd Memory & Attention, Stroop Task, Digit Span) to the AD population.")
        st.markdown("<h4 style=''><b><i>Research Question & Hypothesis:</i></b></h4>", unsafe_allow_html=True)
        st.markdown("<h5 style=''><b><i>Research Question: How does a 40-60-year-old’s sleep chronotype affect their likeness score of getting Alzheimer’s disease?</i></b></h4>", unsafe_allow_html=True)
        st.markdown("""The age range of 40–60 is considered the preclinical stage of
                    Alzheimer’s Disease and is the period when the onset of
                    neurological changes begins to occur. The only way to create a
                    full prediction is to analyze the biology of the brain during AD, a
                    process for which no predictable pattern is currently known.
                    Pioneer scientists have been researching prediction methods
                    and have struggled to do so. Hence, the research team derived
                    a likeness score by using statistical analysis to compare an
                    individual’s cognitive profile to that of an average AD patient.
                    """)
        st.markdown("<h5 style=''><b><i>Hypothesis: Evening chronotypes will have the most influence on cognitive likeness for Alzheimer's Disease in middle-aged to older people.</i></b></h4>", unsafe_allow_html=True)
        st.markdown("""Evening chronotypes experience REM maxprop later in their
                    sleep schedules, and due to social constructs, many evening
                    chronotype individuals may be forced to wake up early,
                    increasing the likelihood that they wake before reaching REM
                    maxprop. This can result in reduced memory consolidation,
                    impaired glymphatic clearance, and lower cognitive
                    performance. Long-term failure to reach REM maxprop may
                    lead to a buildup of beta-amyloid plaques and tau tangles, both
                    of which are key markers of Alzheimer’s Disease. The lack of
                    cognitive maintenance also makes the individual's cognitive
                    profile more similar to that of Alzheimer’s Disease patients,
                    resulting in a higher likeness score and a greater influence of
                    chronotype on that score.
                    """)
        with open("rem_chronotype_diagram.html", "r") as f:
            html_content = f.read()
        components.html(html_content, height=800, width=1200, scrolling=True)
        st.markdown("<h2 style=''><b><i>---------------------------------------------------------------</i></b></h2>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center;'><b><i>Consent</i></b></h2>", unsafe_allow_html=True)
        st.markdown("<h5 style=''><b><i>By using this app you fully consent to/acknowledge the following:</i></b></h5>", unsafe_allow_html=True)
        st.markdown("- You are conscience of all terms and conditions mentioned on this page.")
        st.markdown("- The owners of the app will have access to all of your lifestyle factors as well as your score and its breakdown.")
        st.markdown("- Your account is confidential to the extent where only your password is encrypted by SHA-256 encryption.")
        st.markdown("- The owners of the app will NOT utilize any of your data without your full consent.")

#---SideBar---#

with st.sidebar:
    st.markdown("## 🧭 Navigation")
    if st.button("🏠 Home", use_container_width=True):
        go("home")
    if st.session_state.predict > 1:
        if st.button("📝 Update My Info", use_container_width=True):
            go("input")
        if st.button("💡 Personalized Tips", use_container_width=True):
            go("tips")
    else:
        if st.button("📝 Input Info", use_container_width=True):
            go("input")
    st.divider()
    if st.button("📜 Consent Info", use_container_width=True):
        go("consent")
    if st.button("🚪Log Out!", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.current_user = None
                st.rerun()

#---Pop-ups---#

@st.dialog("Welcome to AD Chronotype")
def get_started():
    st.write("Hey there!")
    st.write("Thank you so much for choosing to use our app! To get started, select the **'INPUT INFO'** button on the Navigation Panel!")
    if st.button("Okay!"):
        st.session_state.predict=1
        st.rerun()

@st.dialog("Project Details")
def project_details():
    st.markdown("This project was built by high schoolers in an attempt to educate the community regarding the effects of lifestyle factors on cognition in relation to Alzheimer's Disease.")
    st.markdown("<h4 style=''><b><i>Procedure:</i></b></h4>", unsafe_allow_html=True)
    st.markdown("- This streamlit-based GitHub-launched website app utilizes an eXtreme Gradient Boosting Regression Machine Learning Model to create an Alzheimer's Disease Cognitive Similarity Score.")
    st.markdown("- The AD Cognitive Similarity Score was derived via statistical analysis that utilizes z-scores, Euclidean distance, and normalization, to compare the results of 101 gathered individuals in 4 self-coded cognitive tests (Mindcrowd Memory & Attention, Stroop Task, Digit Span) to the AD population.")
    if st.button("Done!"):
        st.rerun()

@st.dialog("Factor Details")
def factor_details():
    st.write("Chronotype → Your body's sleep wake preference.")
    st.write("To find your chronotype: https://qxmd.com/calculate/calculator_829/morningness-eveningness-questionnaire-meq#")
    st.write("To view this again, click on the **'Help!'** button in the bottom right corner!")
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
    if st.session_state.predict==0:
        get_started()
    if st.session_state.predict==2:
        st.toast("Success!", icon="✅")
        st.session_state.predict=3
    col1, col2 = st.columns([0.7, 0.3])
    with col1:
        st.markdown("<h1 style='text-align: right; margin: 0;'>ADChronotype</h1>", unsafe_allow_html=True)
    with col2:
        if st.button("?", key="help_icon_circle", help=None):
            project_details()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Score")
        score_metric("Alzheimer's Likeness Score", st.session_state.score)
        st.warning("""
            Note: THIS IS NOT A CLINICAL DIAGNOSIS!
            
            This is simply a statistical assessment of how similar your cognitive profile is to Alzheimer's Disease Patients.
        """) 
        if st.session_state.predict > 1:
                if st.session_state.bmi < 18.5:
                    label, color = "Underweight", "#3498db"
                elif 18.5 <= st.session_state.bmi < 25:
                    label, color = "Healthy Weight", "#2ecc71"
                elif 25 <= st.session_state.bmi < 30:
                    label, color = "Overweight", "#f1c40f"
                else:
                    label, color = "Obese", "#e67e22"
                st.markdown(f"""
                    <div style="padding:10px; border-radius:10px; background-color: {color}22; border: 1px solid {color}; text-align: center; margin-bottom: 20px;">
                        <span style="color: {color}; font-weight: bold; font-size: 1.1rem;">
                            Current BMI: {st.session_state.bmi} — {label}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
        with col2:
            st.markdown("### Factor Contribution")
            st.caption(f"Baseline: {st.session_state.score_baseline}% — shifted by factors below")
            col3, col4 = st.columns(2)
            with col3:
                factor_metric("Chronotype", st.session_state.score_chronotype)
                factor_metric("Sleeptime", st.session_state.score_sleeptime)
                factor_metric("Waketime", st.session_state.score_waketime)
            with col4:
                factor_metric("Age", st.session_state.score_age)
                factor_metric("BMI", st.session_state.score_bmi)
                factor_metric("Ethnicity", st.session_state.score_ethnicity)

#---Input---#

if st.session_state.page == "input":
    with st.form("input_details"):
        chronotype_options = ["Definite Morning","Moderate Morning","Intermediate","Moderate Evening","Definite Evening"]
        ethnicity_options = ["Caucasian", "South Asian", "East Asian", "Hispanic", "African American", "Other"]
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🌙 Sleep Data")
            chronotype = st.selectbox("**Sleep Chronotype**", chronotype_options, index=chronotype_options.index(st.session_state.chronotype))
            sleeptime = st.slider("**Sleep Time (24hr)**", 0, 23, value=int(st.session_state.sleeptime))
            waketime  = st.slider("**Wake Time (24hr)**",  0, 23, value=int(st.session_state.waketime))
        with col2:
            st.subheader("👤 Personal Info")
            age = st.slider("**Age (years)**", 40, 60, value=int(st.session_state.age))
            col3, col4, col5 = st.columns(3)
            with col3:
                weight = st.number_input("**Weight (lbs)**", min_value=100, max_value=300, step=1, value=int(st.session_state.weight))
                st.session_state.weight = weight
            with col4:
                height_ft = st.number_input("**Height (ft)**", min_value=3, max_value=8, step=1, value=int(st.session_state.height_ft))
                st.session_state.height_ft = height_ft
            with col5:
                height_inch = st.number_input("**Height (inch)**", min_value=0, max_value=11, step=1, value=int(st.session_state.height_inch))
                st.session_state.height_inch = height_inch
            BMI = round((703 * st.session_state.weight) / ((st.session_state.height_ft * 12) + st.session_state.height_inch)**2, 1)
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
        st.session_state.waketime = waketime
        st.session_state.age = age
        st.session_state.bmi = BMI
        st.session_state.ethnicity = ethnicity
        default = (chronotype == "Intermediate" and sleeptime == 20 and waketime == 7 and age == 40 and weight == 200 and height_ft == 6 and height_inch == 0 and ethnicity == "South Asian")
        if default and not st.session_state.predict_normal:
            predict_normal()
        else:
            ML()
            save()
    if help:
        factor_details()

#---Tips---#

if st.session_state.page=="tips":
    st.markdown("<h1 style='text-align: center;'>Tips to Lower Your Score</h1>", unsafe_allow_html=True)
    st.info("WORK IN PROGRESS!")
    if st.button("**Exit**"):
        go("home")












































