import streamlit as st
import random, math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import hsv_to_rgb, to_rgb
from io import BytesIO

# --- Shape Functions (from your code) ---

def blob(center=(0.5,0.5), r=0.3, points=200, wobble=0.15):
    """Generate a wobbly closed shape."""
    angles = np.linspace(0, 2*math.pi, points, endpoint=False)
    radii  = r * (1 + wobble*(np.random.rand(points)-0.5))
    x = center[0] + radii * np.cos(angles)
    y = center[1] + radii * np.sin(angles)
    return x, y

def heart(center=(0.5, 0.5), r=0.3, points=200, wobble=0.15):
    """Generate coordinates for a wobbly heart shape."""
    t = np.linspace(0, 2*math.pi, points, endpoint=False)
    base_x = 16 * np.sin(t)**3
    base_y = 13 * np.cos(t) - 5 * np.cos(2*t) - 2 * np.cos(3*t) - np.cos(4*t)
    x_norm = base_x / 16.0
    y_norm = base_y / 16.0
    wobble_factor = 1 + wobble*(np.random.rand(points)-0.5)
    x = center[0] + x_norm * r * wobble_factor
    y = center[1] + y_norm * r * wobble_factor
    return x, y

# --- Palette Function (from your code) ---

def make_palette(k=6, mode="pastel", base_h=0.60):
    """Simple palette generator (HSV pastel/vivid/mono)."""
    cols = []
    for _ in range(k):
        if mode == "pastel":
            h = random.random(); s = random.uniform(0.15,0.35); v = random.uniform(0.9,1.0)
        elif mode == "vivid":
            h = random.random(); s = random.uniform(0.8,1.0);  v = random.uniform(0.8,1.0)
        elif mode == "mono":
            h = base_h;       s = random.uniform(0.2,0.6);  v = random.uniform(0.5,1.0)
        else: # random
            h = random.random(); s = random.uniform(0.3,1.0); v = random.uniform(0.5,1.0)
        cols.append(tuple(hsv_to_rgb([h,s,v])))
    return cols

# --- Drawing Function 1: "Standard" (from your 1st script) ---
# (Modified to return a figure object)

def draw_poster_standard(n_layers, wobble, palette_mode, seed, shape, bg_color):
    """Main drawing function from your first script."""
    random.seed(seed); np.random.seed(seed)
    fig, ax = plt.subplots(figsize=(6,8))
    ax.axis('off')
    ax.set_facecolor(bg_color)

    palette = make_palette(6, mode=palette_mode)
    for _ in range(n_layers):
        cx, cy = random.random(), random.random()
        rr = random.uniform(0.15, 0.45)

        if shape == "heart":
            x, y = heart((cx,cy), r=rr, wobble=wobble)
        else:
            x, y = blob((cx,cy), r=rr, wobble=wobble)

        color = random.choice(palette)
        alpha = random.uniform(0.3, 0.6)
        ax.fill(x, y, color=color, alpha=alpha, edgecolor='none')

    ax.text(0.05, 0.95, f"Interactive Poster • {palette_mode} {shape.title()}",
            transform=ax.transAxes, fontsize=12, weight="bold")
    ax.set_xlim(0,1); ax.set_ylim(0,1)
    
    # Don't call plt.show(), just return the figure
    return fig

# --- Drawing Function 2: "Glowing" (from your 2nd script) ---
# (Modified to take parameters and return a figure object)

