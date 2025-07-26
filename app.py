import streamlit as st
from PIL import Image
import imagehash
import numpy as np
import cv2
from collections import defaultdict

# Constants
BLUR_THRESHOLD = 100
PHASH_THRESHOLD = 5

st.set_page_config(page_title="Exact Duplicates (Non-Blurry)", layout="wide")
st.title("🖼️ Show Only Non-Unique Duplicate Images")

st.markdown("""
Upload multiple images, and this app will:
- Remove blurry images
- Detect duplicate images (using perceptual hash)
- **Only display images that are non-blurry and appear in duplicate groups**
""")

uploaded_files = st.file_uploader(
    "Upload images", type=["jpg", "jpeg", "png"], accept_multiple_files=True
)

def laplacian_variance(image):
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var()

if uploaded_files:
    image_data = []  # (filename, image, phash, sharpness)

    # Load and filter non-blurry images
    for file in uploaded_files:
        try:
            img = Image.open(file).convert("RGB")
            sharpness = laplacian_variance(img)
            if sharpness >= BLUR_THRESHOLD:
                phash = imagehash.phash(img)
                image_data.append((file.name, img, phash, sharpness))
        except Exception as e:
            st.warning(f"Could not load {file.name}: {e}")

    if not image_data:
        st.error("No non-blurry images found.")
        st.stop()

    # Group images by perceptual hash (allowing threshold similarity)
    hash_groups = defaultdict(list)
    used = [False] * len(image_data)

    for i, (_, _, hash_i, _) in enumerate(image_data):
        if used[i]:
            continue
        group = [i]
        used[i] = True
        for j in range(i + 1, len(image_data)):
            if not used[j] and hash_i - image_data[j][2] <= PHASH_THRESHOLD:
                group.append(j)
                used[j] = True
        if len(group) > 1:
            hash_groups[i] = group  # only store groups with duplicates

    # Flatten all duplicate indices
    duplicate_indices = sorted(set(idx for group in hash_groups.values() for idx in group))

    if not duplicate_indices:
        st.success("No duplicate (non-blurry) images found.")
    else:
        st.warning(f"Found {len(duplicate_indices)} duplicate non-unique images:")
        cols = st.columns(4)
        for idx, i in enumerate(duplicate_indices):
            filename, img, _, sharpness = image_data[i]
            with cols[idx % 4]:
                st.image(img, caption=f"{filename} (Sharpness: {sharpness:.1f})", use_container_width=True)
else:
    st.info("Upload multiple images to find duplicate non-unique ones.")
