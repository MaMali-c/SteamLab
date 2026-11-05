"""English (Persian) interface with traceable state and reference information."""

import html
import json
from pathlib import Path

import pandas as pd
import streamlit as st

from steamlab import __version__
from steamlab.core.engine import solve_pt, solve_px, solve_tx
from steamlab.core.errors import SaturationAmbiguity, SteamLabError
from steamlab.core.phase import PHASE_LABELS
from steamlab.core.units import pressure_to_mpa, temperature_to_k
from steamlab.tables.comparison import TableUnavailable, differences, estimate_for_state
from steamlab.tables.repository import load_rows
from steamlab.validation_report import official_report

from .style import apply_style
from .vapor_pressure import vapor_pressure_page

MODES = {
    "PT": "P–T · Pressure & Temperature (فشار و دما)",
    "PX": "P–x · Pressure & Quality (فشار و کیفیت)",
    "TX": "T–x · Temperature & Quality (دما و کیفیت)",
}
PAGES = {
    "calculator": "Properties Calculator (محاسبه خواص)",
    "vapor_pressure": "Vapor Pressure (نمودار فشار بخار)",
    "tables": "Steam Tables (جدول بخار)",
    "validation": "Validation (اعتبارسنجی)",
    "theory": "Theory & Roadmap (مبانی و نقشه راه)",
}
PROPS = {
    "v": ("Specific Volume (حجم ویژه)", "m³/kg", ".7g"),
    "u": ("Internal Energy (انرژی داخلی)", "kJ/kg", ".3f"),
    "h": ("Enthalpy (آنتالپی)", "kJ/kg", ".3f"),
    "s": ("Entropy (آنتروپی)", "kJ/(kg·K)", ".6f"),
}


def mark_stale() -> None:
    st.session_state.stale = st.session_state.get("result") is not None
    st.session_state.error = None
    st.session_state.saturation_hint = None


def reset_inputs() -> None:
    for key in (
        "temperature",
        "pressure",
        "quality",
        "temp_unit",
        "pressure_unit",
        "previous_temp_unit",
        "previous_pressure_unit",
        "mode",
        "result",
        "snapshot",
        "error",
        "stale",
        "saturation_hint",
    ):
        st.session_state.pop(key, None)


def change_temperature_unit() -> None:
    old = st.session_state.get("previous_temp_unit", "°C")
    new = st.session_state.temp_unit
    if st.session_state.get("temperature") is not None:
        value_k = temperature_to_k(st.session_state.temperature, old)
        st.session_state.temperature = value_k if new == "K" else value_k - 273.15
    st.session_state.previous_temp_unit = new
    mark_stale()


def change_pressure_unit() -> None:
    old = st.session_state.get("previous_pressure_unit", "kPa")
    new = st.session_state.pressure_unit
    if st.session_state.get("pressure") is not None:
        value_mpa = pressure_to_mpa(st.session_state.pressure, old)
        st.session_state.pressure = value_mpa / {"kPa": 0.001, "MPa": 1, "bar": 0.1}[new]
    st.session_state.previous_pressure_unit = new
    mark_stale()


def load_example(kind: str) -> None:
    reset_inputs()
    st.session_state.update(
        {
            "mode": "TX" if kind == "mixture" else "PT",
            "temperature": {"vapor": 300.0, "liquid": 50.0, "mixture": 22.5}[kind],
            "pressure": 500.0,
            "quality": 0.5 if kind == "mixture" else None,
            "temp_unit": "°C",
            "pressure_unit": "kPa",
        }
    )


