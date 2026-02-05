import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

#---Setup---#

conn = st.connection("gsheets", type=GSheetsConnection)

def get_data(worksheet_name):
    return conn.read(worksheet=worksheet_name, ttl="0")

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
        "predict": False,
        "predict_normal": False
    }
    for a, b in defaults.items():
        if a not in st.session_state:
            st.session_state[a] = b

norm_state()

st.set_page_config(page_title="ADChronotype")

#---Theme---#

st.markdown("""
    <style>
    /* 1. The Global Vibe */
    .stApp {
        background: radial-gradient(circle at top right, #1E293B, #0F172A);
    }

    /* 2. Sleek Title Styling */
    .main-title {
        font-family: 'sans serif';
        color: #F8FAF8;
        text-align: center;
        padding: 15px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 30px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }

    /* 3. Input Box Highlights (The subtle glow you wanted) */
    .stSelectbox div[data-baseweb="select"], 
    .stNumberInput div[data-baseweb="input"] {
        background-color: #0F172A !important;
        border: 1px solid #4F46E5 !important; /* Subtle purple-blue border */
        border-radius: 8px !important;
        transition: all 0.2s ease-in-out;
    }
    
    /* Highlight effect when clicking into a box */
    .stSelectbox div[data-baseweb="select"]:focus-within, 
    .stNumberInput div[data-baseweb="input"]:focus-within {
        border-color: #A855F7 !important;
        box-shadow: 0 0 8px rgba(168, 85, 247, 0.4) !important;
    }

    /* 4. Trimming the "Thick" Buttons */
    div.stButton > button {
        background: linear-gradient(45deg, #6366F1, #A855F7);
        color: white;
        border: none;
        padding: 6px 20px !important; /* Reduced vertical padding */
        height: auto !important;
        min-height: 35px !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        width: auto !important; /* Stops it from being a giant block */
        transition: all 0.3s ease;
    }

    div.stButton > button:hover {
        box-shadow: 0 0 15px rgba(99, 102, 241, 0.5);
        transform: scale(1.02);
    }
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
            match = users_df[(users_df['username'] == u) & (users_df['password'] == p)]
            if not match.empty:
                st.session_state.logged_in = True
                st.session_state.current_user = u
                st.rerun()
            else:
                st.error("Wrong username or password.") 
    with tab2:
        new_u = st.text_input("New Username")
        new_p = st.text_input("New Password", type="password")
        if st.button("Register"):
            users_df = get_data("Users")
            if new_u in users_df['username'].values:
                st.warning("Username taken!")
            else:
                new_user = pd.DataFrame([{"username": new_u, "password": new_p}])
                updated_df = pd.concat([users_df, new_user], ignore_index=True)
                # We use the worksheet name here
                conn.update(worksheet="Users", data=updated_df)
                st.success("Account created! Now Log In.")
                # Important: Clear cache so the next 'get_data' sees the new user
                st.cache_data.clear()
    st.stop()

#---Consent---#

@st.dialog("Welcome to ADChronotype!")
def consent():
    st.write("*Enter consent info!*")
    if st.button("I Consent!"):
        st.session_state.consent=True
        st.rerun()

if not st.session_state.consent:
    st.error("***You must consent, if you want to use the app!***")
    if st.button("Consent!"):
        consent()
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

@st.dialog("Please Check Your Answers!")
def predict_normal():
    st.write("The values you submitted are the exact same as the default values. Are you sure, the values accurately represent you?")
    if st.button("No, I need to change my answers!"):
        st.rerun()
    if st.button("Yes, predict my likeness score!"):
        st.session_state.predict_normal=True
        go("prediction")

#---Home---#

if st.session_state.page=="home":
    st.markdown("<h1 style='text-align: center;'>ADChronotype</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center;'>Alzheimer's Risk Prediction Platform</h4>", unsafe_allow_html=True)
    if st.button("Click for info about our project!"):
        project_details()
    if st.session_state.predict:
        st.write("**Based on the most recent data you provided, you are**", "**[*input value*]**", "**likely to get Alzheimer's Disease!**")
    if st.button("Input Details"):
        go("input")

#---Input---#

if st.session_state.page=="input":
    st.markdown("<h1 style='text-align: center;'>Input Info</h1>", unsafe_allow_html=True)
    #---Input Values---#
    with st.form("input"):
        chronotype_options=["Definite Morning","Moderate Morning","Intermediate","Moderate Evening","Definite Evening"]
        ethnicity_options=["Caucasian", "South Asian", "East Asian", "Hispanic", "African American", "Native American", "Other"]
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.chronotype=st.selectbox("**What is your sleep chronotype?**",chronotype_options,index=chronotype_options.index(st.session_state.chronotype))
            st.session_state.sleeptime=st.number_input("How long do you sleep for? (hrs)",min_value=0,max_value=24,step=1,value=int(st.session_state.sleeptime))
            st.session_state.sleepquality=st.number_input("What is your sleep quality?",min_value=0,max_value=21,step=1,value=int(st.session_state.sleepquality))
        with col2:
            st.session_state.age=st.number_input("How old are you? (years)",min_value=40,max_value=60,step=1,value=int(st.session_state.age))
            st.session_state.bmi=round(st.number_input("What is your BMI?",min_value=6.7,max_value=100.0,step=0.1,value=float(st.session_state.bmi)),2)
            st.session_state.ethnicity=st.selectbox("**What is your ethnicity?**",ethnicity_options,index=ethnicity_options.index(st.session_state.ethnicity))
        submit=st.form_submit_button("Generate Prediction")
    #---Submit Values---#
    if submit:
        if st.session_state.chronotype=="Intermediate" and st.session_state.sleeptime==8 and st.session_state.sleepquality==5 and st.session_state.age==40 and st.session_state.bmi==22.00 and st.session_state.ethnicity=="South Asian" and st.session_state.predict_normal==False:
            predict_normal()
        else:
            go("prediction")
    if st.button("**Exit**"):
        go("home")

#---Prediction---#

if st.session_state.page == "prediction":
    st.title("Results Analysis")
    col1, col2, = st.columns(2)
    with col1:
        st.metric(label="Alzheimer's Likelihood Score", value="64%", delta="Moderate Risk")
    with col2:
        st.info("This prediction is based on your sleep information, age, and BMI.")
    if st.button("Save to Profile"):
        preds_df = get_data("Predictions")
        new_entry = pd.DataFrame([{
            "username": st.session_state.current_user,
            "chronotype": st.session_state.chronotype,
            "sleeptime": st.session_state.sleeptime,
            "sleepquality": st.session_state.sleepquality,
            "age": st.session_state.age,
            "BMI": st.session_state.bmi,
            "ethnicity": st.session_state.ethnicity,
            "score": "67%"
        }])
        updated_preds = pd.concat([preds_df, new_entry], ignore_index=True)
        conn.update(worksheet="Predictions", data=updated_preds)
        st.success("Saved!")
    if st.button("← Return Home"):
        go("home")



