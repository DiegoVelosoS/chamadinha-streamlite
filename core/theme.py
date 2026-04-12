from __future__ import annotations

import streamlit as st


THEME_STATE_KEY = "main_theme"


def _ensure_theme_state() -> None:
    if THEME_STATE_KEY not in st.session_state:
        st.session_state[THEME_STATE_KEY] = "escuro"


def get_current_theme() -> str:
    _ensure_theme_state()
    return "claro" if st.session_state[THEME_STATE_KEY] == "claro" else "escuro"


def is_light_theme() -> bool:
    return get_current_theme() == "claro"


def render_theme_toggle(location: str = "sidebar") -> bool:
    _ensure_theme_state()
    toggle_value = st.session_state[THEME_STATE_KEY] == "claro"

    if location == "main":
        is_light = st.toggle(
            "Tema claro",
            value=toggle_value,
            help="Desative para usar o tema escuro atual.",
        )
    else:
        is_light = st.sidebar.toggle(
            "Tema claro",
            value=toggle_value,
            help="Desative para usar o tema escuro atual.",
        )

    st.session_state[THEME_STATE_KEY] = "claro" if is_light else "escuro"
    return is_light


def apply_current_theme() -> str:
    theme = get_current_theme()
    if theme == "claro":
        apply_light_theme()
    else:
        apply_black_theme()
    return theme


def setup_theme(show_toggle: bool = False, toggle_location: str = "sidebar") -> str:
    if show_toggle:
        render_theme_toggle(location=toggle_location)
    return apply_current_theme()


def get_theme_tokens(theme: str | None = None) -> dict[str, str]:
    current_theme = theme or get_current_theme()

    if current_theme == "claro":
        return {
            "text_primary": "#0F172A",
            "text_muted": "#334155",
            "chart_presence": "#2563EB",
            "chart_absence": "#DC2626",
            "chart_axis": "#0F172A",
            "chart_grid": "#B9CCE3",
            "chart_background": "#EAF2FB",
        }

    return {
        "text_primary": "#E6ECF8",
        "text_muted": "rgba(250,250,250,0.75)",
        "chart_presence": "#60A5FA",
        "chart_absence": "#F87171",
        "chart_axis": "#E5E7EB",
        "chart_grid": "#334155",
        "chart_background": "#0B0F17",
    }


def apply_black_theme() -> None:
    st.markdown(
        """
        <style>
            :root {
                color-scheme: dark;
            }

            [data-testid="stAppViewContainer"],
            [data-testid="stHeader"] {
                background: #0b0f17;
            }

            [data-testid="stSidebar"] {
                background: #111827;
            }

            [data-testid="stSidebar"] * {
                color: #e6ecf8;
            }

            [data-testid="stMarkdownContainer"] a {
                color: #8ab4ff;
            }

            [data-testid="stTextInputRootElement"] input,
            [data-testid="stNumberInput"] input,
            [data-baseweb="select"] > div,
            textarea {
                background: #111827;
                color: #e6ecf8;
                border-color: #30405f;
            }

            /* Keep buttons readable in all states */
            .stButton > button,
            .stDownloadButton > button,
            .stFormSubmitButton > button {
                background: #0b1f3f;
                color: #ffffff;
                border: 1px solid #2f4f87;
            }

            .stButton > button:hover,
            .stDownloadButton > button:hover,
            .stFormSubmitButton > button:hover {
                background: #15366e;
                color: #ffffff;
                border-color: #4f75b8;
            }

            .stButton > button:focus,
            .stDownloadButton > button:focus,
            .stFormSubmitButton > button:focus {
                outline: 2px solid #7aa2ff;
                outline-offset: 1px;
            }

            .stButton > button:disabled,
            .stDownloadButton > button:disabled,
            .stFormSubmitButton > button:disabled {
                background: #1b1b1b;
                color: #a8a8a8;
                border-color: #3a3a3a;
                opacity: 1;
                cursor: not-allowed;
            }

            [data-testid="stDataFrame"],
            [data-testid="stTable"] {
                border: 1px solid #2a354d;
                border-radius: 8px;
                overflow: hidden;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def apply_light_theme() -> None:
    st.markdown(
        """
        <style>
            /* Fundo principal */
            [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
                background: #f8fafc;
            }

            /* Fundo da sidebar */
            [data-testid="stSidebar"] {
                background: #e5eaf3;
            }

            /* Texto principal */
            body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"] * {
                color: #1a202c;
            }

            /* Botões principais */
            .stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {
                background: #2563eb;
                color: #f8fafc;
                border: 1px solid #2563eb;
            }

            .stButton > button:hover, .stDownloadButton > button:hover, .stFormSubmitButton > button:hover {
                background: #1d4ed8;
                color: #f8fafc;
                border-color: #1d4ed8;
            }

            .stButton > button:disabled, .stDownloadButton > button:disabled, .stFormSubmitButton > button:disabled {
                background: #e0e7ef;
                color: #b6c6d8;
                border-color: #e0e7ef;
                opacity: 1;
                cursor: not-allowed;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
