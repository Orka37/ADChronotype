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

#---Custom CSS for UI/UX vibes---#\

st.markdown(
    """
    <style>
    /* Gradient background for whole app */
    .stApp {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        color: #E5E7EB;
    }

    /* Center all headers */
    h1, h2, h3, h4, h5, h6 {
        text-align: center;
        color: #E5E7EB;
    }

    /* Style buttons */
    div.stButton > button {
        background-color: #4F46E5;
        color: white;
        border-radius: 12px;
        padding: 0.5em 1.2em;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }

    div.stButton > button:hover {
        background-color: #6366F1;
        cursor: pointer;
    }

    /* Style forms and input containers */
    .stForm {
        background-color: #1E293B;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0px 0px 15px rgba(0,0,0,0.3);
        margin-bottom: 20px;
    }

    /* Style markdown cards */
    .stMarkdown {
        background-color: #1E293B;
        padding: 15px 20px;
        border-radius: 12px;
        margin-bottom: 15px;
        box-shadow: 0px 0px 10px rgba(0,0,0,0.2);
    }

    /* Error messages style */
    .stAlert {
        background-color: #7F1D1D !important;
        color: #FEE2E2 !important;
        border-radius: 12px;
        padding: 10px;
    }

    /* Minor tweaks for sliders, number inputs */
    div.stNumberInput > label, div.stSelectbox > label {
        font-weight: bold;
        color: #E5E7EB;
    }

    /* Sidebar background tweak */
    .css-1lcbmhc.e1fqkh3o3 {
        background-color: #0F172A;
    }
    </style>
    """,
    unsafe_allow_html=True
)

#---Consent---#

@st.dialog("Welcome to ADChronotype!")
def consent():
    st.markdown("<div class='stMarkdown'>*Enter consent info!*</div>", unsafe_allow_html=True)
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
    st.markdown("<div class='stMarkdown'>*Enter information regarding our app!*</div>", unsafe_allow_html=True)
    if st.button("Close"):
        st.rerun()

@st.dialog("Please Check Your Answers!")
def predict_normal():
    st.markdown(
        "<div class='stMarkdown'>The values you submitted are the exact same as the default values. Are you sure, the values accurately represent you?</div>", 
        unsafe_allow_html=True
    )
    if st.button("No, I need to change my answers!"):
        st.rerun()
    if st.button("Yes, predict my likeness score!"):
        st.session_state.predict_normal=True
        go("prediction")

#---Home---#

if st.session_state.page=="home":
    st.markdown("<h1>ADChronotype</h1>", unsafe_allow_html=True)
    st.markdown("<h4>Alzheimer's Risk Prediction Platform</h4>", unsafe_allow_html=True)
    if st.button("Click for info about our project!"):
        project_details()
    if st.session_state.predict:
        st.markdown(
            "<div class='stMarkdown'>**Based on the most recent data you provided, you are [*input value*] likely to get Alzheimer's Disease!**</div>", 
            unsafe_allow_html=True
        )
    if st.button("Input Details"):
        go("input")

#---Input---#

if st.session_state.page=="input":
    st.markdown("<h1>Input Info</h1>", unsafe_allow_html=True)
    with st.form("input"):
        chronotype_options=["Definite Morning","Moderate Morning","Intermediate","Moderate Evening","Definite Evening"]
        st.session_state.chronotype=st.selectbox("**What is your sleep chronotype?**",chronotype_options,index=chronotype_options.index(st.session_state.chronotype))
        st.session_state.sleeptime=st.number_input("How long do you sleep for? (hrs)",min_value=0,max_value=24,step=1,value=int(st.session_state.sleeptime))
        st.session_state.age=st.number_input("How old are you? (years)",min_value=40,max_value=60,step=1,value=int(st.session_state.age))
        st.session_state.bmi=round(st.number_input("What is your BMI?",min_value=6.7,max_value=100.0,step=0.1,value=float(st.session_state.bmi)),2)
        ethnicity_options=["Caucasian", "South Asian", "East Asian", "Hispanic", "African American", "Native American", "Other"]
        st.session_state.ethnicity=st.selectbox("**What is your ethnicity?**",ethnicity_options,index=ethnicity_options.index(st.session_state.ethnicity))
        submit=st.form_submit_button("Save & Predict")
    if submit:
        if st.session_state.chronotype=="Intermediate" and st.session_state.sleeptime==8 and st.session_state.age==40 and st.session_state.bmi==22.00 and st.session_state.ethnicity=="South Asian" and st.session_state.predict_normal==False:
            predict_normal()
        else:
            go("prediction")
    if st.button("**Exit**"):
        go("home")

#---Prediction---#

if st.session_state.page=="prediction":
    st.title("Prediction Value")
    st.markdown(
        "<div class='stMarkdown'>**You are [*input value*] likely to get Alzheimer's Disease!**</div>", 
        unsafe_allow_html=True
    )
    st.session_state.predict=True
    if st.button("Home"):
        go("home")
