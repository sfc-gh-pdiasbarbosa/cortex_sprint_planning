import streamlit as st

# --- Styling ---
def generate_styling():
    st.markdown("""
    <style>
    .stMain {
        padding-left: 150px;
        padding-right: 150px;
    }
    .card-container {
        padding: 10px;
        border: 2px solid #ccc;
        border-radius: 5px;
        margin: 5px;
        background-color: #f9f9f9;
        height: 150px;         /* Set a fixed height for all cards */
        overflow-y: auto;
    }
    .card-container.highlighted {
        border-color: #0000ff; /* Highlighted border color */
    }
                
    /* Hide sidebar entirely */
    [data-testid="stSidebar"] {
        display: none
    }

    [data-testid="stSidebarCollapsedControl"] {
        display: none
    }
                
    .main .block-container {
        padding-left: 5rem; /* Adjust as needed */
        padding-right: 5rem; /* Adjust as needed */
    }
    </style>
    """, unsafe_allow_html=True)
