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
        "answer": 0,
        "predict": False,
        "predict_normal": False
    }
    for a, b in defaults.items():
        if a not in st.session_state:
            st.session_state[a] = b

norm_state()

st.set_page_config(page_title="ADChronotype")

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
        chronotype=st.selectbox("**What is your sleep chronotype?**",chronotype_options,index=chronotype_options.index(st.session_state.chronotype))
        sleeptime=st.number_input("How long do you sleep for? (hrs)",min_value=0,max_value=24,step=1,value=int(st.session_state.sleeptime))
        age=st.number_input("How old are you? (years)",min_value=40,max_value=60,step=1,value=int(st.session_state.age))
        bmi=st.number_input("What is your BMI?",min_value=6.7,max_value=100.0,step=0.1,value=float(st.session_state.bmi))
        ethnicity_options=["Caucasian", "South Asian", "East Asian", "Hispanic", "African American", "Native American", "Other"]
        ethnicity=st.selectbox("**What is your ethnicity?**",ethnicity_options,index=ethnicity_options.index(st.session_state.ethnicity))
        submit=st.form_submit_button("Save Changes")
    #---Submit Values---#
    if submit:
        st.session_state.chronotype=chronotype
        st.session_state.sleeptime=sleeptime
        st.session_state.age=age
        st.session_state.bmi=round(bmi,2)
        st.session_state.ethnicity=ethnicity
        #---Verify Everything Answered---#
        if st.session_state.answer==0:
            st.markdown("<span style='color: green; font-weight: bold;'>Answers Successfully Saved!</span>", unsafe_allow_html=True)
            st.session_state.answer=1
        elif st.session_state.answer==1:
            st.markdown("<span style='color: blue; font-weight: bold;'>Answers Successfully Saved!</span>", unsafe_allow_html=True)
            st.session_state.answer=2
        elif st.session_state.answer==2:
            st.markdown("<span style='color: red; font-weight: bold;'>Answers Successfully Saved!</span>", unsafe_allow_html=True)
            st.session_state.answer=0
    col1, col2, col3=st.columns([1,5,1])
    with col1:
        if st.button("**Exit**"):
            go("home")
    with col3:
        if st.button("**Predict**"):
            if st.session_state.chronotype=="Intermediate" and st.session_state.sleeptime==8 and st.session_state.age==40 and st.session_state.bmi==22.00 and st.session_state.ethnicity=="South Asian" and st.session_state.predict_normal==False:
                predict_normal()
            else:
                go("prediction")

if st.session_state.page=="prediction":
    st.title("Prediction Value")
    st.write("**You are**", "**[*input value*]**", "**likely to get Alzheimer's Disease**!")
    st.session_state.predict=True
    if st.button("Home"):
        go("home")
