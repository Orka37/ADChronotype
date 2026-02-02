import streamlit as st

#---Setup---#

def norm_state():
    defaults = {
        "consent": False,
        "page": "home",
        "chronotype": "Intermediate",
        "sleeptime": 8,
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
    /* 1. Subtle background gradient */
    .stApp {
        background: radial-gradient(circle at top right, #1E293B, #0F172A);
    }

    /* 2. Style the form to look like a floating card */
    div[data-testid="stForm"] {
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        background-color: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(10px);
        padding: 30px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.3);
    }

    /* 3. Make labels pop */
    .stMarkdown p {
        font-weight: 500;
        letter-spacing: 0.5px;
    }

    /* 4. Style the input boxes */
    .stSelectbox div[data-baseweb="select"], .stNumberInput div[data-baseweb="input"] {
        background-color: #0F172A !important;
        border-radius: 10px !important;
        border: 1px solid #334155 !important;
    }

    /* 5. The "Save & Predict" Button Glow */
    div.stButton > button:first-child {
        background: linear-gradient(45deg, #6366F1, #A855F7);
        color: white;
        border: none;
        padding: 12px 30px;
        border-radius: 12px;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s ease;
    }
    
    div.stButton > button:first-child:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(99, 102, 241, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)

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
        with col2:
            st.session_state.age=st.number_input("How old are you? (years)",min_value=40,max_value=60,step=1,value=int(st.session_state.age))
            st.session_state.bmi=round(st.number_input("What is your BMI?",min_value=6.7,max_value=100.0,step=0.1,value=float(st.session_state.bmi)),2)
        st.session_state.ethnicity=st.selectbox("**What is your ethnicity?**",ethnicity_options,index=ethnicity_options.index(st.session_state.ethnicity))
        submit=st.form_submit_button("Generate Prediction")
    #---Submit Values---#
    if submit:
        if st.session_state.chronotype=="Intermediate" and st.session_state.sleeptime==8 and st.session_state.age==40 and st.session_state.bmi==22.00 and st.session_state.ethnicity=="South Asian" and st.session_state.predict_normal==False:
            predict_normal()
        else:
            go("prediction")
    if st.button("**Exit**"):
        go("home")

#---Prediction---#

if st.session_state.page == "prediction":
    st.title("Results Analysis")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.metric(label="Alzheimer's Likelihood Score", value="64%", delta="Moderate Risk")
        st.info("This prediction is based on your age, BMI, and sleep patterns.")
    if st.button("← Return Home"):
        go("home")

