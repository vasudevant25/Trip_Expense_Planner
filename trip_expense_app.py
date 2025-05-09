import streamlit as st
import pandas as pd
import os
from datetime import datetime

# File paths
FAMILY_FILE = "families.csv"
EXPENSE_FILE = "expenses.csv"

# Load or create families
if os.path.exists(FAMILY_FILE):
    families_df = pd.read_csv(FAMILY_FILE)
else:
    families_df = pd.DataFrame(columns=["Family Name", "Email", "Contribution Type"])
    families_df.to_csv(FAMILY_FILE, index=False)

# Load or create expenses
if os.path.exists(EXPENSE_FILE):
    print('Reading CSV File')
    expenses_df = pd.read_csv(EXPENSE_FILE)
else:
    expenses_df = pd.DataFrame(columns=["Date", "Spender", "Amount", "Reason", "Remarks", "Start KM", "End KM"])
    expenses_df.to_csv(EXPENSE_FILE, index=False)

# Set page config and gradient background
st.set_page_config(page_title="Trip Expense Tracker", layout="centered")
st.markdown("""
    <style>
        body {
            background: linear-gradient(to bottom right, #e0f7fa, #ffffff);
        }
        .main {
            background-color: rgba(255, 255, 255, 0.8);
            padding: 20px;
            border-radius: 15px;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🚗 Trip Expense Tracker")

# Tabs
tabs = st.tabs(["➕ Add Expense", "📄 View Expenses", "📊 Summary Report", "👨‍👩‍👧‍👦 Manage Families"])

# ➕ Add Expense Tab
with tabs[0]:
    st.header("Add Expense")
    with st.form("expense_form"):
        date = st.date_input("Date", value=datetime.today())
        spender = st.selectbox("Spent by", families_df["Family Name"])
        amount = st.number_input("Amount", min_value=0.0, step=10.0)
        reason = st.text_input("Reason for Expense")
        remarks = st.text_area("Remarks")
        start_km = st.number_input("Start KM", min_value=0)
        end_km = st.number_input("End KM", min_value=0)
        submitted = st.form_submit_button("Add Expense")

        if submitted:
            new_data = pd.DataFrame([{
                "Date": date,
                "Spender": spender,
                "Amount": amount,
                "Reason": reason,
                "Remarks": remarks,
                "Start KM": start_km,
                "End KM": end_km
            }])
            expenses_df = pd.concat([expenses_df, new_data], ignore_index=True)
            expenses_df.to_csv(EXPENSE_FILE, index=False)
            st.success("Expense added successfully!")

# 📄 View Expenses Tab
with tabs[1]:
    st.header("All Expenses")
    if not expenses_df.empty:
        st.dataframe(expenses_df)
    else:
        st.info("No expenses recorded yet.")

# 📊 Summary Report Tab
with tabs[2]:
    st.header("Summary Report")
    if not expenses_df.empty:
        total_expense = expenses_df["Amount"].sum()
        st.metric("Total Trip Expense", f"₹{total_expense:.2f}")

        spent_by_family = expenses_df.groupby("Spender")["Amount"].sum()
        fixed_contributors = families_df[families_df["Contribution Type"] == "Fixed"]["Family Name"]
        shared_families = families_df[families_df["Contribution Type"] == "Shared"]["Family Name"]
        fixed_total = spent_by_family[spent_by_family.index.isin(fixed_contributors)].sum()
        remaining = total_expense - fixed_total
        shared_per_family = remaining / len(shared_families) if len(shared_families) > 0 else 0

        report_data = []
        for family in families_df["Family Name"]:
            spent = spent_by_family.get(family, 0.0)
            if family in fixed_contributors.values:
                to_pay = 0
            else:
                to_pay = shared_per_family - spent
            report_data.append({
                "Family": family,
                "Spent": spent,
                "Should Contribute": 0 if family in fixed_contributors.values else shared_per_family,
                "Pending Amount": round(to_pay, 2)
            })

        report_df = pd.DataFrame(report_data)
        st.dataframe(report_df)
    else:
        st.info("Add expenses to view report.")

# 👨‍👩‍👧‍👦 Manage Families Tab
with tabs[3]:
    st.header("Manage Families")
    st.subheader("Add New Family")
    with st.form("add_family_form"):
        new_family = st.text_input("Family Name")
        email = st.text_input("Email (optional)")
        contribution_type = st.selectbox("Contribution Type", ["Fixed", "Shared"])
        add_btn = st.form_submit_button("Add Family")

        if add_btn:
            if new_family in families_df["Family Name"].values:
                st.warning("Family already exists!")
            else:
                new_row = pd.DataFrame([[new_family, email, contribution_type]], columns=families_df.columns)
                families_df = pd.concat([families_df, new_row], ignore_index=True)
                families_df.to_csv(FAMILY_FILE, index=False)
                st.success(f"Family '{new_family}' added.")

    st.subheader("Existing Families")
    st.dataframe(families_df)
