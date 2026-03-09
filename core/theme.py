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
            :root {
                color-scheme: light;
            }

            [data-testid="stAppViewContainer"],
            [data-testid="stHeader"] {
                background: #eef4fb;
            }

            [data-testid="stSidebar"] {
                background: #dbe7f5;
            }

            [data-testid="stSidebar"] * {
                color: #0f172a;
            }

            [data-testid="stSidebarNav"] a {
                color: #0f172a !important;
            }

            [data-testid="stSidebarNav"] a:hover {
                background: #cddcf0;
            }

            [data-testid="stSidebarNav"] a[aria-current="page"] {
                background: #bed0e8;
                color: #0b1736 !important;
                font-weight: 600;
            }

            [data-testid="stAppViewContainer"] {
                --text-color: #0f172a;
                --background-color: #eef4fb;
                --secondary-background-color: #dbe7f5;
                --primary-color: #1d4ed8;
                color: #0f172a;
            }

            [data-testid="stAppViewContainer"] [data-testid="stMarkdownContainer"],
            [data-testid="stAppViewContainer"] [data-testid="stText"],
            [data-testid="stAppViewContainer"] [data-testid="stCaptionContainer"] {
                color: #1e293b;
            }

            [data-testid="stAppViewContainer"] h1,
            [data-testid="stAppViewContainer"] h2,
            [data-testid="stAppViewContainer"] h3,
            [data-testid="stAppViewContainer"] h4,
            [data-testid="stAppViewContainer"] h5,
            [data-testid="stAppViewContainer"] h6 {
                color: #0b1736 !important;
            }

            [data-testid="stAppViewContainer"] p,
            [data-testid="stAppViewContainer"] li,
            [data-testid="stAppViewContainer"] label,
            [data-testid="stAppViewContainer"] .stCaption {
                color: #1e293b !important;
            }

            [data-testid="stMetricLabel"],
            [data-testid="stMetricValue"] {
                color: #0f172a !important;
            }

            [data-testid="stMetricDelta"] {
                color: #1e293b !important;
            }

            [data-testid="stAlert"] * {
                color: #0f172a !important;
            }

            [data-testid="stAlert"] {
                background: #b8cde4;
                border: 1px solid #8eaed0;
            }

            [data-testid="stExpander"] {
                border-color: #9fb8d6;
                background: #e5eef9;
            }

            [data-testid="stExpander"] summary,
            [data-testid="stExpander"] p,
            [data-testid="stExpander"] span,
            [data-testid="stExpander"] label {
                color: #0f172a !important;
            }

            [data-testid="stMarkdownContainer"] a {
                color: #1d4ed8;
            }

            [data-testid="stTextInputRootElement"] input,
            [data-testid="stNumberInput"] input,
            [data-baseweb="select"] > div,
            [data-baseweb="base-input"] input,
            [data-baseweb="textarea"] textarea,
            textarea {
                background: #f4f8fd;
                color: #0f172a;
                border-color: #8eaed0;
            }

            [data-testid="stFileUploaderDropzone"] {
                background: #b8cde4;
                border: 1px solid #8eaed0;
            }

            [data-testid="stFileUploaderDropzone"] * {
                color: #0f172a !important;
            }

            [data-testid="stFileUploaderDropzone"] button {
                background: #c8d9ec !important;
                color: #0f172a !important;
                border: 1px solid #7f9fc4 !important;
            }

            [data-testid="stFileUploaderDropzone"] button:hover {
                background: #b9cfe7 !important;
                border-color: #678db9 !important;
                color: #0f172a !important;
            }

            [data-testid="stFileUploaderDropzone"] button:focus {
                outline: 2px solid #3b6cc2 !important;
                outline-offset: 1px;
            }

            [data-baseweb="select"] svg,
            [data-baseweb="select"] span,
            [data-baseweb="base-input"] svg {
                color: #0f172a;
                fill: #0f172a;
            }

            [data-testid="stSlider"] * {
                color: #0f172a;
            }

            [data-testid="stCheckbox"] label,
            [data-testid="stRadio"] label,
            [data-testid="stSelectbox"] label,
            [data-testid="stTextInput"] label,
            [data-testid="stNumberInput"] label,
            [data-testid="stDateInput"] label,
            [data-testid="stTimeInput"] label,
            [data-testid="stFileUploader"] label,
            [data-testid="stMultiSelect"] label,
            [data-testid="stToggle"] label {
                color: #0f172a !important;
            }

            [data-testid="stTooltipIcon"] {
                color: #334155 !important;
                opacity: 1 !important;
            }

            [data-testid="stTooltipIcon"] svg {
                stroke: #334155 !important;
                fill: none !important;
                opacity: 1 !important;
            }

            [data-testid="stTooltipIcon"] svg path,
            [data-testid="stTooltipIcon"] svg circle {
                stroke: #334155 !important;
            }

            [data-testid="stTooltipHoverTarget"] {
                opacity: 1 !important;
            }

            [data-baseweb="tooltip"] {
                background: #0f172a;
                color: #f8fafc;
            }

            .stButton > button,
            .stDownloadButton > button,
            .stFormSubmitButton > button {
                background: #d4e2f2;
                color: #0f172a;
                border: 1px solid #7d99bc;
            }

            .stButton > button:hover,
            .stDownloadButton > button:hover,
            .stFormSubmitButton > button:hover {
                background: #bfd3ea;
                color: #0f172a;
                border-color: #587ba7;
            }

            .stButton > button:focus,
            .stDownloadButton > button:focus,
            .stFormSubmitButton > button:focus {
                outline: 2px solid #3b6cc2;
                outline-offset: 1px;
            }

            .stButton > button:disabled,
            .stDownloadButton > button:disabled,
            .stFormSubmitButton > button:disabled {
                background: #dce6f2;
                color: #5d6f87;
                border-color: #adc1d9;
                opacity: 1;
                cursor: not-allowed;
            }

            [data-testid="stDataFrame"],
            [data-testid="stTable"] {
                border: 1px solid #94a3b8;
                border-radius: 8px;
                overflow: hidden;
            }

            [data-testid="stDataFrame"],
            [data-testid="stTable"] {
                background: #ffffff;
            }

            [data-testid="stTable"] * {
                color: #0f172a;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
