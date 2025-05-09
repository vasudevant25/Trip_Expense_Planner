import streamlit as st
import pandas as pd
import os
from datetime import date

# --- File Paths ---
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
    if os.path.exists(FAMILY_FILE):
        try:
            families = pd.read_csv(FAMILY_FILE)
            families = pd.read_csv("families.csv")
            families["Fixed_Amount"] = pd.to_numeric(families["Fixed_Amount"], errors='coerce').fillna(0.0)
        except Exception as e:
            st.warning(f"Error loading families.csv: {e}")
            families = pd.DataFrame(columns=["Family", "Gmail", "Fixed_Amount"])
    else:
        families = pd.DataFrame(columns=["Family", "Gmail", "Fixed_Amount"])

    if os.path.exists(EXPENSE_FILE):
        try:
            expenses = pd.read_csv(EXPENSE_FILE)
            expenses.columns = expenses.columns.str.strip()
            expenses["Amount"] = pd.to_numeric(expenses["Amount"], errors='coerce').fillna(0.0)

        except Exception as e:
            st.warning(f"Error loading expenses.csv: {e}")
            expenses = pd.DataFrame(columns=["Date", "Spent_By", "Amount", "Reason", "Remarks"])
    else:
        expenses = pd.DataFrame(columns=["Date", "Spent_By", "Amount", "Reason", "Remarks"])
    print("Families columns:", families.columns.tolist())
    print("Expenses columns:", expenses.columns.tolist())

    return families, expenses


def save_data(families, expenses):
    families.to_csv(FAMILY_FILE, index=False)
    expenses.to_csv(EXPENSE_FILE, index=False)

families, expenses = load_data()

# --- Tabs Layout ---
tabs = st.tabs(["➕ Add Expense", "📄 View Expenses", "📊 Summary Report", "👥 Manage Families"])

# --- Add Expense Tab ---
with tabs[0]:
    st.header("Add Expense")
    with st.form("expense_form"):
        col1, col2 = st.columns(2)
        with col1:
            date_input = st.date_input("Date", date.today())
            spender = st.selectbox("Spent by", families["Family"] if not families.empty else [])
        with col2:
            amount = st.number_input("Amount", min_value=0.0, format="%.2f")
            reason = st.text_input("Reason for Expense")
        remarks = st.text_area("Remarks")
        submitted = st.form_submit_button("Add Expense")

    if submitted:
        if spender:
            new_expense = pd.DataFrame([[date_input, spender, amount, reason, remarks]],
                                       columns=expenses.columns)
            expenses = pd.concat([expenses, new_expense], ignore_index=True)
            save_data(families, expenses)
            st.success("Expense added successfully!")
        else:
            st.error("Please add at least one family first.")

# --- View Expenses Tab ---
with tabs[1]:
    st.header("View Expenses")
    st.dataframe(expenses)

# --- Summary Report Tab ---
with tabs[2]:
    st.header("Summary Report")
    if not families.empty and not expenses.empty:
        fixed_families = families[families["Fixed_Amount"] > 0]
        shared_families = families[families["Fixed_Amount"] == 0]

        total_expense = expenses["Amount"].sum()
        fixed_total = fixed_families["Fixed_Amount"].sum()
        shared_expense = total_expense - fixed_total

        share_per_family = (shared_expense / len(shared_families)) if len(shared_families) > 0 else 0

        report = []
        for _, row in families.iterrows():
            spent = expenses[expenses["Spent_By"] == row["Family"]]["Amount"].sum()
            expected = row["Fixed_Amount"] if row["Fixed_Amount"] > 0 else share_per_family
            balance = spent - expected
            report.append([row["Family"], spent, expected, balance])

        report_df = pd.DataFrame(report, columns=["Family", "Spent", "Expected", "Balance"])
        st.dataframe(report_df)
    else:
        st.info("Add both families and expenses to generate report.")

# --- Manage Families Tab ---
with tabs[3]:
    st.header("Manage Families")
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
            if family_name in families["Family"].values:
                st.warning("Family already exists!")
            else:
                new_family = pd.DataFrame([[family_name, gmail, fixed_amount]], columns=families.columns)
                families = pd.concat([families, new_family], ignore_index=True)
                save_data(families, expenses)
                st.success(f"Added family: {family_name}")
        else:
            st.error("Family name is required!")
    st.dataframe(families[["Family", "Gmail", "Fixed_Amount"]])  # Shows all columns
