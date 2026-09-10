"""Spray Engineering Calculator.

Stage 1 rebuild: calculator selection home and nozzle flow-rate calculator.
The equations and default reference data are preserved from the supplied HTML.
"""

from __future__ import annotations

import math
from typing import Any

import streamlit as st


st.set_page_config(
    page_title="Spray Engineering Calculator",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="collapsed",
)


OFFICIAL_SITE_URL = "https://www.spray.com/ko-kr"
OFFICIAL_LOGO_URL = (
    "https://www.spray.com/ko-kr/-/media/spray/images/"
    "logo-spray-color-global.svg?iar=0&mh=150&hash=53D0DD1949C24C5AAAE0CBC733354240"
)


APP_CSS = r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800&display=swap');

:root {
  --navy-950: #06192b;
  --navy-900: #082742;
  --blue-600: #0082c6;
  --blue-500: #00a1df;
  --ink: #13283b;
  --muted: #5f7284;
  --line: #d9e3ea;
  --green: #0c9a75;
}
html, body, [class*="css"], [data-testid="stAppViewContainer"] {
  font-family: "Noto Sans KR", "Segoe UI", sans-serif;
}
[data-testid="stAppViewContainer"] {
  color: var(--ink);
  background:
    radial-gradient(circle at 92% 8%, rgba(0,161,223,.10), transparent 25rem),
    linear-gradient(180deg, #ffffff 0, #f5f8fa 27rem, #eef4f7 100%);
}
[data-testid="stHeader"] { background: rgba(255,255,255,.72); }
[data-testid="stMainBlockContainer"] {
  max-width: 1320px;
  padding-top: 1rem;
  padding-bottom: 3rem;
}
#MainMenu, footer { visibility: hidden; }
[data-testid="stSidebar"] { display: none; }

.site-header {
  display: flex; align-items: center; justify-content: space-between; gap: 1rem;
  min-height: 72px; padding: .65rem 1rem; margin-bottom: 1rem;
  border: 1px solid var(--line); background: rgba(255,255,255,.96);
  box-shadow: 0 10px 30px rgba(6,25,43,.07);
}
.official-brand {
  display: inline-flex; align-items: center; gap: .9rem; text-decoration: none !important;
}
.official-brand img { width: 218px; height: 44px; object-fit: contain; object-position: left center; }
.logo-fallback { display: none; color: var(--navy-900); font-size: 1.05rem; font-weight: 800; }
.official-link-label { color: #61768a; font-size: .72rem; font-weight: 700; letter-spacing: .04em; }
.tool-identity { text-align: right; }
.tool-identity strong { display:block; color:var(--navy-900); font-size:.9rem; }
.tool-identity span { color:#758798; font-size:.7rem; letter-spacing:.08em; }

.home-hero {
  position: relative; overflow: hidden; min-height: 300px; display: flex; align-items: center;
  padding: clamp(2rem, 5vw, 4.2rem); border-radius: 2px;
  background:
    radial-gradient(ellipse at 86% 12%, rgba(0,191,239,.55) 0, rgba(0,161,223,.20) 19%, transparent 45%),
    radial-gradient(ellipse at 74% 88%, rgba(255,255,255,.18) 0, transparent 35%),
    linear-gradient(112deg, #06192b 0%, #083456 52%, #007caf 100%);
  box-shadow: 0 24px 55px rgba(6,25,43,.18);
}
.home-hero:before, .home-hero:after {
  content: ""; position: absolute; right: -7%; width: 52%; height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,.65), transparent);
  transform: rotate(-18deg);
  box-shadow: 0 22px 0 rgba(255,255,255,.16), 0 44px 0 rgba(255,255,255,.10);
}
.home-hero:before { top: 36%; }
.home-hero:after { top: 62%; transform: rotate(-25deg); opacity:.65; }
.hero-content { position:relative; z-index:1; max-width:720px; }
.eyebrow { color:#6dd9ff; font-size:.74rem; font-weight:800; letter-spacing:.18em; }
.home-hero h1 {
  margin:.55rem 0 .7rem; color:#fff; font-size:clamp(2rem, 5vw, 4rem);
  line-height:1.06; letter-spacing:-.05em;
}
.home-hero p { max-width:620px; margin:0; color:#d7edf6; font-size:1.02rem; line-height:1.7; }
.section-kicker { margin-top:2.1rem; color:#006aa8; font-size:.72rem; font-weight:800; letter-spacing:.16em; }
.section-title { margin:.2rem 0 .3rem; color:var(--navy-900); font-size:clamp(1.5rem, 3vw, 2.2rem); font-weight:800; letter-spacing:-.035em; }
.section-copy { color:var(--muted); font-size:.9rem; margin-bottom:1rem; }

.calc-card {
  min-height: 230px; padding:1.35rem; border:1px solid var(--line);
  border-top:4px solid var(--blue-600); background:rgba(255,255,255,.96);
  box-shadow:0 14px 35px rgba(10,43,68,.08);
}
.calc-card.pending { border-top-color:#a9b7c2; background:rgba(247,249,250,.94); }
.calc-index { color:var(--blue-600); font-size:.72rem; font-weight:800; letter-spacing:.14em; }
.calc-card.pending .calc-index { color:#8797a4; }
.calc-card h3 { margin:.7rem 0 .55rem; color:var(--navy-900); font-size:1.2rem; }
.calc-card p { min-height:65px; color:var(--muted); font-size:.84rem; line-height:1.65; }
.status-pill {
  display:inline-block; padding:.32rem .6rem; border-radius:999px;
  color:#00689c; background:#e3f5fc; font-size:.68rem; font-weight:800;
}
.status-pill.pending { color:#71808c; background:#e9eef1; }

.page-intro {
  position:relative; overflow:hidden; padding:1.55rem 1.7rem; margin:.35rem 0 1.1rem;
  background:linear-gradient(112deg, #06192b, #083a5e 72%, #007faf);
  border-left:5px solid #00aeef; color:white; box-shadow:0 14px 35px rgba(6,25,43,.14);
}
.page-intro:after {
  content:""; position:absolute; width:330px; height:330px; right:-180px; top:-210px;
  border:1px solid rgba(255,255,255,.25); border-radius:50%;
  box-shadow:0 0 0 46px rgba(255,255,255,.035), 0 0 0 92px rgba(255,255,255,.02);
}
.page-intro .eyebrow { color:#6dd9ff; }
.page-intro h1 { margin:.3rem 0; font-size:clamp(1.65rem, 3vw, 2.55rem); letter-spacing:-.04em; }
.page-intro p { margin:0; color:#cce4ee; font-size:.88rem; }
.panel-heading {
  margin:.2rem 0 .75rem; padding-bottom:.55rem; border-bottom:1px solid var(--line);
  color:var(--navy-900); font-size:.9rem; font-weight:800;
}
.panel-heading span { color:var(--blue-600); margin-right:.35rem; }
.formula-box {
  padding:1rem 1.1rem; border-left:4px solid var(--blue-500); background:#edf8fc;
  color:#29465d; font-size:.82rem; line-height:1.75;
}
.legal-note {
  margin-top:2rem; padding-top:.8rem; border-top:1px solid var(--line);
  color:#718392; font-size:.7rem; line-height:1.6;
}
div[data-testid="stVerticalBlockBorderWrapper"] {
  border-color:var(--line) !important; border-radius:4px !important;
  background:rgba(255,255,255,.94); box-shadow:0 10px 28px rgba(10,43,68,.055);
}
[data-testid="stMetric"] {
  min-height:118px; padding:1rem !important; border-top:3px solid var(--blue-600);
  background:linear-gradient(180deg,#fff,#f4f9fb);
}
[data-testid="stMetricLabel"] { color:#607487; }
[data-testid="stMetricValue"] { color:var(--navy-900); }
div[data-baseweb="radio"] { gap:.45rem; }
div[data-baseweb="radio"] label {
  padding:.5rem .7rem;
  border:1px solid var(--line);
  background:#fff;
  color:var(--ink) !important;
}
div[data-baseweb="radio"] label *,
[data-testid="stRadio"] label,
[data-testid="stRadio"] label * {
  color:var(--ink) !important;
  -webkit-text-fill-color:var(--ink) !important;
  opacity:1 !important;
}
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] span,
[data-testid="stTextInput"] label,
[data-testid="stTextInput"] label p,
[data-testid="stNumberInput"] label,
[data-testid="stNumberInput"] label p,
[data-testid="stSlider"] label,
[data-testid="stSlider"] label p,
[data-testid="stCheckbox"] label,
[data-testid="stCheckbox"] label p {
  color:#29465d !important;
  -webkit-text-fill-color:#29465d !important;
  opacity:1 !important;
}
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input {
  color:#ffffff !important;
  -webkit-text-fill-color:#ffffff !important;
  caret-color:#ffffff !important;
}
.stButton > button { border-radius:2px; min-height:42px; font-weight:750; }
.stButton > button[kind="primary"] { border-color:var(--blue-600); background:var(--blue-600); }
.stButton > button[kind="primary"]:hover { background:#006fa9; border-color:#006fa9; }
div[data-testid="stExpander"] { border-color:var(--line); border-radius:3px; background:#fff; }

@media (max-width: 720px) {
  [data-testid="stMainBlockContainer"] { padding: .55rem .8rem 2rem; }
  .site-header { align-items:flex-start; padding:.65rem .7rem; }
  .official-brand { gap:.5rem; }
  .official-brand img { width:154px; height:36px; }
  .official-link-label { display:none; }
  .tool-identity strong { font-size:.72rem; }
  .tool-identity span { display:none; }
  .home-hero { min-height:250px; padding:1.6rem 1.25rem; }
  .home-hero p { font-size:.87rem; }
  .calc-card { min-height:190px; }
  .page-intro { padding:1.25rem 1rem; }
}
</style>
"""


FLOW_DEFAULTS: dict[str, Any] = {
    "flow_mode": "이류체 노즐 (L/H + Air)",
    "product_name": "표준 이류체 노즐 - B201",
    "target_liquid_input": 2.2,
    "target_liquid_slider": 2.2,
    "target_air_input": 1.0,
    "target_air_slider": 1.0,
    "point_1_active": True,
    "point_1_liquid_pressure": 1.0,
    "point_1_air_pressure": 0.5,
    "point_1_liquid_flow": 3.0,
    "point_1_air_flow": 25.0,
    "point_2_active": True,
    "point_2_liquid_pressure": 2.0,
    "point_2_air_pressure": 1.0,
    "point_2_liquid_flow": 4.0,
    "point_2_air_flow": 35.0,
    "point_3_active": True,
    "point_3_liquid_pressure": 3.0,
    "point_3_air_pressure": 1.5,
    "point_3_liquid_flow": 5.0,
    "point_3_air_flow": 45.0,
}


def initialize_state() -> None:
    st.session_state.setdefault("page", "home")
    for key, value in FLOW_DEFAULTS.items():
        st.session_state.setdefault(key, value)


def reset_flow_state() -> None:
    for key, value in FLOW_DEFAULTS.items():
        st.session_state[key] = value


def navigate(page: str) -> None:
    st.session_state.page = page


def synchronize(source: str, target: str) -> None:
    st.session_state[target] = float(st.session_state[source])


def render_site_header() -> None:
    st.markdown(
        f"""
        <div class="site-header">
          <a class="official-brand" href="{OFFICIAL_SITE_URL}" target="_blank" rel="noopener noreferrer">
            <img src="{OFFICIAL_LOGO_URL}" alt="Spraying Systems Co. 공식 로고"
                 onerror="this.style.display='none';this.nextElementSibling.style.display='inline-block';">
            <span class="logo-fallback">SPRAYING SYSTEMS CO.</span>
            <span class="official-link-label">스프레이시스템코리아 공식 홈페이지 ↗</span>
          </a>
          <div class="tool-identity">
            <strong>Spray Engineering Calculator</strong>
            <span>INDEPENDENT ENGINEERING TOOL</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_footer() -> None:
    st.markdown(
        """
        <div class="legal-note">
          본 계산기는 현장 검토를 돕기 위한 독립적인 계산 도구입니다. 실제 노즐 선정과 운전 조건은
          제조사 데이터시트 및 기술 담당자의 검토 결과를 우선 적용하십시오. Spraying Systems Co. 로고는
          사용자 요청에 따라 공식 홈페이지 연결 영역에 표시됩니다.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_home() -> None:
    render_site_header()
    st.markdown(
        """
        <section class="home-hero">
          <div class="hero-content">
            <div class="eyebrow">SPRAY ENGINEERING WORKSPACE</div>
            <h1>Spray Engineering<br>Calculator</h1>
            <p>현장 조건에 맞는 계산기를 선택하고 필요한 운전값을 빠르게 검토하세요.</p>
          </div>
        </section>
        <div class="section-kicker">SELECT A CALCULATOR</div>
        <div class="section-title">계산기 선택</div>
        <div class="section-copy">총 3개의 계산기를 순서대로 완성합니다. 현재는 첫 번째 계산기를 사용할 수 있습니다.</div>
        """,
        unsafe_allow_html=True,
    )

    columns = st.columns(3, gap="large")
    cards = [
        ("01 · AVAILABLE", "노즐 분사량 계산기", "일류체와 이류체 노즐의 데이터시트 기준점을 이용해 목표 압력에서의 액체 유량과 공기 소모량을 예측합니다.", False),
        ("02 · NEXT", "두 번째 계산기", "두 번째 계산식의 명칭과 입력 조건을 정한 뒤 다음 단계에서 추가합니다.", True),
        ("03 · PLANNED", "세 번째 계산기", "세 번째 계산식은 앞선 계산기를 완성한 다음 같은 화면 체계로 연결합니다.", True),
    ]
    for index, (column, card) in enumerate(zip(columns, cards, strict=True)):
        label, title, description, pending = card
        with column:
            pending_class = " pending" if pending else ""
            status = "제작 예정" if pending else "사용 가능"
            st.markdown(
                f"""<div class="calc-card{pending_class}"><div class="calc-index">{label}</div>
                <h3>{title}</h3><p>{description}</p><span class="status-pill{pending_class}">{status}</span></div>""",
                unsafe_allow_html=True,
            )
            if index == 0:
                st.button("노즐 분사량 계산기 열기  →", key="open_flow_calculator", type="primary",
                          width="stretch", on_click=navigate, args=("flow",))
            else:
                st.button("준비 중", key=f"pending_calculator_{index}", width="stretch", disabled=True)
    render_footer()


def single_fluid_calculation(target_pressure: float, reference_points: list[dict[str, float | bool]]) -> dict[str, Any]:
    point_results: list[dict[str, float | bool]] = []
    valid_k_values: list[float] = []
    for point in reference_points:
        active = bool(point["active"])
        pressure = float(point["liquid_pressure"])
        flow = float(point["liquid_flow"])
        k_value = flow / math.sqrt(pressure) if active and pressure > 0 and flow > 0 else 0.0
        if k_value > 0:
            valid_k_values.append(k_value)
        point_results.append({**point, "liquid_k": k_value, "air_k": 0.0})
    average_k = sum(valid_k_values) / len(valid_k_values) if valid_k_values else 0.0
    target_flow = average_k * math.sqrt(target_pressure) if target_pressure > 0 and average_k > 0 else 0.0
    return {"average_k": average_k, "average_air_k": 0.0, "target_liquid_flow": target_flow,
            "target_air_flow": 0.0, "valid_count": len(valid_k_values), "points": point_results}


def two_fluid_calculation(target_liquid_pressure: float, target_air_pressure: float,
                          reference_points: list[dict[str, float | bool]]) -> dict[str, Any]:
    point_results: list[dict[str, float | bool]] = []
    liquid_k_values: list[float] = []
    air_k_values: list[float] = []
    for point in reference_points:
        active = bool(point["active"])
        liquid_pressure = float(point["liquid_pressure"])
        air_pressure = float(point["air_pressure"])
        liquid_flow = float(point["liquid_flow"])
        air_flow = float(point["air_flow"])
        liquid_k = 0.0
        if active and liquid_pressure > 0 and liquid_flow > 0:
            factor = max(0.15, 1.0 - 0.25 * air_pressure / liquid_pressure)
            liquid_k = liquid_flow / (math.sqrt(liquid_pressure) * factor)
        air_k = air_flow / math.sqrt(air_pressure) if active and air_pressure > 0 and air_flow > 0 else 0.0
        if liquid_k > 0:
            liquid_k_values.append(liquid_k)
        if air_k > 0:
            air_k_values.append(air_k)
        point_results.append({**point, "liquid_k": liquid_k, "air_k": air_k})
    average_k = sum(liquid_k_values) / len(liquid_k_values) if liquid_k_values else 0.0
    average_air_k = sum(air_k_values) / len(air_k_values) if air_k_values else 0.0
    target_liquid_flow = 0.0
    if target_liquid_pressure > 0 and average_k > 0:
        factor = max(0.15, 1.0 - 0.25 * target_air_pressure / target_liquid_pressure)
        target_liquid_flow = average_k * math.sqrt(target_liquid_pressure) * factor
    target_air_flow = (average_air_k * math.sqrt(target_air_pressure)
                       if target_air_pressure > 0 and average_air_k > 0 else 0.0)
    return {"average_k": average_k, "average_air_k": average_air_k,
            "target_liquid_flow": target_liquid_flow, "target_air_flow": target_air_flow,
            "valid_count": len(liquid_k_values), "points": point_results}


def build_reference_points(mode: str) -> list[dict[str, float | bool]]:
    reference_points: list[dict[str, float | bool]] = []
    for number in range(1, 4):
        with st.container(border=True):
            title_column, active_column = st.columns([3, 1])
            with title_column:
                st.markdown(f"**기준점 {number} (P{number})**")
            with active_column:
                active = st.checkbox("사용", key=f"point_{number}_active")
            columns = st.columns(2)
            with columns[0]:
                liquid_pressure = st.number_input(
                    f"액체 압력 P{number} (bar)", 0.0, 100.0, step=0.1, format="%.3f",
                    key=f"point_{number}_liquid_pressure", disabled=not active)
            with columns[1]:
                liquid_unit = "LPM" if mode.startswith("일류체") else "L/H"
                liquid_flow = st.number_input(
                    f"액체 유량 Q{number} ({liquid_unit})", 0.0, 100000.0, step=0.1, format="%.3f",
                    key=f"point_{number}_liquid_flow", disabled=not active)
            air_pressure = float(st.session_state[f"point_{number}_air_pressure"])
            air_flow = float(st.session_state[f"point_{number}_air_flow"])
            if mode.startswith("이류체"):
                air_columns = st.columns(2)
                with air_columns[0]:
                    air_pressure = st.number_input(
                        f"공기 압력 Air{number} (bar)", 0.0, 100.0, step=0.1, format="%.3f",
                        key=f"point_{number}_air_pressure", disabled=not active)
                with air_columns[1]:
                    air_flow = st.number_input(
                        f"공기 유량 QA{number} (NL/min)", 0.0, 100000.0, step=0.1, format="%.3f",
                        key=f"point_{number}_air_flow", disabled=not active)
            reference_points.append({"active": active, "liquid_pressure": float(liquid_pressure),
                                     "air_pressure": float(air_pressure), "liquid_flow": float(liquid_flow),
                                     "air_flow": float(air_flow)})
    return reference_points


def build_chart_spec(mode: str, target_liquid_pressure: float, target_air_pressure: float,
                     result: dict[str, Any]) -> dict[str, Any]:
    points = [p for p in result["points"] if bool(p["active"]) and float(p["liquid_pressure"]) > 0
              and float(p["liquid_flow"]) > 0]
    max_reference_pressure = max((float(p["liquid_pressure"]) for p in points), default=0.0)
    max_pressure = max(5.0, target_liquid_pressure * 1.25, max_reference_pressure * 1.25)
    curve: list[dict[str, float]] = []
    for step in range(81):
        pressure = max_pressure * step / 80
        if mode.startswith("일류체"):
            flow = float(result["average_k"]) * math.sqrt(pressure)
        else:
            ratio = target_air_pressure / (pressure if pressure > 0 else 0.001)
            flow = float(result["average_k"]) * math.sqrt(pressure) * max(0.15, 1.0 - 0.25 * ratio)
        curve.append({"pressure": pressure, "flow": flow})
    references = [{"pressure": float(p["liquid_pressure"]), "flow": float(p["liquid_flow"]),
                   "label": f"P{i}"} for i, p in enumerate(result["points"], start=1)
                  if bool(p["active"]) and float(p["liquid_pressure"]) > 0 and float(p["liquid_flow"]) > 0]
    target = [{"pressure": target_liquid_pressure, "flow": float(result["target_liquid_flow"]), "label": "목표점"}]
    unit = "LPM" if mode.startswith("일류체") else "L/H"
    return {
        "height": 370, "background": "#ffffff",
        "config": {"view": {"stroke": "#d9e3ea"}, "axis": {"labelColor": "#587083",
                   "titleColor": "#18344a", "gridColor": "#dce7ed", "domainColor": "#9db1be"},
                   "font": "Noto Sans KR"},
        "layer": [
            {"data": {"values": curve}, "mark": {"type": "line", "color": "#0082c6", "strokeWidth": 3},
             "encoding": {"x": {"field": "pressure", "type": "quantitative", "title": "액체 압력 Pressure (bar)",
                                "scale": {"domain": [0, max_pressure]}},
                          "y": {"field": "flow", "type": "quantitative", "title": f"분사량 Flow Rate ({unit})",
                                "scale": {"zero": True}},
                          "tooltip": [{"field": "pressure", "type": "quantitative", "title": "압력 (bar)", "format": ".2f"},
                                      {"field": "flow", "type": "quantitative", "title": f"유량 ({unit})", "format": ".3f"}]}},
            {"data": {"values": references}, "mark": {"type": "point", "filled": True, "color": "#075f9b", "size": 95},
             "encoding": {"x": {"field": "pressure", "type": "quantitative"},
                          "y": {"field": "flow", "type": "quantitative"},
                          "tooltip": [{"field": "label", "type": "nominal", "title": "기준점"},
                                      {"field": "pressure", "type": "quantitative", "title": "압력 (bar)", "format": ".3f"},
                                      {"field": "flow", "type": "quantitative", "title": f"유량 ({unit})", "format": ".3f"}]}},
            {"data": {"values": target}, "mark": {"type": "rule", "color": "#0c9a75", "strokeDash": [5, 4]},
             "encoding": {"x": {"field": "pressure", "type": "quantitative"}}},
            {"data": {"values": target}, "mark": {"type": "point", "filled": True, "color": "#0c9a75", "size": 165},
             "encoding": {"x": {"field": "pressure", "type": "quantitative"},
                          "y": {"field": "flow", "type": "quantitative"},
                          "tooltip": [{"field": "label", "type": "nominal", "title": "구분"},
                                      {"field": "pressure", "type": "quantitative", "title": "목표 압력 (bar)", "format": ".3f"},
                                      {"field": "flow", "type": "quantitative", "title": f"예측 유량 ({unit})", "format": ".3f"}]}}
        ]}


def render_target_pressure_controls(mode: str) -> tuple[float, float]:
    st.markdown('<div class="panel-heading"><span>01</span> 목표 운전 조건</div>', unsafe_allow_html=True)
    number_column, slider_column = st.columns([1, 2.2])
    with number_column:
        liquid_pressure = st.number_input(
            "목표 액체 압력 (bar)", 0.1, 10.0, step=0.05, format="%.3f", key="target_liquid_input",
            on_change=synchronize, args=("target_liquid_input", "target_liquid_slider"))
    with slider_column:
        st.slider("액체 압력 빠른 조정", 0.1, 10.0, step=0.05, key="target_liquid_slider",
                  on_change=synchronize, args=("target_liquid_slider", "target_liquid_input"))
    air_pressure = float(st.session_state.target_air_input)
    if mode.startswith("이류체"):
        air_number, air_slider = st.columns([1, 2.2])
        with air_number:
            air_pressure = st.number_input(
                "목표 공기 압력 (bar)", 0.0, 10.0, step=0.05, format="%.3f", key="target_air_input",
                on_change=synchronize, args=("target_air_input", "target_air_slider"))
        with air_slider:
            st.slider("공기 압력 빠른 조정", 0.0, 10.0, step=0.05, key="target_air_slider",
                      on_change=synchronize, args=("target_air_slider", "target_air_input"))
    return float(liquid_pressure), float(air_pressure)


def render_flow_calculator() -> None:
    render_site_header()
    navigation_column, reset_column, _ = st.columns([1.2, 1, 4])
    with navigation_column:
        st.button("← 계산기 선택", key="back_to_home", width="stretch",
                  on_click=navigate, args=("home",))
    with reset_column:
        st.button("기본값 초기화", key="reset_flow", width="stretch", on_click=reset_flow_state)
    st.markdown(
        """<section class="page-intro"><div class="eyebrow">CALCULATOR 01 · NOZZLE FLOW RATE</div>
        <h1>노즐 분사량 계산기</h1><p>데이터시트 기준점을 바탕으로 목표 압력에서의 노즐 분사량을 예측합니다.</p></section>""",
        unsafe_allow_html=True)
    setup_column, product_column = st.columns([1.4, 1])
    with setup_column:
        mode = st.radio("노즐 형식", ("일류체 노즐 (LPM)", "이류체 노즐 (L/H + Air)"),
                        key="flow_mode", horizontal=True)
    with product_column:
        product_name = st.text_input("노즐 / 제품명", key="product_name",
                                     placeholder="노즐 규격 또는 제품명을 입력하세요")
    target_panel, result_panel = st.columns([1.05, 1.5], gap="large")
    with target_panel:
        with st.container(border=True):
            target_liquid_pressure, target_air_pressure = render_target_pressure_controls(mode)
    with result_panel:
        st.markdown('<div class="panel-heading"><span>02</span> 예측 결과</div>', unsafe_allow_html=True)
        result_placeholders = st.columns(3)
    input_panel, chart_panel = st.columns([1, 1.28], gap="large")
    with input_panel:
        st.markdown('<div class="panel-heading"><span>03</span> 데이터시트 기준점</div>', unsafe_allow_html=True)
        st.caption("사용할 기준점만 체크하세요. 유효한 K값의 평균으로 결과를 계산합니다.")
        reference_points = build_reference_points(mode)
    if mode.startswith("일류체"):
        result = single_fluid_calculation(target_liquid_pressure, reference_points)
        unit = "LPM"
    else:
        result = two_fluid_calculation(target_liquid_pressure, target_air_pressure, reference_points)
        unit = "L/H"
    with result_panel:
        with result_placeholders[0]:
            st.metric("예측 액체 분사량", f"{result['target_liquid_flow']:.3f} {unit}")
        with result_placeholders[1]:
            if mode.startswith("이류체"):
                st.metric("예측 공기 소모량", f"{result['target_air_flow']:.3f} NL/min")
            else:
                st.metric("활성 기준점", f"{result['valid_count']} 개")
        with result_placeholders[2]:
            st.metric("평균 유량 계수 K", f"{result['average_k']:.3f}")
        if result["valid_count"] == 0:
            st.warning("계산할 수 있는 기준점이 없습니다. 압력과 유량이 0보다 큰 기준점을 하나 이상 사용하세요.")
        else:
            st.success(f"{product_name or '노즐/제품'} · 유효 기준점 {result['valid_count']}개 평균 적용")
    with input_panel:
        st.markdown("**기준점별 계산 계수**")
        coefficient_columns = st.columns(3)
        for index, (column, point) in enumerate(zip(coefficient_columns, result["points"], strict=True), start=1):
            with column:
                st.metric(f"P{index} · K", f"{float(point['liquid_k']):.3f}" if bool(point["active"]) else "비활성")
    with chart_panel:
        st.markdown('<div class="panel-heading"><span>04</span> 압력－유량 특성 곡선</div>', unsafe_allow_html=True)
        st.vega_lite_chart(spec=build_chart_spec(mode, target_liquid_pressure, target_air_pressure, result),
                           width="stretch")
        if mode.startswith("일류체"):
            st.caption("파란색 곡선은 평균 K값으로 계산한 Q = K·√P 특성입니다. 초록색 점은 목표 운전점입니다.")
        else:
            st.caption("파란색 곡선은 설정한 공기 압력에서의 액체 유량 특성입니다. 초록색 점은 목표 운전점입니다.")
    with st.expander("계산 방식 확인", expanded=False):
        if mode.startswith("일류체"):
            st.markdown("""<div class="formula-box"><strong>일류체 노즐</strong><br>
            ① 기준점 계수: Kᵢ = Qᵢ ÷ √Pᵢ<br>② 평균 계수: K̄ = 유효한 Kᵢ의 산술평균<br>
            ③ 목표 유량: Qₜ = K̄ × √Pₜ<br>압력 단위는 bar, 결과 유량 단위는 LPM입니다.</div>""",
                        unsafe_allow_html=True)
        else:
            st.markdown("""<div class="formula-box"><strong>이류체 노즐</strong><br>
            ① 역압 보정: F = max(0.15, 1 − 0.25 × P<sub>A</sub> ÷ P<sub>L</sub>)<br>
            ② 액체 계수: K<sub>L</sub> = Q<sub>L</sub> ÷ (√P<sub>L</sub> × F)<br>
            ③ 목표 액체 유량: Q<sub>L,t</sub> = K̄<sub>L</sub> × √P<sub>L,t</sub> × F<sub>t</sub><br>
            ④ 공기 계수: K<sub>A</sub> = Q<sub>A</sub> ÷ √P<sub>A</sub><br>
            ⑤ 목표 공기 유량: Q<sub>A,t</sub> = K̄<sub>A</sub> × √P<sub>A,t</sub><br>
            결과 단위는 액체 L/H, 공기 NL/min입니다.</div>""", unsafe_allow_html=True)
        st.caption("첨부 HTML의 계산 모델을 그대로 적용했습니다. 실제 제품 선정 시 제조사 성능표를 우선 확인하세요.")
    render_footer()


def main() -> None:
    st.markdown(APP_CSS, unsafe_allow_html=True)
    initialize_state()
    render_flow_calculator() if st.session_state.page == "flow" else render_home()


if __name__ == "__main__":
    main()
