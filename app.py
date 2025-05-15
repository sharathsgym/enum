import streamlit as st
from PIL import Image
import requests
from io import BytesIO
import pyodbc
import uuid


# URL of the image from the internet
IMAGE_URL = "https://uploadedpics.blob.core.windows.net/charts/b42ec2b0-b1a9-4059-8a9c-b5afea074e42"  # Replace with actual image URL

# Azure SQL Database connection settings
SERVER = 'jskdsdj458.database.windows.net'
DATABASE = 'zxncbzxcb'
USERNAME = 'sharvas45'
PASSWORD = 'Demo@123'
DRIVER = 'ODBC Driver 17 for SQL Server'  # Ensure installed

def clear_and_rerun():
    st.session_state.reset_counter += 1
    st.rerun()

def get_connection():
    if 'db_conn' not in st.session_state:
        st.session_state.db_conn = pyodbc.connect(
            f'DRIVER={DRIVER};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}')
    return st.session_state.db_conn

def close_connection():
    if 'db_conn' in st.session_state:
        st.session_state.db_conn.close()
        del st.session_state.db_conn

# Load image from the internet
def load_image(url):
    response = requests.get(url)
    return Image.open(BytesIO(response.content))

# Function to fetch a single integer from SQL
def fetch_integer_from_sql(school,program,cycle):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(f"""select count(student_id) from ai_student_levels where school = '{school}' and  program = '{program}' and cycle = '{cycle}'
                            and student_id not in (select student_id from ai_evaluator_Responses  where school = '{school}' and  program = '{program}' and cycle = '{cycle}')""")  # Replace with your query
        result = cursor.fetchone()[0]  # Get the first column of the first row
        return int(result)
    except Exception as e:
        st.error(f"Database query failed: {e}")
        return None
    
def next(school,program,cycle):
    try:
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(f"""select top (1) student_id, program,cycle,school,s_class,section,image_url from ai_student_levels where school = '{school}' and  program = '{program}' and cycle = '{cycle}'
                            and student_id not in (select student_id from ai_evaluator_Responses  where school = '{school}' and  program = '{program}' and cycle = '{cycle}')""")  # Replace with your query
        result = cursor.fetchone()  # Get the first column of the first row

        if result:
            studentid=result[0]
            s_class = result[4]
            s_section= result[5]
            image = result[6]
            return studentid,program,cycle,school,s_class,s_section,image
        else: 
            return None
    except Exception as e:
        st.error(f"Database query failed: {e}")
        return None    

# Initialize reset counter if not exists
if "reset_counter" not in st.session_state:
    st.session_state.reset_counter = 0

school = "EP Nyakabanda1"
program = "FM"
cycle = "End of Cycle 5"

st.header(f"""{school}-{program}-{cycle}""", divider="blue")
integer_result = fetch_integer_from_sql(school,program,cycle )

if integer_result ==0:
    st.metric(label="No Evaluations Pending!",value=0)
    exit()

studentid,program,cycle,school,s_class,s_section,image = next(school,program,cycle)

st.metric(label="Total Pending Evaluation", value=integer_result)
left_col, right_col = st.columns([7, 3]) # Adjust width ratios if needed

with left_col:
    try:
        image = load_image(image)
        st.image(image, caption=f"Student-{studentid}", width=500)
    except Exception as e:
        st.error(f"Failed to load image: {e}")

with right_col:
    st.markdown("### Expected Answers:")
    table_md = """
    | Q - A       | Q - A    | Q - A | Q - A |
    |-------------|----------|-------|-------|
    | A - 000000  | B - 0000 | C - 8 | D - 2 |
    | E - 17      | F - 19   | G - 4 | H - 3 |
    | I - 18      | J - 19   | K - 12| L - 22|
    | M - option 2| N - 33   | O - 55| P - 79|
    """
    st.markdown(table_md)
st.markdown(":red[***Check only correct answers below***]")

# Display checkboxes A to P in a row
letters = [chr(i) for i in range(ord('A'), ord('P') + 1)]
cols_per_row = 4
selections = {}

cols = st.columns(4)
selections = {}

reset_id = st.session_state.reset_counter
for idx, letter in enumerate(letters):
    with cols[idx % 4]:
        subcols = st.columns([1, 3])  # Left for label, right for checkbox
        with subcols[0]:
            st.markdown(f"**{letter}**", unsafe_allow_html=True)
        with subcols[1]:
            selections[letter] = st.checkbox("", key=f"""{letter}_{reset_id}""", value=True)
            
              
if st.button("Submit"):
    selected_letters = [k for k, v in selections.items() if v]
    unselected_letters = [k for k, v in selections.items() if not v]

    try:
        conn = get_connection()
        cursor = conn.cursor()
        st.markdown(selections)    # Insert selected options into the database

        query = """INSERT INTO [dbo].[ai_evaluator_Responses]
                    (student_id, question_no, evaluator_grading, program, cycle, school)
                    VALUES (?, ?, ?, ?, ?, ?)"""

        for letter in selected_letters:
            cursor.execute(query, (studentid, letter, 1, program, cycle, school))

        # Insert unchecked letters
        for letter in unselected_letters:
            cursor.execute(query, (studentid, letter, 0, program, cycle, school))

        conn.commit()
        st.success("Responses submitted successfully!")

        close_connection()    # Optionally, refresh the page or load next student
        clear_and_rerun()
    except Exception as e:
            st.error(f"Failed to submit responses: {e}")   