"""
theme.py
========
One place for the look of the whole app.

* Colours follow the active Streamlit theme, which by default follows the operating-system
  setting (light or dark). If the theme cannot be read, CSS `prefers-color-scheme` is used.
* Serif typography is applied to text only. Icon glyphs (sidebar arrows, expander chevrons) keep
  their own icon font, which is what stops names such as "keyboard_double_arrow_right" or
  "expand_more" from showing up as text.
* Cards: any `st.container(key="card_...")` is drawn as a raised, shadowed panel.
"""

from __future__ import annotations

import html

import streamlit as st

LIGHT = {
    "bg1": "#f5f8fc", "bg2": "#e6edf5", "surface": "#ffffff", "surface2": "#f4f8fc",
    "ink": "#17324d", "muted": "#5a7085", "accent": "#244d6b", "accent2": "#3f86b5",
    "accent_dk": "#15344b", "on_accent": "#ffffff", "border": "#d3dfeb", "hl": "rgba(255,255,255,.95)",
    "sh1": "rgba(23,50,77,.10)", "sh2": "rgba(23,50,77,.16)", "sh3": "rgba(23,50,77,.20)",
    "inset": "rgba(23,50,77,.10)", "sb1": "#132b43", "sb2": "#1d4260", "good": "#2b8a68",
    "hero1": "#17324d", "hero2": "#315f7e", "panel": "#eef3f9",
}
DARK = {
    "bg1": "#0a1119", "bg2": "#101b28", "surface": "#162333", "surface2": "#121f2e",
    "ink": "#e9f1f9", "muted": "#97abbd", "accent": "#4c98cc", "accent2": "#7fc2ee",
    "accent_dk": "#2a6a98", "on_accent": "#06121c", "border": "#27394d", "hl": "rgba(255,255,255,.07)",
    "sh1": "rgba(0,0,0,.35)", "sh2": "rgba(0,0,0,.45)", "sh3": "rgba(0,0,0,.55)",
    "inset": "rgba(0,0,0,.45)", "sb1": "#080e15", "sb2": "#122233", "good": "#4cc49b",
    "hero1": "#0f2234", "hero2": "#24506f", "panel": "#0f1b29",
}


def _vars(palette):
    return "".join(f"--{k.replace('_', '-')}:{v};" for k, v in palette.items())


def _active_mode():
    """'light', 'dark' or None when the front end has not reported a theme."""
    try:
        mode = st.context.theme.type
        if mode in ("light", "dark"):
            return mode
    except Exception:
        pass
    return None


