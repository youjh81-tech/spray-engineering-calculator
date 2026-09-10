"""Spray Engineering Calculator - stage 1.

Home with three calculator slots and a nozzle flow-rate calculator.
The nozzle calculator uses two reference points and can export a branded PDF.
"""

from __future__ import annotations

import math
from datetime import datetime
from io import BytesIO
from typing import Any

import requests
import streamlit as st


st.set_page_config(
    page_title="Spray Engineering Calculator",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="collapsed",
)

SITE_URL = "https://www.spray.com/ko-kr"
LOGO_URL = (
    "https://www.spray.com/ko-kr/-/media/spray/images/"
    "logo-spray-color-global.svg"
)

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
.page-title{position:relative;overflow:hidden;margin:.35rem 0 1rem;padding:1.4rem 1.6rem;border-left:5px solid var(--sky);background:linear-gradient(110deg,#061a2d,#093e64 74%,#0083b5);color:#fff;box-shadow:0 13px 32px rgba(7,40,68,.14)}.page-title:after{content:"";position:absolute;right:-170px;top:-225px;width:350px;height:350px;border:1px solid rgba(255,255,255,.28);border-radius:50%;box-shadow:0 0 0 45px rgba(255,255,255,.04),0 0 0 90px rgba(255,255,255,.025)}.page-title h1{margin:.28rem 0;font-size:clamp(1.65rem,3vw,2.45rem);letter-spacing:-.04em}.page-title p{margin:0;color:#cee5ef;font-size:.86rem}
.panel-title{margin:.2rem 0 .7rem;padding-bottom:.5rem;border-bottom:1px solid var(--line);color:var(--navy);font-size:.9rem;font-weight:800}.panel-title span{margin-right:.35rem;color:var(--blue)}
.formula{padding:.9rem 1rem;border-left:4px solid var(--sky);background:#edf8fc;color:#284960;font-size:.81rem;line-height:1.75}.legal{margin-top:1.8rem;padding-top:.8rem;border-top:1px solid var(--line);color:#728695;font-size:.7rem;line-height:1.6}
div[data-testid="stVerticalBlockBorderWrapper"]{border-color:var(--line)!important;border-radius:3px!important;background:rgba(255,255,255,.97);box-shadow:0 9px 25px rgba(7,40,68,.05)}
[data-testid="stMetric"]{min-height:112px;padding:.9rem!important;border-top:3px solid var(--blue);background:linear-gradient(#fff,#f4f9fb)}[data-testid="stMetricLabel"]{color:#607688!important}[data-testid="stMetricValue"]{color:var(--navy)!important}
div[data-baseweb="radio"]{gap:.4rem}div[data-baseweb="radio"] label{padding:.45rem .65rem;border:1px solid var(--line);background:#fff;color:var(--ink)!important}div[data-baseweb="radio"] label *,[data-testid="stRadio"] label *{color:var(--ink)!important;-webkit-text-fill-color:var(--ink)!important;opacity:1!important}
[data-testid="stWidgetLabel"],[data-testid="stWidgetLabel"] *,[data-testid="stTextInput"] label *,[data-testid="stNumberInput"] label *,[data-testid="stSlider"] label *,[data-testid="stCheckbox"] label *{color:#294a61!important;-webkit-text-fill-color:#294a61!important;opacity:1!important}
[data-testid="stTextInput"] input,[data-testid="stNumberInput"] input{color:#fff!important;-webkit-text-fill-color:#fff!important;caret-color:#fff!important}
.stButton>button,.stDownloadButton>button{min-height:42px;border-radius:2px;font-weight:750}.stButton>button[kind="primary"],.stDownloadButton>button[kind="primary"]{border-color:var(--blue);background:var(--blue)}
@media(max-width:720px){[data-testid="stMainBlockContainer"]{padding:.55rem .75rem 2rem}.site-head{align-items:flex-start;padding:.6rem}.brand img{width:150px;height:34px}.brand small,.app-id span{display:none}.app-id strong{font-size:.7rem}.hero{min-height:235px;padding:1.5rem 1.1rem}.hero p{font-size:.85rem}.menu-card{min-height:185px}.page-title{padding:1.15rem .95rem}}
</style>
"""

DEFAULTS: dict[str, Any] = {
    "flow_mode": "일류체 노즐 (LPM)",
    "product_name": "표준 노즐 - B201",
    "target_liquid_input": 5.0,
    "target_liquid_slider": 5.0,
    "target_air_input": 1.0,
    "target_air_slider": 1.0,
    "p1_active": True,
    "p1_liquid_pressure": 2.0,
    "p1_liquid_flow": 4.0,
    "p1_air_pressure": 0.5,
    "p1_air_flow": 25.0,
    "p2_active": True,
    "p2_liquid_pressure": 3.0,
    "p2_liquid_flow": 4.8,
    "p2_air_pressure": 1.0,
    "p2_air_flow": 35.0,
}


def init_state() -> None:
    st.session_state.setdefault("page", "home")
    for key, value in DEFAULTS.items():
        st.session_state.setdefault(key, value)


def reset_calculator() -> None:
    for key, value in DEFAULTS.items():
        st.session_state[key] = value


def go(page: str) -> None:
    st.session_state.page = page


def sync(source: str, target: str) -> None:
    st.session_state[target] = float(st.session_state[source])


def header() -> None:
    st.markdown(
        f"""<div class="site-head"><a class="brand" href="{SITE_URL}" target="_blank" rel="noopener noreferrer">
        <img src="{LOGO_URL}" alt="Spraying Systems Co. 공식 로고" onerror="this.style.display='none';this.nextElementSibling.style.display='inline-block'">
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


@st.cache_data(show_spinner=False, ttl=86400)
def logo_svg() -> bytes | None:
    try:
        response = requests.get(LOGO_URL, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        content = response.content
        return content if b"<svg" in content[:1024] else None
    except Exception:
        return None


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
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

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

    logo: Any
    svg = logo_svg()
    if svg:
        try:
            from svglib.svglib import svg2rlg
            logo = svg2rlg(BytesIO(svg))
            scale = min(145 / logo.width, 42 / logo.height)
            logo.scale(scale, scale)
            logo.width *= scale
            logo.height *= scale
        except Exception:
            logo = Paragraph("<b>SPRAYING SYSTEMS CO.</b>", ParagraphStyle("Logo", parent=normal, fontSize=13, textColor=colors.HexColor("#0878B9")))
    else:
        logo = Paragraph("<b>SPRAYING SYSTEMS CO.</b>", ParagraphStyle("Logo", parent=normal, fontSize=13, textColor=colors.HexColor("#0878B9")))

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
    result_rows = [["항목", "결과"], ["목표 액체 압력", f"{target_liquid:.3f} bar"],
                   ["예측 액체 분사량", f"{result['liquid_flow']:.3f} {unit}"], ["평균 유량 계수 K", f"{result['avg_k']:.3f}"]]
    if mode.startswith("이류체"):
        result_rows.extend([["목표 공기 압력", f"{target_air:.3f} bar"], ["예측 공기 소모량", f"{result['air_flow']:.3f} NL/min"]])
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
    point_rows = [["기준점", "사용", "액체 압력 (bar)", f"액체 유량 ({unit})", "K"]]
    for index, point in enumerate(result["points"], start=1):
        point_rows.append([f"P{index}", "예" if point["active"] else "아니오", f"{float(point['pl']):.3f}", f"{float(point['ql']):.3f}", f"{float(point['kl']):.3f}"])
    point_table = Table(point_rows, colWidths=[25 * mm, 22 * mm, 43 * mm, 47 * mm, 40 * mm])
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
    st.markdown("<div class='panel-title'><span>01</span> 목표 운전 조건</div>", unsafe_allow_html=True)
    a, b = st.columns([1, 2.1])
    with a:
        liquid = st.number_input("목표 액체 압력 (bar)", 0.1, 10.0, step=.05, format="%.3f", key="target_liquid_input", on_change=sync, args=("target_liquid_input", "target_liquid_slider"))
    with b:
        st.slider("액체 압력 빠른 조정", 0.1, 10.0, step=.05, key="target_liquid_slider", on_change=sync, args=("target_liquid_slider", "target_liquid_input"))
    air = float(st.session_state.target_air_input)
    if mode.startswith("이류체"):
        a, b = st.columns([1, 2.1])
        with a:
            air = st.number_input("목표 공기 압력 (bar)", 0.0, 10.0, step=.05, format="%.3f", key="target_air_input", on_change=sync, args=("target_air_input", "target_air_slider"))
        with b:
            st.slider("공기 압력 빠른 조정", 0.0, 10.0, step=.05, key="target_air_slider", on_change=sync, args=("target_air_slider", "target_air_input"))
    return float(liquid), float(air)


def reference_points(mode: str) -> list[dict[str, float | bool]]:
    data = []
    for index in (1, 2):
        with st.container(border=True):
            title_col, check_col = st.columns([3, 1])
            with title_col:
                st.markdown(f"**기준점 {index} (P{index})**")
            with check_col:
                active = st.checkbox("사용", key=f"p{index}_active")
            cols = st.columns(2)
            with cols[0]:
                pl = st.number_input(f"액체 압력 P{index} (bar)", 0.0, 100.0, step=.1, format="%.3f", key=f"p{index}_liquid_pressure", disabled=not active)
            with cols[1]:
                unit = "L/H" if mode.startswith("이류체") else "LPM"
                ql = st.number_input(f"액체 유량 Q{index} ({unit})", 0.0, 100000.0, step=.1, format="%.3f", key=f"p{index}_liquid_flow", disabled=not active)
            pa = float(st.session_state[f"p{index}_air_pressure"])
            qa = float(st.session_state[f"p{index}_air_flow"])
            if mode.startswith("이류체"):
                cols = st.columns(2)
                with cols[0]:
                    pa = st.number_input(f"공기 압력 Air{index} (bar)", 0.0, 100.0, step=.1, format="%.3f", key=f"p{index}_air_pressure", disabled=not active)
                with cols[1]:
                    qa = st.number_input(f"공기 유량 QA{index} (NL/min)", 0.0, 100000.0, step=.1, format="%.3f", key=f"p{index}_air_flow", disabled=not active)
            data.append({"active": active, "pl": float(pl), "ql": float(ql), "pa": float(pa), "qa": float(qa)})
    return data


def flow_calculator() -> None:
    header()
    back, reset, _ = st.columns([1.1, 1, 4])
    with back:
        st.button("← 계산기 선택", width="stretch", on_click=go, args=("home",))
    with reset:
        st.button("기본값 초기화", width="stretch", on_click=reset_calculator)
    st.markdown("""<section class="page-title"><div class="eyebrow">CALCULATOR 01 · NOZZLE FLOW RATE</div><h1>노즐 분사량 계산기</h1><p>두 개의 데이터시트 기준점으로 목표 압력에서의 노즐 분사량을 예측합니다.</p></section>""", unsafe_allow_html=True)
    mode_col, name_col = st.columns([1.35, 1])
    with mode_col:
        mode = st.radio("노즐 형식", ("일류체 노즐 (LPM)", "이류체 노즐 (L/H + Air)"), horizontal=True, key="flow_mode")
    with name_col:
        product = st.text_input("노즐 / 제품명", key="product_name")
    target_col, result_col = st.columns([1.05, 1.5], gap="large")
    with target_col:
        with st.container(border=True):
            target_liquid, target_air = targets(mode)
    with result_col:
        st.markdown("<div class='panel-title'><span>02</span> 예측 결과</div>", unsafe_allow_html=True)
        metric_slots = st.columns(3)
    inputs_col, chart_col = st.columns([1, 1.28], gap="large")
    with inputs_col:
        st.markdown("<div class='panel-title'><span>03</span> 데이터시트 기준점</div>", unsafe_allow_html=True)
        st.caption("P1과 P2 중 사용할 기준점만 체크하세요. 유효한 K값의 평균으로 계산합니다.")
        points = reference_points(mode)
    result = calculate(mode, target_liquid, target_air, points)
    unit = "L/H" if mode.startswith("이류체") else "LPM"
    with result_col:
        with metric_slots[0]:
            st.metric("예측 액체 분사량", f"{result['liquid_flow']:.3f} {unit}")
        with metric_slots[1]:
            st.metric("예측 공기 소모량" if mode.startswith("이류체") else "활성 기준점", f"{result['air_flow']:.3f} NL/min" if mode.startswith("이류체") else f"{result['valid_count']} 개")
        with metric_slots[2]:
            st.metric("평균 유량 계수 K", f"{result['avg_k']:.3f}")
        if result["valid_count"]:
            st.success(f"{product or '노즐/제품'} · 유효 기준점 {result['valid_count']}개 평균 적용")
        else:
            st.warning("압력과 유량이 0보다 큰 기준점을 하나 이상 사용하세요.")
    with inputs_col:
        st.markdown("**기준점별 계산 계수**")
        kcols = st.columns(2)
        for i, (col, point) in enumerate(zip(kcols, result["points"], strict=True), start=1):
            with col:
                st.metric(f"P{i} · K", f"{float(point['kl']):.3f}" if point["active"] else "비활성")
    with chart_col:
        st.markdown("<div class='panel-title'><span>04</span> 압력-유량 특성 곡선</div>", unsafe_allow_html=True)
        st.vega_lite_chart(spec=chart_spec(mode, target_liquid, target_air, result), width="stretch")
        st.caption("파란색은 평균 K 특성곡선, 초록색은 목표 운전점입니다.")
    st.markdown("<div class='panel-title'><span>05</span> PDF 리포트</div>", unsafe_allow_html=True)
    pdf_data = build_pdf(product, mode, target_liquid, target_air, result)
    st.download_button("회사 로고 포함 PDF 리포트 다운로드", data=pdf_data, file_name="nozzle_flow_rate_report.pdf", mime="application/pdf", type="primary", width="stretch")
    with st.expander("계산 방식 확인"):
        if mode.startswith("일류체"):
            st.markdown("<div class='formula'><b>일류체</b><br>① Kᵢ = Qᵢ ÷ √Pᵢ<br>② K̄ = 유효한 Kᵢ의 평균<br>③ Qₜ = K̄ × √Pₜ</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='formula'><b>이류체</b><br>① F = max(0.15, 1 - 0.25 × Pₐ ÷ Pₗ)<br>② Kₗ = Qₗ ÷ (√Pₗ × F)<br>③ Qₗ,ₜ = K̄ₗ × √Pₗ,ₜ × Fₜ<br>④ Kₐ = Qₐ ÷ √Pₐ<br>⑤ Qₐ,ₜ = K̄ₐ × √Pₐ,ₜ</div>", unsafe_allow_html=True)
    footer()


def main() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
    init_state()
    flow_calculator() if st.session_state.page == "flow" else home()


if __name__ == "__main__":
    main()