def init_state() -> None:
    defaults = {
        "mode": "PT",
        "temperature": 300.0,
        "pressure": 500.0,
        "quality": None,
        "temp_unit": "°C",
        "pressure_unit": "kPa",
        "result": None,
        "error": None,
        "stale": False,
        "snapshot": None,
        "saturation_hint": None,
        "previous_temp_unit": "°C",
        "previous_pressure_unit": "kPa",
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def compute() -> None:
    st.session_state.result = None
    st.session_state.error = None
    st.session_state.saturation_hint = None
    st.session_state.stale = False
    mode = st.session_state.mode
    try:
        if mode == "PT":
            state = solve_pt(
                temperature_to_k(st.session_state.temperature, st.session_state.temp_unit),
                pressure_to_mpa(st.session_state.pressure, st.session_state.pressure_unit),
            )
        elif mode == "PX":
            state = solve_px(
                pressure_to_mpa(st.session_state.pressure, st.session_state.pressure_unit),
                st.session_state.quality,
            )
        else:
            state = solve_tx(
                temperature_to_k(st.session_state.temperature, st.session_state.temp_unit),
                st.session_state.quality,
            )
        st.session_state.result = state
        st.session_state.snapshot = MODES[mode]
    except SaturationAmbiguity as exc:
        st.session_state.error = str(exc)
        st.session_state.saturation_hint = exc.temperature_k
    except SteamLabError as exc:
        st.session_state.error = str(exc)


def info_row(label: str, value: str) -> None:
    st.markdown(
        f'<div class="sl-info"><span>{html.escape(label)}</span>'
        f"<strong>{html.escape(value)}</strong></div>",
        unsafe_allow_html=True,
    )


def render_state() -> None:
    state = st.session_state.result
    st.subheader("State Information (اطلاعات حالت)")
    if state is None:
        st.info("Awaiting a valid calculation (در انتظار محاسبه معتبر)")
        return
    if st.session_state.stale:
        st.warning(
            "Previous result — recalculate after editing (نتیجه قبلی است؛ دوباره محاسبه کنید)"
        )
    else:
        st.success("Valid calculated state (حالت محاسبه‌شده معتبر)")
    info_row("Phase (فاز)", PHASE_LABELS[state.phase])
    info_row("IF97 Region (ناحیه محاسباتی)", str(state.region))
    info_row(
        "Vapor Quality (کیفیت بخار)",
        "Not defined (تعریف نمی‌شود)" if state.quality is None else f"{state.quality:.6g}",
    )
    info_row("Temperature (دما)", f"{state.temperature_c:.6f} °C / {state.temperature_k:.6f} K")
    info_row("Absolute Pressure (فشار مطلق)", f"{state.pressure_mpa * 1000:.8g} kPa")
    st.caption(st.session_state.snapshot)
    for note in state.warnings:
        st.warning(note)


def source_frame(rows) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "ID (شناسه)": row.row_id,
                "Page (صفحه)": row.page,
                "Table (جدول)": row.table_id,
                "T (دما) · °C": row.temperature_c,
                "P (فشار) · kPa": row.pressure_kpa,
                "x (کیفیت)": row.quality,
                "v (حجم ویژه) · cm³/g": row.v_cm3_g,
                "v (حجم ویژه) · m³/kg": row.properties["v"],
                "u (انرژی داخلی) · kJ/kg": row.u,
                "h (آنتالپی) · kJ/kg": row.h,
                "s (آنتروپی) · kJ/(kg·K)": row.s,
            }
            for row in rows
        ]
    )


