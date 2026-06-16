"""
ReLoop — keep it in the loop
Pure-Python Streamlit app.  Run:  streamlit run app.py
"""

import os
import base64
import streamlit as st

st.set_page_config(page_title="ReLoop — keep it in the loop", page_icon="🌱",
                   layout="wide", initial_sidebar_state="collapsed")

# ======================================================================
# DATA
# ======================================================================
LANES = {
    "reuse":   {"label": "Reuse",   "desc": "Whole items that still work — sold with a price.",
                "cats": [("clothes", "Clothes & footwear"), ("toys", "Toys & games"),
                         ("furniture", "Furniture"), ("books", "Books & stationery"),
                         ("kitchen", "Kitchen & household"), ("tools", "Tools & hardware")]},
    "recycle": {"label": "Recycle", "desc": "Spent material, bought by weight to be remade.",
                "cats": [("plastic", "Plastic"), ("paper", "Paper & cardboard"),
                         ("metal", "Metal"), ("glass", "Glass"),
                         ("textile", "Textile scrap"), ("wood", "Wood")]},
}
CAT_NAME = {cid: name for L in LANES.values() for cid, name in L["cats"]}
CAT_LANE = {cid: lane for lane, L in LANES.items() for cid, _ in L["cats"]}

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
CAT_WEIGHT = {"clothes": 5, "toys": 4, "furniture": 12, "books": 8, "kitchen": 3,
              "tools": 4, "plastic": 6, "paper": 7, "metal": 5, "glass": 6,
              "textile": 5, "wood": 9}