_CSS = r"""
<style>
/*VARS*/

/* ---------- typography (text only; icons are restored below) ---------- */
.stApp, .stApp p, .stApp li, .stApp label, .stApp input, .stApp textarea, .stApp button,
.stApp select, .stApp span, .stApp div, .stApp summary, .stApp td, .stApp th,
.stApp [data-baseweb], [data-testid="stMarkdownContainer"], [data-testid="stCaptionContainer"] {
    font-family: Georgia, "Times New Roman", serif;
}
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
    font-family: Georgia, "Times New Roman", serif !important;
    letter-spacing: -0.02em;
    color: var(--ink);
}
/* Icon glyphs must keep the icon font, otherwise the ligature name is printed as text. */
.stApp [data-testid="stIconMaterial"],
.stApp [data-testid="stIconMaterial"] *,
.stApp .material-icons, .stApp .material-symbols-rounded,
.stApp .material-symbols-outlined, .stApp span[class*="material-symbols"],
.stApp span[class*="material-icons"] {
    font-family: "Material Symbols Rounded", "Material Symbols Outlined", "Material Icons" !important;
    font-feature-settings: "liga" 1;
    letter-spacing: normal !important;
}

/* ---------- canvas ---------- */
[data-testid="stAppViewContainer"] { background: linear-gradient(180deg, var(--bg1) 0%, var(--bg2) 100%); }
[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 2.2rem; max-width: 1280px; }

/* ---------- sidebar ---------- */
[data-testid="stSidebar"] { background: linear-gradient(180deg, var(--sb1) 0%, var(--sb2) 100%); }
[data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] a,
[data-testid="stSidebar"] label, [data-testid="stSidebar"] div, [data-testid="stSidebar"] li {
    color: #eef3f9;
}
[data-testid="stSidebar"] [aria-current="page"] { background: rgba(255,255,255,.16); border-radius: 8px; }
[data-testid="stSidebar"] a:hover { background: rgba(255,255,255,.08); border-radius: 8px; }

/* ---------- raised cards ---------- */
[class*="st-key-card_"] {
    background: linear-gradient(180deg, var(--surface) 0%, var(--surface2) 100%);
    border: 1px solid var(--border);
    border-top: 4px solid var(--accent);
    border-radius: 16px;
    padding: 1.15rem 1.35rem 1.3rem 1.35rem;
    box-shadow:
        inset 0 1px 0 var(--hl),
        0 1px 2px var(--sh1),
        0 8px 16px -6px var(--sh2),
        0 26px 40px -22px var(--sh3);
    transition: transform .18s ease, box-shadow .18s ease;
}
[class*="st-key-card_"]:hover {
    transform: translateY(-2px);
    box-shadow:
        inset 0 1px 0 var(--hl),
        0 2px 3px var(--sh1),
        0 14px 24px -8px var(--sh2),
        0 34px 48px -22px var(--sh3);
}
[class*="st-key-card_result"] { border-top-color: var(--good); }
[class*="st-key-card_report"] { border-top-color: var(--accent2); }

.ct { display: flex; align-items: center; gap: .8rem; margin: .1rem 0 .55rem 0; }
.ct-badge {
    flex: 0 0 auto; width: 2.1rem; height: 2.1rem; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 1rem; color: var(--on-accent);
    background: radial-gradient(circle at 30% 25%, var(--accent2), var(--accent) 70%);
    box-shadow: inset 0 1px 1px rgba(255,255,255,.45), inset 0 -3px 5px rgba(0,0,0,.22),
                0 3px 6px var(--sh2);
}
.ct-title { font-size: 1.2rem; font-weight: 700; color: var(--ink); line-height: 1.2; }
.ct-sub { font-size: .86rem; color: var(--muted); margin-top: .1rem; line-height: 1.3; }

/* recessed panels */
.eq-box {
    background: var(--panel); border: 1px solid var(--border); border-radius: 12px;
    padding: .85rem 1rem; margin: .3rem 0 .7rem 0; text-align: center; color: var(--ink);
    font-size: 1.12rem; font-style: italic; letter-spacing: .01em;
    box-shadow: inset 0 3px 7px var(--inset), inset 0 -1px 0 var(--hl);
}
.stat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: .6rem; margin: .4rem 0 .6rem 0; }
.stat {
    background: var(--panel); border: 1px solid var(--border); border-radius: 12px; padding: .55rem .75rem;
    box-shadow: inset 0 2px 5px var(--inset);
}
.stat-l { font-size: .74rem; color: var(--muted); }
.stat-v { font-size: 1.05rem; font-weight: 700; color: var(--ink); word-break: break-word; }

/* hero banner */
.hero {
    padding: 1.7rem 2rem; border-radius: 18px; margin-bottom: 1.5rem; color: #fff;
    background: linear-gradient(120deg, var(--hero1) 0%, var(--hero2) 100%);
    box-shadow: inset 0 1px 0 rgba(255,255,255,.25), 0 14px 30px -12px var(--sh3);
}
.hero-eyebrow { font-size: .8rem; letter-spacing: .14em; text-transform: uppercase; opacity: .8; margin-bottom: .5rem; }
.hero-title { font-size: 2.1rem; font-weight: 600; line-height: 1.2; font-family: Georgia, "Times New Roman", serif; }
.hero-sub { font-size: 1.02rem; opacity: .9; margin-top: .6rem; max-width: 820px; }

/* ---------- widgets ---------- */
div[data-testid="stMetric"] {
    background: linear-gradient(180deg, var(--surface), var(--surface2));
    border: 1px solid var(--border); padding: 14px 18px; border-radius: 14px;
    box-shadow: inset 0 1px 0 var(--hl), 0 6px 14px -6px var(--sh2);
}
div[data-baseweb="input"], div[data-baseweb="select"] > div, div[data-baseweb="textarea"] {
    border-radius: 10px !important;
    box-shadow: inset 0 2px 4px var(--inset);
}
div.stButton > button, div[data-testid="stFormSubmitButton"] > button,
div[data-testid="stDownloadButton"] > button {
    border-radius: 10px; font-weight: 600; padding: .55rem 1.2rem;
    border: 1px solid var(--accent-dk);
    background: linear-gradient(180deg, var(--accent2) 0%, var(--accent) 100%);
    color: var(--on-accent);
    box-shadow: inset 0 1px 0 rgba(255,255,255,.35), 0 4px 0 var(--accent-dk), 0 9px 14px -4px var(--sh3);
    transition: transform .12s ease, box-shadow .12s ease, filter .12s ease;
}
div.stButton > button p, div[data-testid="stDownloadButton"] > button p { color: var(--on-accent); }
div.stButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover,
div[data-testid="stDownloadButton"] > button:hover {
    filter: brightness(1.06); transform: translateY(-1px); color: var(--on-accent);
    border-color: var(--accent-dk);
}
div.stButton > button:active, div[data-testid="stDownloadButton"] > button:active {
    transform: translateY(3px);
    box-shadow: inset 0 1px 0 rgba(255,255,255,.2), 0 1px 0 var(--accent-dk), 0 3px 6px -2px var(--sh3);
}
[data-testid="stDataFrame"], [data-testid="stTable"] {
    border: 1px solid var(--border); border-radius: 12px; overflow: hidden;
    box-shadow: 0 5px 12px -6px var(--sh2);
}
[data-testid="stExpander"] {
    border: 1px solid var(--border); border-radius: 12px; background: var(--surface2);
    box-shadow: inset 0 2px 5px var(--inset);
}
[data-testid="stAlert"] { border-radius: 12px; }
hr { border-color: var(--border); }

@media (max-width: 900px) {
    [class*="st-key-card_"] { padding: 1rem; }
    .hero-title { font-size: 1.6rem; }
}
@media (prefers-reduced-motion: reduce) {
    [class*="st-key-card_"], div.stButton > button { transition: none; }
}
</style>
"""


