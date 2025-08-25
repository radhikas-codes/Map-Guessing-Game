import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import streamlit as st

# ---------- Page setup ----------
st.set_page_config(page_title="Map Guessing Game", page_icon="🌍", layout="wide")

# ---------- Map Configurations ----------
MAPS = {
    "US States": {"csv": "50_states.csv", "image": "blank_states_img.gif"},
    "Indian States": {"csv": "indian_states.csv", "image": "indian_states_map.gif"},
    "European Countries": {"csv": "europe_map.csv", "image": "europe_map.gif"},
    "South American Countries": {"csv": "south_america_countries.csv", "image": "south_america_map.gif"},
}

# ---------- Helpers ----------
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["name_norm"] = df["name"].astype(str).str.strip().str.title()
    return df

@st.cache_resource
def load_image(path: str) -> Image.Image:
    return Image.open(path).convert("RGBA")

def turtle_to_pixel(x: float, y: float, width: int, height: int) -> tuple[int, int]:
    px = int(round(x + width / 2))
    py = int(round(height / 2 - y))
    return px, py

def render_map_with_labels(guessed_names: list[str], df: pd.DataFrame, base_img: Image.Image) -> Image.Image:
    img = base_img.copy()
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    for name in guessed_names:
        row = df[df["name_norm"] == name].iloc[0]
        x, y = float(row["x"]), float(row["y"])
        px, py = turtle_to_pixel(x, y, img.width, img.height)
        text = row["name"]
        tw, th = draw.textbbox((0, 0), text, font=font)[2:]
        draw.text((px - tw/2, py - th/2), text, fill=(0, 0, 0, 255), font=font)

    return img

# ---------- UI ----------
st.title("🌍 Map Guessing Game")

# Select which map to play
map_choice = st.selectbox("Choose a map:", list(MAPS.keys()))

# Load data for selected map
df = load_data(MAPS[map_choice]["csv"])
all_names = set(df["name_norm"].tolist())
TOTAL = len(all_names)

# ---------- Session state handling ----------
if "map_choice" not in st.session_state:
    # First run, initialize
    st.session_state.map_choice = map_choice
    st.session_state.guessed = []
    st.session_state.current_guess = ""
elif st.session_state.map_choice != map_choice:
    # Reset only if user changes map
    st.session_state.map_choice = map_choice
    st.session_state.guessed = []
    st.session_state.current_guess = ""

guessed = st.session_state.guessed
base_img = load_image(MAPS[map_choice]["image"])

# --- Layout with two columns ---
col1, col2 = st.columns([3, 1])  # left wider, right narrower

with col1:
    st.subheader(f"{map_choice}: {len(guessed)}/{TOTAL} guessed")
    st.progress(len(guessed) / TOTAL)

    map_img = render_map_with_labels(guessed, df, base_img)
    st.image(map_img, caption=f"Guess the {map_choice.lower()}!", use_container_width=True)

with col2:
    st.write("### Your Guess")

    # Function runs immediately when user presses Enter
    def handle_guess():
        guess = st.session_state.current_guess.strip().title()
        if guess in all_names:
            if guess not in guessed:
                guessed.append(guess)
                st.session_state.guessed = guessed
                st.success(f"✅ Correct! {guess}")
            else:
                st.info(f"ℹ️ Already guessed {guess}")
        elif guess:
            st.error(f"❌ '{guess}' is not valid in {map_choice}")
        st.session_state.current_guess = ""  # clear box after submit

    st.text_input(
        "Enter name:",
        key="current_guess",
        on_change=handle_guess,
        placeholder="Type here and press Enter"
    )

# --- Bottom buttons ---
colb1, colb2, colb3 = st.columns(3)
missing = sorted(list(all_names - set(guessed)))
missing_df = pd.DataFrame(missing, columns=["name"])
csv_bytes = missing_df.to_csv(index=False).encode("utf-8")

with colb1:
    if st.button("Reset game"):
        st.session_state.guessed = []
        st.rerun()

with colb2:
    st.download_button("Download missing.csv", data=csv_bytes, file_name="missing.csv", mime="text/csv")

with colb3:
    if len(guessed) == TOTAL:
        st.success("🎉 You completed this map!")