def render_comparison(rows) -> None:
    st.subheader("Comparison with Steam Table (مقایسه با جدول بخار)")
    state = st.session_state.result
    if state is None:
        st.caption(
            "Checked PDF records will appear after calculation (پس از محاسبه، داده مرجع نمایش داده می‌شود)."
        )
        return
    if st.session_state.stale:
        st.info(
            "Recalculate to compare the edited inputs (برای مقایسه ورودی جدید، دوباره محاسبه کنید)."
        )
        return
    try:
        estimate = estimate_for_state(state, rows)
    except TableUnavailable as exc:
        st.info(str(exc))
        return
    st.caption(estimate.method)
    records = differences(state, estimate)
    st.dataframe(
        pd.DataFrame(
            [
                {
                    "Property (خاصیت)": f"{PROPS[r['property']][0]} · {PROPS[r['property']][1]}",
                    "IF97 (محاسبه)": f"{r['if97']:.8g}",
                    "PDF (جدول)": f"{r['table']:.8g}",
                    "Absolute difference (اختلاف مطلق)": f"{r['absolute']:.6g}",
                    "Relative difference (اختلاف نسبی) · %": "Not defined (تعریف نمی‌شود)"
                    if r["relative_percent"] is None
                    else f"{r['relative_percent']:.6g}",
                }
                for r in records
            ]
        ),
        hide_index=True,
        width="stretch",
    )
    st.caption(
        "Differences include table rounding and interpolation; they are not a certified error bound "
        "(اختلاف‌ها شامل اثر گردکردن جدول و درون‌یابی هستند و کران خطای تضمین‌شده نیستند)."
    )
    with st.expander("Source Rows & Units (ردیف‌های مرجع و واحدها)"):
        st.dataframe(source_frame(estimate.source_rows), hide_index=True, width="stretch")
        st.code("v [m³/kg] = v [cm³/g] × 0.001", language=None)
        st.caption("Original values were retained (اعداد اصلی جدول حفظ شده‌اند).")
        if state.quality is not None:
            st.caption(
                "Saturation comparison uses T for T–x and P for P–x; the other coordinate "
                "can differ between the PDF and IF97 (در اشباع، متغیر مبنا مطابق حالت ورودی "
                "انتخاب می‌شود؛ متغیر دیگر در جدول و استاندارد ممکن است متفاوت باشد)."
            )
    with st.expander("Interpolation Steps (مراحل درون‌یابی)"):
        if not estimate.steps:
            st.write("Exact source node; no interpolation (نقطه مرجع دقیق؛ بدون درون‌یابی).")
        else:
            st.latex(r"w=\frac{z-z_1}{z_2-z_1},\quad y=y_1+w(y_2-y_1)")
            axes = {
                "temperature_c": "T · °C (دما)",
                "pressure_kpa": "P · kPa (فشار)",
                "quality": "x (کیفیت بخار؛ میانگین جرمی)",
            }
            for step in estimate.steps:
                st.write(f"**{PROPS[step.property_name][0]} — {axes[step.coordinate]}**")
                st.code(
                    f"w = ({step.z:.8g} - {step.z1:.8g}) / "
                    f"({step.z2:.8g} - {step.z1:.8g}) = {step.weight:.8g}\n"
                    f"{step.property_name} = {step.y1:.8g} + {step.weight:.8g} × "
                    f"({step.y2:.8g} - {step.y1:.8g}) = {step.result:.8g} "
                    f"{PROPS[step.property_name][1]}",
                    language=None,
                )


