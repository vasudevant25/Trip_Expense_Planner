import streamlit as st
import pandas as pd
from datetime import date

st.title("🚗 Family Trip Expense Splitter")

# ---- Section 1: Trip Distance ----
st.header("Trip Distance")
start_km = st.number_input("Enter Start KM", min_value=0)
end_km = st.number_input("Enter End KM", min_value=start_km)
distance = end_km - start_km
st.write(f"**Total Distance:** {distance} KM")

# ---- Section 2: Fixed Contribution (2 Families) ----
st.header("Fixed Contributions")
fixed_families = {}
fixed_families["Family A"] = st.number_input("Family A Contribution (₹)", min_value=0)
fixed_families["Family B"] = st.number_input("Family B Contribution (₹)", min_value=0)

# ---- Section 3: Expenses Entry ----
st.header("Expense Entry")
if "expenses" not in st.session_state:
    st.session_state.expenses = []

with st.form("expense_form", clear_on_submit=True):
    exp_date = st.date_input("Date", value=date.today())
    amount = st.number_input("Amount (₹)", min_value=0.0)
    reason = st.text_input("Reason")
    spent_by = st.text_input("Spent By")
    remarks = st.text_input("Remarks")
    submitted = st.form_submit_button("Add Expense")
    if submitted:
        st.session_state.expenses.append({
            "Date": exp_date,
            "Amount": amount,
            "Reason": reason,
            "Spent By": spent_by,
            "Remarks": remarks
        })

# ---- Section 4: Expenses Table ----
st.header("All Expenses")
if st.session_state.expenses:
    expenses_df = pd.DataFrame(st.session_state.expenses)
    st.dataframe(expenses_df)

    total_expense = expenses_df["Amount"].sum()
    fixed_total = sum(fixed_families.values())
    remaining = total_expense - fixed_total
    per_family_share = remaining / 4 if remaining > 0 else 0

    # ---- Section 5: Summary ----
    st.subheader("Summary")
    st.write(f"**Total Expense:** ₹{total_expense:.2f}")
    st.write(f"**Fixed Contribution Total (2 Families):** ₹{fixed_total:.2f}")
    st.write(f"**Remaining to be Split (4 Families):** ₹{remaining:.2f}")
    st.write(f"**Each of 4 Families Pays:** ₹{per_family_share:.2f}")
else:
    st.info("No expenses added yet.")
