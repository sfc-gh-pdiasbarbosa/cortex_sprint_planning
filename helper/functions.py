from helper.session import *
from docx import Document
import io
import hashlib

session = create_session()

def generate_session_state():
    if 'requirements_doc' not in st.session_state:
        st.session_state.requirements_doc = None  # list of requirement cards  
    if "uploaded_file_id" not in st.session_state:
        st.session_state.uploaded_file_id = None
    # if 'requirements' not in st.session_state:
    #     st.session_state.requirements = []  # list of requirement cards
    if 'epics' not in st.session_state:
        st.session_state.epics = []         # list of agile epic cards
    if 'stories' not in st.session_state:
        st.session_state.stories = []       # list of user story cards
    if 'tasks' not in st.session_state:
        st.session_state.tasks = []         # list of task cards
    if 'next_id' not in st.session_state:
        st.session_state.next_id = 1
    if 'save_key' not in st.session_state:
        st.session_state.next_id = False

# --- Custom complete function using Snowpark SQL ---
def complete(model, prompt):
    """
    Generate a completion for the given prompt using the specified model.
    """
    return session.sql("SELECT snowflake.cortex.complete(?, ?)", (model, prompt)).collect()[0][0]

# --- Helper function to generate a unique ID for each uploaded file ---
def generate_file_id(uploaded_file):
    file_content = uploaded_file.read()
    file_hash = hashlib.sha256(file_content).hexdigest()
    uploaded_file.seek(0)
    return file_hash

# --- Generation Functions (with tightened prompts) ---
def generate_epic():
    prompt = (
        f"Based on the following requirements, generate a detailed Agile Epic that adheres to Agile best practices. "
        f"The epic should include a clear title, a concise narrative describing the business need, objectives, scope, "
        f"and measurable acceptance criteria.\n"
        f"Return ONLY the epic text without any extra explanation.\n\nRequirements:\n{st.session_state.requirements_doc}\n\nEpic:"
    )
    return complete("llama3-8b", prompt).strip()

def generate_user_stories(epic_text):
    delimiter = "<<<SPLIT>>>"
    prompt = (
        f"Generate a list of user stories for the following agile epic. Each story should have a clear title (starting with '# ' on its own line), a description, and acceptance criteria. "
        f"Use markdown formatting for the story content. IMPORTANT: Do not include any introductory or extra text.\n"
        f"Separate each story by placing the delimiter '{delimiter}' on its own line immediately after the end of the story.\n\n"
        f"Agile Epic: {epic_text}\nOriginal Requirements: {st.session_state.requirements_doc}\n\nUser Stories:"
    )
    stories_text = complete("llama3-8b", prompt)
    stories = [story.strip() for story in stories_text.split(delimiter) if story.strip()]
    stories = [story for story in stories if not story.startswith("Here are")]
    return stories

def break_story_into_tasks(story_text):
    delimiter = "<<<TASK_SPLIT>>>"
    prompt = (
        f"Break down the following user story into actionable tasks. "
        f"Each task should be a concise, one-sentence description. "
        f"Return only the task descriptions without any additional commentary. "
        f"Separate each task by placing the delimiter '{delimiter}' on its own line immediately after each task. "
        f"Do not include any introductory or summary text.\n\n"
        f"User Story:\n{story_text}\n\nTasks:"
    )
    tasks_text = complete("llama3-8b", prompt)
    tasks = [task.strip() for task in tasks_text.split(delimiter) if task.strip()]
    tasks = [task for task in tasks if not task.lower().startswith("here are")]
    return tasks

# --- Callback function to delete a card ---
def delete_card(card, card_type):
    # if card_type == "requirement":
    #     st.session_state.requirements = [c for c in st.session_state.requirements if c["id"] != card["id"]]
    if card_type == "epic":
        st.session_state.epics = [c for c in st.session_state.epics if c["id"] != card["id"]]
    elif card_type == "story":
        st.session_state.stories = [c for c in st.session_state.stories if c["id"] != card["id"]]
    elif card_type == "task":
        st.session_state.tasks = [c for c in st.session_state.tasks if c["id"] != card["id"]]
    st.rerun()

