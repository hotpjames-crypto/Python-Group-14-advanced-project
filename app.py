# This file name is app.py
# Streamlit entry point for the Country Relocation & Culture Guide app.
# Run this file with:  streamlit run app.py

import streamlit as st

from input import validate_country_name, InvalidCountryNameError
from rest_country_api import (
    get_country_info,
    CountryNotFoundError,
    CountryAPIError,
    timezone_difference,
)
from google_api import generate_travel_guide, generate_comparison, AIRequestError
from Storage import (
    save_country_profile,
    save_travel_guide,
    save_comparison,
    get_all_records,
    delete_record,
    PROFILE,
    GUIDE,
    COMPARISON,
)

# --------------------------------------------------------------------------- #
# Page config + session state
# --------------------------------------------------------------------------- #
st.set_page_config(
    page_title="Country Relocation & Culture Guide",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

_defaults = {
    "theme": "light",
    "country_info": None,
    "guide_text": None,
    "compare_a": None,
    "compare_b": None,
    "tz_diffs": None,
    "comparison_text": None,
    "selected_record_id": None,
}
for key, value in _defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# --------------------------------------------------------------------------- #
# Theming — light/dark palettes applied as CSS variables
# --------------------------------------------------------------------------- #
PALETTES = {
    "light": {
        "bg": "#eef2f5",
        "bg_gradient": "linear-gradient(160deg, #eef2f5 0%, #e6edf0 45%, #e8f0ef 100%)",
        "sidebar_bg": "#ffffff",
        "card_bg": "#ffffff",
        "card_border": "rgba(30, 41, 59, 0.08)",
        "text": "#1e293b",
        "text_muted": "#64748b",
        "accent_from": "#3b82a0",
        "accent_to": "#2d6f8e",
        "accent_text": "#ffffff",
        "ai_bg": "linear-gradient(145deg, #eef6f6 0%, #eaf1f5 100%)",
        "ai_border": "#a9c8d4",
        "shadow": "0 10px 30px rgba(30, 41, 59, 0.06)",
        "input_bg": "#ffffff",
        "input_border": "rgba(30, 41, 59, 0.14)",
        "chip_bg": "rgba(59, 130, 160, 0.10)",
        "chip_text": "#2d6f8e",
        "success_bg": "#eafaf3",
        "success_text": "#0f6b4d",
        "error_bg": "#fdf0ef",
        "error_text": "#9a3b34",
    },
    "dark": {
        "bg": "#0f1417",
        "bg_gradient": "linear-gradient(160deg, #0f1417 0%, #121a1e 45%, #0f1a1c 100%)",
        "sidebar_bg": "#151c20",
        "card_bg": "#171f24",
        "card_border": "rgba(255, 255, 255, 0.07)",
        "text": "#e6edf0",
        "text_muted": "#8fa3ad",
        "accent_from": "#5fa8c4",
        "accent_to": "#4a90ad",
        "accent_text": "#0f1417",
        "ai_bg": "linear-gradient(145deg, #16232a 0%, #142024 100%)",
        "ai_border": "#2f5666",
        "shadow": "0 10px 30px rgba(0, 0, 0, 0.35)",
        "input_bg": "#1a2227",
        "input_border": "rgba(255, 255, 255, 0.12)",
        "chip_bg": "rgba(95, 168, 196, 0.16)",
        "chip_text": "#9fd0e2",
        "success_bg": "rgba(45, 212, 158, 0.12)",
        "success_text": "#6ee7b7",
        "error_bg": "rgba(248, 113, 113, 0.12)",
        "error_text": "#fca5a5",
    },
}


def inject_css(theme: str):
    p = PALETTES[theme]
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}

        [data-testid="stAppViewContainer"], .main, [data-testid="stMain"] {{
            background: {p['bg_gradient']} !important;
        }}
        [data-testid="stHeader"] {{
            background: transparent;
        }}
        .block-container {{
            padding-top: 2rem;
        }}
        [data-testid="stSidebar"] {{
            background: {p['sidebar_bg']};
            border-right: 1px solid {p['card_border']};
        }}
        [data-testid="stSidebar"] * {{
            color: {p['text']} !important;
        }}

        .stApp, .stApp p, .stApp span, .stApp label, .stApp li {{
            color: {p['text']};
        }}
        .stMarkdown, .stMarkdown p {{
            color: {p['text']};
        }}

        h1, h2, h3, h4 {{
            color: {p['text']} !important;
            font-weight: 800 !important;
            letter-spacing: -0.02em;
        }}

        /* Hero header */
        .app-hero {{
            padding: 1.6rem 2rem;
            border-radius: 20px;
            background: linear-gradient(120deg, {p['accent_from']}, {p['accent_to']});
            color: {p['accent_text']} !important;
            box-shadow: {p['shadow']};
            margin-bottom: 1.4rem;
        }}
        .app-hero * {{ color: {p['accent_text']} !important; }}
        .app-hero h1 {{ font-size: 1.9rem; margin: 0 0 0.25rem 0; font-weight: 800 !important; }}
        .app-hero p {{ margin: 0; opacity: 0.92; font-size: 0.98rem; }}

        /* Generic bordered containers -> cards */
        [data-testid="stVerticalBlockBorderWrapper"] {{
            background: {p['card_bg']};
            border-radius: 16px !important;
            border: 1px solid {p['card_border']} !important;
            box-shadow: {p['shadow']};
            padding: 0.2rem 0.2rem;
            position: relative;
            overflow: hidden;
        }}
        [data-testid="stVerticalBlockBorderWrapper"]::before {{
            content: "";
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 3px;
            background: linear-gradient(90deg, {p['accent_from']}, {p['accent_to']});
        }}

        /* AI content card variant, applied via marker class before it */
        .ai-card-marker + div [data-testid="stVerticalBlockBorderWrapper"] {{
            background: {p['ai_bg']} !important;
            border: 1px solid {p['ai_border']} !important;
        }}

        .section-label {{
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            color: {p['chip_text']};
            background: {p['chip_bg']};
            padding: 0.25rem 0.7rem;
            border-radius: 999px;
            margin-bottom: 0.6rem;
        }}

        .muted {{ color: {p['text_muted']}; font-size: 0.88rem; }}

        /* Buttons */
        .stButton > button, .stDownloadButton > button {{
            border-radius: 10px;
            font-weight: 600;
            border: 1px solid {p['card_border']};
            transition: all 0.15s ease;
        }}
        .stButton > button[kind="primary"] {{
            background: linear-gradient(120deg, {p['accent_from']}, {p['accent_to']});
            border: none;
            color: {p['accent_text']};
        }}
        .stButton > button[kind="primary"]:hover {{
            filter: brightness(1.08);
            transform: translateY(-1px);
        }}
        .stButton > button:not([kind="primary"]) {{
            background: {p['card_bg']} !important;
            color: {p['text']} !important;
        }}
        .stButton > button:not([kind="primary"]):hover {{
            border-color: {p['accent_from']};
            color: {p['accent_from']} !important;
        }}
        .stButton > button:disabled, .stButton > button:disabled:hover {{
            background: {p['card_bg']} !important;
            color: {p['text_muted']} !important;
            border-color: {p['card_border']} !important;
            opacity: 0.6;
        }}

        /* Form submit buttons (Search / Compare) share primary-button styling */
        .stFormSubmitButton > button {{
            border-radius: 10px;
            font-weight: 600;
            border: none;
            background: linear-gradient(120deg, {p['accent_from']}, {p['accent_to']});
            color: {p['accent_text']} !important;
            transition: all 0.15s ease;
        }}
        .stFormSubmitButton > button:hover {{
            filter: brightness(1.08);
            transform: translateY(-1px);
        }}

        /* Inputs */
        .stTextInput input, .stSelectbox [data-baseweb="select"] > div {{
            background: {p['input_bg']} !important;
            border-radius: 10px !important;
            border: 1px solid {p['input_border']} !important;
            color: {p['text']} !important;
        }}

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 6px;
            background: {p['card_bg']};
            padding: 6px;
            border-radius: 14px;
            border: 1px solid {p['card_border']};
        }}
        .stTabs [data-baseweb="tab"] {{
            border-radius: 10px;
            padding: 8px 16px;
            color: {p['text_muted']};
            font-weight: 600;
        }}
        .stTabs [aria-selected="true"] {{
            background: linear-gradient(120deg, {p['accent_from']}, {p['accent_to']}) !important;
            color: {p['accent_text']} !important;
        }}

        /* Metrics */
        [data-testid="stMetric"] {{
            background: {p['card_bg']};
            border: 1px solid {p['card_border']};
            border-radius: 12px;
            padding: 0.7rem 0.9rem;
        }}
        [data-testid="stMetricLabel"] {{ color: {p['text_muted']} !important; }}

        hr {{ border-color: {p['card_border']}; }}

        /* Scrollable preview panel */
        .preview-scroll {{
            max-height: 60vh;
            overflow-y: auto;
            padding-right: 0.5rem;
        }}

        /* Library list item */
        .lib-item-active {{
            border-left: 3px solid {p['accent_from']};
            padding-left: 0.6rem;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# --------------------------------------------------------------------------- #
# Small render helpers
# --------------------------------------------------------------------------- #
def hero():
    st.markdown(
        """
        <div class="app-hero">
            <h1>🌍 Country Relocation &amp; Culture Guide</h1>
            <p>Research a country, compare two side by side, and get an AI-crafted
            relocation &amp; travel guide — then save it to your personal library.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def ai_card(icon: str, label: str, body_renderer):
    """Renders a visually distinct card for AI-generated content."""
    st.markdown(f'<div class="ai-card-marker"></div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(f'<span class="section-label">{icon} {label}</span>', unsafe_allow_html=True)
        body_renderer()


def country_info_card(info: dict):
    with st.container(border=True):
        col_flag, col_details = st.columns([1, 2.4], vertical_alignment="center")
        with col_flag:
            flag_url = info.get("Flag Image URL")
            if flag_url and flag_url != "N/A":
                st.image(flag_url, use_container_width=True)
            st.markdown(f"### {info.get('Name', '—')}")
        with col_details:
            m1, m2 = st.columns(2)
            m1.metric("Capital", info.get("Capital", "—"))
            m2.metric("Region", info.get("Region", "—"))
            m3, m4 = st.columns(2)
            m3.metric("Population", info.get("Population", "—"))
            m4.metric("Timezones", info.get("Timezones", "—"))
            st.markdown(
                f"<div class='muted'><b>Languages:</b> {info.get('Languages', '—')}</div>"
                f"<div class='muted'><b>Currencies:</b> {info.get('Currencies', '—')}</div>",
                unsafe_allow_html=True,
            )


def status_banner(ok: bool, message: str):
    theme = PALETTES[st.session_state.theme]
    bg = theme["success_bg"] if ok else theme["error_bg"]
    color = theme["success_text"] if ok else theme["error_text"]
    icon = "✅" if ok else "⚠️"
    st.markdown(
        f"""<div style="background:{bg}; color:{color}; padding:0.6rem 0.9rem;
        border-radius:10px; font-size:0.9rem; margin-top:0.4rem;">{icon} {message}</div>""",
        unsafe_allow_html=True,
    )


# --------------------------------------------------------------------------- #
# Sidebar — theme toggle + navigation hint
# --------------------------------------------------------------------------- #
def sidebar():
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        dark_on = st.toggle("🌙 Dark mode", value=(st.session_state.theme == "dark"))
        st.session_state.theme = "dark" if dark_on else "light"

        st.markdown("---")
        st.markdown("### 📚 Your Library")
        records = get_all_records()
        n_profiles = sum(1 for r in records if r["type"] == PROFILE)
        n_guides = sum(1 for r in records if r["type"] == GUIDE)
        n_compare = sum(1 for r in records if r["type"] == COMPARISON)
        st.markdown(
            f"<div class='muted'>{n_profiles} profile(s) · {n_guides} guide(s) · "
            f"{n_compare} comparison(s) saved</div>",
            unsafe_allow_html=True,
        )
        st.markdown("---")
        st.caption("Data: countries.dev · AI: OpenRouter")


# --------------------------------------------------------------------------- #
# Tab 1 — Research a country
# --------------------------------------------------------------------------- #
def research_tab():
    with st.container(border=True):
        st.markdown('<span class="section-label">🔎 Search</span>', unsafe_allow_html=True)
        with st.form("research_search_form", clear_on_submit=False):
            col_input, col_btn = st.columns([4, 1], vertical_alignment="bottom")
            with col_input:
                name_input = st.text_input(
                    "Country name", placeholder="e.g. Japan, Kenya, Brazil",
                    label_visibility="collapsed", key="research_country_name",
                )
            with col_btn:
                search_clicked = st.form_submit_button("Search", type="primary", use_container_width=True)

    if search_clicked:
        try:
            clean_name = validate_country_name(name_input)
        except InvalidCountryNameError as e:
            status_banner(False, str(e))
        else:
            with st.spinner(f"Looking up {clean_name}..."):
                try:
                    st.session_state.country_info = get_country_info(clean_name)
                    st.session_state.guide_text = None
                except CountryNotFoundError as e:
                    st.session_state.country_info = None
                    status_banner(False, str(e))
                except CountryAPIError as e:
                    st.session_state.country_info = None
                    status_banner(False, f"API problem: {e}")
                except Exception as e:
                    st.session_state.country_info = None
                    status_banner(False, f"Unexpected error: {e}")

    info = st.session_state.country_info
    if not info:
        st.info("Search for a country to see its profile here.")
        return

    st.write("")
    country_info_card(info)

    st.write("")
    col_a, col_b, col_c = st.columns([1.4, 1, 1])
    with col_a:
        generate_clicked = st.button(
            "✨ Generate AI Travel Guide", type="primary", use_container_width=True, key="gen_guide_btn"
        )
    with col_b:
        save_profile_clicked = st.button(
            "💾 Save Profile", use_container_width=True, key="save_profile_btn"
        )
    with col_c:
        save_guide_clicked = st.button(
            "💾 Save Guide", use_container_width=True,
            disabled=not st.session_state.guide_text, key="save_guide_btn",
        )

    if save_profile_clicked:
        ok, msg = save_country_profile(info)
        status_banner(ok, msg)

    if generate_clicked:
        with st.spinner("Generating your guide with AI, please wait..."):
            try:
                st.session_state.guide_text = generate_travel_guide(info)
            except AIRequestError as e:
                st.session_state.guide_text = None
                status_banner(False, str(e))
            except Exception as e:
                st.session_state.guide_text = None
                status_banner(False, f"Unexpected error: {e}")

    if save_guide_clicked and st.session_state.guide_text:
        ok, msg = save_travel_guide(st.session_state.guide_text, country_name=info.get("Name"))
        status_banner(ok, msg)

    if st.session_state.guide_text:
        st.write("")
        ai_card(
            "🧭", "AI-Generated Travel &amp; Relocation Guide",
            lambda: st.markdown(st.session_state.guide_text),
        )


# --------------------------------------------------------------------------- #
# Tab 2 — Compare two countries
# --------------------------------------------------------------------------- #
def compare_tab():
    with st.container(border=True):
        st.markdown('<span class="section-label">⚖️ Compare</span>', unsafe_allow_html=True)
        with st.form("compare_search_form", clear_on_submit=False):
            col_a, col_b, col_btn = st.columns([2, 2, 1], vertical_alignment="bottom")
            with col_a:
                name_a = st.text_input("Country A", placeholder="e.g. Germany", key="compare_a_input")
            with col_b:
                name_b = st.text_input("Country B", placeholder="e.g. Vietnam", key="compare_b_input")
            with col_btn:
                compare_clicked = st.form_submit_button("Compare", type="primary", use_container_width=True)

    if compare_clicked:
        try:
            clean_a = validate_country_name(name_a)
            clean_b = validate_country_name(name_b)
        except InvalidCountryNameError as e:
            status_banner(False, str(e))
        else:
            with st.spinner(f"Looking up {clean_a} and {clean_b}..."):
                try:
                    info_a = get_country_info(clean_a)
                    info_b = get_country_info(clean_b)
                    st.session_state.compare_a = info_a
                    st.session_state.compare_b = info_b
                    st.session_state.tz_diffs = timezone_difference(
                        info_a["Timezones"], info_b["Timezones"]
                    )
                    st.session_state.comparison_text = None
                except CountryNotFoundError as e:
                    st.session_state.compare_a = st.session_state.compare_b = None
                    status_banner(False, str(e))
                except CountryAPIError as e:
                    st.session_state.compare_a = st.session_state.compare_b = None
                    status_banner(False, f"API problem: {e}")
                except Exception as e:
                    st.session_state.compare_a = st.session_state.compare_b = None
                    status_banner(False, f"Unexpected error: {e}")

    info_a, info_b = st.session_state.compare_a, st.session_state.compare_b
    if not (info_a and info_b):
        st.info("Enter two countries to compare their profiles here.")
        return

    st.write("")
    col1, col2 = st.columns(2)
    with col1:
        country_info_card(info_a)
    with col2:
        country_info_card(info_b)

    diffs = st.session_state.tz_diffs
    if diffs:
        st.write("")
        with st.container(border=True):
            st.markdown('<span class="section-label">🕒 Timezone Difference</span>', unsafe_allow_html=True)
            for tz_a, tz_b, diff in diffs:
                st.markdown(f"- **{tz_a}** vs **{tz_b}**: `{diff:+g} hours`")

    st.write("")
    col_a, col_b = st.columns([1.4, 1])
    with col_a:
        gen_compare_clicked = st.button(
            "✨ Generate AI Comparison", type="primary", use_container_width=True, key="gen_compare_btn"
        )
    with col_b:
        save_compare_clicked = st.button(
            "💾 Save Comparison", use_container_width=True,
            disabled=not st.session_state.comparison_text, key="save_compare_btn",
        )

    if gen_compare_clicked:
        with st.spinner("Generating comparison with AI, please wait..."):
            try:
                st.session_state.comparison_text = generate_comparison(
                    info_a["Name"], info_b["Name"]
                )
            except AIRequestError as e:
                st.session_state.comparison_text = None
                status_banner(False, str(e))
            except Exception as e:
                st.session_state.comparison_text = None
                status_banner(False, f"Unexpected error: {e}")

    if save_compare_clicked and st.session_state.comparison_text:
        ok, msg = save_comparison(
            st.session_state.comparison_text, info_a.get("Name"), info_b.get("Name")
        )
        status_banner(ok, msg)

    if st.session_state.comparison_text:
        st.write("")
        ai_card(
            "📊", "AI-Generated Comparison",
            lambda: st.markdown(st.session_state.comparison_text),
        )


# --------------------------------------------------------------------------- #
# Tab 3 — Saved library (profiles + guides + comparisons), with preview
# --------------------------------------------------------------------------- #
TYPE_ICON = {PROFILE: "🗂️", GUIDE: "🧭", COMPARISON: "📊"}
TYPE_LABEL = {PROFILE: "Profile", GUIDE: "Travel Guide", COMPARISON: "Comparison"}


def render_saved_content(record: dict):
    rtype = record["type"]
    content = record["content"]
    if rtype == PROFILE and isinstance(content, dict):
        country_info_card(content)
    else:
        ai_card(
            TYPE_ICON.get(rtype, "📄"),
            TYPE_LABEL.get(rtype, "Saved Item"),
            lambda: st.markdown(str(content)),
        )


def library_tab():
    records = get_all_records()
    if not records:
        st.info("Nothing saved yet. Save a country profile, guide, or comparison to see it here.")
        return

    with st.container(border=True):
        st.markdown('<span class="section-label">🔍 Filter</span>', unsafe_allow_html=True)
        col_f, col_s = st.columns([1, 2])
        with col_f:
            type_filter = st.selectbox(
                "Type", ["All", "Profiles", "Guides", "Comparisons"],
                label_visibility="collapsed",
            )
        with col_s:
            query = st.text_input(
                "Search", placeholder="Search by name...", label_visibility="collapsed"
            )

    type_map = {"Profiles": PROFILE, "Guides": GUIDE, "Comparisons": COMPARISON}
    filtered = records
    if type_filter != "All":
        filtered = [r for r in filtered if r["type"] == type_map[type_filter]]
    if query:
        q = query.lower()
        filtered = [r for r in filtered if q in r["title"].lower()]

    if not filtered:
        st.warning("No saved items match that filter.")
        return

    if st.session_state.selected_record_id not in {r["id"] for r in filtered}:
        st.session_state.selected_record_id = filtered[0]["id"]

    st.write("")
    col_list, col_preview = st.columns([1, 2], gap="medium")

    with col_list:
        with st.container(border=True):
            st.markdown('<span class="section-label">📋 Saved Items</span>', unsafe_allow_html=True)
            for r in filtered:
                icon = TYPE_ICON.get(r["type"], "📄")
                is_active = r["id"] == st.session_state.selected_record_id
                label = f"{icon} {'▸ ' if is_active else ''}{r['title']}"
                if st.button(label, key=f"select_{r['id']}", use_container_width=True):
                    st.session_state.selected_record_id = r["id"]
                st.caption(f"{TYPE_LABEL.get(r['type'], '')} · saved {r['saved_at'][:16].replace('T', ' ')}")

    with col_preview:
        selected = next((r for r in filtered if r["id"] == st.session_state.selected_record_id), None)
        if selected:
            top_col, del_col = st.columns([4, 1])
            with top_col:
                st.markdown(f"#### {TYPE_ICON.get(selected['type'], '📄')} {selected['title']}")
                st.caption(f"Saved on {selected['saved_at'][:16].replace('T', ' ')}")
            with del_col:
                if st.button("🗑️ Delete", key=f"delete_{selected['id']}", use_container_width=True):
                    ok, msg = delete_record(selected["id"])
                    status_banner(ok, msg)
                    st.session_state.selected_record_id = None
                    st.rerun()
            render_saved_content(selected)


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def main():
    sidebar()
    inject_css(st.session_state.theme)
    hero()

    tab_research, tab_compare, tab_library = st.tabs(
        ["🔎 Research a Country", "⚖️ Compare Two Countries", "📚 Saved Profiles & Guides"]
    )
    with tab_research:
        research_tab()
    with tab_compare:
        compare_tab()
    with tab_library:
        library_tab()


if __name__ == "__main__":
    main()