# ======================================================================
# ILLUSTRATIONS
# ======================================================================
ICON = {
 "clothes": ("<defs><linearGradient id='clg' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#46c47e'/><stop offset='1' stop-color='#138a4c'/></linearGradient></defs>"
   "<path d='M46 40 L34 47 Q31 49 33 53 L38 62 Q40 65 43 63 L47 60 V86 Q47 89 50 89 H70 Q73 89 73 86 V60 L77 63 Q80 65 82 62 L87 53 Q89 49 86 47 L74 40 L68 40 Q60 49 52 40 Z' fill='url(#clg)'/>"),
 "toys": ("<defs><radialGradient id='tob' cx='38%' cy='32%' r='72%'><stop offset='0' stop-color='#8fd6ff'/><stop offset='1' stop-color='#1f7fce'/></radialGradient></defs>"
   "<circle cx='60' cy='60' r='27' fill='url(#tob)'/><path d='M60 33 A27 27 0 0 1 87 60 L60 60 Z' fill='#ffd23f' opacity='0.92'/>"
   "<path d='M60 60 L60 87 A27 27 0 0 1 33 60 Z' fill='#ff5d5d' opacity='0.92'/><path d='M33 60 A27 27 0 0 1 60 33 L60 60 Z' fill='#ffffff' opacity='0.85'/>"),
 "furniture": ("<defs><linearGradient id='fug' x1='0' y1='0' x2='1' y2='0'><stop offset='0' stop-color='#cf9c5e'/><stop offset='1' stop-color='#a9763c'/></linearGradient></defs>"
   "<path d='M44 40 H52 V64 H44 Z' fill='url(#fug)'/><path d='M44 40 H72 V46 H44 Z' fill='url(#fug)'/><path d='M44 63 H74 V69 H44 Z' fill='url(#fug)'/>"
   "<path d='M44 69 H74 V72 H44 Z' fill='#8a5f2e'/><path d='M45 72 H51 V92 H45 Z' fill='#9c6c36'/><path d='M67 72 H73 V92 H67 Z' fill='#8a5f2e'/>"),
 "books": ("<defs><linearGradient id='bk1' x1='0' x2='1'><stop offset='0' stop-color='#33a564'/><stop offset='1' stop-color='#1c7a44'/></linearGradient>"
   "<linearGradient id='bk2' x1='0' x2='1'><stop offset='0' stop-color='#ecbf63'/><stop offset='1' stop-color='#cf9a3a'/></linearGradient>"
   "<linearGradient id='bk3' x1='0' x2='1'><stop offset='0' stop-color='#5aa0e0'/><stop offset='1' stop-color='#3a7fc0'/></linearGradient></defs>"
   "<rect x='34' y='70' width='52' height='13' rx='2.5' fill='url(#bk3)'/><rect x='38' y='57' width='46' height='13' rx='2.5' fill='url(#bk2)'/><rect x='33' y='44' width='50' height='13' rx='2.5' fill='url(#bk1)'/>"),
 "kitchen": ("<defs><linearGradient id='kig' x1='0' x2='1'><stop offset='0' stop-color='#e9edf1'/><stop offset='0.5' stop-color='#aeb8c2'/><stop offset='1' stop-color='#ced6dd'/></linearGradient></defs>"
   "<rect x='30' y='56' width='10' height='6' rx='3' fill='#8b95a0'/><rect x='80' y='56' width='10' height='6' rx='3' fill='#8b95a0'/>"
   "<path d='M40 56 H80 L77 84 Q77 86 75 86 H45 Q43 86 43 84 Z' fill='url(#kig)'/><rect x='37' y='51' width='46' height='7' rx='3.5' fill='#c2cad2'/>"),
 "tools": ("<defs><linearGradient id='tlh' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#dde3e9'/><stop offset='1' stop-color='#9aa4ae'/></linearGradient>"
   "<linearGradient id='tlw' x1='0' x2='1'><stop offset='0' stop-color='#cb9c5e'/><stop offset='1' stop-color='#a2733c'/></linearGradient></defs>"
   "<rect x='56' y='50' width='9' height='40' rx='4' fill='url(#tlw)'/><path d='M40 41 Q33 43 36 52 L43 52 V46 Z' fill='#8a949e'/>"
   "<path d='M41 40 H73 Q77 40 77 44 V51 H65 V49 H56 V51 H43 V44 Q41 40 41 40 Z' fill='url(#tlh)'/>"),
 "plastic": ("<defs><linearGradient id='plg' x1='0' x2='1'><stop offset='0' stop-color='#cfeafc'/><stop offset='0.5' stop-color='#93c9f0'/><stop offset='1' stop-color='#cfeafc'/></linearGradient></defs>"
   "<rect x='53' y='27' width='14' height='9' rx='2' fill='#138a4c'/><rect x='55' y='36' width='10' height='6' fill='#9fcde9'/>"
   "<path d='M50 42 Q48 47 48 53 V83 Q48 89 54 89 H66 Q72 89 72 83 V53 Q72 47 70 42 Q66 40 60 40 Q54 40 50 42 Z' fill='url(#plg)'/>"),
 "paper": ("<defs><linearGradient id='pa1' x1='0' x2='1'><stop offset='0' stop-color='#dcb784'/><stop offset='1' stop-color='#c69d63'/></linearGradient>"
   "<linearGradient id='pa2' x1='0' x2='1'><stop offset='0' stop-color='#c19a5e'/><stop offset='1' stop-color='#a67d44'/></linearGradient></defs>"
   "<path d='M42 54 L60 60 V88 L42 82 Z' fill='url(#pa1)'/><path d='M78 54 L60 60 V88 L78 82 Z' fill='url(#pa2)'/><path d='M42 54 L60 48 L78 54 L60 60 Z' fill='#e7c794'/>"),
 "metal": ("<defs><linearGradient id='mtg' x1='0' x2='1'><stop offset='0' stop-color='#cdd4db'/><stop offset='0.35' stop-color='#eef2f5'/><stop offset='0.65' stop-color='#aab4bd'/><stop offset='1' stop-color='#d6dce2'/></linearGradient></defs>"
   "<rect x='46' y='38' width='28' height='44' rx='4' fill='url(#mtg)'/><ellipse cx='60' cy='38' rx='14' ry='4' fill='#e6eaee'/>"
   "<ellipse cx='60' cy='38' rx='10' ry='2.6' fill='#9aa4ae'/><rect x='46' y='52' width='28' height='16' fill='#138a4c' opacity='0.92'/>"),
 "glass": ("<defs><linearGradient id='glg' x1='0' x2='1'><stop offset='0' stop-color='#d2efe2'/><stop offset='0.5' stop-color='#a7dcc7'/><stop offset='1' stop-color='#d2efe2'/></linearGradient></defs>"
   "<rect x='48' y='33' width='24' height='10' rx='3' fill='#138a4c'/>"
   "<path d='M48 44 Q60 39 72 44 V80 Q72 85 67 85 H53 Q48 85 48 80 Z' fill='url(#glg)' stroke='#7cc3a8' stroke-width='1.5'/>"),
 "textile": ("<defs><linearGradient id='tx1' x1='0' x2='1'><stop offset='0' stop-color='#f0a0b4'/><stop offset='1' stop-color='#d96f8c'/></linearGradient>"
   "<linearGradient id='tx2' x1='0' x2='1'><stop offset='0' stop-color='#8ccfac'/><stop offset='1' stop-color='#56a87f'/></linearGradient>"
   "<linearGradient id='tx3' x1='0' x2='1'><stop offset='0' stop-color='#a6bce6'/><stop offset='1' stop-color='#7090c8'/></linearGradient></defs>"
   "<path d='M40 74 Q40 70 44 70 H80 Q84 70 84 74 V80 Q84 84 80 84 H44 Q40 84 40 80 Z' fill='url(#tx3)'/>"
   "<path d='M42 63 Q42 59 46 59 H82 Q86 59 86 63 V69 Q86 73 82 73 H46 Q42 73 42 69 Z' fill='url(#tx2)'/>"
   "<path d='M44 52 Q44 48 48 48 H84 Q88 48 88 52 V58 Q88 62 84 62 H48 Q44 62 44 58 Z' fill='url(#tx1)'/>"),
 "wood": ("<defs><linearGradient id='wdg' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#d6ab6e'/><stop offset='1' stop-color='#b07f44'/></linearGradient>"
   "<radialGradient id='wde' cx='50%' cy='50%' r='55%'><stop offset='0' stop-color='#eccea0'/><stop offset='1' stop-color='#bd9355'/></radialGradient></defs>"
   "<path d='M36 52 H72 V74 H36 Z' fill='url(#wdg)'/><ellipse cx='72' cy='63' rx='9' ry='11' fill='url(#wde)'/>"
   "<ellipse cx='72' cy='63' rx='6' ry='7.5' fill='none' stroke='#a87a44' stroke-width='1.2'/>"),
}
def illo(cid):
    return ("<div class='rl-img'><svg viewBox='0 0 120 120' width='150' height='128' xmlns='http://www.w3.org/2000/svg'>"
            "<defs><radialGradient id='bgmint' cx='40%' cy='34%' r='75%'><stop offset='0%' stop-color='#0f3326'/><stop offset='100%' stop-color='#0a2118'/></radialGradient></defs>"
            "<circle cx='60' cy='60' r='56' fill='url(#bgmint)'/><ellipse cx='60' cy='99' rx='27' ry='5' fill='#000' opacity='0.18'/>"
            + ICON.get(cid, "") + "</svg></div>")

