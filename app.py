"""
ReLoop — keep it in the loop
Pure-Python Streamlit app.  Run:  streamlit run app.py
Host: push to GitHub, deploy on https://share.streamlit.io
"""

import os
import base64
import streamlit as st

st.set_page_config(page_title="ReLoop — keep it in the loop",
                   page_icon="🌱", layout="wide")

# ======================================================================
# DATA
# ======================================================================
LANES = {
    "reuse":   {"label": "Reuse",   "cats": [
        ("clothes",   "Clothes & footwear"), ("toys", "Toys & games"),
        ("furniture", "Furniture"), ("books", "Books & stationery"),
        ("kitchen",   "Kitchen & household"), ("tools", "Tools & hardware")]},
    "recycle": {"label": "Recycle", "cats": [
        ("plastic", "Plastic"), ("paper", "Paper & cardboard"),
        ("metal",   "Metal"),   ("glass", "Glass"),
        ("textile", "Textile scrap"), ("wood", "Wood")]},
}
CAT_NAME = {cid: name for L in LANES.values() for cid, name in L["cats"]}
CAT_LANE = {cid: lane for lane, L in LANES.items() for cid, _ in L["cats"]}

# (title, meta, price, buyer, condition, slug)  reuse
# (title, meta, rate,  weight, condition, slug)  recycle
SEED = {
    "clothes": [("Toddler clothes lot — 25 pcs", "Ages 2–4", "₹450 / lot", "Families & resellers", "Good", "clothes_toddler"),
                ("School uniforms ×12", "Lightly used", "₹600 / lot", "Schools & NGOs", "Good", "clothes_uniforms"),
                ("Footwear bundle ×8", "Sizes 3–6", "₹500 / lot", None, "Worn but works", "clothes_footwear")],
    "toys":    [("Mixed toy bundle — 30 pcs", "Cleaned & sorted", "₹700 / lot", "Daycares & NGOs", "Good", "toys_bundle"),
                ("Board games ×6", "Complete sets", "₹500 / lot", "Event hosts", "Like new", "toys_boardgames"),
                ("Soft toys ×15", "Washed", "₹400 / lot", "NGOs", "Good", "toys_soft")],
    "furniture":[("Study chairs ×4", "Sturdy", "₹1200 / lot", "Refurbishers", "Worn but works", "furniture_chairs"),
                ("Office desk", "Solid", "₹1500", None, "Good", "furniture_desk")],
    "books":   [("Story books ×40", "Grades 3–6", "₹600 / lot", "Schools & libraries", "Good", "books_story"),
                ("Engg textbooks ×10", "1st year", "₹500 / lot", "Students", "Like new", "books_textbooks")],
    "kitchen": [("Steel utensil set", "Fully usable", "₹350", None, "Good", "kitchen_utensils"),
                ("Glass jars ×10", "With lids", "₹250 / lot", None, "Like new", "kitchen_jars")],
    "tools":   [("Hand tools lot", "Hammer, pliers, etc", "₹600 / lot", "Makers & repairers", "Worn but works", "tools_handtools"),
                ("Brushes & rollers ×8", "Cleaned", "₹200 / lot", None, "Good", "tools_brushes")],
    "plastic": [("Sorted PET bottles", "Label-free", "₹18 / kg", "25 kg", "Clean & sorted", "plastic_pet"),
                ("HDPE containers", "Rinsed", "₹22 / kg", "15 kg", "Clean & sorted", "plastic_hdpe"),
                ("Mixed rigid plastic", "Incl. broken toys", "₹12 / kg", "40 kg", "Mixed", "plastic_mixed")],
    "paper":   [("Cardboard — flattened", "Dry & clean", "₹9 / kg", "60 kg", "Clean & sorted", "paper_cardboard"),
                ("Old newspapers", "Bundled", "₹12 / kg", "30 kg", "Clean & sorted", "paper_newspaper"),
                ("Office paper", "Assorted", "₹10 / kg", "20 kg", "Mixed", "paper_office")],
    "metal":   [("Aluminium cans", "Crushed", "₹95 / kg", "8 kg", "Clean & sorted", "metal_cans"),
                ("Scrap steel utensils", "Beyond use", "₹35 / kg", "18 kg", "Mixed", "metal_steel")],
    "glass":   [("Glass bottles", "Sorted by colour", "₹3 / kg", "50 kg", "Clean & sorted", "glass_bottles"),
                ("Jar cullet", "Clean", "₹4 / kg", "30 kg", "Clean & sorted", "glass_cullet")],
    "textile": [("Worn cotton clothing", "For shredding", "₹8 / kg", "22 kg", "Mixed", "textile_cotton"),
                ("Fabric off-cuts", "Assorted", "₹10 / kg", "15 kg", "Mixed", "textile_offcuts")],
    "wood":    [("Plywood off-cuts", "Project-sized", "₹6 / kg", "35 kg", "Clean & sorted", "wood_plywood"),
                ("Broken furniture wood", "Salvageable", "₹5 / kg", "28 kg", "Mixed", "wood_furniture")],
}

FACTS = [
    "A plastic bottle can take up to 450 years to break down in a landfill.",
    "Less than 10% of all plastic ever made has actually been recycled.",
    "Reusing an item beats recycling it — it skips all the energy of remaking.",
    "Recycling paper uses far less water and energy than making it from fresh wood.",
]

