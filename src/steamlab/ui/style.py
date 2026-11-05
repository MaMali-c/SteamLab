"""Scoped product styling; calculation code never depends on CSS selectors."""

import streamlit as st


def apply_style(dark: bool) -> None:
    bg, panel, fg, muted, line, soft = (
        ("#061220", "#102238", "#edf5ff", "#aec1d6", "#28415c", "#102e4c")
        if dark
        else ("#f2f6fc", "#ffffff", "#102338", "#455f79", "#ccd9e8", "#e7f0fd")
    )
    st.markdown(
        f"""
    <style>
    .stApp {{ --sl-bg:{bg}; --sl-panel:{panel}; --sl-fg:{fg}; --sl-muted:{muted};
      --sl-line:{line}; --sl-soft:{soft}; background:{bg}; color:{fg}; }}
    [data-testid="stHeader"], [data-testid="stAppViewContainer"] {{background:{bg};color:{fg};}}
    [data-testid="stHeader"] button {{color:{fg};}}
    [data-testid="stSidebar"] {{background:{panel};border-right:1px solid {line};}}
    [data-testid="stSidebar"] * {{color:{fg};}}
    .block-container {{max-width:1440px;padding-top:2rem;padding-bottom:2rem;}}
    [data-testid="stMarkdownContainer"], [data-testid="stWidgetLabel"],
    [data-testid="stCaptionContainer"], [data-testid="stMetricLabel"],
    [data-testid="stMetricValue"], [data-testid="stExpander"] {{color:{fg};}}
    [data-testid="stCaptionContainer"] {{color:{muted};}}
    [data-testid="stCaptionContainer"] p {{color:{muted};}}
    [data-testid="stMarkdownContainer"] h3 {{font-size:20px;line-height:1.6;}}
    [data-testid="stButton"] button[kind="primary"] p {{color:#ffffff!important;}}
    [data-testid="stAppDeployButton"] {{display:none;}}
    [data-testid="stVerticalBlockBorderWrapper"] > div {{border-color:{line}!important;}}
    [data-testid="stNumberInput"] input {{background:{panel};color:{fg};}}
    [data-testid="stNumberInputContainer"] {{background:{panel};border-color:{line};}}
    [data-baseweb="select"] > div {{background:{panel};color:{fg};border-color:{line};}}
    [data-baseweb="select"] input {{color:{fg};}}
    .react-aria-ComboBox [role="group"] {{background:{panel};border:1px solid {line};border-radius:8px;}}
    .react-aria-ComboBox input, .react-aria-ComboBox button {{background:transparent;color:{fg};}}
    [data-testid="stButton"] button[kind="secondary"],
    [data-testid="stDownloadButton"] button {{background:{panel};color:{fg};border-color:{line};}}
    [data-testid="stAlert"] {{background:{soft};color:{fg};}}
    [data-testid="stMetric"] {{background:{panel};border:1px solid {line};
      padding:16px 18px;border-radius:12px;min-width:0;}}
    [data-testid="stMetricValue"] {{font-variant-numeric:tabular-nums;}}
    .sl-hero {{background:linear-gradient(120deg,{panel},{soft});border:1px solid {line};
      padding:25px 28px;border-radius:16px;margin:0 0 24px;border-left:4px solid #1685ff;}}
    .sl-hero h1 {{font-size:28px;font-weight:650;color:{fg};padding:0;margin:4px 0 10px;}}
    .sl-hero p {{color:{muted};margin:0;}}
    .sl-eyebrow {{color:#1685ff;font-size:12px;font-weight:650;letter-spacing:1.5px;}}
    .sl-brand {{font-size:29px;font-weight:700;margin-bottom:4px;}}
    .sl-drop {{display:inline-block;width:22px;height:28px;margin-right:10px;
      background:linear-gradient(140deg,#56dbff,#0873df);border-radius:75% 25% 65% 35%;
      transform:rotate(28deg);vertical-align:middle;}}
    .sl-status {{padding:12px 14px;border-radius:9px;background:{soft};margin-bottom:12px;}}
    .sl-info {{display:flex;justify-content:space-between;gap:18px;flex-wrap:wrap;
      padding:9px 0;border-bottom:1px solid {line};}}
    .sl-info span {{color:{muted};}}
    .sl-info strong {{font-weight:500;}}
    .sl-footer {{color:{muted};font-size:12px;border-top:1px solid {line};margin-top:25px;padding-top:12px;}}
    @media(max-width:760px) {{.block-container {{padding:4.5rem 1rem 1rem;}}
      .sl-hero {{padding:18px;}} .sl-hero h1 {{font-size:23px;}}
      [data-testid="stHorizontalBlock"] {{flex-wrap:wrap;}}
      [data-testid="stColumn"] {{min-width:240px;flex:1 1 240px;}}}}
    </style>""",
        unsafe_allow_html=True,
    )
