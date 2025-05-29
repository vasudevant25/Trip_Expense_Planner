import streamlit as st
import pandas as pd
import os
from datetime import date
import time
from io import BytesIO
import base64

# --- Helper Functions ---
def get_excel_download_link(df, filename, link_text):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    excel_data = output.getvalue()
    b64 = base64.b64encode(excel_data).decode()
    return f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}">{link_text}</a>'

def delete_record(df, index_to_delete):
    return df.drop(index_to_delete).reset_index(drop=True)

# --- File Paths ---
TRIP_FILE = "trips.csv"
FAMILY_FILE = "families.csv"
EXPENSE_FILE = "expenses.csv"

# --- Initialize CSV files if they don't exist ---
def initialize_csv_files():
    if not os.path.exists(TRIP_FILE) or os.path.getsize(TRIP_FILE) == 0:
        pd.DataFrame(columns=["Trip_Name"]).to_csv(TRIP_FILE, index=False)
    
    if not os.path.exists(FAMILY_FILE) or os.path.getsize(FAMILY_FILE) == 0:
        pd.DataFrame(columns=["Trip_Name", "Family", "Gmail", "Fixed_Amount"]).to_csv(FAMILY_FILE, index=False)
    
    if not os.path.exists(EXPENSE_FILE) or os.path.getsize(EXPENSE_FILE) == 0:
        pd.DataFrame(columns=["Trip_Name", "Date", "Spent_By", "Amount", "Reason", "Remarks"]).to_csv(EXPENSE_FILE, index=False)

# Initialize files before setting up the page
initialize_csv_files()

# --- Initial Setup ---
st.set_page_config(page_title="Trip Expense Tracker", page_icon="🚗", layout="wide")