# transparent impact basis: fixed average kg per listing/lot (no random numbers)
CAT_WEIGHT = {"clothes": 5, "toys": 4, "furniture": 12, "books": 8, "kitchen": 3,
              "tools": 4, "plastic": 6, "paper": 7, "metal": 5, "glass": 6,
              "textile": 5, "wood": 9}

# ======================================================================
# DETAILED SHADED ILLUSTRATIONS  (custom SVG — always appropriate)
# ======================================================================
ICON = {
 "clothes": ("<defs><linearGradient id='clg' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#46c47e'/><stop offset='1' stop-color='#138a4c'/></linearGradient></defs>"
   "<path d='M46 40 L34 47 Q31 49 33 53 L38 62 Q40 65 43 63 L47 60 V86 Q47 89 50 89 H70 Q73 89 73 86 V60 L77 63 Q80 65 82 62 L87 53 Q89 49 86 47 L74 40 L68 40 Q60 49 52 40 Z' fill='url(#clg)'/>"
   "<path d='M52 40 Q60 49 68 40' fill='none' stroke='#0c6e3d' stroke-width='2.4'/>"),
 "toys": ("<defs><radialGradient id='tob' cx='38%' cy='32%' r='72%'><stop offset='0' stop-color='#8fd6ff'/><stop offset='1' stop-color='#1f7fce'/></radialGradient></defs>"
   "<circle cx='60' cy='60' r='27' fill='url(#tob)'/><path d='M60 33 A27 27 0 0 1 87 60 L60 60 Z' fill='#ffd23f' opacity='0.92'/>"
   "<path d='M60 60 L60 87 A27 27 0 0 1 33 60 Z' fill='#ff5d5d' opacity='0.92'/><path d='M33 60 A27 27 0 0 1 60 33 L60 60 Z' fill='#ffffff' opacity='0.85'/>"
   "<ellipse cx='50' cy='49' rx='8' ry='5' fill='#ffffff' opacity='0.55'/>"),
 "furniture": ("<defs><linearGradient id='fug' x1='0' y1='0' x2='1' y2='0'><stop offset='0' stop-color='#cf9c5e'/><stop offset='1' stop-color='#a9763c'/></linearGradient></defs>"
   "<path d='M44 40 H52 V64 H44 Z' fill='url(#fug)'/><path d='M44 40 H72 V46 H44 Z' fill='url(#fug)'/><path d='M44 63 H74 V69 H44 Z' fill='url(#fug)'/>"
   "<path d='M44 69 H74 V72 H44 Z' fill='#8a5f2e'/><path d='M45 72 H51 V92 H45 Z' fill='#9c6c36'/><path d='M67 72 H73 V92 H67 Z' fill='#8a5f2e'/>"),
 "books": ("<defs><linearGradient id='bk1' x1='0' x2='1'><stop offset='0' stop-color='#33a564'/><stop offset='1' stop-color='#1c7a44'/></linearGradient>"
   "<linearGradient id='bk2' x1='0' x2='1'><stop offset='0' stop-color='#ecbf63'/><stop offset='1' stop-color='#cf9a3a'/></linearGradient>"
   "<linearGradient id='bk3' x1='0' x2='1'><stop offset='0' stop-color='#5aa0e0'/><stop offset='1' stop-color='#3a7fc0'/></linearGradient></defs>"
   "<rect x='34' y='70' width='52' height='13' rx='2.5' fill='url(#bk3)'/><rect x='38' y='57' width='46' height='13' rx='2.5' fill='url(#bk2)'/><rect x='33' y='44' width='50' height='13' rx='2.5' fill='url(#bk1)'/>"),
 "kitchen": ("<defs><linearGradient id='kig' x1='0' x2='1'><stop offset='0' stop-color='#e9edf1'/><stop offset='0.5' stop-color='#aeb8c2'/><stop offset='1' stop-color='#ced6dd'/></linearGradient></defs>"
   "<rect x='30' y='56' width='10' height='6' rx='3' fill='#8b95a0'/><rect x='80' y='56' width='10' height='6' rx='3' fill='#8b95a0'/>"
   "<path d='M40 56 H80 L77 84 Q77 86 75 86 H45 Q43 86 43 84 Z' fill='url(#kig)'/><rect x='37' y='51' width='46' height='7' rx='3.5' fill='#c2cad2'/>"
   "<rect x='49' y='60' width='5' height='22' rx='2.5' fill='#ffffff' opacity='0.55'/>"),
 "tools": ("<defs><linearGradient id='tlh' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#dde3e9'/><stop offset='1' stop-color='#9aa4ae'/></linearGradient>"
   "<linearGradient id='tlw' x1='0' x2='1'><stop offset='0' stop-color='#cb9c5e'/><stop offset='1' stop-color='#a2733c'/></linearGradient></defs>"
   "<rect x='56' y='50' width='9' height='40' rx='4' fill='url(#tlw)'/><path d='M40 41 Q33 43 36 52 L43 52 V46 Z' fill='#8a949e'/>"
   "<path d='M41 40 H73 Q77 40 77 44 V51 H65 V49 H56 V51 H43 V44 Q41 40 41 40 Z' fill='url(#tlh)'/>"),
 "plastic": ("<defs><linearGradient id='plg' x1='0' x2='1'><stop offset='0' stop-color='#cfeafc'/><stop offset='0.5' stop-color='#93c9f0'/><stop offset='1' stop-color='#cfeafc'/></linearGradient></defs>"
   "<rect x='53' y='27' width='14' height='9' rx='2' fill='#138a4c'/><rect x='55' y='36' width='10' height='6' fill='#9fcde9'/>"
   "<path d='M50 42 Q48 47 48 53 V83 Q48 89 54 89 H66 Q72 89 72 83 V53 Q72 47 70 42 Q66 40 60 40 Q54 40 50 42 Z' fill='url(#plg)'/>"
   "<rect x='53' y='46' width='4' height='40' rx='2' fill='#ffffff' opacity='0.6'/>"),
 "paper": ("<defs><linearGradient id='pa1' x1='0' x2='1'><stop offset='0' stop-color='#dcb784'/><stop offset='1' stop-color='#c69d63'/></linearGradient>"
   "<linearGradient id='pa2' x1='0' x2='1'><stop offset='0' stop-color='#c19a5e'/><stop offset='1' stop-color='#a67d44'/></linearGradient></defs>"
   "<path d='M42 54 L42 46 L52 44 L60 48 Z' fill='#cda268'/><path d='M78 54 L78 46 L68 44 L60 48 Z' fill='#bb8f54'/>"
   "<path d='M42 54 L60 60 V88 L42 82 Z' fill='url(#pa1)'/><path d='M78 54 L60 60 V88 L78 82 Z' fill='url(#pa2)'/><path d='M42 54 L60 48 L78 54 L60 60 Z' fill='#e7c794'/>"),
 "metal": ("<defs><linearGradient id='mtg' x1='0' x2='1'><stop offset='0' stop-color='#cdd4db'/><stop offset='0.35' stop-color='#eef2f5'/><stop offset='0.65' stop-color='#aab4bd'/><stop offset='1' stop-color='#d6dce2'/></linearGradient></defs>"
   "<rect x='46' y='38' width='28' height='44' rx='4' fill='url(#mtg)'/><ellipse cx='60' cy='82' rx='14' ry='4' fill='#b8c0c8'/>"
   "<ellipse cx='60' cy='38' rx='14' ry='4' fill='#e6eaee'/><ellipse cx='60' cy='38' rx='10' ry='2.6' fill='#9aa4ae'/>"
   "<rect x='46' y='52' width='28' height='16' fill='#138a4c' opacity='0.92'/><rect x='50' y='40' width='3' height='40' fill='#ffffff' opacity='0.55'/>"),
 "glass": ("<defs><linearGradient id='glg' x1='0' x2='1'><stop offset='0' stop-color='#d2efe2'/><stop offset='0.5' stop-color='#a7dcc7'/><stop offset='1' stop-color='#d2efe2'/></linearGradient></defs>"
   "<rect x='48' y='33' width='24' height='10' rx='3' fill='#138a4c'/>"
   "<path d='M48 44 Q60 39 72 44 V80 Q72 85 67 85 H53 Q48 85 48 80 Z' fill='url(#glg)' stroke='#7cc3a8' stroke-width='1.5'/>"
   "<rect x='52' y='49' width='4' height='31' rx='2' fill='#ffffff' opacity='0.6'/><rect x='52' y='66' width='16' height='14' rx='2' fill='#7cc3a8' opacity='0.35'/>"),
 "textile": ("<defs><linearGradient id='tx1' x1='0' x2='1'><stop offset='0' stop-color='#f0a0b4'/><stop offset='1' stop-color='#d96f8c'/></linearGradient>"
   "<linearGradient id='tx2' x1='0' x2='1'><stop offset='0' stop-color='#8ccfac'/><stop offset='1' stop-color='#56a87f'/></linearGradient>"
   "<linearGradient id='tx3' x1='0' x2='1'><stop offset='0' stop-color='#a6bce6'/><stop offset='1' stop-color='#7090c8'/></linearGradient></defs>"
   "<path d='M40 74 Q40 70 44 70 H80 Q84 70 84 74 V80 Q84 84 80 84 H44 Q40 84 40 80 Z' fill='url(#tx3)'/>"
   "<path d='M42 63 Q42 59 46 59 H82 Q86 59 86 63 V69 Q86 73 82 73 H46 Q42 73 42 69 Z' fill='url(#tx2)'/>"
   "<path d='M44 52 Q44 48 48 48 H84 Q88 48 88 52 V58 Q88 62 84 62 H48 Q44 62 44 58 Z' fill='url(#tx1)'/>"),
 "wood": ("<defs><linearGradient id='wdg' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#d6ab6e'/><stop offset='1' stop-color='#b07f44'/></linearGradient>"
   "<radialGradient id='wde' cx='50%' cy='50%' r='55%'><stop offset='0' stop-color='#eccea0'/><stop offset='1' stop-color='#bd9355'/></radialGradient></defs>"
   "<path d='M36 52 H72 V74 H36 Z' fill='url(#wdg)'/><ellipse cx='72' cy='63' rx='9' ry='11' fill='url(#wde)'/>"
   "<ellipse cx='72' cy='63' rx='6' ry='7.5' fill='none' stroke='#a87a44' stroke-width='1.2'/><ellipse cx='72' cy='63' rx='3' ry='4' fill='none' stroke='#a87a44' stroke-width='1.2'/>"),
}