def calculator(rows) -> None:
    init_state()
    st.radio(
        "Input Pair (جفت ورودی)",
        list(MODES),
        format_func=MODES.get,
        horizontal=True,
        key="mode",
        on_change=mark_stale,
    )
    left, right = st.columns([1.12, 1], gap="large")
    with left, st.container(border=True):
        st.subheader("Input Parameters (پارامترهای ورودی)")
        mode = st.session_state.mode
        if mode != "PX":
            a, b = st.columns([2, 1])
            a.number_input(
                "Temperature (دما)", key="temperature", format="%.6f", on_change=mark_stale
            )
            b.selectbox(
                "Temperature Unit (واحد دما)",
                ["°C", "K"],
                key="temp_unit",
                on_change=change_temperature_unit,
            )
        if mode != "TX":
            a, b = st.columns([2, 1])
            a.number_input(
                "Absolute Pressure (فشار مطلق)", key="pressure", format="%.8f", on_change=mark_stale
            )
            b.selectbox(
                "Pressure Unit (واحد فشار)",
                ["kPa", "MPa", "bar"],
                key="pressure_unit",
                on_change=change_pressure_unit,
            )
        if mode != "PT":
            st.number_input(
                "Vapor Quality (کیفیت بخار) · 0 ≤ x ≤ 1",
                value=None,
                key="quality",
                format="%.6f",
                on_change=mark_stale,
                placeholder="Enter quality (کیفیت را وارد کنید)",
            )
            st.caption(
                "The other saturation coordinate is calculated (متغیر اشباع دیگر محاسبه می‌شود)."
            )
        a, b = st.columns([2, 1])
        a.button(
            "Calculate Properties (محاسبه خواص)",
            type="primary",
            key="calculate",
            on_click=compute,
            width="stretch",
        )
        b.button("Reset (بازنشانی)", key="reset", on_click=reset_inputs, width="stretch")
        st.caption("Use absolute pressure, not gauge pressure (فشار مطلق وارد کنید؛ نه فشار گیج).")
        if st.session_state.error:
            st.error(st.session_state.error)
    with right, st.container(border=True):
        render_state()
    st.subheader("Thermodynamic Properties (خواص ترمودینامیکی)")
    state = st.session_state.result
    cols = st.columns(2)
    for index, (name, (label, unit, fmt)) in enumerate(PROPS.items()):
        with cols[index % 2]:
            value = "—" if state is None else format(getattr(state, name), fmt)
            st.metric(f"{label} · {unit}", value)
    st.write("")
    with st.container(border=True):
        render_comparison(rows)
    with st.expander("Calculation Details & Assumptions (جزئیات محاسبه و فرضیات)"):
        st.write(
            "Pure water · equilibrium fluid states · IF97 (آب خالص، حالت تعادلی سیال، استاندارد IF97)"
        )
        if state is not None:
            st.write(f"Density (چگالی): **{state.density:.8g} kg/m³**")
            st.latex(r"\rho=\frac1v,\qquad h=u+1000\,P_{\mathrm{MPa}}v")
            if state.quality is not None:
                st.latex(r"y=y_f+x(y_g-y_f),\quad y\in\{v,u,h,s\}")
        st.write(
            "Quality is undefined for single-phase and critical states "
            "(کیفیت بخار برای حالت تک‌فازی و نقطه بحرانی تعریف نمی‌شود)."
        )
        st.write(
            "Display rounding does not change calculations (گردکردن نمایشی بر محاسبه اثر ندارد)."
        )


def tables_page(root: Path, rows) -> None:
    st.subheader("Checked Source Records (رکوردهای مرجع بازبینی‌شده)")
    st.info(
        f"{len(rows)} visually checked records; not the entire PDF "
        f"({len(rows)} رکورد با بازبینی چشمی؛ نه تمام جدول‌های فایل)."
    )
    st.write(
        "Reviewed by the assistant; independent human review is still recommended for the dataset "
        "(بازبینی توسط دستیار انجام شده؛ بازبینی مستقل انسانی داده‌ها هنوز انجام نشده است)."
    )
    st.dataframe(source_frame(rows), hide_index=True, width="stretch")
    st.write(
        "V1 coverage: saturation endpoints at 20, 25, 30 °C; selected superheated rows at "
        "100, 500, 750 kPa (پوشش نسخه اول: نقاط اشباع در دماهای ۲۰، ۲۵ و ۳۰ و "
        "ردیف‌های منتخب فوق‌گرم در فشارهای ۱۰۰، ۵۰۰ و ۷۵۰ کیلوپاسکال)."
    )
    pdf = root / "data/reference/SteamTableSI.pdf"
    if pdf.exists():
        st.download_button(
            "Open Original PDF (دریافت فایل مرجع اصلی)",
            pdf.read_bytes(),
            file_name=pdf.name,
            mime="application/pdf",
        )
    else:
        st.caption(
            "Original PDF is optional; put it in data/reference "
            "(فایل اصلی اختیاری است؛ می‌توانید آن را در پوشه data/reference قرار دهید)."
        )
    with st.expander("Data Provenance (مشخصات منبع داده)"):
        meta = json.loads((root / "data/verified/provenance.json").read_text(encoding="utf-8"))
        st.write(f"Source (منبع): {meta['source_filename']}")
        st.write(f"Pages (تعداد صفحات): {meta['page_count']}")
        st.write(
            "Bibliographic origin not established (نام کتاب و مبنای محاسبات آن مشخص نشده است)."
        )
        st.code(f"SHA-256: {meta['sha256']}", language=None)


