import streamlit as st
from PIL import Image
import imagehash

st.set_page_config(page_title="Distinct Image Detector", layout="wide")
st.title("🖼️ Distinct Image Detector (pHash)")

st.markdown("""
Upload multiple images, and this app will detect duplicates using perceptual hashing,
then show only the distinct images.
""")

uploaded_files = st.file_uploader(
    "Upload images", type=["jpg", "jpeg", "png"], accept_multiple_files=True
)

if uploaded_files:
    images = []
    hashes = []
    duplicates_indices = set()

    # Load images and compute hashes
    for i, file in enumerate(uploaded_files):
        img = Image.open(file).convert("RGB")
        images.append(img)
        img_hash = imagehash.phash(img)
        hashes.append(img_hash)

    # Compare hashes pairwise and mark duplicates
    threshold = 5
    n = len(hashes)
    for i in range(n):
        for j in range(i + 1, n):
            if hashes[i] - hashes[j] <= threshold:
                duplicates_indices.add(j)

    # Filter distinct images
    distinct_images = [img for idx, img in enumerate(images) if idx not in duplicates_indices]

    st.write(f"Uploaded {len(uploaded_files)} images.")
    st.write(f"Found {len(distinct_images)} distinct images after removing duplicates.")

    # Display distinct images with their hashes
    for i, img in enumerate(distinct_images):
        st.image(img, width=250, caption=f"Distinct Image #{i + 1}")

else:
    st.info("Upload one or more images to detect distinct ones.")