# loop emblem for the hero (SVG, not an emoji)
LOOP = ("<svg viewBox='0 0 120 120' width='86' height='86' xmlns='http://www.w3.org/2000/svg'>"
        "<defs><linearGradient id='lp' x1='0' x2='1'><stop offset='0' stop-color='#bff7d3'/><stop offset='1' stop-color='#34e89e'/></linearGradient></defs>"
        "<path d='M88 44 A38 38 0 1 0 96 70' fill='none' stroke='url(#lp)' stroke-width='11' stroke-linecap='round'/>"
        "<path d='M74 30 L92 40 L84 58 Z' fill='#34e89e'/></svg>")

# ======================================================================
# HELPERS
# ======================================================================
def _find(slug):
    if not slug: return None
    for ext in (".jpg", ".jpeg", ".png", ".webp"):
        p = os.path.join("images", slug + ext)
        if os.path.exists(p): return p
    return None

def item_image(it):
    if it.get("img"):
        st.image(it["img"], use_container_width=True); return
    p = _find(it.get("slug")) or _find(it["cid"])
    if p: st.image(p, use_container_width=True)
    else: st.markdown(illo(it["cid"]), unsafe_allow_html=True)

COND_COLOR = {"Like new": "#2ee6a6", "Good": "#34c47e", "Good, fully usable": "#34c47e",
              "Clean & sorted": "#2ee6a6", "Worn but works": "#e0a93b", "Mixed": "#e0a93b", "Contaminated": "#e06a45"}
def badge(c):
    return "" if not c else (f"<span style='display:inline-block;font-size:11px;font-weight:700;padding:2px 9px;"
                             f"border-radius:999px;color:#06241a;background:{COND_COLOR.get(c,'#9fc7b3')}'>{c}</span>")

def init():
    d = st.session_state
    d.setdefault("page", "auth"); d.setdefault("user", {})
    d.setdefault("posted", []); d.setdefault("cart", []); d.setdefault("purchased", [])
    d.setdefault("nid", 1); d.setdefault("mk_lane", None); d.setdefault("mk_cat", None)
init()
def go(p): st.session_state.page = p

def seed_items():
    out = []
    for cid, rows in SEED.items():
        lane = CAT_LANE[cid]
        for i, row in enumerate(rows):
            title, meta, price, bw, cond, slug = row
            it = {"id": f"s_{cid}_{i}", "cid": cid, "cat": CAT_NAME[cid], "lane": lane,
                  "title": title, "meta": meta, "price": price, "cond": cond,
                  "slug": slug, "img": None, "kg": CAT_WEIGHT[cid]}
            if lane == "reuse":
                it["buyer"] = bw
            else:
                it["weight"] = bw
            out.append(it)
    return out