def illo(cid):
    return ("<div class='rl-img'><svg viewBox='0 0 120 120' width='150' height='130' xmlns='http://www.w3.org/2000/svg'>"
            "<defs><radialGradient id='bgmint' cx='40%' cy='34%' r='75%'><stop offset='0%' stop-color='#f4fbf7'/><stop offset='100%' stop-color='#dff0e7'/></radialGradient></defs>"
            "<circle cx='60' cy='60' r='56' fill='url(#bgmint)'/><ellipse cx='60' cy='99' rx='27' ry='5' fill='#0b3a22' opacity='0.10'/>"
            + ICON.get(cid, "") + "</svg></div>")

# ======================================================================
# IMAGE HELPERS
# ======================================================================
def _find(slug):
    if not slug:
        return None
    for ext in (".jpg", ".jpeg", ".png", ".webp"):
        p = os.path.join("images", slug + ext)
        if os.path.exists(p):
            return p
    return None

def item_image(it):
    """Show uploaded bytes > per-item photo > category photo > illustration."""
    if it.get("img"):
        st.image(it["img"], use_container_width=True)
        return
    p = _find(it.get("slug")) or _find(it["cid"])
    if p:
        st.image(p, use_container_width=True)
    else:
        st.markdown(illo(it["cid"]), unsafe_allow_html=True)

