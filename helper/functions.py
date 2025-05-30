from helper.session import *

session = create_session()

def generate_session_state():
    if 'requirements_doc' not in st.session_state:
        st.session_state.requirements_doc = None  # list of requirement cards
    if 'requirements' not in st.session_state:
        st.session_state.requirements = []  # list of requirement cards
    if 'epics' not in st.session_state:
        st.session_state.epics = []         # list of agile epic cards
    if 'stories' not in st.session_state:
        st.session_state.stories = []       # list of user story cards
    if 'tasks' not in st.session_state:
        st.session_state.tasks = []         # list of task cards
    if 'next_id' not in st.session_state:
        st.session_state.next_id = 1

# --- Custom complete function using Snowpark SQL ---
def complete(model, prompt):
    """
    Generate a completion for the given prompt using the specified model.
    """
    return session.sql("SELECT snowflake.cortex.complete(?, ?)", (model, prompt)).collect()[0][0]

# --- Generation Functions (with tightened prompts) ---
def generate_epic(requirement_text):
    prompt = (
        f"Based on the following requirements, generate a detailed Agile Epic that adheres to Agile best practices. "
        f"The epic should include a clear title, a concise narrative describing the business need, objectives, scope, "
        f"and measurable acceptance criteria.\n"
        f"Return ONLY the epic text without any extra explanation.\n\nRequirements:\n{requirement_text}\n\nEpic:"
    )
    return complete("llama3-8b", prompt).strip()

def generate_user_stories(epic_text, req_text):
    delimiter = "<<<SPLIT>>>"
    prompt = (
        f"Generate a list of user stories for the following agile epic. Each story should have a clear title (starting with '# ' on its own line), a description, and acceptance criteria. "
        f"Use markdown formatting for the story content. IMPORTANT: Do not include any introductory or extra text.\n"
        f"Separate each story by placing the delimiter '{delimiter}' on its own line immediately after the end of the story.\n\n"
        f"Agile Epic: {epic_text}\nOriginal Requirements: {req_text}\n\nUser Stories:"
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
    if card_type == "requirement":
        st.session_state.requirements = [c for c in st.session_state.requirements if c["id"] != card["id"]]
    elif card_type == "epic":
        st.session_state.epics = [c for c in st.session_state.epics if c["id"] != card["id"]]
    elif card_type == "story":
        st.session_state.stories = [c for c in st.session_state.stories if c["id"] != card["id"]]
    elif card_type == "task":
        st.session_state.tasks = [c for c in st.session_state.tasks if c["id"] != card["id"]]
    st.rerun()

# --- Dialog for editing/expanding a card ---
@st.dialog("Details", width="large")
def card_details_dialog(card, card_type):
    new_text = st.text_area("", value=card["text"], key=f"text_{card_type}_{card['id']}", height=300)
    btn_cols = st.columns([1, 1, 4])
    if btn_cols[0].button("Save", type="primary", key=f"save_{card_type}_{card['id']}", use_container_width=True):
        card["text"] = new_text
        st.rerun()
    if btn_cols[1].button("Cancel", key=f"cancel_{card_type}_{card['id']}", use_container_width=True):
        st.rerun()

# --- Dialog for adding a new requirement ---
@st.dialog("Add Requirement", width="large")
def add_requirement_dialog():
    req_text = st.text_area("Paste requirement text here:", value="", key="new_req_dialog", height=150)
    btn_cols = st.columns([1, 1, 4])
    if btn_cols[0].button("Save", type="primary", key="save_new_req", use_container_width=True):
        st.session_state.new_requirement = req_text
        st.rerun()
    if btn_cols[1].button("Cancel", key="cancel_new_req", use_container_width=True):
        st.rerun()

# --- Cortex AI Functions for Extra Actions ---
def convert_to_epic(req_card):
    epic_text = generate_epic(req_card["text"])
    st.session_state.epics.append({
         "id": get_next_id(),
         "req_id": req_card["id"],
         "text": epic_text
    })
    st.rerun()

def generate_stories_for_epic(epic_card):
    req_text = next((req["text"] for req in st.session_state.requirements if req["id"] == epic_card["req_id"]), "")
    stories = generate_user_stories(epic_card["text"], req_text)
    for story_text in stories:
        st.session_state.stories.append({
             "id": get_next_id(),
             "epic_id": epic_card["id"],
             "req_id": epic_card["req_id"],
             "text": story_text
        })
    st.rerun()

def break_story(story_card):
    tasks_list = break_story_into_tasks(story_card["text"])
    for task_text in tasks_list:
        st.session_state.tasks.append({
            "id": get_next_id(),
            "story_id": story_card["id"],
            "epic_id": story_card["epic_id"],
            "req_id": story_card["req_id"],
            "text": task_text
        })
    st.rerun()

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