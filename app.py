import streamlit as st
from PIL import Image, ImageOps, ImageEnhance
import io

# Professional Page Setup
st.set_page_config(page_title="Image Processing Utility", layout="wide")

# Enterprise CSS - Minimalist & Clean
st.markdown("""
    <style>
    /* Professional Dark Theme */
    .main { background-color: #0d1117; color: #adbac7; }
    
    /* Input Containers */
    div[data-testid="stColumn"] {
        background-color: #1c2128;
        padding: 24px;
        border-radius: 4px;
        border: 1px solid #444c56;
    }

    /* Standardized Text */
    h1, h2, h3 { color: #f0f6fc !important; font-family: 'Inter', sans-serif; }
    
    /* Professional Button - No Gradients */
    .stButton>button {
        width: 100%;
        background-color: #2da44e;
        color: white;
        border: 1px solid rgba(27, 31, 36, 0.15);
        border-radius: 6px;
        font-weight: 500;
        height: 3rem;
    }
    
    .stButton>button:hover {
        background-color: #2c974b;
        border-color: rgba(27, 31, 36, 0.15);
    }

    /* Hide unnecessary UI elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

st.title("Image Optimization Portal")
st.markdown("Strict adherence to dimension and file size specifications.")
st.divider()

# Mode Selection - Plain Text
mode = st.radio("Select Processing Mode", ["Passport Photo", "Signature", "Document"], horizontal=True)

uploaded_file = st.file_uploader("Upload File", type=["jpg", "jpeg", "png"])

if uploaded_file:
    img = Image.open(uploaded_file).convert("RGB")
    
    col1, col2 = st.columns([1, 1.5], gap="large")

    with col1:
        st.subheader("Configuration")
        
        # Dimension Controls
        if mode == "Passport Photo":
            target_w = st.number_input("Width (px)", value=160)
            target_h = st.number_input("Height (px)", value=210)
            d_min, d_max = 20, 50
        elif mode == "Signature":
            target_w = st.number_input("Width (px)", value=256)
            target_h = st.number_input("Height (px)", value=64)
            d_min, d_max = 10, 20
        else:
            target_w = st.number_input("Width (px)", value=img.width)
            target_h = st.number_input("Height (px)", value=img.height)
            d_min, d_max = 100, 500

        # File Size Guard
        st.markdown("---")
        min_kb = st.number_input("Minimum File Size (KB)", value=d_min)
        max_kb = st.number_input("Maximum File Size (KB)", value=d_max)
        
        # Feature-specific adjustments
        if mode == "Signature":
            ink_color = st.selectbox("Ink Format", ["Blue", "Black"])
            sharpness_val = st.slider("Threshold Level", 0, 255, 140)
        elif mode == "Document":
            format_type = st.selectbox("Export Format", ["JPEG", "PDF"])

    with col2:
        st.subheader("Technical Preview")
        
        # Engine Logic
        if mode == "Signature":
            gray = img.convert("L")
            fn = lambda x : 255 if x > sharpness_val else 0
            bw_mask = gray.point(fn, mode='1').convert("L")
            if ink_color == "Blue":
                blue_ink = Image.new("RGB", bw_mask.size, (0, 56, 175))
                white_bg = Image.new("RGB", bw_mask.size, (255, 255, 255))
                processed_img = Image.composite(white_bg, blue_ink, bw_mask)
            else:
                processed_img = bw_mask.convert("RGB")
        else:
            processed_img = ImageOps.autocontrast(img)

        # High-Fidelity Resizing
        processed_img = processed_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
        st.image(processed_img, width=target_w if mode != "Document" else 500)

    # Execution and Export
    if st.button("Process Image"):
        output_io = io.BytesIO()
        ext = "PDF" if (mode == "Document" and format_type == "PDF") else "JPEG"
        
        # Try High-Quality first
        processed_img.save(output_io, format="JPEG" if ext == "PDF" else ext, quality=100, subsampling=0, optimize=True)
        
        # Reduction Loop
        if output_io.tell() / 1024 > max_kb:
            for q in range(99, 5, -1):
                temp_io = io.BytesIO()
                processed_img.save(temp_io, format="JPEG", quality=q, optimize=True)
                if temp_io.tell() / 1024 <= max_kb:
                    output_io = temp_io
                    break
        
        # Inflation Logic (Forcing Min KB)
        if output_io.tell() / 1024 < min_kb:
            output_io = io.BytesIO()
            processed_img.save(output_io, format="JPEG", quality=100, dpi=(600, 600), optimize=False)

        final_kb = output_io.tell() / 1024
        st.info(f"Generated File Size: {final_kb:.2f} KB")
        st.download_button("Download Processed File", output_io.getvalue(), f"processed_file.{ext.lower()}")