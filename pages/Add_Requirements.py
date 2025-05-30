import streamlit as st
from helper.css import *
import time
from docx import Document # For reading .docx files
import io # For handling byte streams
# --- Styling ---
generate_styling()

from helper.session import *
from helper.functions import *


st.title("Project Requirements")

st.write("---")

if st.session_state.requirements_doc is None:
    upload_type = st.selectbox(
        label="Add Your Project Requirements",
        options=["Type Requirements","Upload Requirements"],
        label_visibility='visible',
        key='option'
    )
    if upload_type == 'Type Requirements':
        requirements = st.text_area(
            label="Project Requirements",
            height=300,
            label_visibility='collapsed',
            placeholder="Type here...",
            max_chars=6000
        )
        if st.button("Submit", use_container_width=True, type='primary'):
            if requirements:
                st.session_state.requirements_doc = requirements
                st.switch_page("pages/Jira_Planner.py")
            else:
                warning_placeholder = st.empty()
                warning_placeholder.warning("Please enter your requirements")
                time.sleep(2.2)  
                # Clear the warning message from the placeholder
                warning_placeholder.empty()
    elif upload_type == 'Upload Requirements':
        requirement_file = st.file_uploader(
        label="Project Requirements", 
        type=["txt", "docx"], 
        accept_multiple_files=False, 
        help='Upload one document with a detailed description of the project requirements', label_visibility='collapsed'
        )
        if requirement_file:
            with st.spinner("Processing Document...",show_time=True):
                try:
                    # Check the MIME type of the uploaded file
                    if requirement_file.type == "text/plain":
                        # For .txt files, read and decode as UTF-8
                        requirements_text = requirement_file.read().decode("utf-8")
                        st.session_state.requirements_doc = requirements_text[:6000]
                        st.toast("Text file processed successfully!", icon="✅")
                    elif requirement_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                        document = Document(io.BytesIO(requirement_file.read()))
                        # Extract text from all paragraphs in the document
                        paragraphs = [para.text for para in document.paragraphs]
                        requirements_text = "\n".join(paragraphs)
                        st.session_state.requirements_doc = requirements_text[:6000]
                        st.toast("Word document processed successfully!", icon="✅")                
                    else:
                        st.warning(f"Unsupported file type: {requirement_file.name}. Please upload a .txt or .docx file.")

                    st.switch_page("pages/Jira_Planner.py")

                except Exception as e:
                    st.error(f"An error occurred while processing the file: {e}")
                    # It's good practice to clear any potentially partial or incorrect data in session state on error
                    if 'requirements' in st.session_state:
                        del st.session_state.requirements_doc

    else:
        st.warning("You have already uploaded your project requirements")
else:
    st.subheader("Would you like to upload requirements for a new project?")
    yes, no = st.columns([50,50])
    with yes:
        if st.button("Yes", use_container_width=True):
            del st.session_state.requirements_doc
            st.session_state.requirements_doc = None
            st.rerun()
    with no:
        if st.button("No", use_container_width=True):
            st.switch_page("pages/Jira_Planner.py")



