import streamlit as st
from supabase import create_client, Client


# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Faculty Allocation System",
    page_icon="🎓",
    layout="centered"
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
# PAGE TITLE
# --------------------------------------------------

st.title("🎓 Faculty Allocation System")
st.subheader("Student Faculty Preference Portal")

st.write(
    "Select your name, verify your details, choose your faculty preference, "
    "and confirm your selection."
)


# --------------------------------------------------
# FETCH STUDENTS
# --------------------------------------------------

student_response = (
    supabase
    .table("students")
    .select(
        "id, name, registration_number, gender, faculty_id"
    )
    .order("name")
    .execute()
)

students = student_response.data

if not students:
    st.error("No student records found.")
    st.stop()


# --------------------------------------------------
# STUDENT SELECTION
# --------------------------------------------------

st.header("👨‍🎓 Student Details")

student_names = [
    student["name"]
    for student in students
]

selected_name = st.selectbox(
    "Select your name",
    student_names
)

selected_student_data = next(
    student
    for student in students
    if student["name"] == selected_name
)


# --------------------------------------------------
# CHECK IF ALREADY ALLOCATED
# --------------------------------------------------

if selected_student_data["faculty_id"] is not None:

    faculty_response = (
        supabase
        .table("faculty")
        .select("id, name")
        .eq(
            "id",
            selected_student_data["faculty_id"]
        )
        .execute()
    )

    allocated_faculty = (
        faculty_response.data[0]["name"]
        if faculty_response.data
        else "Unknown Faculty"
    )

    st.warning(
        f"You have already been allocated to **{allocated_faculty}**."
    )

    st.info(
        "Faculty allocation cannot be changed once confirmed."
    )

    st.stop()


# --------------------------------------------------
# REGISTRATION NUMBER
# --------------------------------------------------

st.text_input(
    "Registration Number",
    value=selected_student_data["registration_number"] or "",
    disabled=True
)


# --------------------------------------------------
# GENDER
# --------------------------------------------------

gender = st.selectbox(
    "Gender",
    [
        "Select Gender",
        "Male",
        "Female"
    ]
)


# --------------------------------------------------
# FETCH FACULTY DATA
# --------------------------------------------------

faculty_response = (
    supabase
    .table("faculty")
    .select("id, name, capacity")
    .order("id")
    .execute()
)

faculty_data = faculty_response.data


# --------------------------------------------------
# CALCULATE FACULTY AVAILABILITY
# --------------------------------------------------

allocated_response = (
    supabase
    .table("students")
    .select("faculty_id")
    .not_.is_("faculty_id", "null")
    .execute()
)

allocated_students = allocated_response.data

allocation_counts = {}

for student in allocated_students:

    faculty_id = student["faculty_id"]

    allocation_counts[faculty_id] = (
        allocation_counts.get(faculty_id, 0) + 1
    )


available_faculties = []

for faculty in faculty_data:

    allocated = allocation_counts.get(
        faculty["id"],
        0
    )

    remaining = faculty["capacity"] - allocated

    if remaining > 0:

        available_faculties.append({
            "id": faculty["id"],
            "name": faculty["name"],
            "capacity": faculty["capacity"],
            "allocated": allocated,
            "remaining": remaining
        })


# --------------------------------------------------
# FACULTY PREFERENCE
# --------------------------------------------------

st.header("👨‍🏫 Faculty Preference")

if not available_faculties:

    st.error(
        "All faculty seats have been filled."
    )

    st.stop()


faculty_options = [
    faculty["name"]
    for faculty in available_faculties
]

selected_faculty_name = st.selectbox(
    "Select your preferred faculty",
    faculty_options
)

selected_faculty = next(
    faculty
    for faculty in available_faculties
    if faculty["name"] == selected_faculty_name
)

selected_faculty_id = selected_faculty["id"]

st.info(
    f"Available seats: **{selected_faculty['remaining']}**"
)


# --------------------------------------------------
# CONFIRM SELECTION
# --------------------------------------------------

st.header("✅ Confirm Selection")

st.write(
    f"**Student:** {selected_student_data['name']}"
)

st.write(
    f"**Registration Number:** "
    f"{selected_student_data['registration_number']}"
)

st.write(
    f"**Gender:** "
    f"{gender if gender != 'Select Gender' else 'Not selected'}"
)

st.write(
    f"**Faculty:** {selected_faculty_name}"
)

confirm = st.button(
    "Confirm Selection",
    width="stretch"
)


# --------------------------------------------------
# ALLOCATION
# --------------------------------------------------

if confirm:

    if gender == "Select Gender":

        st.error(
            "Please select your gender before confirming."
        )

        st.stop()


    # --------------------------------------------------
    # SAFE TRANSACTION-SAFE ALLOCATION
    # --------------------------------------------------

    allocation_response = supabase.rpc(
        "allocate_faculty",
        {
            "p_student_id": selected_student_data["id"],
            "p_faculty_id": selected_faculty_id,
            "p_gender": gender
        }
    ).execute()

    result = allocation_response.data


    if result and result.get("success"):

        st.success(
            "Faculty allocated successfully! 🎉"
        )

        st.balloons()

        st.divider()

        st.subheader("🎓 Allocation Details")

        st.write(
            f"**Student Name:** "
            f"{selected_student_data['name']}"
        )

        st.write(
            f"**Registration Number:** "
            f"{selected_student_data['registration_number']}"
        )

        st.write(
            f"**Gender:** {gender}"
        )

        st.write(
            f"**Faculty:** {selected_faculty_name}"
        )

        st.info(
            "Your faculty allocation has been recorded successfully."
        )


        # --------------------------------------------------
        # REFRESH FACULTY AVAILABILITY
        # --------------------------------------------------

        updated_allocated_response = (
            supabase
            .table("students")
            .select("faculty_id")
            .not_.is_("faculty_id", "null")
            .execute()
        )

        updated_counts = {}

        for student in updated_allocated_response.data:

            faculty_id = student["faculty_id"]

            updated_counts[faculty_id] = (
                updated_counts.get(faculty_id, 0) + 1
            )


        st.subheader("📊 Current Faculty Availability")

        for faculty in faculty_data:

            allocated = updated_counts.get(
                faculty["id"],
                0
            )

            remaining = (
                faculty["capacity"] - allocated
            )

            st.write(
                f"**{faculty['name']}** — "
                f"{allocated}/{faculty['capacity']} allocated "
                f"| {remaining} remaining"
            )


    else:

        message = (
            result.get("message")
            if result
            else "Unable to complete the allocation."
        )

        st.error(
            f"❌ {message}"
        )


# --------------------------------------------------
# FACULTY AVAILABILITY
# --------------------------------------------------

st.divider()

st.header("📊 Faculty Availability")

for faculty in available_faculties:

    allocated = allocation_counts.get(
        faculty["id"],
        0
    )

    remaining = faculty["capacity"] - allocated

    st.write(
        f"**{faculty['name']}** — "
        f"{allocated}/{faculty['capacity']} allocated "
        f"| {remaining} remaining"
    )