def validation_page(root: Path) -> None:
    st.subheader("Independent Reference Checks (بررسی با مرجع مستقل)")
    st.write(
        "Fixed published values: IAPWS tables 5, 15, 33, 36 and 42 "
        "(مقادیر ثابت منتشرشده در جدول‌های ۵، ۱۵، ۳۳، ۳۶ و ۴۲ استاندارد)."
    )
    if st.button("Run Reference Checks (اجرای بررسی‌های مرجع)", key="run_checks", type="primary"):
        try:
            st.session_state.check_results = official_report(
                root / "data/verified/official_checks.json"
            )
        except SteamLabError as exc:
            st.session_state.pop("check_results", None)
            st.error(str(exc))
    report = st.session_state.get("check_results")
    if report:
        passed = sum(row["passed"] for row in report)
        message = f"{passed}/{len(report)} checks passed (بررسی موفق)"
        (st.success if passed == len(report) else st.error)(message)
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "Case (حالت)": r["case"],
                        "Table (جدول)": r["table"],
                        "Property (خاصیت)": r["property"],
                        "Reference (مرجع)": r["expected"],
                        "Computed (محاسبه)": r["actual"],
                        "Absolute difference (اختلاف مطلق)": r["absolute_difference"],
                        "Result (نتیجه)": "Pass (موفق)" if r["passed"] else "Fail (ناموفق)",
                    }
                    for r in report
                ]
            ),
            hide_index=True,
            width="stretch",
        )
    st.caption(
        "Reference tests verify implementation, not universal physical accuracy "
        "(تست‌های مرجع پیاده‌سازی را بررسی می‌کنند، نه دقت فیزیکی یکسان در تمام دامنه)."
    )
    st.link_button(
        "IAPWS Reference (مرجع استاندارد)", "https://iapws.org/technical-guidance/release/IF97-Rev"
    )


def theory_page() -> None:
    st.subheader("Scientific Model (مدل علمی)")
    st.write(
        "IF97 represents fluid water using region-dependent fundamental equations "
        "(استاندارد IF97 خواص آب سیال را با معادلات بنیادی وابسته به ناحیه محاسبه می‌کند)."
    )
    st.latex(r"h=u+Pv,\quad \rho=1/v,\quad x=m_g/(m_f+m_g)")
    st.write("Use consistent units in h=u+Pv (در رابطه آنتالپی، واحدها باید سازگار باشند).")
    st.write(
        "At saturation, T and P are dependent; quality supplies the missing information "
        "(در اشباع، دما و فشار مستقل نیستند؛ کیفیت بخار اطلاعات لازم را تکمیل می‌کند)."
    )
    st.subheader("Software Limits (محدودیت‌های نرم‌افزار)")
    st.write(
        "T: 273.16–2273.15 K; P: 0.000611212677444–100 MPa; P ≤ 50 MPa above 1073.15 K "
        "(بازه دما ۰٫۰۱ تا ۲۰۰۰ درجه سلسیوس؛ سقف فشار بالاتر از ۸۰۰ درجه، ۵۰ مگاپاسکال است)."
    )
    st.write(
        "P–T saturation proximity tolerance: 0.01 K; no automatic snapping "
        "(تلرانس نزدیکی به اشباع ۰٫۰۱ کلوین است؛ ورودی خودکار روی اشباع قرار نمی‌گیرد)."
    )
    st.write(
        "Quality mode excludes the final 0.01 K below the critical temperature "
        "(حالت کیفیت در فاصله کمتر از ۰٫۰۱ کلوین تا دمای بحرانی غیرفعال است)."
    )
    st.write(
        "No ice, saline water, chemical dissociation, metastable-state selection or cp of a mixture "
        "(مدل یخ، آب شور، تفکیک شیمیایی، انتخاب حالت شبه‌پایدار و ظرفیت گرمایی مخلوط وجود ندارد)."
    )
    st.subheader("Planned Features (قابلیت‌های برنامه‌ریزی‌شده)")
    st.write(
        "V1.1: P–h/P–s, Plotly T–s/P–h diagrams, 2D interpolation, CSV export "
        "(نسخه بعد: ورودی‌های فشار–آنتالپی و فشار–آنتروپی، نمودار، درون‌یابی دوبعدی و خروجی CSV)."
    )
    st.write(
        "Later: equipment, Rankine cycle, PDF/Excel reports "
        "(مراحل بعد: تجهیزات، سیکل رانکین و گزارش PDF و Excel)."
    )
    st.caption(
        "These features are not implemented in V1.0 (این امکانات در نسخه اول پیاده‌سازی نشده‌اند)."
    )