COND_COLOR = {"Like new": "#0f7d44", "Good": "#169d57", "Good, fully usable": "#169d57",
              "Clean & sorted": "#0f7d44", "Worn but works": "#c98a16", "Mixed": "#c98a16",
              "Contaminated": "#c0552b"}
def badge(c):
    if not c:
        return ""
    return (f"<span style='display:inline-block;font-size:11px;font-weight:700;padding:2px 9px;"
            f"border-radius:999px;color:#fff;background:{COND_COLOR.get(c,'#5d6b63')}'>{c}</span>")

# ======================================================================
# STATE
# ======================================================================
def init():
    d = st.session_state
    d.setdefault("page", "auth")
    d.setdefault("user", {})
    d.setdefault("posted", [])      # user-listed items (flat)
    d.setdefault("cart", [])        # items added to cart
    d.setdefault("purchased", [])   # items checked out
    d.setdefault("nid", 1)          # id counter
init()

def go(p):
    st.session_state.page = p

def seed_items():
    out = []
    for cid, rows in SEED.items():
        lane = CAT_LANE[cid]
        for i, row in enumerate(rows):
            title, meta, price, buyer_or_weight, cond, slug = row
            it = {"id": f"s_{cid}_{i}", "cid": cid, "cat": CAT_NAME[cid], "lane": lane,
                  "title": title, "meta": meta, "price": price, "cond": cond,
                  "slug": slug, "img": None, "kg": CAT_WEIGHT[cid]}
            if lane == "reuse":
                it["buyer"] = buyer_or_weight
            else:
                it["weight"] = buyer_or_weight
            out.append(it)
    return out

def all_items():
    return st.session_state.posted + seed_items()

def cart_ids():
    return {c["id"] for c in st.session_state.cart}

def bought_ids():
    return {b["id"] for b in st.session_state.purchased}

def cart_kg():
    return sum(c["kg"] for c in st.session_state.cart)

def saved_kg():
    return sum(b["kg"] for b in st.session_state.purchased) + sum(p["kg"] for p in st.session_state.posted)

# ======================================================================
# STYLING — animated aurora + dark glass (no image file required)
# ======================================================================
def forest_overlay():
    """Use the exact uploaded image file if it exists."""
    candidates = [
        os.path.join("images", "Forest (2).jpg"),
        os.path.join("images", "Forest (2).jpeg"),
        os.path.join("images", "Forest (2).png"),
        os.path.join("images", "Forest (2).webp"),
    ]

    for p in candidates:
        if os.path.exists(p):
            ext = os.path.splitext(p)[1].lower()
            mime = "png" if ext == ".png" else ("webp" if ext == ".webp" else "jpeg")
            with open(p, "rb") as f:
                data = base64.b64encode(f.read()).decode()
            return (
                f".stApp::after{{content:'';position:fixed;inset:0;z-index:-2;opacity:.28;"
                f"background:url('data:image/{mime};base64,{data}') center/cover no-repeat;"
                f"mix-blend-mode:luminosity}}"
            )
    return ""

