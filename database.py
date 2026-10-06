import sqlite3

# --------------------------------------------------
# CONNECT TO DATABASE
# --------------------------------------------------

connection = sqlite3.connect("faculty_allocation.db")
cursor = connection.cursor()


# --------------------------------------------------
# ADD REGISTRATION NUMBER COLUMN
# --------------------------------------------------

try:
    cursor.execute("""
        ALTER TABLE students
        ADD COLUMN registration_number TEXT
    """)
except sqlite3.OperationalError:
    pass


# --------------------------------------------------
# ADD GENDER COLUMN
# --------------------------------------------------

try:
    cursor.execute("""
        ALTER TABLE students
        ADD COLUMN gender TEXT
    """)
except sqlite3.OperationalError:
    pass


# --------------------------------------------------
# REGISTRATION NUMBERS
# --------------------------------------------------

registration_numbers = [
    "7376257MB101",
    "7376257MB102",
    "7376257MB104",
    "7376257MB105",
    "7376257MB106",
    "7376257MB107",
    "7376257MB108",
    "7376257MB109",
    "7376257MB110",
    "7376257MB111",
    "7376257MB112",
    "7376257MB113",
    "7376257MB114",
    "7376257MB115",
    "7376257MB116",
    "7376257MB117",
    "7376257MB118",
    "7376257MB119",
    "7376257MB120",
    "7376257MB121",
    "7376257MB122",
    "7376257MB123",
    "7376257MB125",
    "7376257MB126",
    "7376257MB127",
    "7376257MB128",
    "7376257MB129",
    "7376257MB130",
    "7376257MB131",
    "7376257MB132",
    "7376257MB133",
    "7376257MB134",
    "7376257MB135",
    "7376257MB136",
    "7376257MB137",
    "7376257MB138",
    "7376257MB139",
    "7376257MB141",
    "7376257MB142",
    "7376257MB143",
    "7376257MB144",
    "7376257MB145",
    "7376257MB146",
    "7376257MB147"
]


# --------------------------------------------------
# GET STUDENTS IN ID ORDER
# --------------------------------------------------

cursor.execute("""
    SELECT id
    FROM students
    ORDER BY id
""")

student_ids = cursor.fetchall()


# --------------------------------------------------
# ADD REGISTRATION NUMBERS
# --------------------------------------------------

for student, registration_number in zip(
    student_ids,
    registration_numbers
):

    cursor.execute("""
        UPDATE students
        SET registration_number = ?
        WHERE id = ?
    """, (
        registration_number,
        student[0]
    ))


# --------------------------------------------------
# ADD NEW FACULTY
# --------------------------------------------------

try:

    cursor.execute("""
        INSERT INTO faculty (name, capacity)
        VALUES (?, ?)
    """, (
        "Prof. Saranya S",
        5
    ))

    print(
        "Prof. Saranya S added successfully "
        "with capacity 5."
    )

except sqlite3.IntegrityError:

    print(
        "Prof. Saranya S already exists. "
        "No duplicate added."
    )


# --------------------------------------------------
# SET FACULTY CAPACITIES
# --------------------------------------------------

# All faculties have 5 seats by default
cursor.execute("""
    UPDATE faculty
    SET capacity = 5
""")


# Prof. Suganesh S has 4 seats
cursor.execute("""
    UPDATE faculty
    SET capacity = 4
    WHERE name = ?
""", (
    "Prof. Suganesh S",
))

# --------------------------------------------------
# SAVE CHANGES
# --------------------------------------------------

connection.commit()


# --------------------------------------------------
# DISPLAY FINAL FACULTY CAPACITY
# --------------------------------------------------

cursor.execute("""
    SELECT id, name, capacity
    FROM faculty
    ORDER BY id
""")

faculties = cursor.fetchall()

print("\nFaculty Capacity:")
print("-" * 45)

for faculty in faculties:

    print(
        f"{faculty[0]}. "
        f"{faculty[1]} - "
        f"{faculty[2]} seats"
    )

print("-" * 45)

total_capacity = sum(
    faculty[2]
    for faculty in faculties
)

print(f"Total Faculty Capacity: {total_capacity}")
print("Database updated successfully!")


# --------------------------------------------------
# CLOSE DATABASE
# --------------------------------------------------

connection.close()