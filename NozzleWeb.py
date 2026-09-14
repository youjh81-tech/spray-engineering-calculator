"""Spray Engineering Calculator: nine active calculators.

Calculators 02–06 reproduce the supplied AIR/WATER, nozzle, slit and density workbooks.
"""

from __future__ import annotations

import base64
from copy import deepcopy
from contextvars import ContextVar
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
.hero{position:relative;overflow:hidden;min-height:180px;display:flex;align-items:center;padding:20px clamp(1.7rem,5vw,4rem);background:radial-gradient(ellipse at 87% 11%,rgba(0,190,239,.50),transparent 42%),linear-gradient(112deg,#061a2d,#083b60 63%,#007cab);box-shadow:0 22px 52px rgba(7,40,68,.18)}
.hero:after{content:"";position:absolute;right:-12%;top:-72%;width:620px;height:620px;border:1px solid rgba(255,255,255,.25);border-radius:50%;box-shadow:0 0 0 55px rgba(255,255,255,.04),0 0 0 110px rgba(255,255,255,.025)}
.hero>div{position:relative;z-index:1}.eyebrow{color:#6ddcff;font-size:.72rem;font-weight:800;letter-spacing:.18em}.hero h1{padding:0!important;margin:.45rem 0 .65rem;color:#fff;font-size:clamp(1.2rem,3.4vw,2.7rem);white-space:nowrap;line-height:1.08;letter-spacing:-.05em}.hero p{margin:0;color:#d7edf6;font-size:1rem}
.section-kicker{margin-top:2rem;color:#0072ae;font-size:.7rem;font-weight:800;letter-spacing:.16em}.section-title{margin:.2rem 0;color:var(--navy);font-size:clamp(1.45rem,3vw,2.1rem);font-weight:800}.section-copy{color:var(--muted);font-size:.88rem;margin-bottom:1rem}
.menu-card{min-height:215px;padding:1.25rem;border:1px solid var(--line);border-top:4px solid var(--blue);background:#fff;box-shadow:0 13px 32px rgba(7,40,68,.075)}.menu-card.pending{border-top-color:#a8b6c0;background:#f8fafb}.menu-card .num{color:var(--blue);font-size:.7rem;font-weight:800;letter-spacing:.14em}.menu-card.pending .num{color:#8596a3}.menu-card h3{margin:.7rem 0 .5rem;color:var(--navy);font-size:1.16rem}.menu-card p{min-height:63px;color:var(--muted);font-size:.82rem;line-height:1.65}.pill{display:inline-block;padding:.28rem .58rem;border-radius:99px;background:#e1f5fc;color:#006d9e;font-size:.66rem;font-weight:800}.pending .pill{background:#e9eef1;color:#71818d}
.calc-intro{display:flex;align-items:center;justify-content:space-between;gap:2rem;margin:.25rem 0 1.35rem;padding:1.35rem 1.5rem;border:1px solid #cbdde7;border-left:6px solid var(--blue);background:linear-gradient(120deg,#fff 0,#f3f9fc 66%,#e1f3fa 100%);box-shadow:0 10px 28px rgba(7,40,68,.07)}.calc-intro .calc-index{color:#0079b6;font-size:.68rem;font-weight:800;letter-spacing:.16em}.calc-intro h1{margin:.3rem 0 .35rem;color:var(--navy);font-size:clamp(1.65rem,3vw,2.25rem);letter-spacing:-.045em}.calc-intro p{margin:0;color:#587184;font-size:.84rem}.calc-formula{flex:0 0 auto;padding:.75rem 1rem;border-radius:4px;background:#072844;color:#fff;font:700 1rem/1.2 Georgia,serif;letter-spacing:.04em}
.workspace-head{margin:.15rem 0 1rem}.workspace-head span{display:block;color:#0079b6;font-size:.8rem;font-weight:800;letter-spacing:.14em}.workspace-head h2{margin:.22rem 0;color:var(--navy);font-size:1.48rem;line-height:1.3}.workspace-head p{margin:.25rem 0;color:var(--muted);font-size:.9rem}.subhead{margin:.45rem 0 .55rem;color:#153b55;font-size:.84rem;font-weight:800}.subhead:before{content:"";display:inline-block;width:4px;height:13px;margin-right:.45rem;vertical-align:-2px;background:var(--blue)}
.reference-guide{padding:1rem;border:1px solid #bfd9e6;background:#f4f9fc}.catalog-table-head{display:flex;align-items:center;justify-content:space-between;gap:1rem;padding:.8rem 1rem;background:linear-gradient(100deg,#072844,#0a5480);color:#fff}.catalog-table-head span{font-size:.7rem;font-weight:800;letter-spacing:.14em;color:#63d5ff}.catalog-table-head strong{display:block;margin-top:.15rem;font-size:1rem}.catalog-table-head em{font-style:normal;font-size:.74rem;color:#d7edf6}.catalog-scroll{overflow-x:auto;background:#fff;border:1px solid #b9ceda;border-top:0}.catalog-table{width:100%;min-width:900px;border-collapse:collapse;table-layout:fixed;color:#18394f;font-size:.8rem}.catalog-table th,.catalog-table td{padding:.55rem .34rem;border:1px solid #b8cbd6;text-align:center;white-space:nowrap}.catalog-table thead tr:first-child th{background:#0b3a5c;color:#fff;font-weight:800}.catalog-table thead tr:nth-child(2) th{background:#dceff7;color:#123e5b;font-weight:800}.catalog-table th:nth-child(-n+3){width:10%}.catalog-table tbody tr:nth-child(even) td{background:#f5f9fb}.catalog-table tbody .selected-row td{box-shadow:inset 0 2px #e6ca00,inset 0 -2px #e6ca00;background:#eaf6fa}.catalog-table .selected-col{background:#fff7bd!important;box-shadow:inset 3px 0 #efd200,inset -3px 0 #efd200}.catalog-table thead .selected-col{color:#123348!important;background:#ffe45d!important}.catalog-table .row-key,.catalog-table .selected-point{background:#ffe45d!important;color:#092f49;font-weight:900}.guide-copy{display:grid;grid-template-columns:.8fr .8fr 1.15fr 1.45fr;gap:.65rem;margin-top:.75rem}.guide-item,.guide-example,.guide-note{margin:0;padding:.68rem .75rem;line-height:1.55}.guide-item{background:#fff;border-left:4px solid #f0cf00;color:#496478;font-size:.76rem}.guide-item b{display:block;color:var(--navy);font-size:.8rem}.guide-example{background:#dff2fa;color:#23465e;font-size:.76rem}.guide-example b{color:#006fa7}.guide-note{border-left:4px solid var(--blue);background:#fff;color:#405e72;font-size:.76rem}[data-testid="stExpander"] summary{background:#102c42!important;border-radius:2px!important}[data-testid="stExpander"] summary,[data-testid="stExpander"] summary *{color:#fff!important;-webkit-text-fill-color:#fff!important;fill:#fff!important;opacity:1!important;font-size:.9rem!important;font-weight:800!important}
.workspace-head span{font-size:.92rem}.workspace-head h2{font-size:1.68rem}.workspace-head p{font-size:.95rem}.catalog-table thead tr:first-child th:first-child{background:#0b6b62}.catalog-table thead tr:nth-child(2) th{background:#ffecd2}.catalog-table tbody td:first-child{background:#d9f2e8!important;color:#124f48;font-weight:800}.catalog-table .row-key{background:#ffe45d!important;color:#092f49}.guide-item.pressure-key{border-left-color:#ee8a20;background:#ffecd2;color:#654214}.guide-item.nozzle-key{border-left-color:#0b8a72;background:#d9f2e8;color:#17574e}
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
@media(max-width:720px){[data-testid="stMainBlockContainer"]{padding:.55rem .75rem 2rem}.site-head{flex-direction:column;align-items:stretch;gap:.65rem;padding:.8rem}.brand{flex-direction:column;align-items:flex-start;gap:.35rem;min-width:0}.brand img{width:190px;max-width:100%;height:38px}.brand small{display:block;color:#315b73;font-size:.78rem;line-height:1.5;overflow-wrap:anywhere}.app-id{text-align:left;border-top:1px solid var(--line);padding-top:.55rem}.app-id strong{font-size:.82rem}.app-id span{display:block;margin-top:.2rem;color:#315b73;font-size:.72rem;line-height:1.5;letter-spacing:.06em;overflow-wrap:anywhere}.hero{min-height:150px;padding:1rem 1.1rem}.hero p{font-size:.85rem}.menu-card{min-height:185px}.calc-intro{align-items:flex-start;padding:1rem}.calc-formula{display:none}.reference-guide{padding:.65rem}.catalog-table-head{align-items:flex-start;padding:.7rem}.catalog-table-head em{display:none}.guide-copy{grid-template-columns:1fr 1fr}.workspace-head span{font-size:.74rem}.workspace-head h2{font-size:1.32rem}.workspace-head p{font-size:.84rem}}
@media(max-width:720px){.workspace-head span{font-size:.84rem}.workspace-head h2{font-size:1.48rem}.workspace-head p{font-size:.9rem}}
.coefficient-note{font-size:.82rem!important;line-height:1.5;color:#405b70!important;padding:4px 8px;background:#edf3f7;border-radius:4px}.coefficient-note b{font-size:.87rem!important;color:#173c57!important}
[data-testid="stMetric"]{background:#e0f2fb!important;border-radius:6px;padding:12px 15px!important;min-height:90px!important}
[data-testid="stMetricValue"],[data-testid="stMetricValue"] *{font-weight:800!important;color:#073453!important;-webkit-text-fill-color:#073453!important}
[data-testid="stAlert"] p,[data-testid="stAlert"] li,[data-testid="stAlert"] span{color:#263b4b!important;-webkit-text-fill-color:#263b4b!important;opacity:1!important;font-weight:600!important}
[data-testid="stAlert"]{background:#fff3ce!important;border:1px solid #dec16d!important}
</style>
"""

DEFAULTS: dict[str, Any] = {
    "flow_mode": "일류체 노즐 (액체)",
    "product_name": "",
    "target_basis": "압력 기준",
    "target_liquid_input": 5.0,
    "target_liquid_slider": 5.0,
    "target_flow_input": 5.0,
    "target_flow_slider": 5.0,
    "air_diameter": 2.0,
    "air_temperature": 20.0,
    "target_air_flow_input": 35.0,
    "target_air_flow_slider": 35.0,
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
    for key, mapping in {
        "target_basis": {"액체 압력 기준": "압력 기준", "액체 유량 기준": "유량 기준"},
        "flow_mode": {"이류체 노즐 (액체 + 에어)": "외부혼합 이류체 노즐 (액체 + 에어)", "일류체 노즐 (LPM)": "일류체 노즐 (액체)", "이류체 노즐 (L/H + Air)": "외부혼합 이류체 노즐 (액체 + 에어)"},
    }.items():
        if st.session_state.get(key) in mapping:
            st.session_state[key] = mapping[st.session_state[key]]


def reset_conditions() -> None:
    condition_keys = [
        key for key in DEFAULTS
        if (key.startswith("target_") and key != "target_basis") or key.startswith("p1_") or key.startswith("p2_")
    ]
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
        <div class="app-id"><strong>Spray Engineering Calculator</strong><span>No.1 SPRAY SOLUTION PROVIDER</span></div></div>""",
        unsafe_allow_html=True,
    )


def footer() -> None:
    st.markdown(
        """<div class="legal">본 계산기는 현장 검토를 돕기 위한 독립적인 계산 도구입니다. 실제 노즐 선정과 운전 조건은 제조사 데이터시트 및 기술 담당자의 검토 결과를 우선 적용하십시오. Spraying Systems Co. 로고는 사용자 요청에 따라 공식 홈페이지 연결 및 리포트 식별 영역에 표시됩니다.</div>""",
        unsafe_allow_html=True,
    )
    st.markdown('<div style="margin-top:18px;padding:14px 0;border-top:1px solid #cbdde7;color:#294a61;text-align:center;font-size:13px">Powered by Spraying Systems Korea 기술영업부 유재환 수석 <strong><a style="color:#0079b6" href="mailto:jhyou@spray.co.kr">jhyou@spray.co.kr</a></strong></div>', unsafe_allow_html=True)



# The supplied formula uses kgf/cm² absolute, mm² and t + 273.
BAR_PER_KGF_CM2 = 0.980665


def air_capacity(pressure: float, diameter: float, temperature: float) -> float:
    """Air flow for C=1 under the supplied density 1.2 kg/m³ convention."""
    if diameter <= 0 or temperature <= -273 or pressure < 0:
        return 0.0
    area = math.pi * diameter ** 2 / 4
    return (237.6 / 1.2) * area * (pressure / BAR_PER_KGF_CM2 + 1.033) / math.sqrt(temperature + 273)


def liquid_flow_at_pressure(mode: str, pressure: float, target_air: float, avg_k: float) -> float:
    return avg_k * math.sqrt(pressure) if pressure > 0 and avg_k > 0 else 0.0


def pressure_for_flow(mode: str, target_flow: float, target_air: float, avg_k: float) -> float:
    return (target_flow / avg_k) ** 2 if target_flow > 0 and avg_k > 0 else 0.0


def calculate(mode: str, target_basis: str, target_value: float, target_air: float,
              points: list[dict[str, float | bool]], diameter: float = 1.0,
              temperature: float = 20.0) -> dict[str, Any]:
    liquid_ks, air_cs, calculated = [], [], []
    dual = ("이류체" in mode)
    for point in points:
        pl, ql, pa, qa = (float(point[k]) for k in ("pl", "ql", "pa", "qa"))
        active = bool(point["active"])
        kl = ql / math.sqrt(pl) if active and pl > 0 and ql > 0 else 0.0
        capacity = air_capacity(pa, diameter, temperature)
        c = qa / capacity if dual and active and pa > 0 and qa > 0 and capacity > 0 else 0.0
        if kl > 0:
            liquid_ks.append(kl)
        if c > 0:
            air_cs.append(c)
        calculated.append({**point, "kl": kl, "c": c})
    avg_k = sum(liquid_ks) / len(liquid_ks) if liquid_ks else 0.0
    avg_c = sum(air_cs) / len(air_cs) if air_cs else 0.0
    flow_basis = target_basis == "유량 기준"
    target_pressure = pressure_for_flow(mode, target_value, 0, avg_k) if flow_basis else target_value
    liquid_flow = liquid_flow_at_pressure(mode, target_pressure, 0, avg_k)
    air_pressure, air_flow, air_error = target_air, 0.0, ""
    if dual and avg_c > 0:
        if flow_basis:
            # Invert exactly; never present a negative gauge pressure as a valid result.
            air_pressure = (target_air / (avg_c * air_capacity(0, diameter, temperature)) - 1) * 1.033 * BAR_PER_KGF_CM2
            if air_pressure < 0:
                air_error = "목표 공기 유량이 첨부 식의 0 bar 계산 범위보다 작습니다. 목표 유량 또는 기준점을 확인하세요."
                air_pressure = 0.0
            else:
                air_flow = target_air
        else:
            air_flow = avg_c * air_capacity(air_pressure, diameter, temperature)
    return {"avg_k": avg_k, "avg_c": avg_c, "liquid_flow": liquid_flow, "air_flow": air_flow,
            "air_pressure": air_pressure, "air_error": air_error, "air_valid_count": len(air_cs),
            "diameter": diameter, "temperature": temperature,
            "target_basis": target_basis, "target_input": target_value, "target_air_input": target_air,
            "target_pressure": target_pressure, "valid_count": len(liquid_ks), "points": calculated}


def air_chart_result(result: dict[str, Any]) -> dict[str, Any]:
    return {**result, "target_pressure": result["air_pressure"], "liquid_flow": result["air_flow"],
            "points": [{**p, "pl": p["pa"], "ql": p["qa"]} for p in result["points"]]}


def chart_spec(mode: str, target_air: float, result: dict[str, Any], air: bool = False) -> dict[str, Any]:
    if air:
        result = air_chart_result(result)
    active = [p for p in result["points"] if bool(p["active"]) and float(p["pl"]) > 0 and float(p["ql"]) > 0]
    target_pressure = float(result["target_pressure"])
    max_p = max(5.0, target_pressure * 1.25, max((float(p["pl"]) * 1.25 for p in active), default=0.0))
    curve = []
    for i in range(81):
        p = max_p * i / 80
        flow = result["avg_c"] * air_capacity(p, result["diameter"], result["temperature"]) if air else result["avg_k"] * math.sqrt(p)
        curve.append({"pressure": p, "flow": flow})
    refs = [{"pressure": float(p["pl"]), "flow": float(p["ql"]), "label": f"P{i}"}
            for i, p in enumerate(result["points"], start=1)
            if bool(p["active"]) and float(p["pl"]) > 0 and float(p["ql"]) > 0]
    target = [{"pressure": target_pressure, "flow": float(result["liquid_flow"]), "label": "목표점"}]
    unit = "NL/min" if air else ("L/H" if ("이류체" in mode) else "LPM")
    return {"height": 350, "background": "#fff", "config": {"view": {"stroke": "#d6e2e9"},
            "axis": {"labelColor": "#577084", "titleColor": "#14364e", "gridColor": "#dce7ed"}}, "layer": [
        {"data": {"values": curve}, "mark": {"type": "line", "color": "#0085c8", "strokeWidth": 3},
         "encoding": {"x": {"field": "pressure", "type": "quantitative", "title": "공기 압력 (bar)" if air else "액체 압력 (bar)", "scale": {"domain": [0, max_p]}},
                      "y": {"field": "flow", "type": "quantitative", "title": f"분사량 Flow Rate ({unit})", "scale": {"zero": True}},
                      "tooltip": [{"field": "pressure", "title": "압력 (bar)", "format": ".3f"}, {"field": "flow", "title": f"유량 ({unit})", "format": ".3f"}]}},
        {"data": {"values": refs}, "mark": {"type": "point", "filled": True, "color": "#075f9b", "size": 105},
         "encoding": {"x": {"field": "pressure", "type": "quantitative"}, "y": {"field": "flow", "type": "quantitative"},
                      "tooltip": [{"field": "label", "title": "기준점"}, {"field": "pressure", "title": "압력 (bar)"}, {"field": "flow", "title": f"유량 ({unit})"}]}},
        {"data": {"values": target}, "mark": {"type": "rule", "color": "#0a9b73", "strokeDash": [5, 4]},
         "encoding": {"x": {"field": "pressure", "type": "quantitative"}}},
        {"data": {"values": target}, "mark": {"type": "point", "filled": True, "color": "#0a9b73", "size": 175},
         "encoding": {"x": {"field": "pressure", "type": "quantitative"}, "y": {"field": "flow", "type": "quantitative"},
                      "tooltip": [{"field": "label", "title": "구분"}, {"field": "pressure", "title": "계산 압력 (bar)", "format": ".3f"}, {"field": "flow", "title": f"계산 유량 ({unit})", "format": ".3f"}]}}
    ]}


def pdf_curve_drawing(mode: str, target_air: float, result: dict[str, Any], air: bool = False) -> Any:
    from reportlab.graphics.shapes import Circle, Drawing, Line, Path, String
    from reportlab.lib.colors import HexColor

    width, height = 500, (185 if ("이류체" in mode) else 180)
    left, right, bottom, top = 52, 18, 36, 22
    if air:
        result = air_chart_result(result)
    active = [p for p in result["points"] if bool(p["active"]) and float(p["pl"]) > 0 and float(p["ql"]) > 0]
    target_pressure = float(result["target_pressure"])
    max_p = max(5.0, target_pressure * 1.25, max((float(p["pl"]) * 1.25 for p in active), default=0.0))
    curve: list[tuple[float, float]] = []
    for i in range(81):
        p = max_p * i / 80
        flow = result["avg_c"] * air_capacity(p, result["diameter"], result["temperature"]) if air else result["avg_k"] * math.sqrt(p)
        curve.append((p, flow))
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
    drawing.add(Line(x(target_pressure), bottom, x(target_pressure), y(float(result["liquid_flow"])), strokeColor=green, strokeWidth=1, strokeDashArray=[4, 3]))
    drawing.add(Circle(x(target_pressure), y(float(result["liquid_flow"])), 5, fillColor=green, strokeColor=None))
    unit = "NL/min" if air else ("L/H" if ("이류체" in mode) else "LPM")
    drawing.add(String(width / 2, 8, "Air Pressure (bar)" if air else "Liquid Pressure (bar)", fontName="Helvetica-Bold", fontSize=8, fillColor=ink, textAnchor="middle"))
    drawing.add(String(left, height - 10, f"Flow Rate ({unit})", fontName="Helvetica-Bold", fontSize=8, fillColor=ink))
    return drawing


REPORT_NOTICE = "본 리포트는 입력 조건을 바탕으로 계산한 이론 결과입니다. 실제 선정 시 제조사 성능표, 유체 물성 및 현장 조건을 우선 확인하십시오."


def author_inputs() -> None:
    labels = ['부서명', '이름', '이메일 주소', '연락처']
    saved = st.session_state.get('report_author_details', {})
    with st.expander('PDF 작성자 정보 입력 (선택)', expanded=False):
        st.caption('입력한 정보는 1~6번 PDF 하단에 공통으로 표시됩니다. 빈 항목은 표시하지 않습니다.')
        cols = st.columns(4)
        for col, label in zip(cols, labels):
            with col:
                saved[label] = st.text_input(label, value=saved.get(label, ''), max_chars=80, key='report_author_'+label)
    st.session_state['report_author_details'] = dict(saved)



_report_author_snapshot = ContextVar('report_author_snapshot', default=None)


def deferred_pdf(builder, *args):
    """Capture this page's values and author before the download worker runs."""
    author = deepcopy(st.session_state.get('report_author_details', {}))
    values = deepcopy(args)
    def generate():
        token = _report_author_snapshot.set(author)
        try:
            return builder(*values)
        finally:
            _report_author_snapshot.reset(token)
    return generate


def report_page_footer(canvas: Any, doc: Any) -> None:
    from html import escape
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import Paragraph
    canvas.saveState()
    width, _ = doc.pagesize
    left, right = doc.leftMargin, width-doc.rightMargin
    canvas.setStrokeColor(colors.HexColor('#C9D8E1'))
    canvas.line(left, 72, right, 72)
    details = _report_author_snapshot.get()
    if details is None:
        details = st.session_state.get('report_author_details', {})
    text = ' · '.join(escape(label+': '+value.strip()) for label,value in details.items() if value.strip())
    if text:
        style = ParagraphStyle('AuthorFooter', fontName='HYSMyeongJo-Medium', fontSize=8, leading=11, textColor=colors.HexColor('#294A61'))
        paragraph = Paragraph(text, style)
        _, height = paragraph.wrap(right-left, 60)
        paragraph.drawOn(canvas, left, 65-height)
    canvas.setFont('Helvetica', 7)
    canvas.setFillColor(colors.HexColor('#718594'))
    canvas.drawString(left, 15, 'Spray Engineering Calculator - No.1 SPRAY SOLUTION PROVIDER')
    canvas.drawRightString(right, 15, f'Page {doc.page}')
    canvas.restoreState()


def report_header(width: float) -> Any:
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import Image, Paragraph, Table, TableStyle
    logo = Image(BytesIO(base64.b64decode(LOGO_PNG_BASE64)), width=193, height=38)
    logo.hAlign = 'LEFT'
    style = ParagraphStyle('ReportBrand', fontName='Helvetica', fontSize=8, leading=14, alignment=2, textColor=colors.HexColor('#607789'))
    head = Table([[logo, Paragraph('SPRAY ENGINEERING CALCULATOR<br/>No.1 SPRAY SOLUTION PROVIDER', style)]], colWidths=[width*.53,width*.47])
    head.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LINEBELOW',(0,0),(-1,-1),1.2,colors.HexColor('#0085C8')),('LEFTPADDING',(0,0),(0,0),0),('RIGHTPADDING',(-1,0),(-1,0),0),('BOTTOMPADDING',(0,0),(-1,-1),10)]))
    return head


def build_pdf(product: str, mode: str, target_basis: str, target_value: float, target_air: float,
              result: dict[str, Any]) -> bytes:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_RIGHT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont
    from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle, PageBreak

    pdfmetrics.registerFont(UnicodeCIDFont("HYSMyeongJo-Medium"))
    korean = "HYSMyeongJo-Medium"
    buffer = BytesIO()
    document = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=16 * mm, rightMargin=16 * mm,
                                 topMargin=14 * mm, bottomMargin=90, title="노즐 분사량 계산 리포트")
    styles = getSampleStyleSheet()
    normal = ParagraphStyle("KoreanNormal", parent=styles["Normal"], fontName=korean, fontSize=9, leading=14, textColor=colors.HexColor("#294A61"))
    title = ParagraphStyle("KoreanTitle", parent=normal, fontSize=20, leading=25, textColor=colors.HexColor("#072844"), spaceAfter=4)
    section = ParagraphStyle("Section", parent=normal, fontSize=11, leading=16, textColor=colors.HexColor("#072844"), spaceBefore=10, spaceAfter=6)
    right = ParagraphStyle("Right", parent=normal, alignment=TA_RIGHT, fontSize=8, textColor=colors.HexColor("#607789"))

    story: list[Any] = []
    head = report_header(document.width)
    story.extend([head, Spacer(1, 9), Paragraph("노즐 분사량 계산 리포트", title),
                  Paragraph(f"작성일: {datetime.now().strftime('%Y-%m-%d %H:%M')}", normal), Spacer(1, 8)])
    story.append(Paragraph("1. 노즐 / 제품명", section))
    info = Table([["제품명", product or "노즐/제품"], ["노즐 형식", mode]], colWidths=[38 * mm, 139 * mm])
    info.setStyle(TableStyle([("FONTNAME", (0, 0), (-1, -1), korean), ("FONTSIZE", (0, 0), (-1, -1), 9),
                              ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EAF5FA")), ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#183A52")),
                              ("GRID", (0, 0), (-1, -1), .5, colors.HexColor("#C9D8E1")), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                              ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
    story.append(info)
    unit = "L/H" if ("이류체" in mode) else "LPM"
    result_rows = [["항목", "결과"], ["계산 기준", target_basis]]
    if target_basis == "유량 기준":
        result_rows.extend([["목표 액체 유량", f"{target_value:.2f} {unit}"],
                            ["예측 액체 압력", f"{result['target_pressure']:.2f} bar"]])
    else:
        result_rows.extend([["목표 액체 압력", f"{target_value:.2f} bar"],
                            ["예측 액체 분사량", f"{result['liquid_flow']:.2f} {unit}"]])
    result_rows.append(["평균 유량 계수 K", f"{result['avg_k']:.3f}"])
    if ("이류체" in mode):
        result_rows.extend([["공기 노즐 구경 / 온도", f"{result['diameter']:.2f} mm / {result['temperature']:.2f} °C"],
                            ["평균 공기 유량 계수 C", f"{result['avg_c']:.4f}"]])
        if target_basis == "유량 기준":
            result_rows.extend([["목표 공기 유량", f"{target_air:.2f} NL/min"],
                                ["예측 공기 압력", "계산 범위 확인" if result["air_error"] else f"{result['air_pressure']:.2f} bar"]])
        else:
            result_rows.extend([["목표 공기 압력", f"{target_air:.2f} bar"],
                                ["예측 공기 유량", f"{result['air_flow']:.2f} NL/min"]])
    story.append(Paragraph("2. 예측 결과", section))
    results_table = Table(result_rows, colWidths=[75 * mm, 102 * mm])
    results_table.setStyle(TableStyle([("FONTNAME", (0, 0), (-1, -1), korean), ("FONTSIZE", (0, 0), (-1, -1), 9),
                                       ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#072844")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                                       ("TEXTCOLOR", (0, 1), (-1, -1), colors.HexColor("#183A52")), ("GRID", (0, 0), (-1, -1), .5, colors.HexColor("#C9D8E1")),
                                       ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    for row_index, (label, _) in enumerate(result_rows):
        if label.startswith(("예측", "목표")):
            results_table.setStyle(TableStyle([
                ("BACKGROUND", (0, row_index), (-1, row_index), colors.HexColor("#DCF1FA")),
                ("TEXTCOLOR", (0, row_index), (-1, row_index), colors.HexColor("#073453")),
                ("FONTSIZE", (1, row_index), (1, row_index), 12),
                ("FONTNAME", (1, row_index), (1, row_index), "Helvetica-Bold")
            ]))
    story.append(results_table)
    if ("이류체" in mode):
        story.append(Paragraph("공기는 첨부 식의 밀도 1.2 kg/m³ 기준 유량입니다. 압력은 게이지압이며, 내부 계산은 kgf/cm² 절대압력으로 변환합니다.", normal))
        story.extend([PageBreak(), deepcopy(head), Spacer(1, 9)])
    story.append(Paragraph("3. 액체 압력-유량 특성 곡선", section))
    story.append(pdf_curve_drawing(mode, target_air, result))
    if ("이류체" in mode):
        story.append(Paragraph("4. 공기 압력-유량 특성 곡선", section))
        story.append(pdf_curve_drawing(mode, target_air, result, air=True))
    story.append(Paragraph("5. 액체 기준점" if ("이류체" in mode) else "4. 기준점", section))
    point_rows = [["기준점", "액체 압력 (bar)", f"액체 유량 ({unit})", "K"]]
    for index, point in enumerate(result["points"], start=1):
        point_rows.append([f"P{index}", f"{float(point['pl']):.2f}", f"{float(point['ql']):.2f}", f"{float(point['kl']):.3f}"])
    point_table = Table(point_rows, colWidths=[30 * mm, 48 * mm, 55 * mm, 44 * mm])
    point_table.setStyle(TableStyle([("FONTNAME", (0, 0), (-1, -1), korean), ("FONTSIZE", (0, 0), (-1, -1), 8),
                                     ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EAF5FA")), ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#183A52")),
                                     ("GRID", (0, 0), (-1, -1), .5, colors.HexColor("#C9D8E1")), ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                                     ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
    story.append(point_table)
    if ("이류체" in mode):
        story.append(Paragraph("6. 공기 기준점", section))
        air_rows = [["기준점", "공기 압력 (bar)", "공기 유량 (NL/min)", "C"]]
        for index, point in enumerate(result["points"], start=1):
            air_rows.append([f"P{index}", f"{point['pa']:.2f}", f"{point['qa']:.2f}", f"{point['c']:.4f}"])
        air_table = Table(air_rows, colWidths=[30 * mm, 48 * mm, 55 * mm, 44 * mm])
        air_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), korean), ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EAF5FA")),
            ("GRID", (0, 0), (-1, -1), .5, colors.HexColor("#C9D8E1")),
            ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
        story.append(air_table)
    story.extend([Spacer(1, 8), Paragraph("본 리포트는 입력한 데이터시트 기준점의 평균 K값(액체)과 C값(공기)으로 계산한 이론 결과입니다. 실제 선정 시 제조사 성능표, 유체 물성 및 현장 조건을 우선 확인하십시오.", normal)])

    document.build(story, onFirstPage=report_page_footer, onLaterPages=report_page_footer)
    return buffer.getvalue()


def targets(mode: str) -> tuple[str, float, float]:
    st.markdown("<div class='subhead'>목표 운전 조건</div>", unsafe_allow_html=True)
    basis_options = ("압력 기준", "유량 기준")
    target_basis = st.radio(
        "계산 기준",
        basis_options,
        index=basis_options.index(str(DEFAULTS["target_basis"])),
        horizontal=True,
        key="target_basis",
    )
    a, b = st.columns([1, 2.1])
    if target_basis == "유량 기준":
        unit = "L/H" if ("이류체" in mode) else "LPM"
        with a:
            target_value = st.number_input(f"목표 액체 유량 ({unit})", min_value=0.0, max_value=1000.0, step=.01, format="%.2f", key="target_flow_input", on_change=sync, args=("target_flow_input", "target_flow_slider"), **initial_widget_value("target_flow_input"))
        with b:
            st.slider(f"액체 유량 빠른 조정 ({unit})", 0.0, 1000.0, step=.10, key="target_flow_slider", on_change=sync, args=("target_flow_slider", "target_flow_input"), **initial_widget_value("target_flow_slider"))
    else:
        with a:
            target_value = st.number_input("목표 액체 압력 (bar)", min_value=0.0, step=.01, format="%.2f", key="target_liquid_input", **initial_widget_value("target_liquid_input"))
    air = float(st.session_state.get("target_air_input", DEFAULTS["target_air_input"]))
    if ("이류체" in mode):
        a, b = st.columns([1, 2.1])
        if target_basis == "유량 기준":
            with a:
                air = st.number_input("목표 공기 유량 (NL/min)", min_value=0.0, max_value=100000.0, step=.01, format="%.2f", key="target_air_flow_input", on_change=sync, args=("target_air_flow_input", "target_air_flow_slider"), **initial_widget_value("target_air_flow_input"))
            with b:
                st.slider("공기 유량 빠른 조정", 0.0, 100000.0, step=.1, key="target_air_flow_slider", on_change=sync, args=("target_air_flow_slider", "target_air_flow_input"), **initial_widget_value("target_air_flow_slider"))
            return str(target_basis), float(target_value), float(air)
        with a:
            air = st.number_input("목표 공기 압력 (bar)", min_value=0.0, max_value=10.0, step=.01, format="%.2f", key="target_air_input", on_change=sync, args=("target_air_input", "target_air_slider"), **initial_widget_value("target_air_input"))
        with b:
            st.slider("공기 압력 빠른 조정", 0.0, 10.0, step=.05, key="target_air_slider", on_change=sync, args=("target_air_slider", "target_air_input"), **initial_widget_value("target_air_slider"))
    return str(target_basis), float(target_value), float(air)


def reference_points(mode: str) -> list[dict[str, float | bool]]:
    data = []
    for index in (1, 2):
        with st.container(border=True):
            active = st.checkbox(f"기준점 {index} 적용", value=True, key=f"reference_{index}_active")
            cols = st.columns(2)
            with cols[0]:
                pl = st.number_input(f"액체 압력 P{index} (bar)", min_value=0.0, max_value=100.0, step=.01, format="%.2f", key=f"p{index}_liquid_pressure", **initial_widget_value(f"p{index}_liquid_pressure"))
            with cols[1]:
                unit = "L/H" if ("이류체" in mode) else "LPM"
                ql = st.number_input(f"액체 유량 Q{index} ({unit})", min_value=0.0, max_value=100000.0, step=.01, format="%.2f", key=f"p{index}_liquid_flow", **initial_widget_value(f"p{index}_liquid_flow"))
            pa = float(st.session_state.get(f"p{index}_air_pressure", DEFAULTS[f"p{index}_air_pressure"]))
            qa = float(st.session_state.get(f"p{index}_air_flow", DEFAULTS[f"p{index}_air_flow"]))
            if ("이류체" in mode):
                cols = st.columns(2)
                with cols[0]:
                    pa = st.number_input(f"공기 압력 Air{index} (bar)", min_value=0.0, max_value=100.0, step=.01, format="%.2f", key=f"p{index}_air_pressure", **initial_widget_value(f"p{index}_air_pressure"))
                with cols[1]:
                    qa = st.number_input(f"공기 유량 QA{index} (NL/min)", min_value=0.0, max_value=100000.0, step=.01, format="%.2f", key=f"p{index}_air_flow", **initial_widget_value(f"p{index}_air_flow"))
            data.append({"active": active, "pl": float(pl), "ql": float(ql), "pa": float(pa), "qa": float(qa)})
    return data


def flow_calculator() -> None:
    header()
    back, _ = st.columns([1.1, 5])
    with back:
        st.button("← 계산기 목록", width="stretch", on_click=go, args=("home",))
    st.markdown("""<section class="calc-intro"><div><span class="calc-index">CALCULATOR / 01</span><h1>노즐 분사량 계산기</h1><p>두 데이터시트 기준점의 평균 K값으로 목표 압력 또는 목표 유량을 계산합니다.</p></div></section>""", unsafe_allow_html=True)

    with st.expander("기준점 입력 방법", expanded=True):
        st.markdown(
            """<div class="reference-guide">
            <div class="catalog-table-head">
                <div><span>NOZZLE CAPACITY DATA</span><strong>압력별 노즐 용량 기준표</strong></div>
                <em>유량 단위 · L/min</em>
            </div>
            <div class="catalog-scroll">
                <table class="catalog-table" aria-label="압력별 노즐 용량 기준표">
                    <thead>
                        <tr>
                            <th rowspan="2">노즐 번호<br><small>용량 크기</small></th>
                            <th rowspan="2">오리피스<br>직경 (mm)</th>
                            <th rowspan="2">최대 이물<br>통과경 (mm)</th>
                            <th colspan="10">액체 압력별 용량 (L/min)</th>
                        </tr>
                        <tr>
                            <th>0.4</th><th>0.5</th><th>0.7</th><th>1.5</th>
                            <th class="selected-col">2</th><th class="selected-col">3</th>
                            <th>4</th><th>6</th><th>7</th><th>10</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr><td>1</td><td>0.79</td><td>0.64</td><td>0.29</td><td>0.33</td><td>0.38</td><td>0.54</td><td class="selected-col">0.62</td><td class="selected-col">0.74</td><td>0.85</td><td>1.0</td><td>1.1</td><td>1.3</td></tr>
                        <tr><td>1.5</td><td>1.2</td><td>0.64</td><td>0.44</td><td>0.49</td><td>0.57</td><td>0.81</td><td class="selected-col">0.93</td><td class="selected-col">1.1</td><td>1.3</td><td>1.5</td><td>1.6</td><td>1.9</td></tr>
                        <tr class="selected-row"><td class="row-key">2</td><td>1.2</td><td>1.0</td><td>0.59</td><td>0.65</td><td>0.76</td><td>1.1</td><td class="selected-col selected-point">1.2</td><td class="selected-col selected-point">1.5</td><td>1.7</td><td>2.0</td><td>2.2</td><td>2.6</td></tr>
                        <tr><td>3</td><td>1.5</td><td>1.0</td><td>0.88</td><td>0.98</td><td>1.1</td><td>1.6</td><td class="selected-col">1.9</td><td class="selected-col">2.2</td><td>2.5</td><td>3.1</td><td>3.3</td><td>3.9</td></tr>
                    </tbody>
                </table>
            </div>
            <div class="guide-copy">
                <div class="guide-item pressure-key"><b>가로 입력값</b>숫자의 단위는 bar입니다.</div>
                <div class="guide-item nozzle-key"><b>세로 용량 크기</b>노즐 번호로 확인합니다.</div>
                <div class="guide-example"><b>예시 · 노즐 번호 2에서 목표 압력 2.50 bar</b><br>
                기준점 1: <strong>2.00 bar / 1.20 LPM</strong><br>
                기준점 2: <strong>3.00 bar / 1.50 LPM</strong></div>
                <p class="guide-note">목표 압력보다 낮은 값과 높은 값 중 가장 가까운 압력 두 개를 선택하고, 같은 노즐 번호 행의 유량을 입력하세요.</p>
            </div>
            </div>""",
            unsafe_allow_html=True,
        )

    input_col, output_col = st.columns([0.92, 1.38], gap="large")
    with input_col:
        st.markdown("<div class='workspace-head'><span>INPUT CONDITIONS</span><h2>입력 조건</h2><p>노즐 정보와 운전 조건을 순서대로 입력하세요.</p></div>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("<div class='subhead'>노즐 기본 정보</div>", unsafe_allow_html=True)
            mode_options = ("일류체 노즐 (액체)", "외부혼합 이류체 노즐 (액체 + 에어)")
            mode = st.radio("노즐 형식", mode_options, index=mode_options.index(str(DEFAULTS["flow_mode"])), key="flow_mode")
            product = st.text_input("노즐 / 제품명", placeholder="클릭하여 입력", key="product_name", **initial_widget_value("product_name"))
            diameter, temperature = 1.0, 20.0
            if ("이류체" in mode):
                dcol, tcol = st.columns(2)
                with dcol:
                    diameter = st.number_input("공기 노즐 구경 D (mm)", min_value=.01, max_value=100.0, step=.01, format="%.2f", key="air_diameter", **initial_widget_value("air_diameter"))
                with tcol:
                    temperature = st.number_input("공기 온도 (°C)", min_value=-100.0, max_value=500.0, step=.01, format="%.2f", key="air_temperature", **initial_widget_value("air_temperature"))
                st.caption("구경과 온도는 두 공기 기준점 및 목표 조건에 공통 적용됩니다. 액체는 L/H, 공기는 NL/min으로 입력하세요.")
                st.caption("공기 유량은 첨부 식의 밀도 1.2 kg/m³ 기준입니다. 카탈로그의 기준 상태가 다르면 환산 후 입력하세요. 압력은 게이지압입니다.")
            target_basis, target_value, target_air = targets(mode)
            st.markdown("<div class='subhead'>데이터시트 기준점</div>", unsafe_allow_html=True)
            st.caption("선택한 기준점에서 액체 K와 공기 C를 구합니다. 둘 다 선택하면 각각 평균을 적용합니다." if ("이류체" in mode) else "선택한 기준점의 유효한 K값으로 계산합니다. 둘 다 선택하면 평균을 적용합니다.")
            points = reference_points(mode)
            st.button("조건 입력값 초기화", key="reset_conditions", width="stretch", on_click=reset_conditions)

    result = calculate(mode, target_basis, target_value, target_air, points, diameter, temperature)
    unit = "L/H" if ("이류체" in mode) else "LPM"

    with output_col:
        st.markdown("<div class='workspace-head'><span>CALCULATION OUTPUT</span><h2>계산 결과</h2><p>입력값이 바뀌면 결과와 그래프가 즉시 갱신됩니다.</p></div>", unsafe_allow_html=True)
        with st.container(border=True):
            metric_slots = st.columns(2 if ("이류체" in mode) else [1.25, 1, 1])
            with metric_slots[0]:
                if target_basis == "유량 기준":
                    st.metric("예측 액체 압력", f"{result['target_pressure']:.2f} bar")
                else:
                    st.metric("예측 액체 분사량", f"{result['liquid_flow']:.2f} {unit}")
            with metric_slots[1]:
                if ("이류체" in mode):
                    if target_basis == "유량 기준":
                        st.metric("예측 공기 압력", "—" if result["air_error"] or not result["air_valid_count"] else f"{result['air_pressure']:.2f} bar")
                    else:
                        st.metric("예측 공기 유량", f"{result['air_flow']:.2f} NL/min")
                else:
                    st.metric("적용 기준점", f"{result['valid_count']} 개")
            if not ("이류체" in mode):
                with metric_slots[2]:
                    st.metric("평균 유량 계수 K", f"{result['avg_k']:.3f}")
            if ("이류체" in mode):
                st.markdown(f"<div class='coefficient-note'>평균 액체 계수 K <b>{result['avg_k']:.3f}</b> &nbsp; · &nbsp; 평균 공기 계수 C <b>{result['avg_c']:.4f}</b></div>", unsafe_allow_html=True)
                if not result["air_valid_count"]:
                    st.warning("공기 기준점의 압력과 유량을 0보다 크게 입력하세요.")
                if result["air_error"]:
                    st.warning(result["air_error"])
            if result["valid_count"]:
                st.success(f"{product or '제품명 미입력'} · 기준점 {result['valid_count']}개 평균 적용")
            else:
                st.warning("적용할 기준점을 선택하고 해당 압력과 유량을 0보다 크게 입력하세요.")
            st.markdown("<div class='subhead'>기준점별 계산 계수</div>", unsafe_allow_html=True)
            kcols = st.columns(2)
            for i, (col, point) in enumerate(zip(kcols, result["points"], strict=True), start=1):
                with col:
                    st.markdown(f"<div class='coefficient-note'>P{i} · K <b>{float(point['kl']):.3f}</b></div>", unsafe_allow_html=True)
                    if ("이류체" in mode):
                        st.markdown(f"<div class='coefficient-note'>P{i} · C <b>{float(point['c']):.4f}</b></div>", unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown("<div class='subhead'>액체 압력-유량 특성 곡선</div>", unsafe_allow_html=True)
            st.vega_lite_chart(spec=chart_spec(mode, target_air, result), width="stretch")
            st.caption("파란색은 평균 K 특성곡선, 초록색은 목표 운전점입니다.")
            if ("이류체" in mode) and result["air_valid_count"] and not result["air_error"]:
                st.markdown("<div class='subhead'>공기 압력-유량 특성 곡선</div>", unsafe_allow_html=True)
                st.vega_lite_chart(spec=chart_spec(mode, target_air, result, air=True), width="stretch")
                st.caption("파란색은 평균 C 특성곡선, 초록색은 목표 공기 운전점입니다.")

        with st.container(border=True):
            st.markdown("<div class='subhead'>PDF 리포트</div>", unsafe_allow_html=True)
            pdf_data = deferred_pdf(build_pdf, product, mode, target_basis, target_value, target_air, result)
            st.download_button("PDF 리포트 다운로드", disabled=bool(result["air_error"]) or result["valid_count"] == 0 or (("이류체" in mode) and result["air_valid_count"] == 0), data=pdf_data, file_name="nozzle_flow_rate_report.pdf", mime="application/pdf", on_click="ignore", type="primary", width="stretch")
    footer()



PIPE_SIZES = [25, 32, 40, 50, 65, 80, 90, 100, 125, 150, 200]
PIPE_FITTINGS = [('threaded', '나사식 45° 엘보', [0.4, 0.5, 0.6, 0.7, 1.0, 1.1, 1.3, 1.5, 1.8, 2.2, 2.9]), ('threaded', '나사식 90° 엘보', [0.8, 1.1, 1.3, 1.6, 2.0, 2.4, 2.8, 3.2, 3.9, 4.7, 6.2]), ('threaded', '나사식 TEE', [1.7, 2.2, 2.5, 3.2, 4.1, 4.9, 5.6, 6.3, 7.9, 9.3, 12.5]), ('welded', '용접식 45° 엘보', [0.2, 0.2, 0.3, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.2]), ('welded', '용접식 90° 엘보 (short)', [0.5, 0.6, 0.7, 0.9, 1.1, 1.3, 1.5, 1.7, 2.1, 2.5, 3.5]), ('welded', '용접식 90° 엘보 (long)', [0.3, 0.4, 0.5, 0.6, 0.8, 1.0, 1.1, 1.3, 1.6, 1.9, 2.5]), ('welded', '용접식 TEE', [1.3, 1.6, 1.9, 2.4, 3.1, 3.6, 4.2, 4.7, 5.9, 7.0, 9.2]), ('valves', '게이트밸브', [0.2, 0.2, 0.3, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0, 1.3]), ('valves', '앵글밸브', [4.6, 6.0, 7.0, 8.9, 11.3, 13.5, 15.6, 17.6, 21.9, 26.0, 34.2]), ('valves', '체크밸브', [2.3, 3.0, 3.5, 4.4, 5.6, 6.7, 7.7, 8.7, 10.9, 12.9, 17.0]), ('valves', '글로브밸브', [9.0, 11.8, 13.8, 17.7, 21.0, 26.0, None, 34.0, 43.0, 52.0, None])]
AIR_REFERENCE_DIAMETERS = [0.2, 0.5, 0.7, 1.0, 1.3, 1.5, 1.7, 2.0, 3.0, 3.5, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 17.0, 20.0, 25.0, 30.0, 35.0, 40.0]

# Calculators 02–06 are transcribed from the five supplied workbooks.
# Keep the source constants (3.14, 0.785, 273, 9.8) to reproduce Excel results.
CALCULATOR_CARDS = [
    ("flow", "노즐 분사량 계산기", "두 기준점으로 목표 압력의 유량 또는 목표 유량에 필요한 압력을 계산합니다."),
    ("water", "물 기준 노즐 유량 계산기", "노즐 구경·압력·유량을 상호 계산하고 물의 분사 유속을 확인합니다."),
    ("air", "압축 공기량 계산기", "노즐 구경과 압력·온도로 공기량을 계산하고 슬릿의 등가 구경을 환산합니다."),
    ("slit", "SLIT BLOWER 풍량 계산기", "풍속, 유효길이, 슬릿간격으로 풍량과 필요한 접속구 수량을 계산합니다."),
    ("pipe", "배관 선정 계산기", "AIR · WATER 배관의 내경, 유속, 유량과 부속품에 따른 압력손실을 계산합니다."),
    ("density", "밀도·비중별 유량 계산기", "질량·부피 유량과 비중 보정 유량을 환산하고 혼합물의 밀도를 계산합니다."),
    ('layout', 'SprayLayout Pro · 노즐 배치 계산기', '분사 폭과 겹침률을 바탕으로 노즐 수량과 배치를 검토합니다.'),
    ('impact', '노즐 충격력·펌프 계산기', '노즐 충격력과 펌프 이론 계산을 시뮬레이션과 함께 확인합니다.'),
    ('auxiliary', '노즐 현장 보조 계산기', '도포량·마모율·간헐 분사, 단위 환산과 노즐 커버리지를 계산합니다.'),
]

# mode: (field key, label including unit, workbook default, minimum)
CALC_FIELDS = {
    "AIR · 배관 내경": [("p", "압력 (bar · 게이지압)", 3., 0.), ("q", "공기 유량 (L/min · 압력 보정 전)", 1000., 0.), ("v", "배관 내 유속 (m/s)", 20., 0.)],
    "AIR · 배관 유속": [("p", "압력 (bar · 게이지압)", 3., 0.), ("q", "공기 유량 (L/min · 압력 보정 전)", 1000., 0.), ("d", "배관 내경 (mm)", 16.5, 0.)],
    "WATER · 배관 내경": [("q", "물 유량 (L/min)", 45., 0.), ("v", "배관 내 유속 (m/s)", 3., 0.)],
    "WATER · 배관 유속": [("q", "물 유량 (L/min)", 190., 0.), ("d", "배관 내경 (mm)", 51.9, 0.)],
    "WATER · 유량": [("d", "배관 내경 (mm)", 19., 0.), ("v", "배관 내 유속 (m/s)", 3., 0.)],
    "WATER · 압력손실": [("d", "배관 내경 (mm)", 13.5, 0.), ("q", "물 유량 (L/min)", 45., 0.), ("length", "직관 총 길이 (m)", 10., 0.), ("roughness", "표면조도 계수 C", 120., 0.)],
    "솔리드 노즐": [("d", "노즐 구경 D (mm)", 44.6, 0.), ("p", "공기 압력", 1., 0.), ("t", "공기 온도 (°C)", 20., -272.99), ("c", "유량계수 c", 1., 0.)],
    "슬릿 → 등가 노즐": [("length", "슬릿 길이 (mm)", 1300., 0.), ("gap", "슬릿 폭 (mm)", 2., 0.), ("factor", "슬릿 지수 값", .6, 0.), ("p", "공기 압력", 1., 0.), ("t", "공기 온도 (°C)", 20., -272.99), ("c", "유량계수 c", 1., 0.)],
    "유량 계산": [("p", "압력 (bar · 원식 기준)", 3., 0.), ("d", "노즐 구경 (mm)", 2.3, 0.), ("c", "유량계수 C", 1., 0.)],
    "압력 계산": [("q", "목표 유량 (L/min)", 6., 0.), ("d", "노즐 구경 (mm)", 2.3, 0.), ("c", "유량계수 C", 1., 0.)],
    "노즐 구경 계산": [("p", "압력 (bar · 원식 기준)", 3., 0.), ("q", "목표 유량 (L/min)", 6., 0.), ("c", "유량계수 C", 1., 0.)],
    "압력 → 유속": [("p", "압력 (bar · 원식 기준)", 3., 0.)],
    "구경·유속 → 유량": [("d", "노즐 구경 (mm)", 2.3, 0.), ("v", "분사 유속 (m/s)", 24.2, 0.)],
    "풍량·접속구 선정": [("v", "풍속 (m/s)", 140., 0.), ("length", "유효길이 (mm)", 457., 0.), ("gap", "슬릿간격 (mm)", 1.5, 0.)],
    "질량 → 부피 유량": [("mass", "질량 유량 (kg/h)", 3500., 0.), ("rho", "액체 밀도 (kg/m³)", 925., 0.)],
    "부피 유량 단위 환산": [("volume", "부피 유량 (m³/h)", 3.78, 0.)],
    "비중에 따른 유량 보정": [("q", "유량 (L/min)", 63., 0.), ("rho", "액체 밀도 (kg/m³)", 925., 0.)],
    "혼합물 밀도": [("rho_a", "A 용액 밀도 (kg/m³)", 830., 0.), ("mass_a", "A 용액 질량 유량 (kg/h)", 10000., 0.), ("rho_b", "B 용액 밀도 (kg/m³)", 740., 0.), ("mass_b", "B 용액 질량 유량 (kg/h)", 4500., 0.)],
}
CALC_MODES = {
    "pipe": list(CALC_FIELDS)[:6],
    "air": ["솔리드 노즐", "슬릿 → 등가 노즐"],
    "water": ["유량 계산", "압력 계산", "노즐 구경 계산", "압력 → 유속", "구경·유속 → 유량"],
    "slit": ["풍량·접속구 선정"],
    "density": ["질량 → 부피 유량", "부피 유량 단위 환산", "비중에 따른 유량 보정", "혼합물 밀도"],
}
SOURCE_NAMES = {
    "pipe": "배관 선정 계산식_AIR_WATER.xls",
    "air": "노즐 구경에 대한 압축 공기량 계산식.xls",
    "water": "노즐 구경에 대한 물기준 유량 계산식.xls",
    "slit": "SLIT BLOWER 풍량계산식.xlsx",
    "density": "밀도 비중별 유량 계산식.xls",
}
SLIT_APPLICATIONS = [
    ("강력탈수", "100~140", "0.9~1.2"), ("평면탈수", "70~90", "0.7~1"),
    ("액체코팅", "100~120", "0.4~0.7"), ("열풍건조", "60~80", "1.5~3"),
    ("수성니스건조", "40~50", "3.5~5"),
]
CONNECTION_CAPACITY = {'25A (PT 1")': 2.3, '40A (PT 1½")': 4.8, '50A (PT 2")': 7.6}
PIPE_VELOCITIES = [
    ("AIR", "흡입 측", "10~20"), ("AIR", "저압 토출관", "20~30"), ("AIR", "고압 토출관", "10~15"),
    ("WATER", "펌프 토출 측", "2~4"), ("WATER", "펌프 흡입 측", "1~2"), ("WATER", "헤더", "1.0"),
    ("WATER", "헤더 공급관", "1.5~3"), ("WATER", "수직 배관", "1~3"), ("WATER", "일반 장치", "1.5~3"), ("WATER", "냉각수", "1~2.5"),
]


def engineering_result(page: str, mode: str, a: dict[str, Any]) -> dict[str, Any]:
    """Pure calculation, using the original workbook's grouped expressions."""
    for key, value in a.items():
        if isinstance(value, (float, int)):
            if not math.isfinite(value) or (key != "t" and value < 0):
                raise ValueError("입력값은 유효한 0 이상의 숫자여야 합니다.")
    def positive(key: str, label: str) -> float:
        value = float(a[key])
        if value <= 0:
            raise ValueError(f"{label}은(는) 0보다 크게 입력하세요.")
        return value

    metrics: list[tuple[str, float, str]] = []
    formula: list[str] = []
    note = ""
    if page == "pipe":
        # Match the supplied pipe workbook M3/M7, including its pressure constant.
        ratio = (a["p"] + 1.033) / 1.033 if mode.startswith("AIR") else 1.
        if mode.endswith("배관 내경"):
            v = positive("v", "유속")
            d = math.sqrt(a['q'] * 1000 / v / 60 / ratio * 4 / 3.14)
            metrics = [("필요 배관 내경", d, "mm"), ("유효 통과 유량", a['q']/ratio, "L/min")]
            formula = [r"D=\sqrt{\frac{Q\times1000}{60vR}\times\frac{4}{3.14}}"]
        elif mode.endswith("배관 유속"):
            d = positive("d", "배관 내경")
            v = a['q']*1000/(d*d*3.14/4)/60/ratio
            metrics = [("배관 내 유속", v, "m/s"), ("유효 통과 유량", a['q']/ratio, "L/min")]
            formula = [r"v=\frac{Q\times1000}{(3.14D^2/4)\times60\times R}"]
        elif mode == "WATER · 유량":
            q = a['d']**2*3.14/4*60*a['v']/1000
            metrics = [("통과 유량", q, "L/min"), ("시간당 유량", q*.06, "m³/h")]
            formula = [r"Q=\frac{D^2\times3.14}{4}\times\frac{60v}{1000}"]
        else:
            d = positive("d", "배관 내경"); c = positive("roughness", "표면조도 계수")
            total_length = a['length'] + a.get('threaded', 0.) + a.get('welded', 0.) + a.get('valves', 0.)
            dp = 6.174*a['q']**1.85*10**5*total_length/c**1.85/d**4.87
            metrics = [("배관 압력손실", dp, "bar"), ("총 등가길이", total_length, "m")]
            formula = [r"\Delta P=\frac{6.174\times Q^{1.85}\times10^5\times L_{total}}{C^{1.85}\times D^{4.87}}", r"L_{total}=L+L_{thread}+L_{weld}+L_{valve}"]
            note = "직관 길이에 나사식·용접식 부속과 밸브의 등가길이를 더합니다. 원본 표의 C 기본값은 120입니다."
        if mode.startswith("AIR"):
            metrics[1] = ("배관 내 통과 유량", a['q']/ratio, "L/min")
            metrics.append(("시간당 통과 유량", a['q']/ratio*.06, "m³/h"))
            formula.append(r"R=\frac{P+1.033}{1.033},\quad Q_{pipe}=Q_{input}/R")
            note = "입력 공기량에 (압력 + 1.033) / 1.033 보정을 적용합니다. 압력이 높아지면 계산된 통과 유량과 필요 내경 또는 유속이 감소합니다. 첨부 배관식의 상수 1.033을 그대로 적용합니다."
        elif "압력손실" not in mode:
            formula.append(r"R=1\quad(\mathrm{WATER})")
    elif page == "air":
        if a['t'] <= -273: raise ValueError("공기 온도는 -273°C보다 높아야 합니다.")
        d = a['d'] if mode == "솔리드 노즐" else math.sqrt(a['length']*a['gap']*a['factor']*4/3.14)
        p = a['p']/BAR_PER_KGF_CM2 if a.get('pressure_unit') == 'bar' else a['p']
        q = 198*.785*d*d*a['c']*(p+1.033)/math.sqrt(a['t']+273)
        metrics = [("공기 분사량", q, "L/min"), ("시간당 공기량", q*.06, "m³/h")]
        if mode != "솔리드 노즐":
            metrics.append(("등가 노즐 구경", d, "mm"))
            formula.append(r"D=\sqrt{\frac{L\times w\times k\times4}{3.14}}")
        formula.extend([r"Q=\frac{198\times0.785D^2\times c\times(P_g+1.033)}{\sqrt{t+273}}", r"Q_{m^3/h}=0.06Q_{L/min}"])
        note = "공기 밀도 1.2 kg/m³ 기준의 첨부 원식입니다. P_g는 kgf/cm² 게이지압이며, bar 선택 시 0.980665로 나누어 환산합니다. 압력손실·내부 부하를 반영하지 않습니다."
        if a['p'] == 0:
            note += " 게이지압 0에서도 원식은 양수를 반환하므로 실제 무차압 유량으로 사용하지 마세요."
    elif page == "water":
        if mode == "유량 계산":
            q = .0471*a['d']**2*a['c']*math.sqrt(20*9.8*a['p'])
            metrics = [("물 분사량", q, "L/min"), ("시간당 유량", q*.06, "m³/h")]
            formula = [r"Q=0.0471D^2C\sqrt{20\times9.8P}"]
        elif mode == "압력 계산":
            d = positive('d', '노즐 구경'); c = positive('c', '유량계수')
            p = (a['q']/(.0471*d*d*c))**2/(20*9.8)
            metrics = [("필요 압력", p, "bar")]
            formula = [r"P=\frac{[Q/(0.0471D^2C)]^2}{20\times9.8}"]
        elif mode == "노즐 구경 계산":
            p = positive('p', '압력'); c = positive('c', '유량계수')
            d = math.sqrt(a['q']/(.0471*c*math.sqrt(20*9.8*p)))
            metrics = [("필요 노즐 구경", d, "mm")]
            formula = [r"D=\sqrt{\frac{Q}{0.0471C\sqrt{20\times9.8P}}}"]
        elif mode == "압력 → 유속":
            metrics = [("분사 유속", math.sqrt(2*9.8*a['p']*10), "m/s")]
            formula = [r"v=\sqrt{2\times9.8\times P\times10}"]
        else:
            q = (a['d']/1000)**2*3.14/4*a['v']*1000*60
            metrics = [("물 분사량", q, "L/min"), ("시간당 유량", q*.06, "m³/h")]
            formula = [r"Q=\frac{3.14}{4}\left(\frac{D}{1000}\right)^2v\times1000\times60"]
        note = "일직선 패턴 노즐(분사 각도 0°) 기준입니다. 엑셀과 동일한 결과를 위해 원식의 9.8, 3.14 및 압력 환산 근사를 적용합니다."
    elif page == "slit":
        q = a['length']*a['gap']*a['v']*60/1000000
        capacity = CONNECTION_CAPACITY[a['connection']]
        count = math.ceil(round(q/capacity, 12))
        metrics = [("필요 풍량", q, "m³/min"), ("접속구 수량", count, "개"), ("선정 접속구 총 풍량", count*capacity, "m³/min")]
        formula = [r"Q=\frac{L\times w\times v\times60}{1{,}000{,}000}", r"N=\left\lceil Q/Q_{port}\right\rceil"]
        note = "접속구 수량은 첨부 이미지의 구경별 기본풍량으로 나눈 뒤 부족하지 않도록 올림합니다. 배관 거리·방식에 따른 압력손실은 별도 검토 대상입니다."
    elif page == "density":
        if mode == "질량 → 부피 유량":
            rho = positive('rho', '밀도'); q = a['mass']/rho
            metrics = [("부피 유량", q, "m³/h"), ("분당 부피 유량", q*1000/60, "L/min")]
            formula = [r"Q_{m^3/h}=\dot{m}/\rho", r"Q_{L/min}=Q_{m^3/h}\times1000/60"]
        elif mode == "부피 유량 단위 환산":
            q = a['volume']*1000/60
            metrics = [("분당 부피 유량", q, "L/min"), ("초당 부피 유량", q/60, "L/s")]
            formula = [r"Q_{L/min}=Q_{m^3/h}\times1000/60"]
        elif mode == "비중에 따른 유량 보정":
            sg = positive('rho', '밀도')/1000
            to_water = a.get('direction', '액체 → 물') == '액체 → 물'
            q = a['q']*math.sqrt(sg) if to_water else a['q']/math.sqrt(sg)
            metrics = [("물 기준 유량" if to_water else "액체 유량", q, "L/min"), ("비중 SG", sg, "")]
            formula = [r"SG=\rho/1000", r"Q_{water}=Q_{liquid}\sqrt{SG}" if to_water else r"Q_{liquid}=Q_{water}/\sqrt{SG}"]
            note = "동일 노즐·동일 압력에서 밀도 차이에 의한 유량을 보정합니다. 점도와 온도의 추가 영향은 포함하지 않습니다."
        else:
            ra = positive('rho_a', 'A 용액 밀도'); rb = positive('rho_b', 'B 용액 밀도')
            mass = a['mass_a']+a['mass_b']; vol = a['mass_a']/ra+a['mass_b']/rb
            if vol <= 0: raise ValueError("A 또는 B 용액의 질량 유량을 0보다 크게 입력하세요.")
            metrics = [("혼합물 밀도", mass/vol, "kg/m³"), ("총 질량 유량", mass, "kg/h"), ("총 부피 유량", vol, "m³/h")]
            formula = [r"\rho_{mix}=\frac{\dot m_A+\dot m_B}{\dot m_A/\rho_A+\dot m_B/\rho_B}"]
            note = "혼합 전후 부피의 합이 유지된다고 가정합니다. 입력값은 각 용액의 질량 유량입니다."
    else:
        raise ValueError("지원하지 않는 계산기입니다.")
    if any(not math.isfinite(value) for _, value, _ in metrics):
        raise ValueError("계산 범위를 벗어났습니다. 입력값을 확인하세요.")
    return {'metrics': metrics, 'formula': formula, 'note': note}


def engineering_curve_key(page: str, mode: str) -> str:
    if page == 'air': return 'p'
    if mode.startswith('AIR ·') or mode == 'WATER · 압력손실': return 'q'
    return CALC_FIELDS[mode][0][0]


def engineering_curve(page: str, mode: str, values: dict[str, Any]) -> tuple[str, list[dict[str, float]]]:
    """Vary a genuine input; calculate each point through the same validated engine."""
    key = engineering_curve_key(page, mode)
    upper = max(float(values[key])*2, 1.)
    rows = []
    for n in range(1, 51):
        trial = dict(values); trial[key] = upper*n/50
        try: result = engineering_result(page, mode, trial)
        except (ValueError, OverflowError): continue
        rows.append({'x': trial[key], 'y': result['metrics'][0][1]})
    label = next(field[1] for field in CALC_FIELDS[mode] if field[0] == key)
    if key == 'p' and page == 'air': label += f" ({values['pressure_unit']})"
    return label, rows


def reset_engineering(prefix: str) -> None:
    for key in list(st.session_state):
        if str(key).startswith(prefix + '_') and not str(key).endswith('_reset'):
            del st.session_state[key]


def engineering_table(rows: list[dict[str, Any]]) -> None:
    """A scoped light HTML table remains readable even under Streamlit dark mode."""
    from html import escape
    import re
    def display(value: Any) -> str:
        if value is None: return '—'
        if isinstance(value, (float, int)): return f'{value:,.2f}'
        text = str(value)
        if re.fullmatch(r'\d+(\.\d+)?(~\d+(\.\d+)?)?', text):
            return '~'.join(f'{float(v):,.2f}' for v in text.split('~'))
        return text
    columns = list(rows[0]) if rows else []
    head = ''.join('<th>'+escape(c)+'</th>' for c in columns)
    body = ''.join('<tr>'+''.join('<td>'+escape(display(row.get(c)))+'</td>' for c in columns)+'</tr>' for row in rows)
    st.markdown('<div class="engineering-table-wrap"><table class="engineering-table"><thead><tr>'+head+'</tr></thead><tbody>'+body+'</tbody></table></div>', unsafe_allow_html=True)


def engineering_pdf_curve(page: str, mode: str, values: dict[str, Any], result: dict[str, Any]) -> Any:
    from reportlab.graphics.shapes import Circle, Drawing, Line, Path, Rect, String
    from reportlab.lib.colors import HexColor
    xlabel, rows = engineering_curve(page, mode, values)
    current_x = values[engineering_curve_key(page, mode)]
    label, current_y, unit = result['metrics'][0]
    width, height = 507, 180
    left, right, bottom, top = 72, 15, 44, 30
    max_x = max([current_x, 1.] + [r['x'] for r in rows])
    max_y = max([current_y, 1.] + [r['y'] for r in rows])*1.08
    x = lambda v: left+v/max_x*(width-left-right)
    y = lambda v: bottom+v/max_y*(height-bottom-top)
    drawing = Drawing(width, height)
    drawing.add(Rect(0,0,width,height,fillColor=HexColor('#ffffff'),strokeColor=None))
    for i in range(6):
        px, py = max_x*i/5, max_y*i/5
        drawing.add(Line(x(px),bottom,x(px),height-top,strokeColor=HexColor('#dce7ed'),strokeWidth=.6))
        drawing.add(Line(left,y(py),width-right,y(py),strokeColor=HexColor('#dce7ed'),strokeWidth=.6))
        drawing.add(String(x(px),bottom-14,f'{px:,.2f}',fontName='Helvetica',fontSize=7,fillColor=HexColor('#577084'),textAnchor='middle'))
        drawing.add(String(left-6,y(py)-2,f'{py:,.2f}',fontName='Helvetica',fontSize=7,fillColor=HexColor('#577084'),textAnchor='end'))
    curve = Path(strokeColor=HexColor('#0085c8'),strokeWidth=2.4,fillColor=None)
    for i,row in enumerate(rows): (curve.moveTo if i==0 else curve.lineTo)(x(row['x']),y(row['y']))
    drawing.add(curve)
    drawing.add(Line(x(current_x),bottom,x(current_x),y(current_y),strokeColor=HexColor('#0a9b73'),strokeDashArray=[4,3]))
    drawing.add(Circle(x(current_x),y(current_y),4,fillColor=HexColor('#0a9b73'),strokeColor=None))
    drawing.add(String(width/2,10,xlabel,fontName='HYSMyeongJo-Medium',fontSize=8,fillColor=HexColor('#14364e'),textAnchor='middle'))
    drawing.add(String(left,height-13,f'{label} ({unit})',fontName='HYSMyeongJo-Medium',fontSize=9,fillColor=HexColor('#14364e')))
    return drawing


def engineering_pdf(title: str, mode: str, inputs: list[tuple[str, str]], result: dict[str, Any], source: str, page: str, values: dict[str, Any]) -> bytes:
    from html import escape
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont
    from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle, KeepTogether
    font = 'HYSMyeongJo-Medium'
    pdfmetrics.registerFont(UnicodeCIDFont(font))
    normal = ParagraphStyle('NormalKR', fontName=font, fontSize=9, leading=13, textColor=colors.HexColor('#294a61'))
    heading = ParagraphStyle('TitleKR', parent=normal, fontSize=20, leading=28, spaceAfter=10)
    small = ParagraphStyle('SmallKR', parent=normal, fontSize=8, leading=12)
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=44, rightMargin=44, topMargin=38, bottomMargin=90, title=title)
    story = [report_header(doc.width), Spacer(1,18), Paragraph(escape(title), heading)]
    if page != 'air': story.append(Paragraph(escape(mode), normal))
    story.extend([Paragraph(datetime.now().strftime('%Y-%m-%d %H:%M'), small), Spacer(1,12)])
    for section, rows in [('1. 입력 조건', inputs), ('2. 예측 결과', [(label, f'{value:,.2f} {unit}') for label, value, unit in result['metrics']])]:
        story.extend([Paragraph(section, normal), Spacer(1, 6)])
        table = Table([[Paragraph(escape(str(k)), normal), Paragraph(escape(str(v)), normal)] for k, v in rows], colWidths=[270, 237])
        table.setStyle(TableStyle([('BACKGROUND',(0,0),(0,-1),colors.HexColor('#e0f2fb')), ('GRID',(0,0),(-1,-1),.4,colors.HexColor('#cbdde7')), ('VALIGN',(0,0),(-1,-1),'TOP'), ('TOPPADDING',(0,0),(-1,-1),5), ('BOTTOMPADDING',(0,0),(-1,-1),5)]))
        story.extend([table, Spacer(1, 12)])
    story.append(KeepTogether([Paragraph('3. 입력 조건에 따른 변화', normal), Spacer(1,6), engineering_pdf_curve(page, mode, values, result), Paragraph('파란색: 계산 곡선 · 초록색: 현재 입력 조건', small)]))
    story.extend([Spacer(1,8), Paragraph('4. 계산 조건 및 참고 사항', normal), Paragraph(escape(result['note']), small), Spacer(1,10), Paragraph(REPORT_NOTICE, small)])
    doc.build(story, onFirstPage=report_page_footer, onLaterPages=report_page_footer)
    return buf.getvalue()


def engineering_calculator(page: str) -> None:
    st.markdown("""<style>
.engineering-table-wrap{overflow:auto;max-height:540px;border:1px solid #cbdde7;border-radius:4px;margin:12px 0;background:#fff;color-scheme:light}
.engineering-table{width:100%;border-collapse:collapse;background:#fff!important;color:#18394f!important;font-size:14px}
.engineering-table th,.engineering-table td{padding:10px 12px;border:1px solid #d6e2e9!important;white-space:nowrap;color:#18394f!important;-webkit-text-fill-color:#18394f!important}
.engineering-table th{background:#dceff7!important;font-weight:700;position:sticky;top:0}
.engineering-table td{background:#fff!important;text-align:right}
.engineering-table td:first-child{text-align:left;font-weight:600}
.engineering-table tr:nth-child(even) td{background:#f3f9fc!important}
</style>""", unsafe_allow_html=True)
    index = next(i for i, c in enumerate(CALCULATOR_CARDS, 1) if c[0] == page)
    _, title, description = CALCULATOR_CARDS[index-1]
    header()
    back, _ = st.columns([1.1, 5])
    with back: st.button('← 계산기 목록', width='stretch', on_click=go, args=('home',))
    st.markdown(f'<section class="calc-intro"><div><span class="calc-index">CALCULATOR / {index:02d}</span><h1>{title}</h1><p>{description}</p></div></section>', unsafe_allow_html=True)
    left, right = st.columns([.92, 1.38], gap='large')
    with left:
        st.markdown("<div class='workspace-head'><span>INPUT CONDITIONS</span><h2>입력 조건</h2><p>계산 항목을 선택하고 운전 조건을 입력하세요.</p></div>", unsafe_allow_html=True)
        with st.container(border=True):
            mode = st.selectbox('계산 항목', CALC_MODES[page], key=f'{page}_mode')
            prefix = f'{page}_{CALC_MODES[page].index(mode)}'
            values: dict[str, Any] = {}; input_rows = []
            if page in ('water', 'air'):
                product = st.text_input('노즐 / 제품명', placeholder='클릭하여 입력', key=page+'_product_name')
                input_rows.append(('노즐 / 제품명', product or '미입력'))
            if page == 'air':
                unit = st.selectbox('공기 압력 단위 (게이지압)', ['kgf/cm²', 'bar'], key=prefix+'_pressure_unit')
                values['pressure_unit'] = unit; input_rows.append(('압력 단위', unit))
                st.caption('원식 설명은 kgf/cm² 기준입니다. bar 입력값은 자동 환산합니다.')
            if mode == '비중에 따른 유량 보정':
                direction = st.radio('환산 방향', ['액체 → 물', '물 → 액체'], key=prefix+'_direction')
                values['direction'] = direction; input_rows.append(('환산 방향', direction))
            for key, label, default, minimum in CALC_FIELDS[mode]:
                if key == 'p' and page == 'air': label = f'공기 압력 ({values["pressure_unit"]} · 게이지압)'
                if key == 'q' and mode == '비중에 따른 유량 보정': label = ('액체 유량' if direction == '액체 → 물' else '물 기준 유량') + ' (L/min)'
                value = st.number_input(label, min_value=minimum, value=default, step=.01 if default < 10 else 1., format='%.2f', key=prefix+'_'+key)
                values[key] = value; input_rows.append((label, f'{value:.2f}'))
            if mode == 'WATER · 압력손실':
                st.markdown("<div class='subhead'>배관 부속·밸브 등가길이</div>", unsafe_allow_html=True)
                how = st.radio('등가길이 입력 방법', ['직접 입력', '부속품 수량으로 계산'], key=prefix+'_fitting_method')
                if how == '직접 입력':
                    for key, label in [('threaded','나사식 부속 등가길이 (m)'), ('welded','용접식 부속 등가길이 (m)'), ('valves','밸브 등가길이 (m)')]:
                        values[key] = st.number_input(label, min_value=0., value=0., step=.1, format='%.2f', key=prefix+'_'+key)
                        input_rows.append((label, f'{values[key]:.2f}'))
                else:
                    size = st.selectbox('부속품 호칭구경 (A)', PIPE_SIZES, index=3, key=prefix+'_size')
                    input_rows.append(('부속품 호칭구경 (A)', str(size)))
                    values.update(threaded=0., welded=0., valves=0.)
                    for group, fitting, lengths in PIPE_FITTINGS:
                        length = lengths[PIPE_SIZES.index(size)]
                        if length is None:
                            st.caption(f'{fitting}: 원본에 {size}A 등가길이가 없습니다. 직접 입력을 이용하세요.'); continue
                        number = st.number_input(f'{fitting} · {length:.2f} m/개', min_value=0, value=0, step=1, format='%.2f', key=prefix+'_'+fitting)
                        values[group] += number*length
                        if number: input_rows.append((fitting, f'{number:.2f}개 × {length:.2f} m'))
                    for key, label in [('threaded','나사식 합계'), ('welded','용접식 합계'), ('valves','밸브 합계')]:
                        input_rows.append((label, f'{values[key]:.2f} m'))
            if page == 'slit':
                values['connection'] = st.selectbox('접속구 구경', list(CONNECTION_CAPACITY), key=prefix+'_connection')
                input_rows.append(('접속구 구경', values['connection']))
                st.caption(f"접속구 1개당 기본풍량: {CONNECTION_CAPACITY[values['connection']]:.2f} m³/min")
            st.button('엑셀 예시값으로 초기화', key=prefix+'_reset', width='stretch', on_click=reset_engineering, args=(prefix,))
        if page == 'pipe' and mode != 'WATER · 압력손실':
            fluid = 'AIR' if mode.startswith('AIR') else 'WATER'
            st.markdown(f"### {fluid} 배관 권장 유속")
            engineering_table([{'사용 개소':where, '유속 (m/s)':v} for kind, where, v in PIPE_VELOCITIES if kind == fluid])
            if fluid == 'AIR':
                st.caption('AIR 최대 허용유속: 120 m/s')
    with right:
        st.markdown("<div class='workspace-head'><span>CALCULATION OUTPUT</span><h2>계산 결과</h2><p>입력값이 바뀌면 결과와 그래프가 즉시 갱신됩니다.</p></div>", unsafe_allow_html=True)
        try:
            result = engineering_result(page, mode, values)
        except (ValueError, OverflowError) as error:
            st.warning(str(error) if isinstance(error, ValueError) else '입력값이 너무 큽니다. 계산 범위 안의 값을 입력하세요.')
            result = None
        if result is not None:
            with st.container(border=True):
                for start in range(0, len(result['metrics']), 2):
                    columns = st.columns(2)
                    for col, (label, value, unit) in zip(columns, result['metrics'][start:start+2]):
                        with col: st.metric(label + (f' ({unit})' if unit else ''), f'{value:,.2f}')
                if result['note']: st.caption(result['note'])
            with st.container(border=True):
                xlabel, rows = engineering_curve(page, mode, values)
                label, _, unit = result['metrics'][0]
                st.markdown("<div class='subhead'>입력 조건에 따른 변화</div>", unsafe_allow_html=True)
                curve_key = engineering_curve_key(page, mode)
                st.vega_lite_chart(spec={
                    'height': 350, 'background': '#ffffff',
                    'layer': [
                        {'data': {'values': rows}, 'mark': {'type':'line','color':'#0085c8','strokeWidth':3}, 'encoding': {'x': {'field':'x','type':'quantitative','title':xlabel}, 'y': {'field':'y','type':'quantitative','title':f'{label} ({unit})'}, 'tooltip':[{'field':'x','title':xlabel,'format':'.2f'},{'field':'y','title':label,'format':'.2f'}]}},
                        {'data': {'values': [{'x':values[curve_key], 'y':result['metrics'][0][1]}]}, 'mark': {'type':'point','color':'#0a9b73','filled':True,'size':110}, 'encoding':{'x':{'field':'x','type':'quantitative'},'y':{'field':'y','type':'quantitative'}}},
                    ], 'config': {'view': {'stroke':'#d6e2e9','fill':'#ffffff'}, 'axis': {'labelColor':'#577084','titleColor':'#14364e','gridColor':'#dce7ed','domainColor':'#d6e2e9','tickColor':'#d6e2e9','format':'.2f'}}
                }, width='stretch', theme=None)
                st.caption('파란색은 선택한 입력값에 따른 계산 결과, 초록색은 현재 조건입니다. 다른 입력값은 고정합니다.')
            with st.container(border=True):
                st.markdown("<div class='subhead'>PDF 리포트</div>", unsafe_allow_html=True)
                st.download_button('PDF 리포트 다운로드', data=deferred_pdf(engineering_pdf, title, mode, input_rows, result, SOURCE_NAMES[page], page, values), file_name=f'{page}_calculation_report.pdf', mime='application/pdf', on_click='ignore', type='primary', width='stretch')
    if page == 'pipe' and mode == 'WATER · 압력손실':
        st.markdown('### 부속품 등가길이 참고표')
        st.markdown('<style>.engineering-table-wrap{max-height:none}.engineering-table th,.engineering-table td{white-space:normal;min-width:64px}.engineering-table th:first-child,.engineering-table td:first-child{min-width:180px}</style>', unsafe_allow_html=True)
        engineering_table([{'부속품':name, **{f'{size}A':length for size, length in zip(PIPE_SIZES, lengths)}} for _, name, lengths in PIPE_FITTINGS])
        st.caption('등가길이 단위: m. 호칭구경과 실제 배관 내경은 다릅니다. 좁은 화면에서는 표를 좌우로 이동할 수 있습니다.')
    if page == 'air':
        with st.expander('노즐 구경·압력별 공기량 참고표'):
            pressures = [.7, 1., 1.5, 2., 2.5, 3., 4., 5., 7., 10.]
            st.caption(f"현재 온도 {values['t']:.2f}°C와 유량계수 {values['c']:.2f} 적용 · 압력 단위 {values['pressure_unit']} · 유량 L/min")
            if values['t'] > -273:
                engineering_table([{'구경 (mm)':d, **{f'{p:.2f}':round(engineering_result('air','솔리드 노즐',dict(values,d=d,p=p))['metrics'][0][1],2) for p in pressures}} for d in AIR_REFERENCE_DIAMETERS])
    elif page == 'slit':
        with st.expander('용도별 풍속·슬릿간격 / 접속구 선정 기준', expanded=True):
            engineering_table([{'용도':name, '풍속 (m/s)':speed, '슬릿간격 (mm)':gap} for name, speed, gap in SLIT_APPLICATIONS])
            engineering_table([{'접속구 구경':name,'1개당 기본풍량 (m³/min)':capacity} for name,capacity in CONNECTION_CAPACITY.items()])
            st.caption('첨부 이미지의 예제에는 풍속·풍량·수량 간 불일치가 있어, 계산기는 입력한 풍속으로 Q=A×v를 계산하고 접속구 수량을 올림합니다.')
        with st.expander('엑셀에 삽입된 원본 이미지'):
            if st.checkbox('원본 참고 이미지 불러오기', key='load_slit_images'):
                from calculator_assets import SLIT_SOURCE_IMAGES
                for data in SLIT_SOURCE_IMAGES:
                    st.image(base64.b64decode(data), width='stretch')
    footer()



def embedded_calculator(page: str) -> None:
    import gzip
    import streamlit.components.v1 as components
    from calculator_assets import payloads
    filenames = {'layout': 'AI SprayLayout Pro (Tony).html', 'impact': '노즐 충격력 분석 및 펌프 이론 계산기 (Ben).html'}
    html_bytes = gzip.decompress(base64.b64decode(payloads[page]))
    if page == 'layout':
        st.markdown("""<style>
[data-testid="stMainBlockContainer"]{max-width:none!important;padding:0!important}
[data-testid="stHeader"],#MainMenu{display:none!important}
[data-testid="stMainBlockContainer"]>div{gap:0!important}
</style>""", unsafe_allow_html=True)
        st.button('← 계산기 목록', on_click=go, args=('home',))
        # Original logic and layout; only put the footer after the document.
        # A fixed footer creates a feedback loop when an iframe sizes to content.
        html = html_bytes.decode('utf-8-sig')
        html = html.replace('</head>', '<style>@media screen{.footer{position:static!important;height:auto!important;min-height:42px;flex-wrap:wrap;padding-top:8px;padding-bottom:8px}}</style></head>', 1)
        # Streamlit 1.63's built-in measurement includes the previous viewport
        # height, which cannot shrink after a narrow-screen layout. Measure the
        # original document body instead, without changing its UI or handlers.
        html += """<script>
(() => {
  let pending = false;
  const resize = () => {
    if (pending) return;
    pending = true;
    requestAnimationFrame(() => {
      pending = false;
      const body = document.body;
      window.parent.postMessage({type: 'streamlit:iframe:setSize',
        width: Math.ceil(body.getBoundingClientRect().width),
        height: Math.ceil(Math.max(body.getBoundingClientRect().height, body.scrollHeight))}, '*');
    });
  };
  new ResizeObserver(resize).observe(document.body);
  window.addEventListener('load', resize);
  window.addEventListener('resize', resize);
})();
</script>"""
        st.iframe(html, height='content', width='stretch')
        return
    index = 7 if page == 'layout' else 8
    _, title, description = CALCULATOR_CARDS[index-1]
    header()
    back, _ = st.columns([1.1, 5])
    with back:
        st.button('← 계산기 목록', width='stretch', on_click=go, args=('home',))
    st.markdown(f'<section class="calc-intro"><div><span class="calc-index">CALCULATOR / {index:02d}</span><h1>{title}</h1><p>{description}</p></div></section>', unsafe_allow_html=True)
    st.caption('계산기 안의 PDF 저장 버튼에서 인쇄 대상을 PDF로 선택하세요.')
    components.html(html_bytes.decode('utf-8-sig'), height=1500, scrolling=True)
    st.download_button('단독 실행용 HTML 다운로드', data=html_bytes, file_name=filenames[page], mime='text/html', key='download_'+page)
    footer()


def density_report(title: str, sections: list) -> bytes:
    from html import escape
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
    pdfmetrics.registerFont(UnicodeCIDFont('HYSMyeongJo-Medium'))
    style = ParagraphStyle('density', fontName='HYSMyeongJo-Medium', fontSize=9, leading=14)
    heading = ParagraphStyle('densityTitle', parent=style, fontSize=19, leading=26)
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=38, rightMargin=38, topMargin=38, bottomMargin=90, title=title)
    story = [report_header(doc.width), Spacer(1,18), Paragraph(title, heading), Spacer(1,12), Paragraph(datetime.now().strftime('%Y-%m-%d %H:%M'), style), Paragraph('노란색: 입력값 / 회색: 계산 결과', style), Spacer(1,22)]
    for name, formula, rows in sections:
        block = [Paragraph(name, heading), Spacer(1,8), Paragraph(escape(formula), style), Spacer(1,12)]
        cells = [[Paragraph(escape(str(text)).replace('\n','<br/>'),style) for text,kind in row] for row in rows]
        table = Table(cells, colWidths=[(A4[0]-76)/len(rows[0])]*len(rows[0]))
        styles = [('GRID',(0,0),(-1,-1),.7,colors.black),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('TOPPADDING',(0,0),(-1,-1),12),('BOTTOMPADDING',(0,0),(-1,-1),12)]
        for y,row in enumerate(rows):
            for x,(text,kind) in enumerate(row):
                styles.append(('BACKGROUND',(x,y),(x,y),colors.HexColor({'input':'#fff600','output':'#dedede','label':'#fce9d9'}[kind])))
        table.setStyle(TableStyle(styles));block.extend([table,Spacer(1,30)]);story.append(KeepTogether(block))
    story += [Paragraph(f'{len(sections)+1}. 계산 조건 및 참고 사항', heading), Spacer(1,8), Paragraph('유체 온도 및 점도, 혼합 시 부피 변화에 따라 실제 결과가 달라질 수 있습니다.',style), Spacer(1,10), Paragraph(REPORT_NOTICE,style)]
    doc.build(story, onFirstPage=report_page_footer, onLaterPages=report_page_footer)
    return buf.getvalue()


def density_calculator() -> None:
    header()
    st.button('← 계산기 목록', on_click=go, args=('home',))
    st.markdown('<section class="calc-intro"><div><span class="calc-index">CALCULATOR / 06</span><h1>밀도·비중별 유량 계산기</h1><p>노란색은 입력값, 회색은 계산 결과입니다. 두 양식은 각각 계산하고 PDF로 저장합니다.</p></div></section>', unsafe_allow_html=True)
    st.markdown('''<style>
.st-key-density_sheet [data-testid="stNumberInputContainer"],.st-key-density_sheet input{background:#fff600!important;color:#142f42!important;-webkit-text-fill-color:#142f42!important;color-scheme:light}
.st-key-density_sheet [data-testid="stNumberInput"] label{background:#fce9d9;padding:8px;width:100%;color:#142f42!important}
.st-key-density_sheet [data-testid="stMetric"]{background:#dedede!important;padding:12px;border:1px solid #a5a5a5;min-height:100px}
.st-key-density_sheet [data-testid="stMetric"] *{color:#142f42!important;-webkit-text-fill-color:#142f42!important}
.st-key-density_sheet [data-testid="stMetricValue"]{font-size:25px}
.st-key-density_sheet [role="tablist"]{gap:12px;height:auto!important;padding:8px 0 16px;flex-wrap:wrap}
.st-key-density_sheet [role="tab"]{background:#e3edf5!important;border:2px solid #718da4!important;border-radius:8px!important;padding:16px 24px!important;height:auto!important;min-height:58px;color:#163c56!important}
.st-key-density_sheet [role="tab"] p{font-size:19px!important;font-weight:700!important;color:inherit!important;-webkit-text-fill-color:inherit!important}
.st-key-density_sheet [role="tab"][aria-selected="true"]{background:#006da6!important;color:#fff!important;border-color:#006da6!important}

</style>''', unsafe_allow_html=True)
    st.info('밀도는 단위 부피당 질량(kg/m³), 비중은 기준 물의 밀도에 대한 비율로 단위가 없습니다. 이 계산기는 물의 기준 밀도를 1,000 kg/m³로 두어 비중 = 밀도 ÷ 1,000을 적용합니다. 따라서 밀도 1,000 kg/m³는 비중 1, 밀도 925 kg/m³는 비중 0.925입니다. 실제 물의 밀도는 온도에 따라 달라지므로 정밀 환산 시 기준 온도를 확인하세요.')
    st.markdown('### 아래에서 사용할 계산식을 선택하세요')
    with st.container(key='density_sheet'):
        tab1,tab2=st.tabs(['① 유량 단위·비중 환산','② 혼합물 밀도'])
        with tab1:
            st.info('1 → 2 → 3 순서로 계산하세요. 1단계의 Vol. Liquid Flow Rate (m³/h)를 2단계의 Liquid Flow Rate (m³/h)에 입력하고, 2단계 결과 Liquid Flow Rate (L/min)를 3단계 입력에 넣으면 최종 Water Flow Rate (L/min)가 계산됩니다. 단계 간 값은 직접 옮겨 입력하며, 자동으로 복사되지 않습니다.')
            sections=[]; valid=True
            definitions=[('1. 무게 단위를 부피 단위로 변환','질량 → 부피 유량',[('mass','Liquid Flow Rate (kg/h)',3500.),('rho','Density (kg/m³)',925.)],'Vol. Liquid Flow Rate (m³/h)','부피 유량 (m³/h) = 질량 유량 (kg/h) / 밀도 (kg/m³)'),
                         ('2. 부피 단위 환산','부피 유량 단위 환산',[('volume','Liquid Flow Rate (m³/h)',3.78)],'Liquid Flow Rate (L/min)','유량 (L/min) = 유량 (m³/h) × 1000 / 60'),
                         ('3. 비중에 따른 유량 변환 (Liquid → Water)','비중에 따른 유량 보정',[('q','Liquid Flow Rate (L/min)',63.),('rho','Density (kg/m³)',925.)],'Water Flow Rate (L/min)','비중 = 밀도 / 1000; 물 기준 유량 = 액체 유량 × √비중')]
            for i,(title,mode,fields,output,formula) in enumerate(definitions):
                st.subheader(title);st.caption(formula)
                if i == 1: st.markdown('🔴 1단계의 **Vol. Liquid Flow Rate (m³/h)** 결과를 아래 입력칸에 넣으세요.')
                if i == 2: st.markdown('🔵 2단계의 **Liquid Flow Rate (L/min)** 결과를 아래 입력칸에 넣으세요. 동일 유체의 밀도를 적용합니다.')
                cols=st.columns(len(fields)+1);values={};row=[]
                for col,(key,label,default) in zip(cols,fields):
                    with col: values[key]=st.number_input(label,min_value=0.,value=default,step=.01,format='%.2f',key=f'density_form_{i}_{key}')
                    row.extend([(label,'label'),(f'{values[key]:,.2f}','input')])
                try: result=engineering_result('density',mode,values);number=result['metrics'][0][1]
                except (ValueError,OverflowError) as e:
                    valid=False;number=None;st.warning(str(e))
                with cols[-1]: st.metric(output,'—' if number is None else f'{number:,.2f}')
                row.extend([(output,'label'),('—' if number is None else f'{number:,.2f}','output')]);sections.append((title,formula,[row]));st.divider()
            if valid:
                st.download_button('유량 단위·비중 환산 PDF 다운로드',deferred_pdf(density_report, '유량 단위·비중 환산',sections),file_name='density_flow_report.pdf',mime='application/pdf', on_click='ignore',key='density_flow_pdf')
        with tab2:
            st.subheader('혼합물 밀도 구하는 계산식')
            formula='혼합물 밀도 = (v1 × d1 + v2 × d2) / (v1 + v2) = 총 질량 유량 / 총 부피 유량'
            st.caption(formula);st.caption('A 용액: 밀도 d1, 부피 유량 v1 = 질량 유량 / d1 · B 용액: 밀도 d2, 부피 유량 v2 = 질량 유량 / d2')
            vals={};rows=[]
            for tag,rho,mass in [('A',830.,10000.),('B',740.,4500.)]:
                cols=st.columns([.7,1,1])
                with cols[0]: st.markdown(f'### {tag} 용액')
                with cols[1]: vals['rho_'+tag.lower()]=st.number_input(f'{tag} Density (kg/m³)',min_value=0.,value=rho,step=.01,format='%.2f',key='mix_rho_'+tag)
                with cols[2]: vals['mass_'+tag.lower()]=st.number_input(f'{tag} Flow Rate (kg/h)',min_value=0.,value=mass,step=.01,format='%.2f',key='mix_mass_'+tag)
                rows.append([(tag+' 용액','label'),('Density\n(kg/m³)','label'),(f"{vals['rho_'+tag.lower()]:,.2f}",'input'),('Flow Rate\n(kg/h)','label'),(f"{vals['mass_'+tag.lower()]:,.2f}",'input')])
            try:
                result=engineering_result('density','혼합물 밀도',vals);density,total=result['metrics'][0][1],result['metrics'][1][1]
            except (ValueError,OverflowError) as e: st.warning(str(e))
            else:
                cols=st.columns([.7,1,1])
                with cols[0]: st.markdown('### TOTAL LIQUID')
                with cols[1]: st.metric('Density (kg/m³)',f'{density:,.2f}')
                with cols[2]: st.metric('Flow Rate (kg/h)',f'{total:,.2f}')
                rows.append([('TOTAL LIQUID','label'),('Density\n(kg/m³)','label'),(f'{density:,.2f}','output'),('Flow Rate\n(kg/h)','label'),(f'{total:,.2f}','output')])
                st.caption('혼합 전후 부피의 합이 유지된다고 가정합니다. 유체 온도 및 점도에 따라 실제 결과가 달라질 수 있습니다.')
                st.download_button('혼합물 밀도 PDF 다운로드',deferred_pdf(density_report, '혼합물 밀도 계산', [('1. 혼합물 밀도',formula,rows)]),file_name='mixture_density_report.pdf',mime='application/pdf', on_click='ignore',key='density_mix_pdf')
    footer()


# Conversion factors use Pa, L/min, kg and L as base units (NIST SP 811).
AUX_UNITS = {
    '압력': {'bar':100000., 'MPa':1e6, 'kPa':1000., 'Pa':1., 'psi':6894.757293168, 'kgf/cm²':98066.5, 'atm':101325.},
    '유량': {'L/min':1., 'L/h':1/60, 'L/s':60., 'm³/h':1000/60, 'm³/min':1000., 'mL/min':.001, 'US gpm':3.785411784, 'Imperial gpm':4.54609, 'ft³/min (CFM)':28.316846592},
    '온도': {'°C':1., '°F':1., 'K':1.},
    '질량': {'kg':1., 'g':.001, 'mg':.000001, 't':1000., 'lb':.45359237, 'oz':.028349523125},
    '체적': {'L':1., 'mL':.001, 'm³':1000., 'cm³':.001, 'US gal':3.785411784, 'Imperial gal':4.54609, 'ft³':28.316846592, 'in³':.016387064},
}


def auxiliary_convert(category: str, value: float, source: str, target: str) -> float:
    if not math.isfinite(value): raise ValueError('유효한 숫자를 입력하세요.')
    if category == '온도':
        kelvin = value+273.15 if source=='°C' else (value-32)*5/9+273.15 if source=='°F' else value
        if kelvin < -1e-10: raise ValueError('절대영도(0 K / -273.15°C) 이상으로 입력하세요.')
        kelvin=max(0.,kelvin)
        result=kelvin-273.15 if target=='°C' else (kelvin-273.15)*9/5+32 if target=='°F' else kelvin
    else: result=value*AUX_UNITS[category][source]/AUX_UNITS[category][target]
    if not math.isfinite(result): raise ValueError('입력값이 계산 범위를 벗어났습니다.')
    return result


def nozzle_triangle(mode: str, height: float, angle: float, coverage: float) -> tuple[float,float,float]:
    if not all(math.isfinite(v) for v in (height,angle,coverage)): raise ValueError('유효한 숫자를 입력하세요.')
    if mode != '분사각 계산' and not 0 < angle < 180: raise ValueError('전체 분사각은 0° 초과, 180° 미만이어야 합니다.')
    if mode != '높이 계산' and height <= 0: raise ValueError('노즐 높이는 0보다 커야 합니다.')
    if mode != '커버리지 계산' and coverage <= 0: raise ValueError('커버리지는 0보다 커야 합니다.')
    if mode == '커버리지 계산': coverage=2*height*math.tan(math.radians(angle/2))
    elif mode == '높이 계산': height=coverage/(2*math.tan(math.radians(angle/2)))
    else: angle=math.degrees(2*math.atan(coverage/(2*height)))
    if not all(math.isfinite(v) for v in (height,angle,coverage)): raise ValueError('입력값이 계산 범위를 벗어났습니다.')
    return height,angle,coverage


def spray_aux_result(kind: str, a: dict) -> list:
    if any(not math.isfinite(v) or v < 0 for v in a.values()): raise ValueError('0 이상의 유효한 숫자를 입력하세요.')
    def positive(key, label):
        if a[key] <= 0: raise ValueError(label+'은(는) 0보다 커야 합니다.')
        return a[key]
    if 'count' in a and (a['count']<1 or not a['count'].is_integer()): raise ValueError('노즐 수는 1 이상의 정수로 입력하세요.')
    if kind == 'coating':
        length=positive('length','제품 길이');width=positive('width','제품 폭')
        efficiency=positive('efficiency','도포 효율')
        if efficiency>100: raise ValueError('도포 효율은 100% 이하여야 합니다.')
        dose=a['dose']
        duration=length/(positive('speed','제품 이동 속도')*1000/60) if a['moving']==1 else positive('duration','제품당 ON 분사 시간')
        required=dose/(efficiency/100)
        q=required/duration*60/1000/a['count']
        rows=[('제품 면적',length*width,'mm²'),('제품 면적 (제곱미터)',length*width/1000000,'m²'),('제품당 ON 분사 시간',duration,'초'),('제품당 총 분사량',required,'mL/개'),('필요 노즐당 ON 유량',q,'L/min·개'),('필요 전체 ON 유량',q*a['count'],'L/min')]
        if a['moving']==1:
            products=positive('products','분당 이송 제품 수량')
            if not products.is_integer(): raise ValueError('분당 이송 제품 수량은 정수로 입력하세요.')
            maximum=a['speed']*1000/length
            if products>maximum+1e-10: raise ValueError(f'이송 속도와 제품 길이 기준 최대 수량은 {math.floor(maximum):,d}개/분입니다. 수량·속도·길이를 확인하세요.')
            pitch=a['speed']*1000/products
            rows.extend([('분당 이송 제품 수량',products,'개/min'),('최대 이송 제품 수량 (간격 없음)',math.floor(maximum),'개/min'),('제품 사이 간격',max(0.,pitch-length),'mm'),('노즐당 분당 평균 유량',required*products/1000/a['count'],'L/min·개'),('전체 분당 평균 유량',required*products/1000,'L/min')])
    elif kind == 'wear':
        ref=positive('reference','새 노즐 기준 유량');days=positive('elapsed','현재까지 사용 일수')
        delta=a['measured']-ref;rate=delta/ref*100
        rows=[('현재 유량 증가율 (마모 지표)',rate,'%'),('현재까지 사용 일수',days,'일')]
        if delta>=0:
            daily=delta/days;future=a['measured']+daily*a['future']
            rows.extend([('월 유량 증가량',daily*30,'L/min·월'),('예상 누적 사용 일수',days+a['future'],'일'),('예상 노즐 유량',future,'L/min'),('예상 유량 증가율 (마모 지표)',(future/ref-1)*100,'%')])
    else:
        duration=positive('on','ON 분사 시간');cycle=duration+a['off']
        q=a['volume']/duration*60/1000 if kind=='pulse_reverse' else a['flow']
        shot=q*duration/60*1000
        rows=[('노즐당 1회 ON 분사량',shot,'mL/회'),('노즐당 주기 평균 유량',shot/cycle*60/1000,'L/min'),('노즐당 시간당 사용량',shot/cycle*3600/1000,'L/h'),('시간당 분사 횟수',3600/cycle,'회/h')]
    if any(not math.isfinite(value) for _,value,_ in rows): raise ValueError('입력값이 계산 범위를 벗어났습니다.')
    return rows


def spray_grouped_results(kind: str, rows: list, inputs: dict) -> None:
    from html import escape
    data = {label:(value,unit) for label,value,unit in rows}
    def value(label):
        if label not in data: return '—'
        number,unit=data[label]
        decimals=2 if 'L/min' in unit else 0
        return f'{number:,.{decimals}f} {unit}'
    def table(title, headings, body):
        cells=''.join('<tr>'+''.join('<td>'+escape(str(c))+'</td>' for c in row)+'</tr>' for row in body)
        return '<section class="spray-summary"><h3>'+escape(title)+'</h3><table><thead><tr>'+''.join('<th>'+escape(c)+'</th>' for c in headings)+'</tr></thead><tbody>'+cells+'</tbody></table></section>'
    css='<style>.spray-summary{background:white;border:1px solid #cbdde7;border-radius:8px;margin:0 0 14px;padding:14px;color:#17394f;color-scheme:light}.spray-summary h3{font-size:17px!important;margin:0 0 10px!important;color:#17394f!important}.spray-summary table{width:100%;border-collapse:collapse;font-size:14px}.spray-summary th{background:#e3f2fa;color:#17394f}.spray-summary td,.spray-summary th{padding:9px 8px;border-bottom:1px solid #dce7ed;text-align:left;overflow-wrap:anywhere;color:#17394f!important}.spray-summary td:not(:first-child){font-weight:600}.spray-summary tr:last-child td{border-bottom:0}</style>'
    if kind=='coating':
        moving=inputs['moving']==1
        head=['구분','노즐 추천 유량']+(['노즐 ON 분사 유량'] if moving else [])
        body=[['노즐 1개',value('필요 노즐당 ON 유량')]+([value('노즐당 분당 평균 유량')] if moving else []),['전체 노즐',value('필요 전체 ON 유량')]+([value('전체 분당 평균 유량')] if moving else [])]
        html=table('필요 노즐 유량',head,body)
        html+=table('제품 1개 기준',['항목','계산 결과'],[['면적',value('제품 면적')+' / '+value('제품 면적 (제곱미터)')],['ON 분사 시간',value('제품당 ON 분사 시간')],['총 분사량',value('제품당 총 분사량')]])
        if moving:
            html+=table('제품 이송',['항목','계산 결과'],[['입력 수량 / 최대 수량',value('분당 이송 제품 수량')+' / '+value('최대 이송 제품 수량 (간격 없음)')],['제품 사이 간격',value('제품 사이 간격')]])
    else:
        html=table('현재 상태와 향후 예상',['항목','현재','예상'],[['사용 일수',value('현재까지 사용 일수'),value('예상 누적 사용 일수')],['노즐 유량',f"{inputs['measured']:,.2f} L/min",value('예상 노즐 유량')],['유량 증가율',value('현재 유량 증가율 (마모 지표)'),value('예상 유량 증가율 (마모 지표)')]])
        if '월 유량 증가량' in data:
            html+=table('예측 기준',['항목','값'],[['새 노즐 기준 유량',f"{inputs['reference']:,.2f} L/min"],['추가 사용 일수',f"{inputs['future']:,.0f} 일"],['월 유량 증가량 (30일)',value('월 유량 증가량')]])
    st.markdown(css+html,unsafe_allow_html=True)


def spray_aux_panel(kind: str) -> None:
    extra={};calc=kind
    if kind=='coating':
        st.markdown('### 제품당 도포량으로 필요 노즐 유량 계산')
        motion=st.radio('제품 분사 방식',['이동 제품','정지 제품'],horizontal=True,key='product_motion')
        extra={'moving':float(motion=='이동 제품')}
        fields=[('length','제품 길이 · 이동 방향 (mm)',300.),('width','제품 폭 (mm)',200.),('dose','제품 1개에 도포할 양 (mL/개)',5.),('count','동시에 분사하는 노즐 수 (개)',1.),('efficiency','도포 효율 (Puls%)',100.)]
        if motion=='이동 제품': fields[2:2]=[('speed','제품 이동 속도 (m/min)',10.),('products','분당 이송 제품 수량 (개/min)',10.)]
        else: fields.insert(2,('duration','제품당 ON 분사 시간 (초)',2.))
        note='제품 한 면에 도포하는 총량을 입력하세요. 모든 노즐이 같은 유량으로 제품 전체 폭을 도포한다고 가정합니다. 이동 제품의 분사 시간은 제품 길이 ÷ 이동 속도입니다. 제품 폭은 면적 확인에 사용하며 노즐 수·배치는 별도로 선정하세요. 한 줄 이송을 가정하며, 제품 사이에서는 분사를 정지합니다. 분당 수량은 평균 사용량에 반영되며 ON 유량은 제품 통과 시간으로 계산합니다. Puls%는 기존 도포 효율 보정값으로 적용합니다.'
        formula='노즐당 ON 유량(L/min) = 제품당 도포량(mL) ÷ 도포 효율 ÷ 노즐 수 ÷ ON 시간(초) × 60 ÷ 1000'
    elif kind=='wear':
        st.markdown('### 사용 일수에 따른 유량 증가·마모 추정')
        fields=[('reference','새 노즐 기준 유량 (L/min)',1.),('measured','현재 측정 유량 (L/min)',1.1),('elapsed','현재까지 실제 사용 일수 (일)',100.),('future','향후 추가 사용 일수 (일)',50.)]
        note='동일한 압력·유체·온도에서 측정한 노즐당 유량을 비교합니다. 표시하는 마모율은 유량 증가율이며 실제 재료 마모율이 아닙니다. 하루 가동시간과 사용 조건이 같고 유량 증가 속도가 일정하다고 가정한 선형 추정입니다. 월 유량 증가량은 30일 기준입니다. 실제 마모는 비선형일 수 있어 교체 시점 보증값으로 사용할 수 없습니다.'
        formula='예상 유량 = 현재 유량 + (현재 유량 − 새 노즐 유량) ÷ 사용 일수 × 추가 사용 일수'
    else:
        st.markdown('### 간헐 분사량·노즐 유량 계산')
        mode=st.radio('계산 방향',['1회 분사량 → 노즐 유량','노즐 유량 → 1회 분사량'],horizontal=True,key='pulse_new_direction')
        calc='pulse_reverse' if mode.startswith('1회') else 'pulse_forward'
        fields=[('volume','노즐당 1회 ON 분사량 (mL)',10.)] if calc=='pulse_reverse' else [('flow','노즐당 ON 유량 (L/min)',1.)]
        fields += [('on','ON 분사 시간 (초)',1.),('off','OFF 정지 시간 (초)',1.)]
        note='정지 시간은 주기 평균 유량과 시간당 사용량에 반영됩니다. ON 중 노즐 유량은 1회 분사량과 ON 시간으로 결정되므로 OFF 시간만 변경해도 변하지 않습니다. 밸브 응답 지연과 기동 과도유량은 제외합니다.'
        formula='노즐당 평균 유량(L/min) = 1회 분사량(mL) ÷ (ON 시간 + OFF 시간)(초) × 60 ÷ 1000'
    left,right=st.columns(2);a=dict(extra)
    with left:
        for key,label,default in fields:
            integer_display=kind in ('coating','pulse') or key in ('elapsed','future')
            if kind=='coating' and key=='efficiency':
                st.markdown('<div style="display:flex;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:6px;color:#294a61;font-size:14px"><span>도포 효율 (Puls%)</span><mark style="background:#fff2a8;color:#593f00;padding:3px 7px;border-radius:4px;font-weight:700">도표 효율과 노즐 추천 유량은 반비례</mark></div>',unsafe_allow_html=True)
            a[key]=st.number_input(label,min_value=0.,max_value=100. if key=='efficiency' else None,value=default,step=1. if integer_display else .01,format='%.0f' if integer_display else '%.2f',key='spray_v3_'+kind+'_'+key,label_visibility='collapsed' if kind=='coating' and key=='efficiency' else 'visible')
        st.caption(note)
    with right:
        try:
            rows=spray_aux_result(calc,a)
            if kind in ('coating','wear'):
                spray_grouped_results(kind, rows, a)
            else:
                for label,value,unit in rows:
                    decimals = 2 if 'L/min' in unit else 0
                    st.metric(label,f'{value:,.{decimals}f} {unit}')
            if kind=='coating': st.caption('L/min 결과 외에는 정수로 반올림하여 표시합니다. 작은 면적(m²)이나 짧은 시간은 0으로 보일 수 있으나 계산은 반올림 전 값을 사용합니다.')
            if kind=='wear' and a['measured']<a['reference']: st.warning('현재 유량이 새 노즐보다 작아 마모 증가 추정을 표시하지 않습니다. 압력·막힘·측정 조건을 확인하세요.')
            st.caption(formula)
        except (ValueError,OverflowError) as e: st.warning(str(e))


def auxiliary_calculator() -> None:
    header()
    st.button('← 계산기 목록',on_click=go,args=('home',))
    st.markdown('<section class="calc-intro"><div><span class="calc-index">CALCULATOR / 09</span><h1>노즐 현장 보조 계산기</h1><p>도포량·마모율·간헐 분사를 계산하고 단위 환산과 노즐 커버리지를 확인하세요.</p></div></section>',unsafe_allow_html=True)
    st.markdown('''<style>[data-testid="stTabs"] [role="tab"]{padding:12px 20px!important;height:auto!important;border:1px solid #7195ae!important;border-radius:6px;background:#e3edf5!important;color:#163c56!important}[data-testid="stTabs"] [role="tab"][aria-selected="true"]{background:#006da6!important;color:white!important}[data-testid="stTabs"] [role="tab"] p{color:inherit!important;font-weight:700}</style>''',unsafe_allow_html=True)
    coating,wear,pulse,units,triangle=st.tabs(['① 도포량','② 마모율·유량 예측','③ 간헐 분사','④ 단위 환산','⑤ 삼각함수·노즐 커버리지'])
    with coating: spray_aux_panel('coating')
    with wear: spray_aux_panel('wear')
    with pulse: spray_aux_panel('pulse')
    with units:
        category=st.selectbox('환산 항목',list(AUX_UNITS),key='aux_category')
        choices=list(AUX_UNITS[category]);left,right=st.columns(2)
        with left:
            source=st.selectbox('입력 단위',choices,key='aux_from_'+category)
            value=st.number_input('입력값',value=1.,format='%.2f',key='aux_value_'+category)
        with right:
            target=st.selectbox('결과 단위',choices,index=1,key='aux_to_'+category)
            try:
                result=auxiliary_convert(category,value,source,target)
                st.metric('환산 결과',f'{result:,.2f} {target}')
                st.caption(f'{value:,.2f} {source} = {result:,.2f} {target}')
            except ValueError as e: st.warning(str(e))
        if category=='압력': st.caption('단위만 환산합니다. 게이지압과 절대압 사이의 기준압 보정은 하지 않습니다.')
        if category=='유량': st.caption('체적 유량 단위 환산입니다. 기체의 압력·온도 및 표준상태(NL, SCFM) 보정은 포함하지 않습니다.')
        if category in ('체적','유량'): st.caption('미국 US gallon과 영국 Imperial gallon은 서로 다른 단위입니다.')
        st.caption('환산 계수: NIST SP 811. 내부 계산은 표시 자릿수로 반올림하지 않습니다.')
    with triangle:
        mode=st.selectbox('계산 항목',['커버리지 계산','높이 계산','분사각 계산'],key='aux_triangle_mode')
        length_unit=st.selectbox('높이·커버리지 단위',['mm','cm','m','in'],key='aux_length_unit')
        st.caption('입력한 길이는 선택한 단위로 해석됩니다. 분사각은 중심선 양쪽을 합한 전체 각도입니다.')
        left,right=st.columns([1,1.4]);h,a,w=100.,65.,127.41
        with left:
            if mode!='높이 계산': h=st.number_input('노즐 높이 H ('+length_unit+')',min_value=0.,value=100.,format='%.2f',key='aux_height')
            if mode!='분사각 계산': a=st.number_input('전체 분사각 θ (°)',min_value=0.,max_value=180.,value=65.,format='%.2f',key='aux_angle')
            if mode!='커버리지 계산': w=st.number_input('커버리지 W ('+length_unit+')',min_value=0.,value=127.41,format='%.2f',key='aux_width')
            st.markdown('**W = 2 × H × tan(θ / 2)**')
            st.caption('노즐 중심선이 평평한 대상면에 수직이고 분사가 대칭인 경우의 이론 폭입니다. 실제 분사각·유효 커버리지는 압력과 노즐 특성에 따라 달라질 수 있습니다.')
        with right:
            try: h,a,w=nozzle_triangle(mode,h,a,w)
            except ValueError as e: st.warning(str(e))
            else:
                label,val,unit=('커버리지 W',w,length_unit) if mode=='커버리지 계산' else ('노즐 높이 H',h,length_unit) if mode=='높이 계산' else ('전체 분사각 θ',a,'°')
                st.metric(label,f'{val:,.2f} {unit}')
                scale=min(400/w,230/h);x=w/2*scale;y=70+h*scale
                st.markdown(f'''<svg viewBox="0 0 560 390" role="img" aria-label="노즐 높이와 전체 분사각에 따른 커버리지" style="width:100%;background:white;border:1px solid #cbdde7;border-radius:8px"><polygon points="280,70 {280-x},{y} {280+x},{y}" fill="#e0f2fb" stroke="#0085c8" stroke-width="2"/><line x1="280" y1="70" x2="280" y2="{y}" stroke="#577084" stroke-dasharray="5 4"/><circle cx="280" cy="70" r="6" fill="#14364e"/><text x="280" y="30" text-anchor="middle" fill="#14364e">전체 분사각 θ = {a:.2f}°</text><text x="290" y="{70+h*scale/2}" fill="#14364e">H = {h:,.2f} {length_unit}</text><text x="280" y="350" text-anchor="middle" fill="#006da6">커버리지 W = {w:,.2f} {length_unit}</text></svg>''',unsafe_allow_html=True)
        with st.expander('기본 삼각함수 sin · cos · tan'):
            theta=st.number_input('각도 (°)',value=30.,format='%.2f',key='aux_trig_angle')
            radians=math.radians(theta%360);c=math.cos(radians)
            cols=st.columns(3)
            for col,label,value in zip(cols,['sin','cos','tan'],[f'{math.sin(radians):.2f}',f'{c:.2f}','정의되지 않음' if abs(c)<1e-12 else f'{math.tan(radians):.2f}']):
                with col: st.metric(label,value)
    footer()


def home() -> None:
    st.markdown("""<style>
[data-testid="stToolbar"],[data-testid="stToolbarActions"],[data-testid="stAppDeployButton"]{display:none!important}
.menu-card .card-bottom{display:flex;justify-content:space-between;align-items:center;gap:12px}
.menu-card .card-author{color:#294a61;font-size:.88rem;font-weight:800;letter-spacing:.04em;white-space:nowrap}
</style>""", unsafe_allow_html=True)
    header()
    st.markdown('''<section class="hero"><div><div class="eyebrow">SPRAY ENGINEERING WORKSPACE</div>
    <h1>Spray Engineering Calculator</h1><p>현장 조건에 맞는 계산기를 선택하고 필요한 운전값을 빠르게 검토하세요.</p></div></section>
    <div class="section-kicker">SELECT A CALCULATOR</div><div class="section-title">계산기 선택</div>
    <div class="section-copy">총 9개의 계산기를 사용할 수 있습니다.</div>''', unsafe_allow_html=True)
    for row in range(0, len(CALCULATOR_CARDS), 3):
        columns = st.columns(3, gap='large')
        for offset, col in enumerate(columns):
            i = row+offset
            if i >= len(CALCULATOR_CARDS): break
            with col:
                if i < len(CALCULATOR_CARDS):
                    page, title, copy = CALCULATOR_CARDS[i]
                    author = 'By TONY' if page == 'layout' else 'By BEN' if page == 'impact' else ''
                    st.markdown(f"<div class='menu-card'><div class='num'>{i+1:02d} · AVAILABLE</div><h3>{title}</h3><p>{copy}</p><div class='card-bottom'><span class='pill'>사용 가능</span><span class='card-author'>{author}</span></div></div>", unsafe_allow_html=True)
                    st.button(f'{title} 열기 →', key='open_'+page, type='primary', width='stretch', on_click=go, args=(page,))
                else:
                    st.markdown(f"<div class='menu-card pending' aria-label='{i+1}번 빈 계산기 공간'><div class='num'>{i+1:02d}</div><h3>&nbsp;</h3><p>&nbsp;</p></div>", unsafe_allow_html=True)

    footer()


def main() -> None:
    init_state()
    if st.session_state.page in ('home','flow','water','air','slit','pipe','density','auxiliary'):
        st.markdown('<style>[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stToolbarActions"],[data-testid="stAppDeployButton"]{display:none!important}</style>', unsafe_allow_html=True)
    if st.session_state.page != "layout":
        st.markdown(CSS, unsafe_allow_html=True)
    content = st.container()
    if st.session_state.page in ('flow','water','air','slit','pipe','density'):
        author_inputs()
    with content:
        if st.session_state.page == "flow":
            flow_calculator()
        elif st.session_state.page in ('layout', 'impact'):
            embedded_calculator(st.session_state.page)
        elif st.session_state.page == "density":
            density_calculator()
        elif st.session_state.page == "auxiliary":
            auxiliary_calculator()
        elif st.session_state.page in CALC_MODES:
            engineering_calculator(st.session_state.page)
        else:
            home()



if __name__ == "__main__":
    _ = main()

