import streamlit as st
from PIL import Image
import imagehash
import cv2
import numpy as np

st.set_page_config(page_title="Distinct Image Detector", layout="wide")
st.title("🖼️ Distinct Image Detector (pHash + Blur Detection)")

st.markdown("""
Upload multiple images, and this app will detect duplicates using perceptual hashing,
then show only the distinct and non-blurry images.
""")

def detect_blur(image, threshold=100):
    # Convert PIL image to grayscale OpenCV image
    open_cv_image = np.array(image.convert('L'))  # grayscale
    # Calculate the Laplacian variance
    laplacian_var = cv2.Laplacian(open_cv_image, cv2.CV_64F).var()
    return laplacian_var < threshold  # True if blurry

uploaded_files = st.file_uploader(
    "Upload images", type=["jpg", "jpeg", "png"], accept_multiple_files=True
)

if uploaded_files:
    images = []
    hashes = []
    duplicates_indices = set()
    blurry_indices = set()

    # Load images, detect blur and compute hashes
    for i, file in enumerate(uploaded_files):
        img = Image.open(file).convert("RGB")
        if detect_blur(img):
            blurry_indices.add(i)
        images.append(img)
        img_hash = imagehash.phash(img)
        hashes.append(img_hash)

    # Compare hashes pairwise and mark duplicates (only on non-blurry images)
    threshold = 5
    n = len(hashes)
    for i in range(n):
        if i in blurry_indices:
            continue
        for j in range(i + 1, n):
            if j in blurry_indices:
                continue
            if hashes[i] - hashes[j] <= threshold:
                duplicates_indices.add(j)

    # Filter distinct images excluding duplicates and blurry ones
    distinct_images = [
        img for idx, img in enumerate(images) 
        if idx not in duplicates_indices and idx not in blurry_indices
    ]

    st.write(f"Uploaded {len(uploaded_files)} images.")
    st.write(f"Excluded {len(blurry_indices)} blurry images.")
    st.write(f"Found {len(distinct_images)} distinct, non-blurry images after removing duplicates.")

    # Display distinct images with their hashes
    for i, img in enumerate(distinct_images):
        st.image(img, width=250, caption=f"Distinct Image #{i + 1}")

else:
    st.info("Upload one or more images to detect distinct ones and filter out blurry images.")
