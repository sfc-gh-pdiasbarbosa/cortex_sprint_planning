import streamlit as st
from helper.css import *
import time
from docx import Document
import io
import hashlib
from helper.functions import generate_session_state, generate_file_id

# --- Styling ---
generate_styling()
generate_session_state()
from helper.session import *
from helper.functions import *

st.title(":pencil: Project Requirements")

st.write("---")

requirement_file = st.file_uploader(
label="Upload Requirements (Optional)", 
type=["txt", "docx"], 
accept_multiple_files=False, 
label_visibility="visible",
help='Upload one document with a detailed description of the project requirements',
)

if requirement_file:
    with st.spinner("Processing Document...",show_time=True):
        try:
            # Check the MIME type of the uploaded file
            if requirement_file.type == "text/plain":
                # For .txt files, read and decode as UTF-8
                requirements_text = requirement_file.read().decode("utf-8")
            elif requirement_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                document = Document(io.BytesIO(requirement_file.read()))
                # Extract text from all paragraphs in the document
                paragraphs = [para.text for para in document.paragraphs]
                requirements_text = "\n".join(paragraphs)
            else:
                st.warning(f"Unsupported file type: {requirement_file.name}. Please upload a .txt or .docx file.")
            requirements_text = requirements_text[:6000]
            st.session_state.requirements_doc = requirements_text   
        except Exception as e:
            st.error(f"An error occurred while processing the file: {e}")    
        
        file_id = generate_file_id(requirement_file)
        if file_id != st.session_state.uploaded_file_id:
            st.toast("Word Document Processed Successfully!", icon="✅")   
            st.session_state.uploaded_file_id = file_id 

requirements = st.text_area(
    placeholder="Type here...",
    value=(st.session_state.requirements_doc or ""),
    label="Project Requirements",
    height=300,
    label_visibility='collapsed',
    max_chars=6000
)
if st.button("Submit", use_container_width=True, type='primary'):
    if requirements.strip():
        st.session_state.requirements_doc = requirements
        with st.spinner("Creating Jira Epics, Stories, and Tasks...", show_time=True):
            
            convert_to_epic()
            st.toast("Generated Epic Successfully!", icon="✅")

            if st.session_state.epics != []:
                for epic in st.session_state.epics:
                    generate_stories_for_epic(epic)
                st.toast("Generated Stories Successfully!", icon="✅")
            else:
                st.warning("Could not generate epics, please try again.")

            if st.session_state.stories != []:
                for story in st.session_state.stories:
                    break_story(story)
                st.toast("Generated Tasks Successfully!", icon="✅")
            else:
                st.warning("Could not generate stories, please try again.")
            st.switch_page("pages/Jira_Planner.py")
    else:
        warning_placeholder = st.empty()
        warning_placeholder.warning("Please enter your requirements")
        time.sleep(2.2)  
        # Clear the warning message from the placeholder
        warning_placeholder.empty()
