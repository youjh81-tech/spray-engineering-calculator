"""Spray Engineering Calculator - stage 1.

Home with three calculator slots and a nozzle flow-rate calculator.
The nozzle calculator uses two reference points and can export a branded PDF.
"""

from __future__ import annotations

import base64
import math
from datetime import datetime
from io import BytesIO
from typing import Any

import streamlit as st


st.set_page_config(
    page_title="Spray Engineering Calculator",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="collapsed",
)

SITE_URL = "https://www.spray.com/ko-kr"
LOGO_PNG_BASE64 = (
    "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"
)
LOGO_DATA_URI = f"data:image/png;base64,{LOGO_PNG_BASE64}"

CSS = r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800&display=swap');
:root{--navy:#072844;--navy2:#0a3b60;--blue:#0085c8;--sky:#00aeef;--ink:#102c42;--muted:#617789;--line:#d6e2e9;--paper:#fff;--bg:#f1f6f9;--green:#0a9b73}
html,body,[class*="css"],[data-testid="stAppViewContainer"]{font-family:"Noto Sans KR","Segoe UI",sans-serif}
[data-testid="stAppViewContainer"]{color:var(--ink);background:radial-gradient(circle at 93% 5%,rgba(0,174,239,.12),transparent 24rem),linear-gradient(#fff 0,#f5f9fb 30rem,#edf4f7 100%)}
[data-testid="stHeader"]{background:rgba(255,255,255,.74)}
[data-testid="stMainBlockContainer"]{max-width:1280px;padding-top:1rem;padding-bottom:3rem}
[data-testid="stSidebar"]{display:none} #MainMenu,footer{visibility:hidden}
.site-head{display:flex;align-items:center;justify-content:space-between;gap:1rem;min-height:70px;padding:.65rem 1rem;margin-bottom:1rem;border:1px solid var(--line);background:rgba(255,255,255,.97);box-shadow:0 9px 28px rgba(7,40,68,.07)}
.brand{display:flex;align-items:center;gap:.8rem;text-decoration:none!important}.brand img{width:215px;height:43px;object-fit:contain;object-position:left}.brand-fallback{display:none;color:var(--navy);font-weight:800}.brand small{color:#62798b;font-size:.7rem;font-weight:700}.app-id{text-align:right}.app-id strong{display:block;color:var(--navy);font-size:.88rem}.app-id span{color:#7a8e9d;font-size:.66rem;letter-spacing:.1em}
.hero{position:relative;overflow:hidden;min-height:280px;display:flex;align-items:center;padding:clamp(1.7rem,5vw,4rem);background:radial-gradient(ellipse at 87% 11%,rgba(0,190,239,.50),transparent 42%),linear-gradient(112deg,#061a2d,#083b60 63%,#007cab);box-shadow:0 22px 52px rgba(7,40,68,.18)}
.hero:after{content:"";position:absolute;right:-12%;top:-72%;width:620px;height:620px;border:1px solid rgba(255,255,255,.25);border-radius:50%;box-shadow:0 0 0 55px rgba(255,255,255,.04),0 0 0 110px rgba(255,255,255,.025)}
.hero>div{position:relative;z-index:1}.eyebrow{color:#6ddcff;font-size:.72rem;font-weight:800;letter-spacing:.18em}.hero h1{margin:.45rem 0 .65rem;color:#fff;font-size:clamp(2rem,5vw,3.8rem);line-height:1.08;letter-spacing:-.05em}.hero p{margin:0;color:#d7edf6;font-size:1rem}
.section-kicker{margin-top:2rem;color:#0072ae;font-size:.7rem;font-weight:800;letter-spacing:.16em}.section-title{margin:.2rem 0;color:var(--navy);font-size:clamp(1.45rem,3vw,2.1rem);font-weight:800}.section-copy{color:var(--muted);font-size:.88rem;margin-bottom:1rem}
.menu-card{min-height:215px;padding:1.25rem;border:1px solid var(--line);border-top:4px solid var(--blue);background:#fff;box-shadow:0 13px 32px rgba(7,40,68,.075)}.menu-card.pending{border-top-color:#a8b6c0;background:#f8fafb}.menu-card .num{color:var(--blue);font-size:.7rem;font-weight:800;letter-spacing:.14em}.menu-card.pending .num{color:#8596a3}.menu-card h3{margin:.7rem 0 .5rem;color:var(--navy);font-size:1.16rem}.menu-card p{min-height:63px;color:var(--muted);font-size:.82rem;line-height:1.65}.pill{display:inline-block;padding:.28rem .58rem;border-radius:99px;background:#e1f5fc;color:#006d9e;font-size:.66rem;font-weight:800}.pending .pill{background:#e9eef1;color:#71818d}
.calc-intro{display:flex;align-items:center;justify-content:space-between;gap:2rem;margin:.25rem 0 1.35rem;padding:1.35rem 1.5rem;border:1px solid #cbdde7;border-left:6px solid var(--blue);background:linear-gradient(120deg,#fff 0,#f3f9fc 66%,#e1f3fa 100%);box-shadow:0 10px 28px rgba(7,40,68,.07)}.calc-intro .calc-index{color:#0079b6;font-size:.68rem;font-weight:800;letter-spacing:.16em}.calc-intro h1{margin:.3rem 0 .35rem;color:var(--navy);font-size:clamp(1.65rem,3vw,2.25rem);letter-spacing:-.045em}.calc-intro p{margin:0;color:#587184;font-size:.84rem}.calc-formula{flex:0 0 auto;padding:.75rem 1rem;border-radius:4px;background:#072844;color:#fff;font:700 1rem/1.2 Georgia,serif;letter-spacing:.04em}
.workspace-head{margin:.1rem 0 .75rem}.workspace-head span{display:block;color:#0085c8;font-size:.65rem;font-weight:800;letter-spacing:.15em}.workspace-head h2{margin:.12rem 0;color:var(--navy);font-size:1.2rem}.workspace-head p{margin:.15rem 0;color:var(--muted);font-size:.78rem}.subhead{margin:.45rem 0 .55rem;color:#153b55;font-size:.84rem;font-weight:800}.subhead:before{content:"";display:inline-block;width:4px;height:13px;margin-right:.45rem;vertical-align:-2px;background:var(--blue)}
.panel-title{margin:.2rem 0 .7rem;padding-bottom:.5rem;border-bottom:1px solid var(--line);color:var(--navy);font-size:.9rem;font-weight:800}.panel-title span{margin-right:.35rem;color:var(--blue)}
.formula{padding:.9rem 1rem;border-left:4px solid var(--sky);background:#edf8fc;color:#284960;font-size:.81rem;line-height:1.75}.legal{margin-top:1.8rem;padding-top:.8rem;border-top:1px solid var(--line);color:#728695;font-size:.7rem;line-height:1.6}
div[data-testid="stVerticalBlockBorderWrapper"]{border-color:var(--line)!important;border-radius:3px!important;background:rgba(255,255,255,.97);box-shadow:0 9px 25px rgba(7,40,68,.05)}
[data-testid="stMetric"]{min-height:112px;padding:.9rem!important;border-top:3px solid var(--blue);background:linear-gradient(#fff,#f4f9fb)}[data-testid="stMetricLabel"]{color:#607688!important}[data-testid="stMetricValue"]{color:var(--navy)!important;font-size:clamp(1.35rem,2vw,1.95rem)!important;line-height:1.18!important;white-space:nowrap!important;overflow:visible!important;text-overflow:clip!important}[data-testid="stMetricValue"] *{font-size:inherit!important;white-space:nowrap!important;overflow:visible!important;text-overflow:clip!important}
div[data-baseweb="radio"]{gap:.4rem}div[data-baseweb="radio"] label{padding:.45rem .65rem;border:1px solid var(--line);background:#fff;color:var(--ink)!important}div[data-baseweb="radio"] label *,[data-testid="stRadio"] label *{color:var(--ink)!important;-webkit-text-fill-color:var(--ink)!important;opacity:1!important}
[data-testid="stWidgetLabel"],[data-testid="stWidgetLabel"] *,[data-testid="stTextInput"] label *,[data-testid="stNumberInput"] label *,[data-testid="stSlider"] label *,[data-testid="stCheckbox"] label *{color:#294a61!important;-webkit-text-fill-color:#294a61!important;opacity:1!important}
[data-testid="stTextInput"] div[data-baseweb="input"],[data-testid="stNumberInput"] div[data-baseweb="input"],[data-testid="stTextInput"] input,[data-testid="stNumberInput"] input{background:#242731!important;border-color:#242731!important}
[data-testid="stTextInput"] input,[data-testid="stNumberInput"] input{color:#fff!important;-webkit-text-fill-color:#fff!important;caret-color:#fff!important;padding-right:.75rem!important}
[data-testid="stTextInput"] input::placeholder{color:#b9c3cc!important;-webkit-text-fill-color:#b9c3cc!important;opacity:1!important}[data-testid="stTextInput"] input:focus::placeholder{color:transparent!important;-webkit-text-fill-color:transparent!important}
[data-testid="stNumberInput"] button{display:none!important}
.stButton>button,.stDownloadButton>button{min-height:42px;border-radius:2px;font-weight:750;color:#fff!important;-webkit-text-fill-color:#fff!important;background:#111827!important;border-color:#111827!important}.stButton>button *,.stDownloadButton>button *{color:#fff!important;-webkit-text-fill-color:#fff!important;opacity:1!important}.stButton>button[kind="primary"],.stDownloadButton>button[kind="primary"]{border-color:var(--blue)!important;background:var(--blue)!important}
@media(max-width:720px){[data-testid="stMainBlockContainer"]{padding:.55rem .75rem 2rem}.site-head{align-items:flex-start;padding:.6rem}.brand img{width:150px;height:34px}.brand small,.app-id span{display:none}.app-id strong{font-size:.7rem}.hero{min-height:235px;padding:1.5rem 1.1rem}.hero p{font-size:.85rem}.menu-card{min-height:185px}.calc-intro{align-items:flex-start;padding:1rem}.calc-formula{display:none}}
</style>
"""

DEFAULTS: dict[str, Any] = {
    "flow_mode": "일류체 노즐 (LPM)",
    "product_name": "",
    "target_liquid_input": 5.0,
    "target_liquid_slider": 5.0,
    "target_air_input": 1.0,
    "target_air_slider": 1.0,
    "p1_liquid_pressure": 2.0,
    "p1_liquid_flow": 4.0,
    "p1_air_pressure": 0.5,
    "p1_air_flow": 25.0,
    "p2_liquid_pressure": 3.0,
    "p2_liquid_flow": 4.8,
    "p2_air_pressure": 1.0,
    "p2_air_flow": 35.0,
}


def init_state() -> None:
    st.session_state.setdefault("page", "home")


def reset_conditions() -> None:
    condition_keys = [key for key in DEFAULTS if key.startswith("target_") or key.startswith("p1_") or key.startswith("p2_")]
    for key in condition_keys:
        st.session_state[key] = 0.0


def go(page: str) -> None:
    st.session_state.page = page


def sync(source: str, target: str) -> None:
    st.session_state[target] = float(st.session_state[source])


def initial_widget_value(key: str) -> dict[str, Any]:
    return {} if key in st.session_state else {"value": DEFAULTS[key]}


def header() -> None:
    st.markdown(
        f"""<div class="site-head"><a class="brand" href="{SITE_URL}" target="_blank" rel="noopener noreferrer">
        <img src="{LOGO_DATA_URI}" alt="Spraying Systems Co. 공식 로고" onerror="this.style.display='none';this.nextElementSibling.style.display='inline-block'">
        <span class="brand-fallback">SPRAYING SYSTEMS CO.</span><small>스프레이시스템코리아 공식 홈페이지 ↗</small></a>
        <div class="app-id"><strong>Spray Engineering Calculator</strong><span>INDEPENDENT ENGINEERING TOOL</span></div></div>""",
        unsafe_allow_html=True,
    )


def footer() -> None:
    st.markdown(
        """<div class="legal">본 계산기는 현장 검토를 돕기 위한 독립적인 계산 도구입니다. 실제 노즐 선정과 운전 조건은 제조사 데이터시트 및 기술 담당자의 검토 결과를 우선 적용하십시오. Spraying Systems Co. 로고는 사용자 요청에 따라 공식 홈페이지 연결 및 리포트 식별 영역에 표시됩니다.</div>""",
        unsafe_allow_html=True,
    )


def home() -> None:
    header()
    st.markdown(
        """<section class="hero"><div><div class="eyebrow">SPRAY ENGINEERING WORKSPACE</div>
        <h1>Spray Engineering<br>Calculator</h1><p>현장 조건에 맞는 계산기를 선택하고 필요한 운전값을 빠르게 검토하세요.</p></div></section>
        <div class="section-kicker">SELECT A CALCULATOR</div><div class="section-title">계산기 선택</div>
        <div class="section-copy">총 3개의 계산기를 순서대로 완성합니다. 현재는 첫 번째 계산기를 사용할 수 있습니다.</div>""",
        unsafe_allow_html=True,
    )
    cols = st.columns(3, gap="large")
    cards = [
        ("01 · AVAILABLE", "노즐 분사량 계산기", "두 개의 데이터시트 기준점으로 목표 압력의 액체 유량과 공기 소모량을 예측합니다.", False),
        ("02 · NEXT", "두 번째 계산기", "두 번째 계산식은 다음 단계에서 같은 화면 체계로 추가합니다.", True),
        ("03 · PLANNED", "세 번째 계산기", "세 번째 계산식은 앞선 계산기를 완성한 뒤 연결합니다.", True),
    ]
    for index, (col, card) in enumerate(zip(cols, cards, strict=True)):
        label, title, copy, pending = card
        with col:
            css_class = " pending" if pending else ""
            st.markdown(
                f"<div class='menu-card{css_class}'><div class='num'>{label}</div><h3>{title}</h3><p>{copy}</p><span class='pill'>{'제작 예정' if pending else '사용 가능'}</span></div>",
                unsafe_allow_html=True,
            )
            if index == 0:
                st.button("노즐 분사량 계산기 열기 →", type="primary", width="stretch", on_click=go, args=("flow",))
            else:
                st.button("준비 중", key=f"pending_{index}", width="stretch", disabled=True)
    footer()


def calculate(mode: str, target_liquid: float, target_air: float, points: list[dict[str, float | bool]]) -> dict[str, Any]:
    liquid_ks: list[float] = []
    air_ks: list[float] = []
    calculated: list[dict[str, float | bool]] = []
    dual = mode.startswith("이류체")
    for point in points:
        active = bool(point["active"])
        pl = float(point["pl"])
        ql = float(point["ql"])
        pa = float(point["pa"])
        qa = float(point["qa"])
        kl = 0.0
        ka = 0.0
        if active and pl > 0 and ql > 0:
            if dual:
                factor = max(0.15, 1.0 - 0.25 * pa / pl)
                kl = ql / (math.sqrt(pl) * factor)
            else:
                kl = ql / math.sqrt(pl)
            liquid_ks.append(kl)
        if dual and active and pa > 0 and qa > 0:
            ka = qa / math.sqrt(pa)
            air_ks.append(ka)
        calculated.append({**point, "kl": kl, "ka": ka})
    avg_k = sum(liquid_ks) / len(liquid_ks) if liquid_ks else 0.0
    avg_air_k = sum(air_ks) / len(air_ks) if air_ks else 0.0
    liquid_flow = 0.0
    if target_liquid > 0 and avg_k > 0:
        factor = max(0.15, 1.0 - 0.25 * target_air / target_liquid) if dual else 1.0
        liquid_flow = avg_k * math.sqrt(target_liquid) * factor
    air_flow = avg_air_k * math.sqrt(target_air) if dual and target_air > 0 and avg_air_k > 0 else 0.0
    return {"avg_k": avg_k, "avg_air_k": avg_air_k, "liquid_flow": liquid_flow, "air_flow": air_flow,
            "valid_count": len(liquid_ks), "points": calculated}


def chart_spec(mode: str, target_liquid: float, target_air: float, result: dict[str, Any]) -> dict[str, Any]:
    active = [p for p in result["points"] if bool(p["active"]) and float(p["pl"]) > 0 and float(p["ql"]) > 0]
    max_p = max(5.0, target_liquid * 1.25, max((float(p["pl"]) * 1.25 for p in active), default=0.0))
    curve = []
    for i in range(81):
        p = max_p * i / 80
        if mode.startswith("이류체"):
            factor = max(0.15, 1.0 - 0.25 * target_air / (p if p > 0 else 0.001))
        else:
            factor = 1.0
        curve.append({"pressure": p, "flow": float(result["avg_k"]) * math.sqrt(p) * factor})
    refs = [{"pressure": float(p["pl"]), "flow": float(p["ql"]), "label": f"P{i}"}
            for i, p in enumerate(result["points"], start=1)
            if bool(p["active"]) and float(p["pl"]) > 0 and float(p["ql"]) > 0]
    target = [{"pressure": target_liquid, "flow": float(result["liquid_flow"]), "label": "목표점"}]
    unit = "L/H" if mode.startswith("이류체") else "LPM"
    return {"height": 350, "background": "#fff", "config": {"view": {"stroke": "#d6e2e9"},
            "axis": {"labelColor": "#577084", "titleColor": "#14364e", "gridColor": "#dce7ed"}}, "layer": [
        {"data": {"values": curve}, "mark": {"type": "line", "color": "#0085c8", "strokeWidth": 3},
         "encoding": {"x": {"field": "pressure", "type": "quantitative", "title": "액체 압력 Pressure (bar)", "scale": {"domain": [0, max_p]}},
                      "y": {"field": "flow", "type": "quantitative", "title": f"분사량 Flow Rate ({unit})", "scale": {"zero": True}},
                      "tooltip": [{"field": "pressure", "title": "압력 (bar)", "format": ".3f"}, {"field": "flow", "title": f"유량 ({unit})", "format": ".3f"}]}},
        {"data": {"values": refs}, "mark": {"type": "point", "filled": True, "color": "#075f9b", "size": 105},
         "encoding": {"x": {"field": "pressure", "type": "quantitative"}, "y": {"field": "flow", "type": "quantitative"},
                      "tooltip": [{"field": "label", "title": "기준점"}, {"field": "pressure", "title": "압력 (bar)"}, {"field": "flow", "title": f"유량 ({unit})"}]}},
        {"data": {"values": target}, "mark": {"type": "rule", "color": "#0a9b73", "strokeDash": [5, 4]},
         "encoding": {"x": {"field": "pressure", "type": "quantitative"}}},
        {"data": {"values": target}, "mark": {"type": "point", "filled": True, "color": "#0a9b73", "size": 175},
         "encoding": {"x": {"field": "pressure", "type": "quantitative"}, "y": {"field": "flow", "type": "quantitative"},
                      "tooltip": [{"field": "label", "title": "구분"}, {"field": "pressure", "title": "목표 압력 (bar)"}, {"field": "flow", "title": f"예측 유량 ({unit})"}]}}
    ]}


def pdf_curve_drawing(mode: str, target_liquid: float, target_air: float, result: dict[str, Any]) -> Any:
    from reportlab.graphics.shapes import Circle, Drawing, Line, Path, String
    from reportlab.lib.colors import HexColor

    width, height = 500, 250
    left, right, bottom, top = 52, 18, 36, 22
    active = [p for p in result["points"] if bool(p["active"]) and float(p["pl"]) > 0 and float(p["ql"]) > 0]
    max_p = max(5.0, target_liquid * 1.25, max((float(p["pl"]) * 1.25 for p in active), default=0.0))
    curve: list[tuple[float, float]] = []
    for i in range(81):
        p = max_p * i / 80
        factor = max(0.15, 1.0 - 0.25 * target_air / (p if p > 0 else 0.001)) if mode.startswith("이류체") else 1.0
        curve.append((p, float(result["avg_k"]) * math.sqrt(p) * factor))
    max_q = max(1.0, float(result["liquid_flow"]) * 1.2, max((q for _, q in curve), default=0.0) * 1.08,
                max((float(p["ql"]) * 1.2 for p in active), default=0.0))
    x = lambda value: left + value / max_p * (width - left - right)
    y = lambda value: bottom + value / max_q * (height - bottom - top)
    drawing = Drawing(width, height)
    grid, axis, blue, green, ink = map(HexColor, ["#DDE7ED", "#718797", "#0085C8", "#0A9B73", "#14364E"])
    for i in range(6):
        px = max_p * i / 5
        py = max_q * i / 5
        drawing.add(Line(x(px), bottom, x(px), height - top, strokeColor=grid, strokeWidth=.6))
        drawing.add(Line(left, y(py), width - right, y(py), strokeColor=grid, strokeWidth=.6))
        drawing.add(String(x(px), bottom - 15, f"{px:.1f}", fontName="Helvetica", fontSize=7, fillColor=axis, textAnchor="middle"))
        drawing.add(String(left - 7, y(py) - 2, f"{py:.1f}", fontName="Helvetica", fontSize=7, fillColor=axis, textAnchor="end"))
    drawing.add(Line(left, bottom, width - right, bottom, strokeColor=axis, strokeWidth=1.1))
    drawing.add(Line(left, bottom, left, height - top, strokeColor=axis, strokeWidth=1.1))
    path = Path()
    for index, (pressure, flow) in enumerate(curve):
        (path.moveTo if index == 0 else path.lineTo)(x(pressure), y(flow))
    path.strokeColor, path.strokeWidth, path.fillColor = blue, 2.2, None
    drawing.add(path)
    for index, point in enumerate(result["points"], start=1):
        if bool(point["active"]) and float(point["pl"]) > 0 and float(point["ql"]) > 0:
            drawing.add(Circle(x(float(point["pl"])), y(float(point["ql"])), 4, fillColor=HexColor("#075F9B"), strokeColor=None))
            drawing.add(String(x(float(point["pl"])), y(float(point["ql"])) + 7, f"P{index}", fontName="Helvetica-Bold", fontSize=7, fillColor=ink, textAnchor="middle"))
    drawing.add(Line(x(target_liquid), bottom, x(target_liquid), y(float(result["liquid_flow"])), strokeColor=green, strokeWidth=1, strokeDashArray=[4, 3]))
    drawing.add(Circle(x(target_liquid), y(float(result["liquid_flow"])), 5, fillColor=green, strokeColor=None))
    unit = "L/H" if mode.startswith("이류체") else "LPM"
    drawing.add(String(width / 2, 8, "Liquid Pressure (bar)", fontName="Helvetica-Bold", fontSize=8, fillColor=ink, textAnchor="middle"))
    drawing.add(String(left, height - 10, f"Flow Rate ({unit})", fontName="Helvetica-Bold", fontSize=8, fillColor=ink))
    return drawing


def build_pdf(product: str, mode: str, target_liquid: float, target_air: float,
              result: dict[str, Any]) -> bytes:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_RIGHT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont
    from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    pdfmetrics.registerFont(UnicodeCIDFont("HYSMyeongJo-Medium"))
    korean = "HYSMyeongJo-Medium"
    buffer = BytesIO()
    document = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=16 * mm, rightMargin=16 * mm,
                                 topMargin=14 * mm, bottomMargin=16 * mm, title="노즐 분사량 계산 리포트")
    styles = getSampleStyleSheet()
    normal = ParagraphStyle("KoreanNormal", parent=styles["Normal"], fontName=korean, fontSize=9, leading=14, textColor=colors.HexColor("#294A61"))
    title = ParagraphStyle("KoreanTitle", parent=normal, fontSize=20, leading=25, textColor=colors.HexColor("#072844"), spaceAfter=4)
    section = ParagraphStyle("Section", parent=normal, fontSize=11, leading=16, textColor=colors.HexColor("#072844"), spaceBefore=10, spaceAfter=6)
    right = ParagraphStyle("Right", parent=normal, alignment=TA_RIGHT, fontSize=8, textColor=colors.HexColor("#607789"))

    logo = Image(BytesIO(base64.b64decode(LOGO_PNG_BASE64)), width=68 * mm, height=13.4 * mm)
    logo.hAlign = "LEFT"

    story: list[Any] = []
    head = Table([[logo, Paragraph("SPRAY ENGINEERING CALCULATOR<br/>INDEPENDENT REPORT", right)]], colWidths=[105 * mm, 72 * mm])
    head.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LINEBELOW", (0, 0), (-1, -1), 1.2, colors.HexColor("#0085C8")), ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
    story.extend([head, Spacer(1, 9), Paragraph("노즐 분사량 계산 리포트", title),
                  Paragraph(f"작성일: {datetime.now().strftime('%Y-%m-%d %H:%M')}", normal), Spacer(1, 8)])
    story.append(Paragraph("1. 노즐 / 제품명", section))
    info = Table([["제품명", product or "노즐/제품"], ["노즐 형식", mode]], colWidths=[38 * mm, 139 * mm])
    info.setStyle(TableStyle([("FONTNAME", (0, 0), (-1, -1), korean), ("FONTSIZE", (0, 0), (-1, -1), 9),
                              ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EAF5FA")), ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#183A52")),
                              ("GRID", (0, 0), (-1, -1), .5, colors.HexColor("#C9D8E1")), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                              ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
    story.append(info)
    unit = "L/H" if mode.startswith("이류체") else "LPM"
    result_rows = [["항목", "결과"], ["목표 액체 압력", f"{target_liquid:.2f} bar"],
                   ["예측 액체 분사량", f"{result['liquid_flow']:.2f} {unit}"], ["평균 유량 계수 K", f"{result['avg_k']:.3f}"]]
    if mode.startswith("이류체"):
        result_rows.extend([["목표 공기 압력", f"{target_air:.2f} bar"], ["예측 공기 소모량", f"{result['air_flow']:.2f} NL/min"]])
    story.append(Paragraph("2. 예측 결과", section))
    results_table = Table(result_rows, colWidths=[75 * mm, 102 * mm])
    results_table.setStyle(TableStyle([("FONTNAME", (0, 0), (-1, -1), korean), ("FONTSIZE", (0, 0), (-1, -1), 9),
                                       ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#072844")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                                       ("TEXTCOLOR", (0, 1), (-1, -1), colors.HexColor("#183A52")), ("GRID", (0, 0), (-1, -1), .5, colors.HexColor("#C9D8E1")),
                                       ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    story.append(results_table)
    story.append(Paragraph("3. 압력-유량 특성 곡선", section))
    story.append(pdf_curve_drawing(mode, target_liquid, target_air, result))
    story.append(Paragraph("4. 기준점", section))
    point_rows = [["기준점", "액체 압력 (bar)", f"액체 유량 ({unit})", "K"]]
    for index, point in enumerate(result["points"], start=1):
        point_rows.append([f"P{index}", f"{float(point['pl']):.2f}", f"{float(point['ql']):.2f}", f"{float(point['kl']):.3f}"])
    point_table = Table(point_rows, colWidths=[30 * mm, 48 * mm, 55 * mm, 44 * mm])
    point_table.setStyle(TableStyle([("FONTNAME", (0, 0), (-1, -1), korean), ("FONTSIZE", (0, 0), (-1, -1), 8),
                                     ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EAF5FA")), ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#183A52")),
                                     ("GRID", (0, 0), (-1, -1), .5, colors.HexColor("#C9D8E1")), ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                                     ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
    story.append(point_table)
    story.extend([Spacer(1, 8), Paragraph("본 리포트는 입력한 데이터시트 기준점의 평균 K값으로 계산한 이론 결과입니다. 실제 선정 시 제조사 성능표, 유체 물성 및 현장 조건을 우선 확인하십시오.", normal)])

    def page_footer(canvas: Any, doc: Any) -> None:
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#C9D8E1"))
        canvas.line(16 * mm, 12 * mm, 194 * mm, 12 * mm)
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(colors.HexColor("#718594"))
        canvas.drawString(16 * mm, 8 * mm, "Spray Engineering Calculator - Independent Engineering Tool")
        canvas.drawRightString(194 * mm, 8 * mm, f"Page {doc.page}")
        canvas.restoreState()

    document.build(story, onFirstPage=page_footer, onLaterPages=page_footer)
    return buffer.getvalue()


def targets(mode: str) -> tuple[float, float]:
    st.markdown("<div class='subhead'>목표 운전 조건</div>", unsafe_allow_html=True)
    a, b = st.columns([1, 2.1])
    with a:
        liquid = st.number_input("목표 액체 압력 (bar)", min_value=0.0, max_value=10.0, step=.01, format="%.2f", key="target_liquid_input", on_change=sync, args=("target_liquid_input", "target_liquid_slider"), **initial_widget_value("target_liquid_input"))
    with b:
        st.slider("액체 압력 빠른 조정", 0.0, 10.0, step=.05, key="target_liquid_slider", on_change=sync, args=("target_liquid_slider", "target_liquid_input"), **initial_widget_value("target_liquid_slider"))
    air = float(st.session_state.get("target_air_input", DEFAULTS["target_air_input"]))
    if mode.startswith("이류체"):
        a, b = st.columns([1, 2.1])
        with a:
            air = st.number_input("목표 공기 압력 (bar)", min_value=0.0, max_value=10.0, step=.01, format="%.2f", key="target_air_input", on_change=sync, args=("target_air_input", "target_air_slider"), **initial_widget_value("target_air_input"))
        with b:
            st.slider("공기 압력 빠른 조정", 0.0, 10.0, step=.05, key="target_air_slider", on_change=sync, args=("target_air_slider", "target_air_input"), **initial_widget_value("target_air_slider"))
    return float(liquid), float(air)


def reference_points(mode: str) -> list[dict[str, float | bool]]:
    data = []
    for index in (1, 2):
        with st.container(border=True):
            st.markdown(f"**기준점 {index} (P{index})**")
            cols = st.columns(2)
            with cols[0]:
                pl = st.number_input(f"액체 압력 P{index} (bar)", min_value=0.0, max_value=100.0, step=.01, format="%.2f", key=f"p{index}_liquid_pressure", **initial_widget_value(f"p{index}_liquid_pressure"))
            with cols[1]:
                unit = "L/H" if mode.startswith("이류체") else "LPM"
                ql = st.number_input(f"액체 유량 Q{index} ({unit})", min_value=0.0, max_value=100000.0, step=.01, format="%.2f", key=f"p{index}_liquid_flow", **initial_widget_value(f"p{index}_liquid_flow"))
            pa = float(st.session_state.get(f"p{index}_air_pressure", DEFAULTS[f"p{index}_air_pressure"]))
            qa = float(st.session_state.get(f"p{index}_air_flow", DEFAULTS[f"p{index}_air_flow"]))
            if mode.startswith("이류체"):
                cols = st.columns(2)
                with cols[0]:
                    pa = st.number_input(f"공기 압력 Air{index} (bar)", min_value=0.0, max_value=100.0, step=.01, format="%.2f", key=f"p{index}_air_pressure", **initial_widget_value(f"p{index}_air_pressure"))
                with cols[1]:
                    qa = st.number_input(f"공기 유량 QA{index} (NL/min)", min_value=0.0, max_value=100000.0, step=.01, format="%.2f", key=f"p{index}_air_flow", **initial_widget_value(f"p{index}_air_flow"))
            data.append({"active": True, "pl": float(pl), "ql": float(ql), "pa": float(pa), "qa": float(qa)})
    return data


def flow_calculator() -> None:
    header()
    back, _ = st.columns([1.1, 5])
    with back:
        st.button("← 계산기 목록", width="stretch", on_click=go, args=("home",))
    st.markdown("""<section class="calc-intro"><div><span class="calc-index">CALCULATOR / 01</span><h1>노즐 분사량 계산기</h1><p>두 데이터시트 기준점의 평균 K값으로 목표 압력의 분사량을 계산합니다.</p></div><div class="calc-formula">Q = K√P</div></section>""", unsafe_allow_html=True)

    input_col, output_col = st.columns([0.92, 1.38], gap="large")
    with input_col:
        st.markdown("<div class='workspace-head'><span>INPUT CONDITIONS</span><h2>입력 조건</h2><p>노즐 정보와 운전 조건을 순서대로 입력하세요.</p></div>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("<div class='subhead'>노즐 기본 정보</div>", unsafe_allow_html=True)
            mode_options = ("일류체 노즐 (LPM)", "이류체 노즐 (L/H + Air)")
            mode = st.radio("노즐 형식", mode_options, index=mode_options.index(str(DEFAULTS["flow_mode"])), key="flow_mode")
            product = st.text_input("노즐 / 제품명", placeholder="클릭하여 입력", key="product_name", **initial_widget_value("product_name"))
            target_liquid, target_air = targets(mode)
            st.markdown("<div class='subhead'>데이터시트 기준점</div>", unsafe_allow_html=True)
            st.caption("P1과 P2를 모두 적용하여 두 K값의 평균으로 계산합니다.")
            points = reference_points(mode)
            st.button("조건 입력값 초기화", key="reset_conditions", width="stretch", on_click=reset_conditions)

    result = calculate(mode, target_liquid, target_air, points)
    unit = "L/H" if mode.startswith("이류체") else "LPM"

    with output_col:
        st.markdown("<div class='workspace-head'><span>CALCULATION OUTPUT</span><h2>계산 결과</h2><p>입력값이 바뀌면 결과와 그래프가 즉시 갱신됩니다.</p></div>", unsafe_allow_html=True)
        with st.container(border=True):
            metric_slots = st.columns([1.25, 1, 1])
            with metric_slots[0]:
                st.metric("예측 액체 분사량", f"{result['liquid_flow']:.2f} {unit}")
            with metric_slots[1]:
                st.metric("예측 공기 소모량" if mode.startswith("이류체") else "적용 기준점", f"{result['air_flow']:.2f} NL/min" if mode.startswith("이류체") else f"{result['valid_count']} 개")
            with metric_slots[2]:
                st.metric("평균 유량 계수 K", f"{result['avg_k']:.3f}")
            if result["valid_count"]:
                st.success(f"{product or '제품명 미입력'} · 기준점 {result['valid_count']}개 평균 적용")
            else:
                st.warning("두 기준점의 압력과 유량을 0보다 크게 입력하세요.")
            st.markdown("<div class='subhead'>기준점별 계산 계수</div>", unsafe_allow_html=True)
            kcols = st.columns(2)
            for i, (col, point) in enumerate(zip(kcols, result["points"], strict=True), start=1):
                with col:
                    st.metric(f"P{i} · K", f"{float(point['kl']):.3f}")

        with st.container(border=True):
            st.markdown("<div class='subhead'>압력-유량 특성 곡선</div>", unsafe_allow_html=True)
            st.vega_lite_chart(spec=chart_spec(mode, target_liquid, target_air, result), width="stretch")
            st.caption("파란색은 평균 K 특성곡선, 초록색은 목표 운전점입니다.")

        with st.container(border=True):
            st.markdown("<div class='subhead'>PDF 리포트</div>", unsafe_allow_html=True)
            pdf_data = build_pdf(product, mode, target_liquid, target_air, result)
            st.download_button("PDF 리포트 다운로드", data=pdf_data, file_name="nozzle_flow_rate_report.pdf", mime="application/pdf", type="primary", width="stretch")
            with st.expander("계산 방식 확인"):
                if mode.startswith("일류체"):
                    st.markdown("<div class='formula'><b>일류체</b><br>① Kᵢ = Qᵢ ÷ √Pᵢ<br>② K̄ = 유효한 Kᵢ의 평균<br>③ Qₜ = K̄ × √Pₜ</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div class='formula'><b>이류체</b><br>① F = max(0.15, 1 - 0.25 × Pₐ ÷ Pₗ)<br>② Kₗ = Qₗ ÷ (√Pₗ × F)<br>③ Qₗ,ₜ = K̄ₗ × √Pₗ,ₜ × Fₜ<br>④ Kₐ = Qₐ ÷ √Pₐ<br>⑤ Qₐ,ₜ = K̄ₐ × √Pₐ,ₜ</div>", unsafe_allow_html=True)
    footer()


def main() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
    init_state()
    if st.session_state.page == "flow":
        flow_calculator()
    else:
        home()


if __name__ == "__main__":
    _ = main()
