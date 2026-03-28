import streamlit as st
from main import FamilyExpenseTracker
import matplotlib.pyplot as plt
from streamlit_option_menu import option_menu
from pathlib import Path

# Streamlit config
st.set_page_config(page_title="Family Expense Tracker", page_icon="💰")

# Load CSS safely (FIXED)
current_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()
css_file = current_dir / "styles" / "main.css"

if css_file.exists():
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Session state
if "expense_tracker" not in st.session_state:
    st.session_state.expense_tracker = FamilyExpenseTracker()

expense_tracker = st.session_state.expense_tracker

# Title
st.markdown("<h1 style='text-align: center;'>💰 Family Expense Tracker</h1>", unsafe_allow_html=True)

# Menu
selected = option_menu(
    menu_title=None,
    options=["Data Entry", "Data Overview", "Data Visualization"],
    icons=["pencil-fill", "clipboard-data", "bar-chart-fill"],
    orientation="horizontal",
)

# ---------------- DATA ENTRY ----------------
if selected == "Data Entry":

    st.subheader("👨‍👩‍👧 Add Family Member")

    member_name = st.text_input("Name")
    earning_status = st.checkbox("Earning Status")
    earnings = st.number_input("Earnings", min_value=0) if earning_status else 0

    if st.button("Add Member"):
        try:
            existing = [m for m in expense_tracker.members if m.name == member_name]

            if not existing:
                expense_tracker.add_family_member(member_name, earning_status, earnings)
                st.success("✅ Member added")
            else:
                expense_tracker.update_family_member(existing[0], earning_status, earnings)
                st.success("🔄 Member updated")

        except ValueError as e:
            st.error(str(e))

    st.subheader("💸 Add Expense")

    category = st.selectbox("Category", [
        "Housing", "Food", "Transportation", "Entertainment",
        "Medical", "Investment", "Miscellaneous"
    ])

    description = st.text_input("Description")
    value = st.number_input("Amount", min_value=1)
    date = st.date_input("Date")

    if st.button("Add Expense"):
        try:
            expense_tracker.merge_similar_category(value, category, description, date)
            st.success("✅ Expense added")
        except ValueError as e:
            st.error(str(e))


# ---------------- DATA OVERVIEW ----------------
elif selected == "Data Overview":

    st.subheader("📊 Overview")

    if not expense_tracker.members:
        st.info("Add members first")
    else:
        for m in expense_tracker.members:
            st.write(f"{m.name} | ₹{m.earnings}")

    if not expense_tracker.expense_list:
        st.info("Add expenses first")
    else:
        for e in expense_tracker.expense_list:
            st.write(f"{e.category} - ₹{e.value}")

    total_income = expense_tracker.calculate_total_earnings()
    total_expense = expense_tracker.calculate_total_expenditure()
    balance = total_income - total_expense

    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Income", total_income)
    col2.metric("💸 Expense", total_expense)
    col3.metric("📊 Balance", balance)


# ---------------- VISUALIZATION ----------------
elif selected == "Data Visualization":

    if not expense_tracker.expense_list:
        st.info("No data to visualize")
    else:
        categories = [e.category for e in expense_tracker.expense_list]
        values = [e.value for e in expense_tracker.expense_list]

        fig, ax = plt.subplots()
        ax.pie(values, labels=categories, autopct="%1.1f%%")
        st.pyplot(fig)