st.markdown(f"""
<style>
/* ---- make Streamlit transparent so our background shows ---- */
.stApp,[data-testid="stAppViewContainer"],[data-testid="stHeader"]{{background:transparent !important}}

/* ---- animated emerald aurora (always works, no file) ---- */
.stApp::before{{content:"";position:fixed;inset:-20%;z-index:-3;
  background:
    radial-gradient(38% 44% at 18% 22%, rgba(46,230,166,.30), transparent 60%),
    radial-gradient(42% 50% at 82% 28%, rgba(20,160,110,.34), transparent 60%),
    radial-gradient(50% 55% at 60% 88%, rgba(8,90,62,.40), transparent 62%),
    linear-gradient(160deg,#04130d 0%,#082018 55%,#03100b 100%);
  animation:drift 22s ease-in-out infinite alternate;filter:saturate(1.15)}}
@keyframes drift{{0%{{transform:translate(0,0) scale(1.05)}}
                 100%{{transform:translate(-3%,-3%) scale(1.18)}}}}
{forest_overlay()}

/* floating leaves */
.amb{{position:fixed;inset:0;z-index:-1;pointer-events:none;overflow:hidden}}
.amb b{{position:absolute;bottom:-40px;font-size:22px;opacity:.5;animation:rise linear infinite}}
@keyframes rise{{0%{{transform:translateY(0) rotate(0);opacity:0}}
                10%{{opacity:.55}}90%{{opacity:.5}}
                100%{{transform:translateY(-115vh) rotate(320deg);opacity:0}}}}

/* ---- force readable light text everywhere ---- */
.block-container{{max-width:1080px;padding-top:1.2rem}}
.block-container, .block-container p, .block-container li, .block-container label,
[data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] *{{color:#e9f6ee !important}}
[data-testid="stCaptionContainer"], .block-container small{{color:#a9d2bd !important}}
h1,h2,h3,h4{{font-family:'Trebuchet MS',Verdana,sans-serif !important;font-weight:800 !important;
  color:#ffffff !important;letter-spacing:-.01em}}

/* hero gradient title */
.hero{{font-size:46px;line-height:1.05;font-weight:900;margin:.1em 0 .15em;
  background:linear-gradient(92deg,#9ff5c8,#39e0a0 55%,#bff7d3);
  -webkit-background-clip:text;background-clip:text;color:transparent}}

/* ---- glass cards (st.container border) ---- */
[data-testid="stVerticalBlockBorderWrapper"]{{
  background:rgba(255,255,255,.07) !important;
  border:1px solid rgba(255,255,255,.14) !important;
  border-radius:18px !important;backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);
  box-shadow:0 18px 50px -24px rgba(0,0,0,.7)}}

/* inputs readable in dark */
.stTextInput input,.stTextInput textarea,[data-baseweb="input"] input,
[data-baseweb="select"]>div,[data-baseweb="textarea"] textarea{{
  background:rgba(255,255,255,.10) !important;color:#eafff2 !important;
  border-color:rgba(255,255,255,.18) !important}}
[data-testid="stFileUploaderDropzone"]{{background:rgba(255,255,255,.06) !important}}

/* sidebar glass */
section[data-testid="stSidebar"] > div{{background:rgba(6,22,15,.78) !important;backdrop-filter:blur(12px)}}
section[data-testid="stSidebar"] *{{color:#e9f6ee !important}}

/* buttons */
.stButton>button{{border-radius:11px;border:1px solid rgba(255,255,255,.18);
  background:rgba(255,255,255,.08);color:#eafff2 !important;font-weight:700}}
.stButton>button:hover{{border-color:#39e0a0}}
.stButton>button[kind="primary"]{{background:linear-gradient(92deg,#1ec98a,#34e89e) !important;
  color:#06241a !important;border:none}}

/* eco ticker */
.rl-ticker{{position:relative;overflow:hidden;height:44px;display:flex;align-items:center;
  background:linear-gradient(90deg,rgba(11,75,52,.9),rgba(20,160,110,.85));
  border:1px solid rgba(255,255,255,.14);border-radius:14px;margin:2px 0 20px;backdrop-filter:blur(6px)}}
.rl-badge{{position:absolute;left:0;top:0;bottom:0;z-index:3;display:flex;align-items:center;gap:7px;
  background:#06241a;color:#7cf2a8 !important;font-weight:800;font-size:12px;letter-spacing:.12em;padding:0 16px}}
.rl-badge .pulse{{width:8px;height:8px;border-radius:50%;background:#7cf2a8;animation:pls 1.2s ease-in-out infinite}}
@keyframes pls{{0%,100%{{opacity:.4;transform:scale(.8)}}50%{{opacity:1;transform:scale(1.2)}}}}
.rl-track{{overflow:hidden;width:100%;margin-left:120px}}
.rl-tk{{display:inline-flex;white-space:nowrap;animation:marq 26s linear infinite}}
.rl-tk:hover{{animation-play-state:paused}}
.rl-tk span{{color:#eafff2;font-weight:600;font-size:14px}}
.rl-tk b{{color:#7cf2a8;margin:0 14px}}
@keyframes marq{{from{{transform:translateX(0)}}to{{transform:translateX(-50%)}}}}

/* bits */
.rl-brand{{display:flex;align-items:center;gap:10px;font-weight:800;font-size:24px;color:#fff}}
.rl-leaf{{width:30px;height:30px;border-radius:50%;
  background:linear-gradient(135deg,#34e89e,#1ba35d);display:flex;align-items:center;justify-content:center;
  box-shadow:0 0 18px rgba(52,232,158,.5)}}
.rl-img{{height:120px;display:flex;align-items:center;justify-content:center;
  background:rgba(255,255,255,.06);border-radius:12px;margin-bottom:8px;overflow:hidden}}
.rl-tag{{display:inline-block;font-size:11px;font-weight:700;padding:3px 9px;border-radius:999px;
  background:rgba(52,232,158,.18);color:#9ff5c8 !important}}
.rl-tag.rec{{background:rgba(80,200,210,.16);color:#9fe8e0 !important}}
.rl-name{{font-weight:800;font-size:16px;color:#ffffff !important;margin:6px 0 2px}}
.rl-meta{{font-size:12px;color:#a9d2bd !important}}
.rl-buyer{{display:inline-block;font-size:11px;font-weight:600;color:#9ff5c8 !important;
  background:rgba(52,232,158,.14);padding:2px 8px;border-radius:999px;margin-top:3px}}
.rl-price{{font-weight:800;font-size:18px;color:#7cf2a8 !important;margin-top:3px}}
.step{{background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.12);
  border-radius:14px;padding:16px;height:100%}}
hr{{margin:.9rem 0;border-color:rgba(255,255,255,.12)}}
</style>
<div class="amb">
  <b style="left:8%;animation-duration:17s;animation-delay:0s">🍃</b>
  <b style="left:24%;animation-duration:23s;animation-delay:4s">🌿</b>
  <b style="left:43%;animation-duration:19s;animation-delay:8s">🍃</b>
  <b style="left:61%;animation-duration:26s;animation-delay:2s">🌿</b>
  <b style="left:77%;animation-duration:21s;animation-delay:11s">🍃</b>
  <b style="left:90%;animation-duration:24s;animation-delay:6s">🌿</b>
</div>
""", unsafe_allow_html=True)