def all_items(): return st.session_state.posted + seed_items()
def cart_ids(): return {c["id"] for c in st.session_state.cart}
def bought_ids(): return {b["id"] for b in st.session_state.purchased}
def cart_kg(): return sum(c["kg"] for c in st.session_state.cart)
def saved_kg(): return sum(b["kg"] for b in st.session_state.purchased) + sum(p["kg"] for p in st.session_state.posted)

# ======================================================================
# STYLING
# ======================================================================
def forest_overlay():
    for ext in (".jpg", ".jpeg", ".png", ".webp"):
        p = os.path.join("images", "forest" + ext)
        if os.path.exists(p):
            mime = "png" if ext == ".png" else ("webp" if ext == ".webp" else "jpeg")
            data = base64.b64encode(open(p, "rb").read()).decode()
            return (f".stApp::after{{content:'';position:fixed;inset:0;z-index:-2;opacity:.30;"
                    f"background:url('data:image/{mime};base64,{data}') center/cover no-repeat;mix-blend-mode:luminosity}}")
    return ""

st.markdown(f"""
<style>
.stApp,[data-testid="stAppViewContainer"],[data-testid="stHeader"]{{background:transparent !important}}
/* hide the streamlit sidebar entirely — we use a top nav */
section[data-testid="stSidebar"],[data-testid="collapsedControl"]{{display:none !important}}

.stApp::before{{content:"";position:fixed;inset:-20%;z-index:-3;
  background:
    radial-gradient(38% 44% at 18% 22%, rgba(46,230,166,.28), transparent 60%),
    radial-gradient(42% 50% at 82% 28%, rgba(20,160,110,.32), transparent 60%),
    radial-gradient(50% 55% at 60% 88%, rgba(8,90,62,.42), transparent 62%),
    linear-gradient(160deg,#04130d 0%,#072018 55%,#03100b 100%);
  animation:drift 24s ease-in-out infinite alternate;filter:saturate(1.15)}}
@keyframes drift{{0%{{transform:translate(0,0) scale(1.05)}}100%{{transform:translate(-3%,-3%) scale(1.18)}}}}
{forest_overlay()}
.amb{{position:fixed;inset:0;z-index:-1;pointer-events:none;overflow:hidden}}
.amb i{{position:absolute;bottom:-30px;width:7px;height:7px;border-radius:50%;
  background:radial-gradient(circle,#7cf2a8,rgba(124,242,168,0));opacity:.6;animation:rise linear infinite}}
@keyframes rise{{0%{{transform:translateY(0)}}100%{{transform:translateY(-115vh)}}}}

.block-container{{max-width:1120px;padding-top:.8rem}}
.block-container,.block-container p,.block-container li,.block-container label,
[data-testid="stMarkdownContainer"],[data-testid="stMarkdownContainer"] *{{color:#e9f6ee !important}}
[data-testid="stCaptionContainer"],.block-container small{{color:#a9d2bd !important}}
h1,h2,h3,h4{{font-family:'Trebuchet MS',Verdana,sans-serif !important;font-weight:800 !important;color:#fff !important}}

/* TOP NAV */
.nav-brand{{display:flex;align-items:center;gap:9px;font-weight:800;font-size:21px;color:#fff;padding-top:6px}}
.nav-leaf{{width:28px;height:28px;border-radius:50%;background:linear-gradient(135deg,#34e89e,#1ba35d);
  display:flex;align-items:center;justify-content:center;box-shadow:0 0 16px rgba(52,232,158,.5)}}

/* HERO */
.hero{{position:relative;overflow:hidden;border-radius:24px;padding:34px 30px 30px;margin:4px 0 18px;text-align:center;
  background:linear-gradient(120deg,rgba(11,75,52,.78),rgba(20,160,110,.42));
  border:1px solid rgba(255,255,255,.16);box-shadow:0 26px 70px -34px rgba(0,0,0,.8)}}
.hero .emb{{display:flex;justify-content:center;margin-bottom:4px}}
.hero .name{{font-size:46px;font-weight:900;line-height:1;margin:2px 0 6px;
  background:linear-gradient(92deg,#bff7d3,#39e0a0 60%,#9ff5c8);-webkit-background-clip:text;background-clip:text;color:transparent}}
.hero .sub{{font-size:24px;font-weight:800;color:#eafff2;letter-spacing:.02em}}
.hero .tag{{font-size:15px;color:#cdeaDB;margin-top:6px}}

/* glass cards + hover */
[data-testid="stVerticalBlockBorderWrapper"]{{background:rgba(255,255,255,.07) !important;border:1px solid rgba(255,255,255,.14) !important;
  border-radius:18px !important;backdrop-filter:blur(10px);box-shadow:0 18px 50px -26px rgba(0,0,0,.75);
  transition:transform .18s ease, box-shadow .18s ease, border-color .18s ease}}
[data-testid="stVerticalBlockBorderWrapper"]:hover{{transform:translateY(-4px);border-color:rgba(57,224,160,.55) !important}}

.stat{{background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.14);border-radius:14px;padding:14px;text-align:center}}
.stat .n{{font-size:24px;font-weight:900;color:#7cf2a8;line-height:1}}
.stat .l{{font-size:11px;color:#a9d2bd;margin-top:5px;letter-spacing:.05em;text-transform:uppercase}}

.stTextInput input,[data-baseweb="input"] input{{background:rgba(255,255,255,.10) !important;color:#eafff2 !important;border-color:rgba(255,255,255,.18) !important}}
[data-testid="stFileUploaderDropzone"]{{background:rgba(255,255,255,.06) !important}}
.stRadio [role="radiogroup"]{{gap:6px}}

.stButton>button{{border-radius:12px;border:1px solid rgba(255,255,255,.16);background:rgba(255,255,255,.08);
  color:#eafff2 !important;font-weight:700;transition:all .15s}}
.stButton>button:hover{{border-color:#39e0a0;transform:translateY(-1px)}}
.stButton>button[kind="primary"]{{background:linear-gradient(92deg,#1ec98a,#34e89e) !important;color:#06241a !important;border:none}}

.rl-ticker{{position:relative;overflow:hidden;height:42px;display:flex;align-items:center;
  background:linear-gradient(90deg,rgba(11,75,52,.92),rgba(20,160,110,.85));
  border:1px solid rgba(255,255,255,.14);border-radius:14px;margin:0 0 12px}}
.rl-badge{{position:absolute;left:0;top:0;bottom:0;z-index:3;display:flex;align-items:center;gap:7px;
  background:#06241a;color:#7cf2a8 !important;font-weight:800;font-size:12px;letter-spacing:.12em;padding:0 16px}}
.rl-badge .pulse{{width:8px;height:8px;border-radius:50%;background:#7cf2a8;animation:pls 1.2s ease-in-out infinite}}
@keyframes pls{{0%,100%{{opacity:.4;transform:scale(.8)}}50%{{opacity:1;transform:scale(1.2)}}}}
.rl-track{{overflow:hidden;width:100%;margin-left:118px}}
.rl-tk{{display:inline-flex;white-space:nowrap;animation:marq 26s linear infinite}}
.rl-tk:hover{{animation-play-state:paused}}
.rl-tk span{{color:#eafff2;font-weight:600;font-size:14px}}.rl-tk b{{color:#7cf2a8;margin:0 14px}}
@keyframes marq{{from{{transform:translateX(0)}}to{{transform:translateX(-50%)}}}}

.rl-img{{height:128px;display:flex;align-items:center;justify-content:center;background:rgba(255,255,255,.05);border-radius:12px;margin-bottom:8px;overflow:hidden}}
.rl-tag{{display:inline-block;font-size:11px;font-weight:700;padding:3px 9px;border-radius:999px;background:rgba(52,232,158,.18);color:#9ff5c8 !important}}
.rl-tag.rec{{background:rgba(80,200,210,.16);color:#9fe8e0 !important}}
.rl-name{{font-weight:800;font-size:16px;color:#fff !important;margin:6px 0 2px}}
.rl-meta{{font-size:12px;color:#a9d2bd !important}}
.rl-buyer{{display:inline-block;font-size:11px;font-weight:600;color:#9ff5c8 !important;background:rgba(52,232,158,.14);padding:2px 8px;border-radius:999px;margin-top:3px}}
.rl-price{{display:inline-block;font-weight:900;font-size:16px;color:#06241a !important;margin-top:6px;background:linear-gradient(92deg,#bff7d3,#39e0a0);padding:4px 12px;border-radius:999px}}
.crumb{{color:#9ff5c8 !important;font-weight:700;letter-spacing:.03em}}
hr{{margin:.7rem 0;border-color:rgba(255,255,255,.12)}}
</style>
<div class="amb"><i style="left:9%;animation-duration:16s"></i><i style="left:26%;animation-duration:22s;animation-delay:5s"></i>
<i style="left:44%;animation-duration:18s;animation-delay:9s"></i><i style="left:63%;animation-duration:25s;animation-delay:2s"></i>
<i style="left:80%;animation-duration:20s;animation-delay:12s"></i><i style="left:92%;animation-duration:23s;animation-delay:7s"></i></div>
""", unsafe_allow_html=True)