# --- Custom CSS for Hotstar-like Theme with compact spacing ---
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
    
    /* Header Styling */
    h1, h2, h3, h4, h5, h6 {
        color: #FFDD57;
        margin: 8px 0 !important;
        padding: 0 !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }
    
    /* Clean Container Styling */
    .stTabs {
        background: transparent;
        border-radius: 10px;
        padding: 10px;
    }
    
    div[data-testid="stElementContainer"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    /* Compact Container Spacing */
    [data-testid="stHorizontalBlock"] {
        padding: 0 !important;
        margin: 0 !important;
        gap: 0.5rem !important;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        padding: 0 !important;
        margin-bottom: 0.5rem !important;
    }

    [data-testid="stColumn"] {
        padding: 0 !important;
        margin: 0 !important;
    }
    
    /* Tab Styling */
    .stTabs [role="tab"] {
        color: white;
        font-weight: bold;
        transition: all 0.3s ease;
        border-radius: 5px;
        padding: 8px 16px;
        margin: 0 4px;
        background: rgba(255, 255, 255, 0.05);
        border: none;
    }
    
    .stTabs [role="tab"]:hover {
        transform: translateY(-2px);
        background: rgba(255, 255, 255, 0.1);
    }
    
    .stTabs [aria-selected="true"] {
        border-bottom: 3px solid #FF4500;
        color: #FFDD57;
        background: rgba(255, 255, 255, 0.1);
    }
    
    /* Button Styling */
    .stButton>button {
        background: linear-gradient(145deg, #FF4500, #FF6B3D);
        color: black !important;
        font-weight: bold;
        border-radius: 10px;
        padding: 2px 6px !important;
        margin: 0 !important;
        border: none;
        box-shadow: 0 4px 10px rgba(255, 69, 0, 0.2);
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(255, 69, 0, 0.3);
    }
    
    .stButton>button:active {
        transform: translateY(1px);
    }
    
    /* Input Field Styling */
    .stTextInput>div>input, .stNumberInput>div>input, .stSelectbox>div>div>div {
        background-color: rgba(240, 240, 240, 0.95);
        color: black;
        border-radius: 8px;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* Metric Card Styling */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        color: #FFDD57 !important;
        font-weight: bold;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    }
    
    /* Content Container Styling */
    div[data-testid="stVerticalBlock"] > div {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Download Button Styling */
    a {
        color: #FFDD57 !important;
        text-decoration: none;
        padding: 4px 8px !important;
        margin: 0 0 8px 0 !important;
        background: rgba(255, 221, 87, 0.1);
        border-radius: 10px;
        border: 1px solid rgba(255, 221, 87, 0.3);
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
        display: inline-block;
    }
    
    a:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(0, 0, 0, 0.25);
        background: rgba(255, 221, 87, 0.15);
    }
    
    /* Progress Bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #FF4500, #FF6B3D);
        box-shadow: 0 2px 6px rgba(255, 69, 0, 0.2);
        border-radius: 10px;
    }
    
    /* DataFrames/Tables */
    .stDataFrame {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 8px !important;
        margin: 4px 0 !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .dataframe {
        color: white !important;
        background: rgba(255, 255, 255, 0.02);
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* Alert Messages */
    .stAlert {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 10px;
    }

    /* Even more compact expense rows */
    .expense-row {
        padding: 4px 8px !important;
        margin: 2px 0 !important;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 4px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        line-height: 1.2;
    }
    
    .expense-row:hover {
        background: rgba(255, 255, 255, 0.08);
    }

    /* Remove extra padding from columns in expense view */
    div[data-testid="column"] {
        padding: 0 !important;
        margin: 0 !important;
    }

    /* Adjust vertical spacing between elements */
    .element-container, .stMarkdown {
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Form Submit Button Text Styling */
    button[kind="primary"] {
        color: black !important;
        font-weight: bold !important;
    }

    button[data-testid="stFormSubmitButton"] > div {
        color: black !important;
        font-weight: bold !important;
    }

    /* Ensure form submit button text is visible */
    [data-testid="stFormSubmitButton"] p {
        color: black !important;
        font-weight: bold !important;
    }

    /* Override any other button text colors */
    .stButton button p {
        color: black !important;
        font-weight: bold !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# After the imports, add:
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False

# --- Load or Initialize Data ---
def load_data():
    # Create empty DataFrames with correct columns
    trips = pd.DataFrame(columns=["Trip_Name"])
    families = pd.DataFrame(columns=["Trip_Name", "Family", "Gmail", "Fixed_Amount"])
    expenses = pd.DataFrame(columns=["Trip_Name", "Date", "Spent_By", "Amount", "Reason", "Remarks"])
    
    # Save empty DataFrames if files don't exist
    if not os.path.exists(TRIP_FILE):
        trips.to_csv(TRIP_FILE, index=False)
    else:
        try:
            trips = pd.read_csv(TRIP_FILE)
        except:
            trips.to_csv(TRIP_FILE, index=False)
    
    if not os.path.exists(FAMILY_FILE):
        families.to_csv(FAMILY_FILE, index=False)
    else:
        try:
            families = pd.read_csv(FAMILY_FILE)
            families["Fixed_Amount"] = pd.to_numeric(families["Fixed_Amount"], errors='coerce').fillna(0.0)
        except:
            families.to_csv(FAMILY_FILE, index=False)
    
    if not os.path.exists(EXPENSE_FILE):
        expenses.to_csv(EXPENSE_FILE, index=False)
    else:
        try:
            expenses = pd.read_csv(EXPENSE_FILE)
            expenses.columns = expenses.columns.str.strip()
            expenses["Amount"] = pd.to_numeric(expenses["Amount"], errors='coerce').fillna(0.0)
            # Convert Date column to datetime
            expenses["Date"] = pd.to_datetime(expenses["Date"]).dt.date
        except:
            expenses.to_csv(EXPENSE_FILE, index=False)
    
    return trips, families, expenses

def save_data(trips, families, expenses):
    # Convert date objects to string before saving
    expenses_to_save = expenses.copy()
    expenses_to_save["Date"] = expenses_to_save["Date"].astype(str)
    
    # Update session state
    st.session_state.trips = trips
    st.session_state.families = families
    st.session_state.expenses = expenses
    
    # Save to files
    trips.to_csv(TRIP_FILE, index=False)
    families.to_csv(FAMILY_FILE, index=False)
    expenses_to_save.to_csv(EXPENSE_FILE, index=False)
    
    # Force refresh of the data
    st.session_state.data_loaded = True

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
tabs = st.tabs(["➕ Add Expense", "📄 View Expenses", "�� Summary Report", "💰 Payment Suggestions", "👥 Manage Families"])

# --- Add Expense Tab ---
with tabs[0]:
    st.header(f"Add Expense - Trip: {selected_trip}")
    
    # Add form key to session state if not exists
    if 'form_submitted' not in st.session_state:
        st.session_state.form_submitted = False
    
    with st.form("expense_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            date_input = st.date_input("Date", date.today())
            spender = st.selectbox("Spent by", trip_families["Family"] if not trip_families.empty else [])
        with col2:
            amount = st.number_input("Amount", min_value=0.0, format="%.2f")
            reason = st.text_input("Reason for Expense")
        remarks = st.text_area("Remarks")
        submitted = st.form_submit_button("Add Expense", disabled=st.session_state.form_submitted)

    if submitted and not st.session_state.form_submitted:
        if spender:
            st.session_state.form_submitted = True
            
            # Show progress bar
            progress_text = "Adding expense..."
            progress_bar = st.progress(0)
            
            for i in range(100):
                time.sleep(0.01)  # Simulate work being done
                progress_bar.progress(i + 1)
            
            # Create new expense with proper date type
            new_expense = pd.DataFrame({
                "Trip_Name": [selected_trip],
                "Date": [date_input],
                "Spent_By": [spender],
                "Amount": [amount],
                "Reason": [reason],
                "Remarks": [remarks]
            })
            
            expenses = pd.concat([expenses, new_expense], ignore_index=True)
            save_data(trips, families, expenses)
            
            progress_bar.empty()  # Remove progress bar
            st.success("Expense added successfully!")
            st.session_state.form_submitted = False  # Reset form state
            st.rerun()
        else:
            st.error("Please add at least one family first.")

    # Show recent expenses with delete option
    if not trip_expenses.empty:
        st.subheader("Recent Expenses")
        recent_expenses = trip_expenses.sort_values('Date', ascending=False).head(5)
        
        for idx, row in recent_expenses.iterrows():
            col1, col2, col3 = st.columns([0.8, 0.1, 0.1])
            with col1:
                st.write(f"📅 {row['Date']} | 👤 {row['Spent_By']} | 💰 ₹{row['Amount']} | 📝 {row['Reason']}")
            with col2:
                if st.button("🗑️", key=f"del_exp_{idx}"):
                    expenses = delete_record(expenses, idx)
                    save_data(trips, families, expenses)
                    st.rerun()

# --- View Expenses Tab ---
with tabs[1]:
    st.header(f"View Expenses - Trip: {selected_trip}")
    
    if not trip_expenses.empty:
        # Add export button
        st.markdown(get_excel_download_link(trip_expenses, 
                                          f"{selected_trip}_expenses.xlsx",
                                          "📥 Download Expenses Report"), 
                   unsafe_allow_html=True)
        
        # Display expenses with compact styling
        for idx, row in trip_expenses.iterrows():
            col1, col2 = st.columns([0.95, 0.05])
            with col1:
                st.markdown(
                    f"""<div class="expense-row">
                        <span style="color: #FFDD57;">📅 {row['Date']}</span> | 
                        <span style="color: #FF4500;">👤 {row['Spent_By']}</span> | 
                        <span style="color: #4CAF50;">💰 ₹{row['Amount']:.2f}</span> | 
                        <span style="color: #B0B0B0;">📝 {row['Reason']} {f"✍️ {row['Remarks']}" if row['Remarks'] else ''}</span>
                    </div>""", 
                    unsafe_allow_html=True
                )
            with col2:
                if st.button("🗑️", key=f"del_exp_view_{idx}", help="Delete expense"):
                    expenses = delete_record(expenses, idx)
                    save_data(trips, families, expenses)
                    st.rerun()
    else:
        st.info("No expenses recorded yet.")

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
        
        # Add export button for summary
        st.markdown(get_excel_download_link(report_df, 
                                          f"{selected_trip}_summary.xlsx",
                                          "📥 Download Summary Report"), 
                   unsafe_allow_html=True)
        
        st.dataframe(report_df)
    else:
        st.info("Add both families and expenses to generate report.")

# --- Payment Suggestions Tab ---
with tabs[3]:
    st.header(f"Payment Suggestions - Trip: {selected_trip}")
    if not trip_families.empty and not trip_expenses.empty:
        # Calculate total expenses and shares
        total_expense = trip_expenses["Amount"].sum()
        
        # Separate fixed and shared amount families
        fixed_families = trip_families[trip_families["Fixed_Amount"] > 0]
        shared_families = trip_families[trip_families["Fixed_Amount"] == 0]
        
        # Calculate fixed and shared amounts
        fixed_total = fixed_families["Fixed_Amount"].sum()
        shared_expense = total_expense - fixed_total
        share_per_family = (shared_expense / len(shared_families)) if len(shared_families) > 0 else 0
        
        # Create detailed report
        detailed_report = []
        for _, row in trip_families.iterrows():
            spent = trip_expenses[trip_expenses["Spent_By"] == row["Family"]]["Amount"].sum()
            is_fixed = row["Fixed_Amount"] > 0
            expected = row["Fixed_Amount"] if is_fixed else share_per_family
            balance = spent - expected
            category = "Fixed Amount" if is_fixed else "Shared Amount"
            detailed_report.append({
                "Family": row["Family"],
                "Category": category,
                "Total Spent": spent,
                "Expected Share": expected,
                "Balance": balance
            })
        
        # Convert to DataFrame and display detailed summary
        detailed_df = pd.DataFrame(detailed_report)
        
        # Display category-wise summary
        st.subheader("Category-wise Summary")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("📌 Fixed Amount Members")
            fixed_df = detailed_df[detailed_df["Category"] == "Fixed Amount"]
            if not fixed_df.empty:
                st.dataframe(fixed_df)
            else:
                st.info("No fixed amount members")
                
        with col2:
            st.write("📌 Shared Amount Members")
            shared_df = detailed_df[detailed_df["Category"] == "Shared Amount"]
            if not shared_df.empty:
                st.dataframe(shared_df)
            else:
                st.info("No shared amount members")
        
        # Calculate and display payment suggestions
        st.subheader("💸 Payment Suggestions")
        
        # Convert balances to a simple list of who owes what
        balances = detailed_df[["Family", "Balance"]].values.tolist()
        
        # Separate into who needs to pay and who needs to receive
        debtors = [(family, abs(balance)) for family, balance in balances if balance < 0]
        creditors = [(family, balance) for family, balance in balances if balance > 0]
        
        # Sort by amount
        debtors.sort(key=lambda x: x[1], reverse=True)
        creditors.sort(key=lambda x: x[1], reverse=True)
        
        # Generate payment suggestions
        suggestions = []
        i, j = 0, 0
        
        while i < len(debtors) and j < len(creditors):
            debtor, debt = debtors[i]
            creditor, credit = creditors[j]
            
            if abs(debt) < 0.01 or abs(credit) < 0.01:  # Skip tiny amounts
                if abs(debt) < 0.01: i += 1
                if abs(credit) < 0.01: j += 1
                continue
                
            amount = min(debt, credit)
            suggestions.append({
                "From": debtor,
                "To": creditor,
                "Amount": round(amount, 2)
            })
            
            debtors[i] = (debtor, debt - amount)
            creditors[j] = (creditor, credit - amount)
            
            if abs(debtors[i][1]) < 0.01: i += 1
            if abs(creditors[j][1]) < 0.01: j += 1
        
        if suggestions:
            # Add export button for payment suggestions
            suggestions_df = pd.DataFrame(suggestions)
            st.markdown(get_excel_download_link(suggestions_df, 
                                              f"{selected_trip}_payment_suggestions.xlsx",
                                              "📥 Download Payment Suggestions"), 
                       unsafe_allow_html=True)
            st.dataframe(suggestions_df)
        else:
            st.info("No payments needed - all balances are settled!")
            
        # Display overall trip statistics
        st.subheader("📊 Trip Statistics")
        stats_col1, stats_col2, stats_col3 = st.columns(3)
        with stats_col1:
            st.metric("Total Trip Expense", f"₹{total_expense:.2f}")
        with stats_col2:
            st.metric("Fixed Expenses", f"₹{fixed_total:.2f}")
        with stats_col3:
            st.metric("Shared Expenses", f"₹{shared_expense:.2f}")
            
    else:
        st.info("Add both families and expenses to generate payment suggestions.")

# --- Manage Families Tab ---
with tabs[4]:
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
                st.rerun()
        else:
            st.error("Family name is required!")
    
    # Show current families with delete option
    if not trip_families.empty:
        st.subheader("Current Family Members")
        for idx, row in trip_families.iterrows():
            col1, col2 = st.columns([0.9, 0.1])
            with col1:
                st.write(f"👤 {row['Family']} | ✉️ {row['Gmail']} | 💰 Fixed Amount: ₹{row['Fixed_Amount']}")
            with col2:
                if st.button("🗑️", key=f"del_fam_{idx}"):
                    # Check if family has any expenses
                    if row['Family'] in trip_expenses['Spent_By'].values:
                        st.error("Cannot delete family with existing expenses. Please delete their expenses first.")
                    else:
                        families = delete_record(families, idx)
                        save_data(trips, families, expenses)
                        st.rerun()
    else:
        st.info("No families added yet for this trip.")
