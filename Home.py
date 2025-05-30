import streamlit as st
# Set page config to wide.
st.set_page_config(layout="wide")
from helper.css import *
generate_styling()

from helper.session import *
from helper.functions import *
# --- Session State Initialization ---
generate_session_state()

st.snow()

st.title(":snowboarder: Home")

st.markdown("---")
st.write("Streamline your project setup with our Jira automation tool. Effortlessly generate a comprehensive suite of Jira items, including epics, stories, tasks, and sub-tasks, directly from your inputs. Click the button below to begin and experience a more efficient workflow all with the power of Cortex AI!")
if st.button("Begin Your Jira Journey", key="page1_btn", use_container_width=True, type="primary"):
    st.switch_page("pages/Add_Requirements.py")

st.write("")
st.subheader("FAQ")
with st.expander("What is the purpose of this app?"):
    st.write("Test..")

with st.expander("What is JIRA?"):
    st.write("Test..")


with st.expander("Some more FAQs.."):
    st.write("Test..")