def ticker():
    run = "".join(f"<span>{f}</span><b>◆</b>" for f in FACTS)
    st.markdown("<div class='rl-ticker'><div class='rl-badge'><span class='pulse'></span>ECO FACTS</div>"
                f"<div class='rl-track'><div class='rl-tk'>{run}{run}</div></div></div>",
                unsafe_allow_html=True)

def brand():
    st.markdown("<div class='rl-brand'><span class='rl-leaf'>🌱</span> ReLoop</div>", unsafe_allow_html=True)

# ======================================================================
# SIDEBAR
# ======================================================================
def sidebar():
    if not st.session_state.user:
        return
    s = st.sidebar
    s.markdown("<div class='rl-brand'><span class='rl-leaf'>🌱</span> ReLoop</div>", unsafe_allow_html=True)
    name = st.session_state.user.get("name", "Friend").title()
    s.caption(f"Hi {name.split()[0]} 👋")
    s.divider()

    # cart + impact snapshot
    s.markdown(f"### 🧺 Cart")
    s.write(f"**{len(st.session_state.cart)} item(s)**")
    s.success(f"This cart will keep about **{cart_kg():.0f} kg** out of a landfill 🌱")
    s.metric("Kept from landfill (total)", f"{saved_kg():.0f} kg")
    s.divider()

    nav = [("🏠 Home", "home"), ("🛒 Marketplace", "market"),
           ("➕ Sell an item", "sell"), ("🧺 My cart", "cart"),
           ("👤 My profile", "account")]
    for label, page in nav:
        if s.button(label, use_container_width=True, key=f"nav_{page}"):
            go(page); st.rerun()
    s.divider()
    if s.button("Log out", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

# ======================================================================
# ITEM CARD (shared by marketplace)
# ======================================================================
def item_card(it, col):
    with col:
        with st.container(border=True):
            item_image(it)
            tagcls = "rl-tag" if it["lane"] == "reuse" else "rl-tag rec"
            tagtxt = "REUSE" if it["lane"] == "reuse" else "RECYCLE · BY WEIGHT"
            st.markdown(f"<span class='{tagcls}'>{tagtxt}</span> {badge(it.get('cond'))}"
                        f"<div class='rl-name'>{it['title']}</div>"
                        f"<div class='rl-meta'>{it['cat']} · {it['meta']}</div>", unsafe_allow_html=True)
            if it.get("buyer"):
                st.markdown(f"<div class='rl-buyer'>Bought by {it['buyer']}</div>", unsafe_allow_html=True)
            price = it["price"] if it["lane"] == "reuse" else f"{it['price']} · {it.get('weight','')}"
            st.markdown(f"<div class='rl-price'>{price}</div>", unsafe_allow_html=True)
            st.caption(f"≈ {it['kg']} kg saved")
            st.write("")
            if it["id"] in bought_ids():
                st.success("✓ Purchased")
            elif it["id"] in cart_ids():
                st.button("In cart ✓", key=f"in_{it['id']}", use_container_width=True, disabled=True)
            else:
                if st.button("Add to cart 🧺", key=f"add_{it['id']}", use_container_width=True, type="primary"):
                    st.session_state.cart.append(it)
                    st.rerun()

# ======================================================================
# PAGES
# ======================================================================
def page_auth():
    ticker(); brand()
    st.markdown("### Keep it in the loop")
    st.write("Buy and sell reusable goods and recyclable materials — so they get used again instead of dumped.")
    t1, t2 = st.tabs(["Log in", "Sign up"])
    with t1:
        e = st.text_input("Email", key="li")
        st.text_input("Password", type="password", key="lp")
        if st.button("Log in", type="primary", use_container_width=True):
            if e.strip():
                st.session_state.user = {"name": e.split("@")[0].replace(".", " ").replace("_", " ")}
                go("home"); st.rerun()
            else:
                st.warning("Enter your email to continue.")
    with t2:
        e = st.text_input("Email", key="si")
        p = st.text_input("Create a password", type="password", key="sp")
        if st.button("Continue", type="primary", use_container_width=True):
            if not e.strip():
                st.warning("Enter your email to continue.")
            elif len(p) < 6:
                st.warning("Password needs at least 6 characters.")
            else:
                st.session_state.user = {"email": e}
                go("setup"); st.rerun()

def page_setup():
    ticker(); brand()
    st.markdown("### Tell us who you are")
    name = st.text_input("Full name")
    prof = st.selectbox("You are a…", ["Select…", "Household", "Maker / Student",
        "Daycare / School / NGO", "Small business / Workshop", "Recycler / Scrap dealer",
        "Refurbisher / Reseller", "Other"])
    city = st.text_input("City", placeholder="e.g. Hyderabad")
    if st.button("Enter ReLoop", type="primary"):
        if not name.strip():
            st.warning("Add your name.")
        elif prof == "Select…":
            st.warning("Pick what you are.")
        else:
            st.session_state.user = {"name": name, "prof": prof, "city": city}
            go("home"); st.rerun()

def page_home():
    ticker(); brand()
    name = st.session_state.user.get("name", "there").split(" ")[0].title()
    st.markdown("""
    <div class='hero-box'>
        <h1>♻ ReLoop</h1>
        <h2>Buy • Reuse • Recycle</h2>
        <p>Keeping useful materials out of landfills and in the loop.</p>
    </div>
    """, unsafe_allow_html=True)

    st.write("**Reuse** still-usable goods, or **recycle** spent material by weight. "
             "Buy what others no longer need, or sell what you're done with.")

    st.write("")
    st.markdown("##### How it works")
    a, b, c = st.columns(3)
    a.markdown("<div class='step'>1 · Sell 📦<br><span class='rl-meta'>List an item you don't need — with a photo and condition.</span></div>", unsafe_allow_html=True)
    b.markdown("<div class='step'>2 · Buy 🛒<br><span class='rl-meta'>Browse the marketplace and add things to your cart.</span></div>", unsafe_allow_html=True)
    c.markdown("<div class='step'>3 · Loop ♻️<br><span class='rl-meta'>Each item gets reused or remade — not dumped.</span></div>", unsafe_allow_html=True)

    st.write("")
    st.markdown("##### What would you like to do?")
    x, y = st.columns(2)
    with x:
        with st.container(border=True):
            st.markdown("### 🛒 Browse marketplace")
            st.caption("Find reusable goods and recyclable materials near you.")
            if st.button("Open marketplace", type="primary", use_container_width=True):
                go("market"); st.rerun()
    with y:
        with st.container(border=True):
            st.markdown("### ➕ Sell an item")
            st.caption("List something you're done with so it gets a new life.")
            if st.button("Sell an item", use_container_width=True):
                go("sell"); st.rerun()

    st.markdown("## 🌟 Featured Listings")
    featured = all_items()[:3]
    cols = st.columns(3)
    for item, col in zip(featured, cols):
        item_card(item, col)

    st.write("")
    m1, m2, m3 = st.columns(3)
    m1.metric("In your cart", f"{len(st.session_state.cart)} item(s)")
    m2.metric("Cart will save", f"{cart_kg():.0f} kg")
    m3.metric("You've saved", f"{saved_kg():.0f} kg")

def page_market():
    ticker(); brand()
    st.markdown("## 🛒 Marketplace")
    st.caption("Everything listed — including items you post — shows up here.")

    market_type = st.radio("Marketplace", ["All", "Reuse", "Recycle"], horizontal=True)
    cat = st.selectbox("Category", ["All"] + [CAT_NAME[c] for c in CAT_NAME])
    q = st.text_input("Search", placeholder="🔍 Search items...")

    items = all_items()
    if market_type != "All":
        items = [i for i in items if i["lane"] == market_type.lower()]
    if cat != "All":
        items = [i for i in items if i["cat"] == cat]
    if q.strip():
        ql = q.lower()
        items = [i for i in items if ql in i["title"].lower() or ql in i["cat"].lower()]

    st.write(f"**{len(items)} item(s)**")
    if not items:
        st.info("No items match. Try clearing the filters.")
    for r in range(0, len(items), 3):
        cols = st.columns(3)
        for it, col in zip(items[r:r+3], cols):
            item_card(it, col)

def page_sell():
    ticker(); brand()
    st.markdown("## ➕ Sell an item")
    st.caption("All fields are required, including a photo. Your item appears in the marketplace right after.")

    lane_label = st.radio("Is it still usable, or only good for material?",
                          ["Reuse — still usable as-is", "Recycle — spent, sold by weight"], horizontal=False)
    lane = "reuse" if lane_label.startswith("Reuse") else "recycle"
    cats = [CAT_NAME[c] for c, _ in LANES[lane]["cats"]]
    cat_label = st.selectbox("Category", cats)
    cid = next(c for c in CAT_NAME if CAT_NAME[c] == cat_label)

    title = st.text_input("Item name")
    photo = st.file_uploader("Photo (required)", type=["png", "jpg", "jpeg"])
    if photo is not None:
        st.image(photo, width=220, caption="Preview")

    if lane == "reuse":
        qty = st.text_input("Lot size / quantity", placeholder="e.g. 25 pieces")
        cond = st.selectbox("Condition", ["Select…", "Like new", "Good, fully usable", "Worn but works"])
        price = st.text_input("Price (₹)", placeholder="e.g. 450")
    else:
        weight = st.text_input("Approx. weight available", placeholder="e.g. 25 kg")
        cond = st.selectbox("Quality / condition", ["Select…", "Clean & sorted", "Mixed", "Contaminated"])
        rate = st.text_input("Rate (₹ / kg)", placeholder="e.g. 18")
    note = st.text_input("Notes", placeholder="who it suits / sorting details")

    if st.button("List it on the marketplace", type="primary"):
        miss = []
        if not title.strip(): miss.append("name")
        if photo is None: miss.append("photo")
        if cond == "Select…": miss.append("condition")
        if not note.strip(): miss.append("notes")
        if lane == "reuse":
            if not qty.strip(): miss.append("lot size")
            if not price.strip(): miss.append("price")
        else:
            if not weight.strip(): miss.append("weight")
            if not rate.strip(): miss.append("rate")
        if miss:
            st.warning("Please fill in: " + ", ".join(miss) + ".")
        else:
            iid = f"u_{st.session_state.nid}"; st.session_state.nid += 1
            it = {"id": iid, "cid": cid, "cat": cat_label, "lane": lane, "title": title,
                  "cond": cond, "slug": None, "img": photo.getvalue(), "kg": CAT_WEIGHT[cid]}
            if lane == "reuse":
                it["meta"] = f"{qty} · {note}"
                it["price"] = price if price.strip().startswith("₹") else "₹" + price.strip()
                it["buyer"] = None
            else:
                it["meta"] = note
                it["price"] = "₹" + rate.strip().replace("₹", "").replace("/kg", "").strip() + " / kg"
                it["weight"] = weight
            st.session_state.posted.insert(0, it)
            st.success("Listed! It's now live in the marketplace 🌱")
            go("market"); st.rerun()

def page_cart():
    ticker(); brand()
    st.markdown("## 🧺 Your cart")
    cart = st.session_state.cart
    if not cart:
        st.info("Your cart is empty. Browse the marketplace and add items.")
        if st.button("🛒 Go to marketplace", type="primary"):
            go("market"); st.rerun()
        return

    st.success(f"🌍 Checking out this cart keeps about **{cart_kg():.0f} kg** of material out of a landfill.")
    for idx, it in enumerate(list(cart)):
        with st.container(border=True):
            a, b, c = st.columns([1, 3, 1])
            with a:
                item_image(it)
            b.markdown(f"**{it['title']}**  \n<span class='rl-meta'>{it['cat']} · "
                       f"{'Reuse' if it['lane']=='reuse' else 'Recycle'}</span> {badge(it.get('cond'))}  \n"
                       f"<span class='rl-price'>{it['price']}</span> · ≈ {it['kg']} kg",
                       unsafe_allow_html=True)
            if c.button("Remove", key=f"rm_{idx}"):
                st.session_state.cart.pop(idx); st.rerun()

    st.divider()
    st.markdown(f"### Total: {len(cart)} item(s) · ~{cart_kg():.0f} kg saved")
    if st.button("✅ Checkout", type="primary", use_container_width=True):
        st.session_state.purchased.extend(cart)
        st.session_state.cart = []
        st.success("Done! These items are now yours and counted in your impact.")
        go("account"); st.rerun()

def page_account():
    ticker(); brand()
    u = st.session_state.user
    st.markdown(f"## 👤 {u.get('name','My profile')}")
    st.caption(" · ".join([x for x in [u.get('prof'), u.get('city')] if x]) or "Your ReLoop profile")

    bought, posted = st.session_state.purchased, st.session_state.posted
    st.markdown("### 🌍 Your impact")
    c1, c2, c3 = st.columns(3)
    c1.metric("Items purchased", len(bought))
    c2.metric("Items listed", len(posted))
    c3.metric("Kept from landfill", f"{saved_kg():.0f} kg")
    st.caption("Counts are exact. Weight is an **estimate** from a fixed average per category "
               "(clothing lot ≈ 5 kg, furniture ≈ 12 kg, wood ≈ 9 kg…) — no random numbers, so the "
               "same activity always gives the same figure.")
    st.progress(min(saved_kg() / 100, 1.0), text="Toward your first 100 kg saved")

    st.divider()
    st.markdown("### 🛍️ Items you've purchased")
    if not bought:
        st.info("Nothing purchased yet — add items to your cart and check out.")
    else:
        for r in range(0, len(bought), 3):
            for it, col in zip(bought[r:r+3], st.columns(3)):
                item_card_static(it, col)

    st.divider()
    st.markdown("### 🏷️ Items you've listed")
    if not posted:
        st.info("You haven't listed anything yet — use **Sell an item**.")
    else:
        for r in range(0, len(posted), 3):
            for it, col in zip(posted[r:r+3], st.columns(3)):
                item_card_static(it, col)

    st.divider()
    if st.button("🏠 Back to home"):
        go("home"); st.rerun()

def item_card_static(it, col):
    with col:
        with st.container(border=True):
            item_image(it)
            st.markdown(f"<div class='rl-name'>{it['title']}</div>"
                        f"<div class='rl-meta'>{it['cat']}</div> {badge(it.get('cond'))}"
                        f"<div class='rl-price'>{it.get('price','')}</div>", unsafe_allow_html=True)
            st.caption(f"≈ {it['kg']} kg")

# ======================================================================
# ROUTER
# ======================================================================
sidebar()
{
    "auth": page_auth, "setup": page_setup, "home": page_home, "market": page_market,
    "sell": page_sell, "cart": page_cart, "account": page_account,
}.get(st.session_state.page, page_auth)()

st.markdown("""
<style>
.hero-box{
text-align:center;
padding:60px;
border-radius:25px;
background:rgba(255,255,255,.08);
backdrop-filter:blur(12px);
margin-bottom:20px;
}
.hero-box h1{font-size:72px;margin:0;}
.hero-box h2{color:#7cf2a8;}
.hero-box p{color:#d4f2df;font-size:18px;}
</style>
""", unsafe_allow_html=True)