# --- Dialog for editing/expanding a card ---
@st.dialog("Details", width="large")
def card_details_dialog(card, card_type):
    unique_id = f"{card_type}_{card['id']}"
    save_key = f"save_clicked_{unique_id}"

    new_text = st.text_area("", value=card["text"], key=f"text_{card_type}_{card['id']}", height=300)
    btn_cols = st.columns([1, 1, 4])
    if btn_cols[0].button("Save", type="primary", key=f"save_{card_type}_{card['id']}", use_container_width=True):
        card["text"] = new_text
        st.session_state[save_key] = True
        st.rerun()
    cancel_disabled = st.session_state[save_key]
    if btn_cols[1].button("Cancel", key=f"cancel_{card_type}_{card['id']}", use_container_width=True):
        disabled=cancel_disabled
        st.rerun()

# --- Dialog for adding a new requirement ---
@st.dialog("Add Requirement", width="large")
def add_requirement_dialog():
    save_clicked_key = "new_req_save_clicked"
    if save_clicked_key not in st.session_state:
        st.session_state[save_clicked_key] = False

    # req_text = st.text_area("Paste requirement text here:", value=st.session_state.requirements_doc, key="new_req_dialog", height=150)

    requirement_file = st.file_uploader(
    label="Upload Requirements (Optional)", 
    type=["txt", "docx"], 
    accept_multiple_files=False, 
    label_visibility="visible",
    help='Upload one document with a detailed description of the project requirements',
    )

    requirements_text = None

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

    btn_cols = st.columns([1, 1])

    # TODO ensure that the text box is not blank
    if btn_cols[0].button("Save", type="primary", key="save_new_req", use_container_width=True):
        st.session_state[save_clicked_key] = True
        st.session_state.clear()
        generate_session_state()
        st.session_state.requirements_doc = requirements
        st.session_state[save_clicked_key] = True

        if st.session_state.requirements_doc.strip():
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
        st.rerun()
    if btn_cols[1].button("Cancel", key="cancel_new_req", use_container_width=True, disabled=st.session_state[save_clicked_key]):
        st.rerun()

# --- Cortex AI Functions for Extra Actions ---
def convert_to_epic():
    epic_text = generate_epic()
    st.session_state.epics.append({
         "id": get_next_id(),
        #  "req_id": req_card["id"],
         "text": epic_text
    })
    # st.rerun()

def generate_stories_for_epic(epic_card):
    # req_text = next((req["text"] for req in st.session_state.requirements if req["id"] == epic_card["req_id"]), "")
    stories = generate_user_stories(epic_card["text"])
    for story_text in stories:
        st.session_state.stories.append({
             "id": get_next_id(),
             "epic_id": epic_card["id"],
            #  "req_id": epic_card["req_id"],
             "text": story_text
        })
    #st.rerun()

def break_story(story_card):
    tasks_list = break_story_into_tasks(story_card["text"])
    for task_text in tasks_list:
        st.session_state.tasks.append({
            "id": get_next_id(),
            "story_id": story_card["id"],
            "epic_id": story_card["epic_id"],
            # "req_id": story_card["req_id"],
            "text": task_text
        })
    #st.rerun()

# --- Helper function to render a card as a styled box with buttons ---
def render_card(card, card_type, extra_actions=None, highlight=False):
    # Set default extra_actions for task cards if none provided.
    if extra_actions is None:
        if card_type == "task":
            extra_actions = [ (":material/info:", "select_task", select_task) ]
        else:
            extra_actions = []
    
    # Use the CSS class for styling the card.
    container_class = "card-container"
    if highlight:
        container_class += " highlighted"
    
    full_text = card["text"]
    truncated = full_text if len(full_text) <= 100 else full_text[:100] + "…"
    
    with st.container(border=True):
        st.markdown(
            f"<div class='{container_class}'>"
            f"{truncated}<br><br>",
            unsafe_allow_html=True,
        )
        btn_cols = st.columns(2 + len(extra_actions))
        # Expand/Edit button.
        if btn_cols[0].button("", icon=":material/open_in_full:", key=f"edit_{card_type}_{card['id']}", use_container_width=True):
            card_details_dialog(card, card_type)
        # Delete button.
        if btn_cols[1].button("", icon=":material/delete:", key=f"delete_{card_type}_{card['id']}", use_container_width=True):
            delete_card(card, card_type)
        # Extra action buttons.
        for idx, (icon, key_suffix, callback) in enumerate(extra_actions):
            if btn_cols[idx+2].button("", type="primary", icon=icon, key=f"{key_suffix}_{card['id']}", use_container_width=True):
                callback(card)
        st.markdown("</div>", unsafe_allow_html=True)


def get_next_id():
    current = st.session_state.next_id
    st.session_state.next_id += 1
    return current

def select_task(task):
    st.session_state.selected_task = task
    st.rerun()