def apply_theme():
    """Inject the global stylesheet. Call once per run from the entry file."""
    mode = _active_mode()
    if mode == "dark":
        vars_css = f":root{{{_vars(DARK)}}}"
    elif mode == "light":
        vars_css = f":root{{{_vars(LIGHT)}}}"
    else:  # theme not reported yet: let the browser/OS decide
        vars_css = (f":root{{{_vars(LIGHT)}}}"
                    f"@media (prefers-color-scheme: dark){{:root{{{_vars(DARK)}}}}}")
    st.markdown(_CSS.replace("/*VARS*/", vars_css), unsafe_allow_html=True)


def hero(title, subtitle="", eyebrow=""):
    eb = f'<div class="hero-eyebrow">{html.escape(eyebrow)}</div>' if eyebrow else ""
    sub = f'<div class="hero-sub">{html.escape(subtitle)}</div>' if subtitle else ""
    st.markdown(f'<div class="hero">{eb}<div class="hero-title">{html.escape(title)}</div>{sub}</div>',
                unsafe_allow_html=True)


def card_title(number, title, subtitle=""):
    badge = f'<div class="ct-badge">{html.escape(str(number))}</div>' if number != "" else ""
    sub = f'<div class="ct-sub">{html.escape(subtitle)}</div>' if subtitle else ""
    st.markdown(f'<div class="ct">{badge}<div><div class="ct-title">{html.escape(title)}</div>{sub}</div></div>',
                unsafe_allow_html=True)


def equation_box(text):
    st.markdown(f'<div class="eq-box">{html.escape(text)}</div>', unsafe_allow_html=True)


def stat_tiles(items):
    """items: list of (label, value) shown as recessed tiles."""
    tiles = "".join(
        f'<div class="stat"><div class="stat-l">{html.escape(str(l))}</div>'
        f'<div class="stat-v">{html.escape(str(v))}</div></div>' for l, v in items)
    st.markdown(f'<div class="stat-grid">{tiles}</div>', unsafe_allow_html=True)
