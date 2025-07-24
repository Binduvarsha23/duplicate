import streamlit as st
from PIL import Image, ImageFilter
import imagehash
import numpy as np

st.set_page_config(page_title="Distinct Image Detector", layout="wide")
st.title("🖼️ Distinct Image Detector (pHash + Pillow Blur Detection)")

st.markdown("""
Upload multiple images. This app will:
- Detect and remove **duplicate images** using perceptual hashing (pHash)
- Detect and remove **blurry images** using edge variance (Pillow-based)
""")

def detect_blur_pillow(image, threshold=100):
    """Detect blur using edge variance (Pillow only)."""
    gray = image.convert("L")
    edges = gray.filter(ImageFilter.FIND_EDGES)
    variance = np.var(np.array(edges))
    return variance < threshold

blur_threshold = st.slider(
    "Blur detection threshold (lower = stricter)", min_value=5, max_value=500, value=100
)

uploaded_files = st.file_uploader(
    "Upload images", type=["jpg", "jpeg", "png"], accept_multiple_files=True
)

if uploaded_files:
    images = []
    hashes = []
    duplicates_indices = set()
    blurry_indices = set()

    for i, file in enumerate(uploaded_files):
        img = Image.open(file).convert("RGB")
        if detect_blur_pillow(img, threshold=blur_threshold):
            blurry_indices.add(i)
        images.append(img)
        hashes.append(imagehash.phash(img))

    threshold = 5  # hamming distance for pHash
    for i in range(len(hashes)):
        if i in blurry_indices:
            continue
        for j in range(i + 1, len(hashes)):
            if j in blurry_indices:
                continue
            if hashes[i] - hashes[j] <= threshold:
                duplicates_indices.add(j)

    distinct_images = [
        img for idx, img in enumerate(images)
        if idx not in duplicates_indices and idx not in blurry_indices
    ]

    st.write(f"📥 Uploaded: {len(uploaded_files)} image(s)")
    st.write(f"🫣 Blurry images removed: {len(blurry_indices)}")
    st.write(f"🧮 Distinct non-blurry images: {len(distinct_images)}")

    for i, img in enumerate(distinct_images):
        st.image(img, width=250, caption=f"Distinct Image #{i + 1}")
else:
    st.info("Please upload images to begin.")
