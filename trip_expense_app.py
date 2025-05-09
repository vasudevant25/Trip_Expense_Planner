import streamlit as st
import pandas as pd
import os
from datetime import date

# File paths
FAMILY_FILE = "families.csv"
EXPENSE_FILE = "expenses.csv"

# Load data
def load_families():
    return pd.read_csv(FAMILY_FILE)

def load_expenses():
    if os.path.exists(EXPENSE_FILE):
        return pd.read_csv(EXPENSE_FILE)
    else:
        return pd.DataFrame(columns=["Date", "Spender", "Amount", "Reason", "Remarks", "Start KM", "End KM"])

def save_expense(row):
    df = load_expenses()
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    print('Saving Family Expense in ',EXPENSE_FILE)
    df.to_csv(EXPENSE_FILE, index=False)

st.set_page_config(page_title="Trip Expense Manager", layout="centered")
st.title("🚗 Trip Expense Manager")

families_df = load_families()
expenses_df = load_expenses()

# -- Expense Entry Section --
st.header("➕ Add New Expense")
with st.form("expense_form"):
    spender = st.selectbox("Who Spent?", families_df["Family Name"].tolist())
    amount = st.number_input("Amount Spent", min_value=0.0, step=10.0)
    reason = st.text_input("Reason for Expense")
    remarks = st.text_input("Remarks (optional)")
    start_km = st.number_input("Start KM", min_value=0)
    end_km = st.number_input("End KM", min_value=0)
    submitted = st.form_submit_button("Add Expense")

    if submitted:
        row = {
            "Date": date.today().isoformat(),
            "Spender": spender,
            "Amount": amount,
            "Reason": reason,
            "Remarks": remarks,
            "Start KM": start_km,
            "End KM": end_km
        }
        save_expense(row)
        st.success("Expense added!")

# -- View All Expenses --
st.header("📋 All Expenses")
if not expenses_df.empty:
    expenses_df = load_expenses()
    st.dataframe(expenses_df)
else:
    st.info("No expenses added yet.")

# -- Report Section --
st.header("📊 Expense Summary")

if not expenses_df.empty:
    family_spent = expenses_df.groupby("Spender")["Amount"].sum().reset_index()
    shared_families = families_df[families_df["Contribution Type"] == "Shared"]["Family Name"].tolist()
    total_shared_expense = expenses_df[~expenses_df["Spender"].isin(families_df[families_df["Contribution Type"] == "Fixed"]["Family Name"])]["Amount"].sum()
    
    equal_share = total_shared_expense / len(shared_families) if shared_families else 0

    report_df = family_spent.copy()
    report_df["Should Pay"] = report_df["Spender"].apply(lambda x: equal_share if x in shared_families else 0)
    report_df["Difference"] = report_df["Amount"] - report_df["Should Pay"]
    report_df.columns = ["Family", "Spent", "Share to Pay", "Difference"]

    st.dataframe(report_df)
else:
    st.info("Report will appear after adding some expenses.")

st.caption("Built with ❤️ by Vasudevan")