def ticker():
    run = "".join(f"<span>{f}</span><b>•</b>" for f in FACTS)
    st.markdown("<div class='rl-ticker'><div class='rl-badge'><span class='pulse'></span>ECO FACTS</div>"
                f"<div class='rl-track'><div class='rl-tk'>{run}{run}</div></div></div>", unsafe_allow_html=True)

def topnav():
    """Custom horizontal nav — replaces the Streamlit sidebar."""
    c = st.columns([2.4, 1, 1.3, 1, 1, 1.05, 1])
    c[0].markdown("<div class='nav-brand'><span class='nav-leaf'>🌱</span> ReLoop</div>", unsafe_allow_html=True)
    nav = [("Home", "home"), ("Marketplace", "market"), ("Sell", "sell"),
           ("Cart", "cart"), ("Profile", "account")]
    for (label, page), col in zip(nav, c[1:6]):
        active = st.session_state.page == page or (page == "market" and st.session_state.page == "market")
        if col.button(label, key=f"tn_{page}", use_container_width=True,
                      type="primary" if active else "secondary"):
            if page == "market":
                st.session_state.mk_lane = None; st.session_state.mk_cat = None
            go(page); st.rerun()
    if c[6].button("Log out", key="tn_out", use_container_width=True):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()

def head():
    ticker(); topnav(); st.write("")

