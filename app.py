import streamlit as st
from PIL import Image
import requests
from io import BytesIO
import pyodbc


# URL of the image from the internet
IMAGE_URL = "https://uploadedpics.blob.core.windows.net/charts/b42ec2b0-b1a9-4059-8a9c-b5afea074e42"  # Replace with actual image URL

# Azure SQL Database connection settings
SERVER = 'jskdsdj458.database.windows.net'
DATABASE = 'zxncbzxcb'
USERNAME = 'sharvas45'
PASSWORD = 'Demo@123'
DRIVER = 'ODBC Driver 18 for SQL Server'  # Ensure installed



# Load image from the internet
def load_image(url):
    response = requests.get(url)
    return Image.open(BytesIO(response.content))

# Function to fetch a single integer from SQL
def fetch_integer_from_sql():
    try:
        
        conn = pyodbc.connect(
            f'DRIVER={DRIVER};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}'
        )
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) from [dbo].[ai_student_responses]")  # Replace with your query
        result = cursor.fetchone()[0]  # Get the first column of the first row
        conn.close()
        return result
    except Exception as e:
        st.error(f"Database query failed: {e}")
        return None

# Display the image
try:
    image = load_image(IMAGE_URL)
    st.image(image, caption="Fetched from Internet")
except Exception as e:
    st.error(f"Failed to load image: {e}")

# Display checkboxes A to P in a row
letters = [chr(i) for i in range(ord('A'), ord('P') + 1)]
cols = st.columns(len(letters))
selections = {}

for i, letter in enumerate(letters):
    with cols[i]:
        selections[letter] = st.checkbox(letter)

# Fetch and display integer result
st.markdown("### SQL Integer Result")
integer_result = fetch_integer_from_sql()
if integer_result is not None:
    st.metric(label="Total Rows in Table", value=integer_result)