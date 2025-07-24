import streamlit as st
from PIL import Image
import imagehash

# Set page config
st.set_page_config(page_title="Image Duplicate Checker", layout="centered")

st.title("🔍 Image Duplicate Detector (pHash)")

st.markdown("""
Upload two images to check if they are duplicates or near-duplicates using **perceptual hashing**.
""")

# Upload images
img1_file = st.file_uploader("Upload Image 1", type=["jpg", "jpeg", "png"], key="img1")
img2_file = st.file_uploader("Upload Image 2", type=["jpg", "jpeg", "png"], key="img2")

if img1_file and img2_file:
    # Load and display images
    img1 = Image.open(img1_file).convert("RGB")
    img2 = Image.open(img2_file).convert("RGB")

    st.image([img1, img2], caption=["Image 1", "Image 2"], width=300)

    # Compute perceptual hashes
    hash1 = imagehash.phash(img1)
    hash2 = imagehash.phash(img2)
    distance = hash1 - hash2

    st.markdown(f"**Hash 1:** `{hash1}`")
    st.markdown(f"**Hash 2:** `{hash2}`")
    st.markdown(f"**Hamming Distance:** `{distance}`")

    # Determine duplicate status
    threshold = 5  # adjustable
    if distance <= threshold:
        st.success("✅ These images are near-duplicates!")
    else:
        st.error("❌ These images are not duplicates.")
else:
    st.info("👆 Upload two images above to begin.")
