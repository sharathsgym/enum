import streamlit as st
from PIL import Image
import requests
from io import BytesIO

# URL of the image from the internet
IMAGE_URL = "https://uploadedpics.blob.core.windows.net/charts/b42ec2b0-b1a9-4059-8a9c-b5afea074e42"  # Replace with actual image URL

# Load image from the internet
def load_image(url):
    response = requests.get(url)
    return Image.open(BytesIO(response.content))


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