def main(root: Path) -> None:
    st.set_page_config(page_title="SteamLab (آزمایشگاه بخار)", page_icon="💧", layout="wide")
    # Reassign widget-backed inputs so Streamlit retains them on pages/modes
    # where their controls are not rendered (including their unit conversion state).
    for key in ("mode", "temperature", "pressure", "quality", "temp_unit", "pressure_unit"):
        if key in st.session_state:
            st.session_state[key] = st.session_state[key]
    with st.sidebar:
        st.markdown(
            '<div class="sl-brand"><span class="sl-drop" aria-hidden="true"></span>SteamLab</div>',
            unsafe_allow_html=True,
        )
        st.caption("Thermodynamic Properties & Analysis (خواص و تحلیل ترمودینامیکی)")
        st.caption(f"V{__version__} · IAPWS-IF97")
        page = st.radio("Workspace (محیط کار)", list(PAGES), format_func=PAGES.get, key="page")
        theme = st.radio(
            "Appearance (ظاهر)", ["Dark (تیره)", "Light (روشن)"], key="appearance", horizontal=True
        )
        st.divider()
        st.caption("Learning Examples (مثال‌های آموزشی)")
        if page == "calculator":
            st.button(
                "Superheated Vapor (بخار فوق‌گرم)",
                on_click=load_example,
                args=("vapor",),
                width="stretch",
            )
            st.button(
                "Compressed Liquid (مایع فشرده)",
                on_click=load_example,
                args=("liquid",),
                width="stretch",
            )
            st.button(
                "Saturated Mixture (مخلوط اشباع)",
                on_click=load_example,
                args=("mixture",),
                width="stretch",
            )
        st.caption(
            "Local calculations · no account required (محاسبات محلی؛ بدون نیاز به حساب کاربری)"
        )
    apply_style(theme.startswith("Dark"))
    st.markdown(
        """<div class="sl-hero"><div class="sl-eyebrow">STEAMLAB / WATER &amp; STEAM</div>
    <h1>Thermodynamic Properties (خواص ترمودینامیکی)</h1>
    <p>Calculate · understand · verify (محاسبه، یادگیری، اعتبارسنجی)</p></div>""",
        unsafe_allow_html=True,
    )
    try:
        rows = load_rows(root / "data/verified/steam_table_sample.csv")
    except (OSError, ValueError, KeyError) as exc:
        st.error("Reference dataset could not be loaded (داده مرجع خوانده نشد).")
        st.caption(str(exc))
        rows = ()
    if page == "calculator":
        calculator(rows)
    elif page == "vapor_pressure":
        vapor_pressure_page()
    elif page == "tables":
        tables_page(root, rows)
    elif page == "validation":
        validation_page(root)
    else:
        theory_page()
    st.markdown(
        '<div class="sl-footer">SteamLab V1.0 · Python / IAPWS-IF97 · '
        "Educational engineering software (نرم‌افزار آموزشی مهندسی)"
        '<div dir="rtl" lang="fa"><strong>محمدعلی شمشیری</strong></div></div>',
        unsafe_allow_html=True,
    )
