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
                
    button[data-testid="stBaseButton-primary"]:hover {
        background-color: #1ABCEB;
        border: 1px solid #1ABCEB;
                
    }
    
    button[data-testid="stBaseButton-primary"]{
        background-color: #00A1D9;
        border: 1px solid #00A1D9;
        transition: background-color 0.3s ease, border-color 0.3s ease;
    }

    button[data-testid="stBaseButton-primary"]:active {
        background-color: #00A1D9;  /* Optional: return to original or darken slightly */
        border: 1px solid #00A1D9;
        color: white;  /* Keep text white on click */
    }          
                
    button[data-testid="stBaseButton-secondary"] {
        background-color: transparent !important;
        border: 1px solid #00A1D9 !important;
        color: #00A1D9 !important;
        transition: all 0.3s ease;
        box-shadow: none !important;
    }

    button[data-testid="stBaseButton-secondary"]:hover,
    button[data-testid="stBaseButton-secondary"]:focus,
    button[data-testid="stBaseButton-secondary"]:active,
    button[data-testid="stBaseButton-secondary"]:focus:active {
        background-color: rgba(26, 188, 235, 0.1) !important;
        color: #00A1D9 !important;
        border-color: #1ABCEB !important;
        box-shadow: none !important;
        outline: none !important;
    }

    details > summary {
        color: none !important; 
        outline: none !important;
    }

    details > summary:hover,
    details > summary:active,
    details > summary:focus {
       color: inherit !important;
    }
                
    details > summary svg {
        fill: currentColor !important;
        transition: fill 0.3s ease;
    }

    details > summary:hover svg,
    details > summary:active svg,
    details > summary:focus svg {
        fill: currentColor !important;
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