def draw_poster_glowing(n_layers, seed, shape, palette_mode, bg_color):
    """Generates a 3D-like poster with shadows and glowing pastel colors."""
    random.seed(seed); np.random.seed(seed)
    fig, ax = plt.subplots(figsize=(7,7))
    ax.axis('off')
    ax.set_facecolor(bg_color) 
    
    # We made palette_mode a parameter
    palette = make_palette(k=8, mode=palette_mode) 
    shapes_to_draw = []

    for depth in range(n_layers):
        cx, cy = random.random(), random.random()
        rr = random.uniform(0.15, 0.45)
        current_wobble = random.uniform(0.08, 0.20) # Wobble is randomized per-shape

        if shape == "heart":
            x, y = heart((cx,cy), r=rr, wobble=current_wobble)
        else: # 'blob'
            x, y = blob((cx,cy), r=rr, wobble=current_wobble)

        main_color = random.choice(palette)
        main_alpha = 0.5 + depth*0.08
        shapes_to_draw.append({
            'x': x, 'y': y,
            'main_color': main_color,
            'main_alpha': min(main_alpha, 1.0)
        })

    for i, s in enumerate(shapes_to_draw):
        x, y = s['x'], s['y']
        main_color = s['main_color']
        main_alpha = s['main_alpha']
        glow_alpha = 0.08 
        glow_offset = 0.008 
        ax.fill(x + glow_offset, y - glow_offset, color=main_color, alpha=glow_alpha, edgecolor='none')
        ax.fill(x - glow_offset, y + glow_offset, color=main_color, alpha=glow_alpha, edgecolor='none')
        
        shadow_color = (0.05, 0.05, 0.10) 
        ax.fill(x + 0.015, y - 0.015, color=shadow_color, alpha=0.20, edgecolor='none') 
        ax.fill(x, y, color=main_color, alpha=main_alpha, edgecolor='none')

    ax.set_xlim(0,1); ax.set_ylim(0,1)
    ax.set_title(f"3D-like Glowing Poster • {shape.title()}",
                 fontsize=14, weight="bold", color="white")
    
    # Don't call plt.show(), just return the figure
    return fig

# --- Streamlit UI (User Interface) ---

st.set_page_config(layout="wide")
st.title("Generative Poster App 🎨")
st.sidebar.title("Controls")

# 1. Main Style Selection
poster_style = st.sidebar.radio(
    "Select Poster Style",
    ("Standard", "Glowing"),
    help="Choose between the simple poster or the 3D-like glowing version."
)

st.sidebar.subheader("Common Settings")
# 2. Common Controls
shape = st.sidebar.selectbox("Shape", ["blob", "heart"], index=1 if poster_style == "Glowing" else 0)
n_layers = st.sidebar.slider("Number of Layers", 1, 30, 8)
palette_mode = st.sidebar.selectbox("Palette Mode", ["pastel", "vivid", "mono", "random"], index=0)

# 3. Seed / Reproducibility
st.sidebar.subheader("Layout Seed")
if 'seed' not in st.session_state:
    st.session_state.seed = random.randint(0, 10000)

if st.sidebar.button("New Random Layout"):
    st.session_state.seed = random.randint(0, 10000)

seed = st.sidebar.number_input("Current Seed", value=st.session_state.seed, step=1)
st.session_state.seed = seed

# 4. Conditional UI (Specific controls for each style)
if poster_style == "Standard":
    st.sidebar.subheader("Standard Style Controls")
    wobble = st.sidebar.slider("Wobble", 0.01, 0.3, 0.15)
    bg_hex = st.sidebar.color_picker("Background Color", "#F7F7F7") # Light default
    bg_rgb = to_rgb(bg_hex)

    # Generate the Standard poster
    fig = draw_poster_standard(n_layers, wobble, palette_mode, seed, shape, bg_rgb)
    
else: # Glowing Style
    st.sidebar.subheader("Glowing Style Controls")
    bg_hex = st.sidebar.color_picker("Background Color", "#262633") # Dark default
    bg_rgb = to_rgb(bg_hex)
    st.sidebar.info("Note: 'Wobble' is randomized for each shape in this style.")

    # Generate the Glowing poster
    fig = draw_poster_glowing(n_layers, seed, shape, palette_mode, bg_rgb)


# 5. Display the Plot in Streamlit
st.pyplot(fig)

# --- Download Button ---
buf = BytesIO()
fig.savefig(buf, format="png", dpi=300, bbox_inches='tight', pad_inches=0.1, facecolor=bg_rgb)

st.sidebar.download_button(
    label="Download Poster (PNG)",
    data=buf.getvalue(),
    file_name=f"poster_{poster_style.lower()}_{shape}_{seed}.png",
    mime="image/png"
)
