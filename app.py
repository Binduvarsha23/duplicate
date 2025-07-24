import streamlit as st
from PIL import Image
import imagehash
import numpy as np
import cv2
import matplotlib.pyplot as plt
import io

# Constants
BLUR_THRESHOLD = 100
PHASH_THRESHOLD = 5

st.set_page_config(page_title="Distinct & Non-Blurry Image Detector", layout="wide")
st.title("🖼️ Distinct & Non-Blurry Image Detector")

st.markdown("""
Upload multiple images, the app will:
- Remove blurry images (using OpenCV Laplacian)
- Remove duplicates (using perceptual hashing)
- Display only distinct, non-blurry images
""")

uploaded_files = st.file_uploader(
    "Upload images", type=["jpg", "jpeg", "png"], accept_multiple_files=True
)

def is_blurry(image):
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    lap_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    return lap_var < BLUR_THRESHOLD

if uploaded_files:
    images = []
    filenames = []
    blurry_indices = set()
    duplicate_indices = set()

    # Load images and filenames
    for file in uploaded_files:
        try:
            img = Image.open(file).convert("RGB")
            images.append(img)
            filenames.append(file.name)
        except Exception as e:
            st.warning(f"Could not load {file.name}: {e}")

    if not images:
        st.error("No valid images loaded.")
        st.stop()

    # Detect blurry images
    for i, img in enumerate(images):
        if is_blurry(img):
            blurry_indices.add(i)

    # Detect duplicates
    for i in range(len(images)):
        if i in blurry_indices:
            continue
        for j in range(i + 1, len(images)):
            if j in blurry_indices:
                continue
            if imagehash.phash(images[i]) - imagehash.phash(images[j]) <= PHASH_THRESHOLD:
                duplicate_indices.add(j)

    # Filter distinct, non-blurry
    final_indices = [
        i for i in range(len(images)) 
        if i not in blurry_indices and i not in duplicate_indices
    ]

    st.write(f"Uploaded {len(images)} images.")
    st.write(f"Removed {len(blurry_indices)} blurry images.")
    st.write(f"Removed {len(duplicate_indices)} duplicate images.")
    st.write(f"Displaying {len(final_indices)} distinct, non-blurry images.")

    # Display results in grid
    cols = st.columns(4)
    for idx, i in enumerate(final_indices):
        with cols[idx % 4]:
            st.image(images[i], caption=filenames[i], use_column_width=True)
else:
    st.info("Upload one or more images to get started.")
