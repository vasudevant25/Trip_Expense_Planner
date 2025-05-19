import streamlit as st
import pandas as pd
import os
import time
from datetime import date

# --- File Paths ---
TRIP_FILE = "trips.csv"
FAMILY_FILE = "families.csv"
EXPENSE_FILE = "expenses.csv"

# --- Initial Setup ---
st.set_page_config(page_title="Trip Expense Tracker", page_icon="🚗", layout="wide")

# --- Custom CSS for Hotstar-like Theme ---
st.markdown(
    """
    <style>
    body {
        background: linear-gradient(135deg, #001F3F, #003366);
        color: white;
    }
    .stApp {
        background: linear-gradient(135deg, #001F3F, #003366);
        color: white;
    }
    h1, h2, h3, h4, h5, h6 {
        color: white;
    }
    .stTabs [role="tab"] {
        color: white;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] {
        border-bottom: 3px solid #FF4500;
        color: #FFDD57;
    }
    .stButton>button {
        background-color: #FF4500;
        color: black important;
        font-weight: bold;
        border-radius: 10px;
        padding: 0.5em 1em;
    }
    .stTextInput>div>input, .stNumberInput>div>input, .stSelectbox>div>div>div {
        background-color: #f0f0f0;
        color: black;
    }
    .st-emotion-cache-1s2v671{
     color: white;
    }
    button[data-testid="stBaseButton-secondaryFormSubmit"] p {
        color: black !important; /* Force label text color to black */
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Load or Initialize Data ---
def load_data():
    if os.path.exists(TRIP_FILE):
        trips = pd.read_csv(TRIP_FILE)
    else:
        trips = pd.DataFrame(columns=["Trip_Name"])

    if os.path.exists(FAMILY_FILE):
        families = pd.read_csv(FAMILY_FILE)
        families["Fixed_Amount"] = pd.to_numeric(families["Fixed_Amount"], errors='coerce').fillna(0.0)
    else:
        families = pd.DataFrame(columns=["Trip_Name", "Family", "Gmail", "Fixed_Amount"])

    if os.path.exists(EXPENSE_FILE):
        expenses = pd.read_csv(EXPENSE_FILE)
        expenses.columns = expenses.columns.str.strip()
        expenses["Amount"] = pd.to_numeric(expenses["Amount"], errors='coerce').fillna(0.0)
    else:
        expenses = pd.DataFrame(columns=["Trip_Name", "Date", "Spent_By", "Amount", "Reason", "Remarks"])

    return trips, families, expenses

def save_data(trips, families, expenses):
    trips.to_csv(TRIP_FILE, index=False)
    families.to_csv(FAMILY_FILE, index=False)
    expenses.to_csv(EXPENSE_FILE, index=False)

trips, families, expenses = load_data()

# --- Select or Create Trip ---
st.sidebar.header("Select or Create Trip")
trip_names = trips["Trip_Name"].tolist()
selected_trip = st.sidebar.selectbox("Choose a Trip", trip_names)

with st.sidebar.form("trip_form"):
    new_trip = st.text_input("Add New Trip")
    add_trip = st.form_submit_button("Add Trip")

if add_trip and new_trip:
    if new_trip not in trip_names:
        trips = pd.concat([trips, pd.DataFrame([[new_trip]], columns=["Trip_Name"])]).reset_index(drop=True)
        save_data(trips, families, expenses)
        st.sidebar.success(f"Trip '{new_trip}' added. Please select it from the dropdown.")
    else:
        st.sidebar.warning("Trip already exists.")

if not selected_trip:
    st.warning("Please select or add a trip to proceed.")
    st.stop()

# --- Filter data for selected trip ---
trip_families = families[families["Trip_Name"] == selected_trip]
trip_expenses = expenses[expenses["Trip_Name"] == selected_trip]

# --- Tabs Layout ---
tabs = st.tabs(["➕ Add Expense", "📄 View Expenses", "📊 Summary Report", "👥 Manage Families"])

# --- Add Expense Tab ---
with tabs[0]:
    st.header(f"Add Expense - Trip: {selected_trip}")
    with st.form("expense_form"):
        col1, col2 = st.columns(2)
        with col1:
            date_input = st.date_input("Date", date.today())
            spender = st.selectbox("Spent by", trip_families["Family"] if not trip_families.empty else [])
        with col2:
            amount = st.number_input("Amount", min_value=0.0, format="%.2f")
            reason = st.text_input("Reason for Expense")
        remarks = st.text_area("Remarks")
        submitted = st.form_submit_button("Add Expense")

    if submitted:
        if spender:
            new_expense = pd.DataFrame([[selected_trip, date_input, spender, amount, reason, remarks]],
                                       columns=["Trip_Name", "Date", "Spent_By", "Amount", "Reason", "Remarks"])
            expenses = pd.concat([expenses, new_expense], ignore_index=True)
            save_data(trips, families, expenses)
            st.success("Expense added successfully!")
            time.sleep(5)
            st.rerun() 
        else:
            st.error("Please add at least one family first.")

# --- View Expenses Tab ---
#with tabs[1]:
#   st.header(f"View Expenses - Trip: {selected_trip}")
#  st.dataframe(trip_expenses)
# View Expenses Tab (Updated)
with tabs[1]:
    st.header(f"View Expenses - Trip: {selected_trip}")

    # Mark duplicates
    trip_expenses["Duplicate"] = trip_expenses.duplicated(
        subset=["Trip_Name", "Date", "Spent_By", "Amount", "Reason", "Remarks"],
        keep='first'
    )

    if trip_expenses["Duplicate"].any():
        st.warning("Duplicate expenses detected below. You can delete them.")
    
    for idx, row in trip_expenses.iterrows():
        with st.expander(f"{row['Date']} | {row['Spent_By']} | ₹{row['Amount']} - {row['Reason']}"):
            st.write(f"**Remarks:** {row['Remarks']}")
            st.write(f"**Duplicate:** {'Yes' if row['Duplicate'] else 'No'}")
            if st.button(f"🗑️ Delete Expense #{idx}", key=f"del_{idx}"):
                expenses.drop(index=trip_expenses.index[idx], inplace=True)
                expenses.reset_index(drop=True, inplace=True)
                save_data(trips, families, expenses)
                st.success("Expense deleted successfully.")
                time.sleep(2)
                st.rerun()
# --- Summary Report Tab ---
with tabs[2]:
    st.header(f"Summary Report - Trip: {selected_trip}")
    if not trip_families.empty and not trip_expenses.empty:
        fixed_families = trip_families[trip_families["Fixed_Amount"] > 0]
        shared_families = trip_families[trip_families["Fixed_Amount"] == 0]

        total_expense = trip_expenses["Amount"].sum()
        fixed_total = fixed_families["Fixed_Amount"].sum()
        shared_expense = total_expense - fixed_total
        share_per_family = (shared_expense / len(shared_families)) if len(shared_families) > 0 else 0

        report = []
        for _, row in trip_families.iterrows():
            spent = trip_expenses[trip_expenses["Spent_By"] == row["Family"]]["Amount"].sum()
            expected = row["Fixed_Amount"] if row["Fixed_Amount"] > 0 else share_per_family
            balance = spent - expected
            report.append([row["Family"], spent, expected, balance])

        report_df = pd.DataFrame(report, columns=["Family", "Spent", "Expected", "Balance"])
        st.dataframe(report_df)
    else:
        st.info("Add both families and expenses to generate report.")

# --- Manage Families Tab ---
with tabs[3]:
    st.header(f"Manage Families - Trip: {selected_trip}")
    with st.form("family_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            family_name = st.text_input("Family Name")
        with col2:
            gmail = st.text_input("Gmail (optional)")
        with col3:
            fixed_amount = st.number_input("Fixed/Share Amount", min_value=0.0, format="%.2f")
        add_family = st.form_submit_button("Add Family")

    if add_family:
        if family_name:
            if family_name in trip_families["Family"].values:
                st.warning("Family already exists for this trip!")
            else:
                new_family = pd.DataFrame([[selected_trip, family_name, gmail, fixed_amount]],
                                          columns=["Trip_Name", "Family", "Gmail", "Fixed_Amount"])
                families = pd.concat([families, new_family], ignore_index=True)
                save_data(trips, families, expenses)
                st.success(f"Added family: {family_name}")
                time.sleep(5)
                st.rerun()
        else:
            st.error("Family name is required!")
    st.dataframe(trip_families[["Family", "Gmail", "Fixed_Amount"]])