def stat(col, n, label):
    col.markdown(f"<div class='stat'><div class='n'>{n}</div><div class='l'>{label}</div></div>", unsafe_allow_html=True)

# ======================================================================
# ITEM CARD
# ======================================================================
def item_card(it, col, buyable=True):
    with col:
        with st.container(border=True):
            item_image(it)
            tagcls = "rl-tag" if it["lane"] == "reuse" else "rl-tag rec"
            tagtxt = "REUSE" if it["lane"] == "reuse" else "BY WEIGHT"
            st.markdown(f"<span class='{tagcls}'>{tagtxt}</span> {badge(it.get('cond'))}"
                        f"<div class='rl-name'>{it.get('title') or ''}</div>"
                        f"<div class='rl-meta'>{it.get('cat') or ''} · {it.get('meta') or ''}</div>", unsafe_allow_html=True)
            if it.get("buyer"):
                st.markdown(f"<div class='rl-buyer'>Bought by {it['buyer']}</div>", unsafe_allow_html=True)
            price = it.get("price") or "" if it["lane"] == "reuse" else f"{it.get('price') or ''} · {it.get('weight','')}"
            st.markdown(f"<span class='rl-price'>{price}</span>", unsafe_allow_html=True)
            st.caption(f"about {it['kg']} kg kept from landfill")
            if not buyable:
                return
            st.write("")
            if it["id"] in bought_ids():
                st.success("Purchased")
            elif it["id"] in cart_ids():
                st.button("In cart", key=f"in_{it['id']}", use_container_width=True, disabled=True)
            elif st.button("Add to cart", key=f"add_{it['id']}", use_container_width=True, type="primary"):
                st.session_state.cart.append(it); st.rerun()

# ======================================================================
# PAGES
# ======================================================================
def page_auth():
    ticker()
    st.markdown(f"<div class='hero'><div class='emb'>{LOOP}</div>"
                "<div class='name'>ReLoop</div><div class='sub'>Buy · Reuse · Recycle</div>"
                "<div class='tag'>Keeping useful materials out of landfills and in the loop.</div></div>",
                unsafe_allow_html=True)
    t1, t2 = st.tabs(["Log in", "Sign up"])
    with t1:
        e = st.text_input("Email", key="li")
        st.text_input("Password", type="password", key="lp")
        if st.button("Log in", type="primary", use_container_width=True):
            if e.strip():
                st.session_state.user = {"name": e.split("@")[0].replace(".", " ").replace("_", " ")}
                go("home"); st.rerun()
            else: st.warning("Enter your email to continue.")
    with t2:
        e = st.text_input("Email", key="si")
        p = st.text_input("Create a password", type="password", key="sp")
        if st.button("Continue", type="primary", use_container_width=True):
            if not e.strip(): st.warning("Enter your email to continue.")
            elif len(p) < 6: st.warning("Password needs at least 6 characters.")
            else:
                st.session_state.user = {"email": e}; go("setup"); st.rerun()

