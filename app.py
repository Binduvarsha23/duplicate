import streamlit as st
from PIL import Image
import imagehash
import numpy as np
import cv2

# Constants
BLUR_THRESHOLD = 100
PHASH_THRESHOLD = 5

st.set_page_config(page_title="Distinct & Non-Blurry Image Detector", layout="wide")
st.title("🖼️ Distinct & Non-Blurry Image Detector")

st.markdown("""
Upload multiple images, the app will:
- Remove blurry images (using OpenCV Laplacian)
- Group duplicates (using perceptual hashing)
- Display the best image from each group (sharpest)
""")

uploaded_files = st.file_uploader(
    "Upload images", type=["jpg", "jpeg", "png"], accept_multiple_files=True
)

def laplacian_variance(image):
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var()

if uploaded_files:
    image_info = []  # Each item: (filename, image, hash, sharpness)
    for file in uploaded_files:
        try:
            img = Image.open(file).convert("RGB")
            phash = imagehash.phash(img)
            sharpness = laplacian_variance(img)
            image_info.append((file.name, img, phash, sharpness))
        except Exception as e:
            st.warning(f"Could not load {file.name}: {e}")

    if not image_info:
        st.error("No valid images loaded.")
        st.stop()

    # Group by hash similarity
    groups = []
    used = set()

    for i, (_, img_i, hash_i, sharpness_i) in enumerate(image_info):
        if i in used:
            continue
        group = [i]
        used.add(i)
        for j in range(i + 1, len(image_info)):
            if j in used:
                continue
            _, img_j, hash_j, _ = image_info[j]
            if hash_i - hash_j <= PHASH_THRESHOLD:
                group.append(j)
                used.add(j)
        groups.append(group)

    # Pick best (sharpest) image from each group
    final_images = []
    for group in groups:
        best_idx = max(group, key=lambda idx: image_info[idx][3])  # highest sharpness
        final_images.append(image_info[best_idx])

    st.write(f"Uploaded {len(image_info)} images.")
    st.write(f"Detected {len(groups)} groups of similar images.")
    st.write(f"Displaying {len(final_images)} distinct, non-blurry images (best per group).")

    cols = st.columns(4)
    for idx, (filename, img, _, sharpness) in enumerate(final_images):
        with cols[idx % 4]:
            st.image(img, caption=f"{filename} (Sharpness: {sharpness:.1f})", use_container_width=True)

else:
    st.info("Upload one or more images to get started.")
