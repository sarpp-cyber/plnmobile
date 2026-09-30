import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import math
import io
import random

st.set_page_config(page_title="PLN Mobile Review Generator", page_icon="⚡", layout="wide")

# Link Spreadsheet Anda
SPREADSHEET_ID = "1cfwLW6uTVc6KRAtV9aGadcN0NRWsDCutdtAf5AFRC-s"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=60)
def load_data():
    try:
        df = pd.read_csv(CSV_URL)
        df.columns = [c.strip().title() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Gagal memuat data dari Spreadsheet: {e}")
        return pd.DataFrame()

def draw_star(draw, center, size, color):
    cx, cy = center
    points = []
    for i in range(10):
        r = size if i % 2 == 0 else size / 2.5
        angle = i * math.pi / 5 - math.pi / 2
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        points.append((x, y))
    draw.polygon(points, fill=color)

def render_full_image(template_path, nama, tanggal, ulasan, rating):
    # Membuka gambar asli versi FULL (tanpa di-crop)
    img = Image.open(template_path).convert("RGBA")
    draw = ImageDraw.Draw(img)

    # 1. Bersihkan teks lama dengan warna background Play Store (#1b1b1b / RGB: 27, 27, 27)
    draw.rectangle([(120, 1280), (550, 1365)], fill=(27, 27, 27))
    draw.rectangle([(35, 1375), (600, 1515)], fill=(27, 27, 27))

    # 2. Font
    try:
        font_nama = ImageFont.truetype("LiberationSans-Bold.ttf", 25)
        font_info = ImageFont.truetype("LiberationSans-Regular.ttf", 20)
        font_ulasan = ImageFont.truetype("LiberationSans-Regular.ttf", 21)
    except IOError:
        try:
            font_nama = ImageFont.truetype("arialbd.ttf", 25)
            font_info = ImageFont.truetype("arial.ttf", 20)
            font_ulasan = ImageFont.truetype("arial.ttf", 21)
        except IOError:
            font_nama = font_info = font_ulasan = ImageFont.load_default()

    # 3. Gambar Nama
    draw.text((125, 1288), str(nama), fill="#FFFFFF", font=font_nama)

    # 4. Gambar Bintang & Tanggal
    start_x = 135
    y_star = 1335
    star_size = 9
    spacing = 22
    for i in range(int(rating)):
        draw_star(draw, (start_x + i * spacing, y_star), star_size, "#8ab4f8")
    
    draw.text((start_x + int(rating) * spacing + 12, 1324), str(tanggal), fill="#8ab4f8", font=font_info)

    # 5. Gambar Paragraf Ulasan (Auto-wrap)
    max_width = 540
    curr_y = 1385
    words = str(ulasan).split()
    lines = []
    curr_line = ""

    for w in words:
        test = f"{curr_line} {w}".strip()
        bbox = font_ulasan.getbbox(test)
        if (bbox[2] - bbox[0]) <= max_width:
            curr_line = test
        else:
            lines.append(curr_line)
            curr_line = w
    if curr_line:
        lines.append(curr_line)

    for line in lines[:4]:
        draw.text((40, curr_y), line, fill="#D0D0D0", font=font_ulasan)
        curr_y += 33

    return img.convert("RGB")


# --- TAMPILAN DASHBOARD ---
st.title("⚡ PLN Mobile - Review Generator")

df = load_data()
if df.empty:
    st.error("Data tidak ditemukan.")
    st.stop()

if "random_idx" not in st.session_state:
    st.session_state.random_idx = random.randint(0, len(df) - 1)

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Pengaturan Data")
    if st.button("🎲 Ambil Ulasan Acak (Random)", use_container_width=True):
        st.session_state.random_idx = random.randint(0, len(df) - 1)
        st.rerun()

    row = df.iloc[st.session_state.random_idx]

    nama = st.text_input("Nama Pengulas:", value=str(row.get("Nama", "")))
    tanggal = st.text_input("Tanggal:", value=str(row.get("Tanggal", "")))
    rating = st.slider("Rating Bintang:", 1, 5, int(row.get("Rating", 5)))
    ulasan = st.text_area("Teks Ulasan:", value=str(row.get("Ulasan", "")), height=140)

with col2:
    st.subheader("Preview Gambar Versi Penuh (Full)")
    # Path template screenshot original Anda
    template_path = "WhatsApp Image 2026-09-30 at 08.15.09.jpeg"
    
    hasil = render_full_image(template_path, nama, tanggal, ulasan, rating)
    st.image(hasil, use_container_width=True)

    buf = io.BytesIO()
    hasil.save(buf, format="PNG")
    st.download_button(
        "📥 Download Gambar Full (PNG)",
        data=buf.getvalue(),
        file_name=f"review_full_{nama.replace(' ', '_')}.png",
        mime="image/png",
        use_container_width=True
    )