def page_setup():
    ticker()
    st.markdown("### Tell us who you are")
    name = st.text_input("Full name")
    prof = st.radio("You are a…", ["Household", "Maker / Student", "Daycare / School / NGO",
        "Small business / Workshop", "Recycler / Scrap dealer", "Refurbisher / Reseller", "Other"])
    city = st.text_input("City", placeholder="e.g. Hyderabad")
    if st.button("Enter ReLoop", type="primary"):
        if not name.strip(): st.warning("Add your name.")
        else:
            st.session_state.user = {"name": name, "prof": prof, "city": city}; go("home"); st.rerun()

def page_home():
    head()
    st.markdown(f"<div class='hero'><div class='emb'>{LOOP}</div>"
                "<div class='name'>ReLoop</div><div class='sub'>Buy · Reuse · Recycle</div>"
                "<div class='tag'>Keeping useful materials out of landfills and in the loop.</div></div>",
                unsafe_allow_html=True)

    st.markdown("#### What would you like to do?")
    a, b = st.columns(2)
    with a:
        with st.container(border=True):
            st.markdown("### Browse marketplace")
            st.write("Find reusable goods and recyclable materials. Pick Reuse or Recycle, then a category.")
            if st.button("Browse marketplace", type="primary", use_container_width=True):
                st.session_state.mk_lane = None; st.session_state.mk_cat = None
                go("market"); st.rerun()
    with b:
        with st.container(border=True):
            st.markdown("### Sell an item")
            st.write("List something you're done with — it appears in the marketplace instantly.")
            if st.button("Sell an item", use_container_width=True):
                go("sell"); st.rerun()

    st.write("")
    c1, c2, c3 = st.columns(3)
    stat(c1, f"{len(st.session_state.cart)}", "In your cart")
    stat(c2, f"{cart_kg():.0f} kg", "Cart will save")
    stat(c3, f"{saved_kg():.0f} kg", "You've saved")

def page_market():
    head()
    lane, cat = st.session_state.mk_lane, st.session_state.mk_cat

    # level 1 — choose lane
    if not lane:
        st.markdown("## Marketplace")
        st.caption("First, what are you after?")
        a, b = st.columns(2)
        for col, lk in zip((a, b), ("reuse", "recycle")):
            with col:
                with st.container(border=True):
                    st.markdown(f"### {LANES[lk]['label']}")
                    st.write(LANES[lk]["desc"])
                    if st.button(f"Browse {LANES[lk]['label']}", key=f"lane_{lk}",
                                 type="primary", use_container_width=True):
                        st.session_state.mk_lane = lk; st.rerun()
        return

    # level 2 — choose category
    if not cat:
        st.markdown(f"<span class='crumb'>Marketplace › {LANES[lane]['label']}</span>", unsafe_allow_html=True)
        if st.button("← Back"):
            st.session_state.mk_lane = None; st.rerun()
        st.markdown(f"## {LANES[lane]['label']} — pick a category")
        cats = LANES[lane]["cats"]
        for r in range(0, len(cats), 3):
            for (cid, name), col in zip(cats[r:r+3], st.columns(3)):
                with col:
                    with st.container(border=True):
                        st.markdown(illo(cid), unsafe_allow_html=True)
                        n = len([i for i in all_items() if i["cid"] == cid])
                        st.markdown(f"<div class='rl-name'>{name or ''}</div>"
                                    f"<div class='rl-meta'>{n} item(s)</div>", unsafe_allow_html=True)
                        st.write("")
                        if st.button("Open", key=f"cat_{cid}", use_container_width=True, type="primary"):
                            st.session_state.mk_cat = cid; st.rerun()
        return

    # level 3 — items
    st.markdown(f"<span class='crumb'>Marketplace › {LANES[lane]['label']} › {CAT_NAME[cat]}</span>", unsafe_allow_html=True)
    if st.button("← Back to categories"):
        st.session_state.mk_cat = None; st.rerun()
    st.markdown(f"## {CAT_NAME[cat]}")
    q = st.text_input("Search", placeholder="Search items…", key=f"q_{cat}")
    items = [i for i in all_items() if i["cid"] == cat]
    if q.strip():
        items = [i for i in items if q.lower() in i["title"].lower()]
    st.caption(f"{len(items)} item(s)")
    if not items:
        st.info("Nothing here yet.")
    for r in range(0, len(items), 3):
        for it, col in zip(items[r:r+3], st.columns(3)):
            item_card(it, col)

