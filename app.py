import streamlit as st
from PIL import Image
import imagehash
import cv2
import numpy as np

st.set_page_config(page_title="Distinct Image Detector", layout="wide")
st.title("🖼️ Distinct Image Detector (pHash + Blur Detection)")

st.markdown("""
Upload multiple images. This app will:
- Detect and remove **duplicate images** using perceptual hashing (pHash)
- Detect and remove **blurry images** using Laplacian variance
""")

def detect_blur(image, threshold=100):
    """Detect if an image is blurry using the Laplacian variance method."""
    gray = np.array(image.convert("L"))  # Convert to grayscale
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    return laplacian_var < threshold  # True if blurry

uploaded_files = st.file_uploader(
    "Upload images", type=["jpg", "jpeg", "png"], accept_multiple_files=True
)

if uploaded_files:
    images = []
    hashes = []
    duplicates_indices = set()
    blurry_indices = set()

    # Load images, check for blur, and compute pHash
    for i, file in enumerate(uploaded_files):
        img = Image.open(file).convert("RGB")
        if detect_blur(img):
            blurry_indices.add(i)
        images.append(img)
        img_hash = imagehash.phash(img)
        hashes.append(img_hash)

    # Detect duplicates
    threshold = 5  # Hamming distance threshold
    for i in range(len(hashes)):
        if i in blurry_indices:
            continue
        for j in range(i + 1, len(hashes)):
            if j in blurry_indices:
                continue
            if hashes[i] - hashes[j] <= threshold:
                duplicates_indices.add(j)

    # Filter distinct, non-blurry images
    distinct_images = [
        img for idx, img in enumerate(images)
        if idx not in duplicates_indices and idx not in blurry_indices
    ]

    st.write(f"📥 Uploaded {len(uploaded_files)} image(s).")
    st.write(f"🫣 Excluded {len(blurry_indices)} blurry image(s).")
    st.write(f"🧮 Found {len(distinct_images)} distinct, non-blurry image(s).")

    # Display the images
    for i, img in enumerate(distinct_images):
        st.image(img, width=250, caption=f"Distinct Image #{i + 1}")

else:
    st.info("Please upload images to begin.")
