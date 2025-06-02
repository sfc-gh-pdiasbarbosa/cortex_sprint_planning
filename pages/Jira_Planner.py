import streamlit as st
from helper.css import *
# --- Styling ---
generate_styling()

from helper.css import *
from helper.session import *
from helper.functions import *
from helper.functions import generate_session_state

# Get the active Snowpark session (native Streamlit app within Snowflake)
session = create_session()

generate_session_state()


# --- Main UI ---
st.title(":bookmark_tabs: Jira Planner")

st.write("---")

if st.session_state.requirements_doc:
    with st.container(height=500, border=False):
        # Create four columns with dynamic width (wider layout)
        col_epic, col_story, col_task = st.columns(3, gap="medium")

        # --- Requirements Column ---
        # with col_req:
        #     st.markdown("### Requirements")
        #     for req in st.session_state.requirements:
        #         highlight = False
        #         if "selected_task" in st.session_state:
        #             if req["id"] == st.session_state.selected_task.get("req_id"):
        #                 highlight = True
        #         # Extra action button: convert requirement into an epic.
        #         extra = [ (":material/auto_fix_high:", "convert_req", convert_to_epic) ]
        #         render_card(req, "requirement", extra_actions=extra, highlight=highlight)
        #     if st.button("Add Epic", key="btn_add_requirement", use_container_width=True):
        #         add_requirement_dialog()
        #     if "new_requirement" in st.session_state:
        #         new_req_text = st.session_state.new_requirement
        #         if new_req_text.strip():
        #             st.session_state.requirements.append({
        #                 "id": get_next_id(),
        #                 "text": new_req_text.strip()
        #             })
        #         del st.session_state.new_requirement
        #         st.rerun()



        # --- Epics Column ---
        with col_epic:
            st.markdown("""
            <div style="text-align: center;">
                <h2>Epic</h3>
            </div>
            """, unsafe_allow_html=True)

            for epic in st.session_state.epics:
                highlight = False
                if "selected_task" in st.session_state:
                    if epic["id"] == st.session_state.selected_task.get("epic_id"):
                        highlight = True
                # Extra action button: generate user stories from the epic.
                extra = [ (":material/auto_fix_high:", "gen_stories", generate_stories_for_epic) ]
                render_card(epic, "epic", extra_actions=extra, highlight=highlight)

        # --- Stories Column ---
        with col_story:
            st.markdown("""
            <div style="text-align: center;">
                <h2>User Stories</h3>
            </div>
            """, unsafe_allow_html=True)
            for story in st.session_state.stories:
                highlight = False
                if "selected_task" in st.session_state:
                    if story["id"] == st.session_state.selected_task.get("story_id"):
                        highlight = True
                # Extra action button: break the story into tasks.
                extra = [ (":material/auto_fix_high:", "break_story", break_story) ]
                render_card(story, "story", extra_actions=extra, highlight=highlight)

        # --- Tasks Column ---
        with col_task:
            st.markdown("""
            <div style="text-align: center;">
                <h2>Tasks</h3>
            </div>
            """, unsafe_allow_html=True)
            for task in st.session_state.tasks:
                highlight = False
                if "selected_task" in st.session_state:
                    if task["id"] == st.session_state.selected_task.get("id"):
                        highlight = True
                # Task cards will show the default info button and highlight if selected.
                render_card(task, "task", highlight=highlight)

    if st.button("Edit Project Requirements", use_container_width=True, type='primary'):
        add_requirement_dialog()
else:
    st.warning("Please upload your requirements before accessing this page")
    if st.button("OK", key="confirm_yes", use_container_width=True, type='primary'):
        st.switch_page("pages/Add_Requirements.py")
        st.rerun()