def page_sell():
    head()
    st.markdown("## Sell an item")
    st.caption("All fields are required, including a photo. It shows in the marketplace right after.")
    lane = "reuse" if st.radio("Is it still usable, or only good for material?",
        ["Still usable (Reuse)", "Spent — by weight (Recycle)"], horizontal=True).startswith("Still") else "recycle"
    cat_label = st.radio("Category", [CAT_NAME[c] for c, _ in LANES[lane]["cats"]], horizontal=True)
    cid = next(c for c in CAT_NAME if CAT_NAME[c] == cat_label)

    title = st.text_input("Item name")
    photo = st.file_uploader("Photo (required)", type=["png", "jpg", "jpeg"])
    if photo is not None:
        st.image(photo, width=220, caption="Preview")
    if lane == "reuse":
        qty = st.text_input("Lot size / quantity", placeholder="e.g. 25 pieces")
        cond = st.radio("Condition", ["Like new", "Good, fully usable", "Worn but works"], horizontal=True)
        price = st.text_input("Price (₹)", placeholder="e.g. 450")
    else:
        weight = st.text_input("Approx. weight available", placeholder="e.g. 25 kg")
        cond = st.radio("Quality", ["Clean & sorted", "Mixed", "Contaminated"], horizontal=True)
        rate = st.text_input("Rate (₹ / kg)", placeholder="e.g. 18")
    note = st.text_input("Notes", placeholder="who it suits / sorting details")

    if st.button("List it on the marketplace", type="primary"):
        miss = []
        if not title.strip(): miss.append("name")
        if photo is None: miss.append("photo")
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
            st.session_state.mk_lane = lane; st.session_state.mk_cat = cid
            st.success("Listed! Taking you to it in the marketplace…")
            go("market"); st.rerun()

def page_cart():
    head()
    st.markdown("## Your cart")
    cart = st.session_state.cart
    if not cart:
        st.info("Your cart is empty.")
        if st.button("Go to marketplace", type="primary"):
            st.session_state.mk_lane = None; st.session_state.mk_cat = None; go("market"); st.rerun()
        return
    st.success(f"Checking out this cart keeps about {cart_kg():.0f} kg of material out of a landfill.")
    for idx, it in enumerate(list(cart)):
        with st.container(border=True):
            a, b, c = st.columns([1, 3, 1])
            with a: item_image(it)
            b.markdown(f"<div class='rl-name'>{it['title']}</div>"
                       f"<div class='rl-meta'>{it['cat']} · {'Reuse' if it['lane']=='reuse' else 'Recycle'}</div>"
                       f"{badge(it.get('cond'))} <span class='rl-price'>{it['price']}</span>", unsafe_allow_html=True)
            if c.button("Remove", key=f"rm_{idx}"):
                st.session_state.cart.pop(idx); st.rerun()
    st.divider()
    st.markdown(f"### Total: {len(cart)} item(s) · about {cart_kg():.0f} kg saved")
    if st.button("Checkout", type="primary", use_container_width=True):
        st.session_state.purchased.extend(cart); st.session_state.cart = []
        st.success("Done — counted in your impact.")
        go("account"); st.rerun()

def page_account():
    head()
    u = st.session_state.user
    st.markdown(f"<div class='hero'><div class='name' style='font-size:34px'>{u.get('name','My profile')}</div>"
                f"<div class='tag'>{' · '.join([x for x in [u.get('prof'), u.get('city')] if x]) or 'Your ReLoop profile'}</div></div>",
                unsafe_allow_html=True)
    bought, posted = st.session_state.purchased, st.session_state.posted
    c1, c2, c3 = st.columns(3)
    stat(c1, len(bought), "Items purchased")
    stat(c2, len(posted), "Items listed")
    stat(c3, f"{saved_kg():.0f} kg", "Kept from landfill")
    st.caption("Counts are exact. Weight is an estimate from a fixed average per category "
               "(clothing lot ≈ 5 kg, furniture ≈ 12 kg, wood ≈ 9 kg) — no random numbers.")
    st.write(""); st.markdown("### Items you've purchased")
    if not bought: st.info("Nothing purchased yet.")
    else:
        for r in range(0, len(bought), 3):
            for it, col in zip(bought[r:r+3], st.columns(3)): item_card(it, col, buyable=False)
    st.write(""); st.markdown("### Items you've listed")
    if not posted: st.info("You haven't listed anything yet.")
    else:
        for r in range(0, len(posted), 3):
            for it, col in zip(posted[r:r+3], st.columns(3)): item_card(it, col, buyable=False)

# ======================================================================
# ROUTER
# ======================================================================
{
    "auth": page_auth, "setup": page_setup, "home": page_home, "market": page_market,
    "sell": page_sell, "cart": page_cart, "account": page_account,
}.get(st.session_state.page, page_auth)()

st.markdown("<div style='text-align:center;color:#6f9a85;font-size:11px;margin-top:30px'>"
            "ReLoop build v3 · top-nav + drill-down</div>", unsafe_allow_html=True)
