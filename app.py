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

def detect_blur_pillow(image, threshold=20):
    """Detect blur using edge variance (Pillow only). Lower variance = more blurry."""
    edges = image.filter(ImageFilter.FIND_EDGES).convert("L")
    variance = np.var(np.array(edges))
    return variance < threshold

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
        if detect_blur_pillow(img):
            blurry_indices.add(i)
        images.append(img)
        hashes.append(imagehash.phash(img))

    # Detect duplicates using pHash
    threshold = 5
    for i in range(len(hashes)):
        if i in blurry_indices:
            continue
        for j in range(i + 1, len(hashes)):
            if j in blurry_indices:
                continue
            if hashes[i] - hashes[j] <= threshold:
                duplicates_indices.add(j)

    # Keep only distinct, non-blurry images
    distinct_images = [
        img for idx, img in enumerate(images)
        if idx not in duplicates_indices and idx not in blurry_indices
    ]

    st.write(f"📥 Uploaded {len(uploaded_files)} image(s).")
    st.write(f"🫣 Excluded {len(blurry_indices)} blurry image(s).")
    st.write(f"🧮 Found {len(distinct_images)} distinct, non-blurry image(s).")

    for i, img in enumerate(distinct_images):
        st.image(img, width=250, caption=f"Distinct Image #{i + 1}")

else:
    st.info("Please upload images to begin.")
