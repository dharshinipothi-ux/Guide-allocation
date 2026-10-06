
import streamlit as st
import pandas as pd
from io import BytesIO
from supabase import create_client, Client


# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Admin Dashboard",
    page_icon="🔐",
    layout="wide"
)


# --------------------------------------------------
# SUPABASE CONNECTION
# --------------------------------------------------

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# --------------------------------------------------
# ADMIN LOGIN
# --------------------------------------------------

st.title("🔐 Admin Dashboard")

ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]

password = st.text_input(
    "Enter Admin Password",
    type="password"
)

if password != ADMIN_PASSWORD:
    st.warning("Please enter the correct admin password.")
    st.stop()


st.success("Admin login successful!")


# --------------------------------------------------
# FETCH DATA
# --------------------------------------------------

students_response = (
    supabase
    .table("students")
    .select(
        "id, name, registration_number, gender, faculty_id"
    )
    .order("name")
    .execute()
)

students = students_response.data


faculty_response = (
    supabase
    .table("faculty")
    .select("id, name, capacity")
    .order("id")
    .execute()
)

faculty_data = faculty_response.data


# --------------------------------------------------
# PREPARE DATA
# --------------------------------------------------

faculty_lookup = {
    faculty["id"]: faculty["name"]
    for faculty in faculty_data
}

student_df = pd.DataFrame(students)

if not student_df.empty:
    student_df["faculty_name"] = student_df["faculty_id"].map(
        faculty_lookup
    )

    student_df["status"] = student_df["faculty_id"].apply(
        lambda x: "Allocated" if pd.notna(x) else "Pending"
    )

allocated_count = sum(
    1
    for student in students
    if student["faculty_id"] is not None
)

total_students = len(students)
pending_count = total_students - allocated_count
faculty_count = len(faculty_data)


# --------------------------------------------------
# DASHBOARD METRICS
# --------------------------------------------------

st.subheader("📊 Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Students",
    total_students
)

col2.metric(
    "Allocated",
    allocated_count
)

col3.metric(
    "Pending",
    pending_count
)

col4.metric(
    "Faculty Count",
    faculty_count
)


st.divider()


# --------------------------------------------------
# FACULTY SUMMARY
# --------------------------------------------------

st.subheader("👨‍🏫 Faculty Allocation Summary")

faculty_summary = []

for faculty in faculty_data:

    allocated = sum(
        1
        for student in students
        if student["faculty_id"] == faculty["id"]
    )

    remaining = faculty["capacity"] - allocated

    faculty_summary.append({
        "Faculty": faculty["name"],
        "Capacity": faculty["capacity"],
        "Allocated": allocated,
        "Remaining": remaining
    })

faculty_df = pd.DataFrame(faculty_summary)

st.dataframe(
    faculty_df,
    width="stretch",
    hide_index=True
)


st.divider()


# --------------------------------------------------
# STUDENT ALLOCATION REPORT
# --------------------------------------------------

st.subheader("👨‍🎓 Student Allocation Report")

search = st.text_input(
    "🔎 Search by Student Name or Registration Number"
)

display_df = student_df.copy()

if search:
    search_lower = search.lower()

    display_df = display_df[
        display_df["name"]
        .str.lower()
        .str.contains(search_lower, na=False)
        |
        display_df["registration_number"]
        .str.lower()
        .str.contains(search_lower, na=False)
    ]


display_df = display_df[
    [
        "name",
        "registration_number",
        "gender",
        "faculty_name",
        "status"
    ]
]

display_df = display_df.rename(
    columns={
        "name": "Student Name",
        "registration_number": "Registration Number",
        "gender": "Gender",
        "faculty_name": "Faculty",
        "status": "Status"
    }
)

st.dataframe(
    display_df,
    width="stretch",
    hide_index=True
)


# --------------------------------------------------
# EXCEL DOWNLOAD
# --------------------------------------------------

st.divider()

st.subheader("📥 Download Report")

excel_buffer = BytesIO()

with pd.ExcelWriter(
    excel_buffer,
    engine="openpyxl"
) as writer:

    faculty_df.to_excel(
        writer,
        index=False,
        sheet_name="Faculty Summary"
    )

    display_df.to_excel(
        writer,
        index=False,
        sheet_name="Student Allocations"
    )

st.download_button(
    label="📥 Download Excel Report",
    data=excel_buffer.getvalue(),
    file_name="faculty_allocation_report.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    width="stretch"
)

