"""Spray Engineering Calculator - Streamlit deployment entry point.

The engineering equations in the system-analysis page preserve the constants,
defaults, and calculation order from the user-provided HTML calculator.
"""

from __future__ import annotations

import html
import math
from datetime import datetime
from io import BytesIO
from typing import Any

import streamlit as st


st.set_page_config(
    page_title="Spray Engineering Calculator",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="auto",
)


PATTERNS: dict[str, dict[str, float | str]] = {
    "표준 부채꼴 (Standard Flat Fan)": {
        "coefficient": 0.024,
        "peak_factor": 1.45,
        "short": "FLAT FAN",
    },
    "솔리드 스트림 (Solid Stream)": {
        "coefficient": 0.026,
        "peak_factor": 1.00,
        "short": "SOLID STREAM",
    },
    "풀콘 / 원추형 (Full Cone)": {
        "coefficient": 0.018,
        "peak_factor": 1.25,
        "short": "FULL CONE",
    },
}

PIPE_INNER_DIAMETERS_MM: dict[int, float] = {
    15: 16.1,
    20: 21.6,
    25: 27.6,
    32: 35.7,
    40: 41.6,
    50: 52.9,
    65: 67.9,
    80: 80.7,
}


APP_CSS = r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800&display=swap');

:root {
  --navy-950: #041a2f;
  --navy-900: #062848;
  --navy-800: #0b3a63;
  --blue-600: #087cc1;
  --blue-500: #13a2e3;
  --blue-100: #dff3fd;
  --slate-900: #122033;
  --slate-600: #53667b;
  --slate-300: #cad6e2;
  --surface: #ffffff;
  --canvas: #f3f7fb;
  --success: #139b7a;
  --warning: #ed9c20;
  --danger: #dc5363;
}

html, body, [class*="css"], [data-testid="stAppViewContainer"] {
  font-family: "Noto Sans KR", "Segoe UI", sans-serif;
}

[data-testid="stAppViewContainer"] {
  background:
    radial-gradient(circle at 88% 4%, rgba(19,162,227,.08), transparent 22rem),
    var(--canvas);
  color: var(--slate-900);
}

[data-testid="stHeader"] { background: transparent; }
[data-testid="stMainBlockContainer"] {
  max-width: 1380px;
  padding-top: 1.25rem;
  padding-bottom: 3.5rem;
}

[data-testid="stSidebar"] {
  background: linear-gradient(175deg, #041a2f 0%, #062b4b 60%, #07416a 100%);
  border-right: 1px solid rgba(255,255,255,.08);
}
[data-testid="stSidebar"] * { color: #eaf6fc; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: #c5d9e8; }
[data-testid="stSidebar"] div[role="radiogroup"] label {
  border: 1px solid rgba(255,255,255,.10);
  border-radius: 10px;
  padding: .55rem .7rem;
  margin-bottom: .3rem;
  transition: .15s ease;
}
[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
  background: rgba(19,162,227,.13);
  border-color: rgba(83,190,237,.35);
}
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,.12); }

.brand-shell {
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.4rem;
  padding: 1.3rem 1.55rem;
  margin: 0 0 1.15rem 0;
  border-radius: 16px;
  background: linear-gradient(118deg, #041a2f 0%, #06365d 62%, #087cc1 100%);
  box-shadow: 0 14px 34px rgba(4,31,56,.16);
}
.brand-shell:after {
  content: "";
  position: absolute;
  width: 320px;
  height: 320px;
  right: -170px;
  top: -210px;
  border: 1px solid rgba(255,255,255,.22);
  border-radius: 50%;
  box-shadow: 0 0 0 45px rgba(255,255,255,.035), 0 0 0 90px rgba(255,255,255,.025);
}
.brand-left { display: flex; align-items: center; gap: 1rem; z-index: 1; }
.brand-mark {
  display: grid;
  place-items: center;
  width: 52px;
  height: 52px;
  flex: 0 0 52px;
  border-radius: 13px 13px 20px 13px;
  background: linear-gradient(145deg, #31c1ef, #087cc1);
  color: white;
  font-weight: 900;
  font-size: 1.08rem;
  letter-spacing: -.07em;
  border: 1px solid rgba(255,255,255,.38);
  box-shadow: inset 0 1px 0 rgba(255,255,255,.28), 0 7px 16px rgba(0,0,0,.18);
}
.brand-kicker { color: #69cff4; font-size: .68rem; font-weight: 800; letter-spacing: .16em; }
.brand-title { color: #fff; font-size: clamp(1.18rem, 2.2vw, 1.75rem); font-weight: 800; letter-spacing: -.035em; }
.brand-sub { color: #c2ddec; font-size: .82rem; margin-top: .18rem; }
.brand-badge {
  z-index: 1;
  color: #dff4fd;
  background: rgba(2,19,34,.32);
  border: 1px solid rgba(157,220,246,.24);
  border-radius: 999px;
  padding: .48rem .75rem;
  font-size: .72rem;
  white-space: nowrap;
}
.official-logo-link {
  z-index: 2;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-width: 214px;
  padding: .5rem .75rem .58rem;
  border-radius: 11px;
  background: #ffffff;
  border: 1px solid rgba(255,255,255,.52);
  box-shadow: 0 8px 20px rgba(1,20,36,.2);
  text-decoration: none !important;
  transition: transform .16s ease, box-shadow .16s ease;
}
.official-logo-link:hover {
  transform: translateY(-1px);
  box-shadow: 0 11px 24px rgba(1,20,36,.26);
}
.official-logo-link span {
  color: #64788a;
  font-size: .52rem;
  font-weight: 800;
  letter-spacing: .12em;
  margin-bottom: .27rem;
}
.official-logo-link img {
  display: block;
  width: 184px;
  max-width: 100%;
  height: auto;
}

.sidebar-brand { padding: .55rem .25rem 1rem; }
.sidebar-brand .mini-mark {
  width: 36px; height: 36px; display: inline-grid; place-items: center;
  background: #12a4e3; color: #fff; border-radius: 9px 9px 14px 9px;
  font-weight: 900; margin-right: .45rem;
}
.sidebar-brand strong { color: #fff; font-size: .98rem; }
.sidebar-note {
  margin-top: 1rem; padding: .75rem; border-radius: 10px;
  background: rgba(0,0,0,.14); border: 1px solid rgba(255,255,255,.09);
  color: #aec7d9; font-size: .7rem; line-height: 1.65;
}

.section-kicker {
  color: var(--blue-600); font-size: .68rem; font-weight: 800;
  letter-spacing: .13em; margin-bottom: .2rem;
}
.section-title {
  color: var(--navy-950); font-size: 1.25rem; font-weight: 800;
  letter-spacing: -.025em; margin-bottom: .25rem;
}
.section-copy { color: var(--slate-600); font-size: .82rem; line-height: 1.65; margin-bottom: .8rem; }
.hairline { height: 1px; background: #d7e2ec; margin: 1.45rem 0; }

div[data-testid="stVerticalBlockBorderWrapper"] {
  background: rgba(255,255,255,.94);
  border-color: #d6e2ec;
  border-radius: 14px;
  box-shadow: 0 8px 22px rgba(15,44,71,.055);
}
div[data-testid="stNumberInput"] input,
div[data-testid="stTextInput"] input,
div[data-baseweb="select"] > div {
  border-color: #cbd9e5 !important;
  background: #fbfdff !important;
}
div[data-testid="stNumberInput"] input:focus,
div[data-testid="stTextInput"] input:focus {
  border-color: var(--blue-500) !important;
  box-shadow: 0 0 0 2px rgba(19,162,227,.12) !important;
}

.hero-result {
  position: relative; overflow: hidden;
  padding: 1.35rem 1.45rem 1.15rem;
  border-radius: 16px;
  background: linear-gradient(128deg, #041b31, #07395f 68%, #086fa9);
  color: #fff;
  box-shadow: 0 12px 27px rgba(5,42,72,.16);
}
.hero-result:before {
  content:""; position:absolute; right:-30px; bottom:-65px;
  width:190px; height:190px; border-radius:50%;
  border:28px solid rgba(49,193,239,.10);
}
.hero-label { position:relative; color:#9bdcf4; font-size:.72rem; font-weight:700; letter-spacing:.08em; }
.hero-value { position:relative; font-size:clamp(2.05rem,4vw,3.25rem); font-weight:800; letter-spacing:-.06em; line-height:1.12; margin:.35rem 0 .15rem; }
.hero-value small { font-size:.9rem; letter-spacing:0; color:#d6eaf5; margin-left:.2rem; }
.hero-sub { position:relative; color:#bdd6e5; font-size:.78rem; }
.gauge-labels { display:flex; justify-content:space-between; color:#9eb8ca; font-size:.61rem; margin-top:1rem; }
.gauge-track { height:6px; border-radius:99px; margin-top:.35rem; background:rgba(255,255,255,.14); overflow:hidden; }
.gauge-fill { height:100%; border-radius:99px; background:linear-gradient(90deg,#24bfad,#35c5e8 55%,#f1aa36 78%,#e85e6b); }

.metric-grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:.7rem; margin-top:.75rem; }
.metric-grid.three { grid-template-columns:repeat(3,minmax(0,1fr)); }
.metric-grid.spray-metrics { grid-template-columns:repeat(2,minmax(0,1fr)); }
.metric-card {
  min-height:106px; padding:.9rem 1rem; background:#fff; border:1px solid #d7e3ed;
  border-radius:12px; box-shadow:0 5px 15px rgba(10,49,78,.04);
}
.metric-label { color:#60758a; font-size:.66rem; font-weight:600; min-height:2.15em; line-height:1.35; }
.metric-value { color:#092a47; font-size:1.32rem; font-weight:800; letter-spacing:-.04em; margin-top:.4rem; }
.metric-value small { display:inline-block; white-space:nowrap; font-size:.65rem; font-weight:600; color:#71869a; letter-spacing:0; margin-left:.16rem; }
.metric-meta { color:#7a8da0; font-size:.63rem; margin-top:.16rem; }

.diagram-card {
  margin-top:.75rem; background:linear-gradient(180deg,#fafdff,#eef6fb);
  border:1px solid #d6e4ee; border-radius:14px; padding:.45rem .8rem .25rem;
}
.diagram-caption { display:flex; justify-content:space-between; gap:.6rem; color:#60758a; font-size:.65rem; padding:.2rem .15rem .45rem; }
.status-strip {
  display:flex; align-items:center; justify-content:space-between; gap:1rem;
  background:#eaf7f4; border:1px solid #bfe5db; border-radius:11px; padding:.75rem .9rem;
  color:#176f5b; font-size:.75rem; margin-top:.75rem;
}
.status-strip.warning { background:#fff7e8; border-color:#f2d396; color:#8a5b0d; }
.status-strip.danger { background:#fff0f2; border-color:#efc0c7; color:#9d3040; }
.status-strip strong { font-size:.82rem; }

.flow-hero {
  padding:1.2rem; border-radius:14px; color:#fff;
  background:linear-gradient(130deg,#06345a,#087dbd);
}
.flow-hero .eyebrow { color:#9edcf4; font-size:.7rem; font-weight:700; }
.flow-hero .big { font-size:2.45rem; line-height:1.12; font-weight:800; letter-spacing:-.05em; margin:.35rem 0; }
.flow-hero .big span { font-size:.85rem; letter-spacing:0; color:#d5eaf5; }
.flow-hero .sub { color:#c1dcea; font-size:.75rem; }

.feature-grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:.85rem; }
.feature-card { background:#fff; border:1px solid #d9e4ed; border-radius:13px; padding:1.1rem; }
.feature-no { color:#129dd8; font-size:.64rem; font-weight:800; letter-spacing:.1em; }
.feature-title { color:#082b49; font-size:.94rem; font-weight:800; margin:.25rem 0; }
.feature-copy { color:#667b8e; font-size:.72rem; line-height:1.55; }

.formula-box {
  padding:.9rem 1rem; border-left:3px solid #12a4e3; background:#eef7fc;
  border-radius:0 10px 10px 0; color:#36566f; font-size:.76rem; line-height:1.7;
}
.formula-box code { color:#065d91; background:#dceff9; padding:.12rem .3rem; border-radius:4px; }
.independent-note {
  background:#f7fafc; border:1px solid #dce5ec; border-radius:10px;
  padding:.72rem .85rem; color:#627486; font-size:.68rem; line-height:1.6;
}

div.stDownloadButton > button, div.stButton > button {
  min-height:2.7rem; border-radius:9px; font-weight:700;
  border:1px solid #087cc1; color:#fff; background:linear-gradient(135deg,#087cc1,#07558a);
}
div.stDownloadButton > button:hover, div.stButton > button:hover {
  color:#fff; border-color:#065d91; box-shadow:0 7px 16px rgba(8,124,193,.18);
}

@media (max-width: 1300px) { .brand-badge { display:none; } }
@media (max-width: 900px) {
  .metric-grid, .metric-grid.three, .feature-grid { grid-template-columns:repeat(2,minmax(0,1fr)); }
  .official-logo-link { min-width: 180px; }
  .official-logo-link img { width: 154px; }
}
@media (max-width: 620px) {
  [data-testid="stMainBlockContainer"] { padding-left:.8rem; padding-right:.8rem; }
  .brand-shell { padding:1rem; flex-direction:column; align-items:stretch; }
  .brand-mark { width:44px; height:44px; flex-basis:44px; }
  .brand-sub { display:none; }
  .official-logo-link { width:100%; min-width:0; padding:.45rem .65rem .5rem; }
  .official-logo-link img { width:164px; }
  .metric-grid, .metric-grid.three, .feature-grid { grid-template-columns:1fr 1fr; gap:.5rem; }
  .metric-card { min-height:96px; padding:.75rem; }
  .metric-value { font-size:1.12rem; }
  .diagram-caption, .status-strip { align-items:flex-start; flex-direction:column; }
}
</style>
"""


def calculate_nozzle_flow(
    nozzle_count: int,
    single_flow_g_min: float,
    duty_cycle: float = 1.0,
    operating_hours: float = 1.0,
    tank_mass_kg: float = 20.0,
) -> dict[str, float]:
    """Calculate the original mass-flow calculator values."""
    duty = min(max(duty_cycle, 0.0), 1.0)
    continuous_g_min = max(nozzle_count, 0) * max(single_flow_g_min, 0.0)
    effective_g_min = continuous_g_min * duty
    kg_h = effective_g_min * 60.0 / 1000.0
    period_kg = kg_h * max(operating_hours, 0.0)
    tank_hours = tank_mass_kg / kg_h if kg_h > 0 else math.inf
    return {
        "continuous_g_min": continuous_g_min,
        "effective_g_min": effective_g_min,
        "kg_h": kg_h,
        "period_kg": period_kg,
        "tank_hours": tank_hours,
        "duty_percent": duty * 100.0,
    }


def calculate_system(
    *,
    pattern_name: str,
    pressure_bar: float,
    flow_l_min: float,
    spray_angle_deg: float,
    spray_distance_mm: float,
    nozzle_qty: int,
    pipe_size_a: int,
    pipe_length_m: float,
    elbow_qty: int,
    vertical_height_m: float,
    filter_loss_bar: float,
) -> dict[str, float | str]:
    """Preserve the supplied HTML calculator's equations and constants."""
    pattern = PATTERNS[pattern_name]
    coefficient = float(pattern["coefficient"])
    peak_factor = float(pattern["peak_factor"])

    p = max(float(pressure_bar), 0.0)
    q = max(float(flow_l_min), 0.0)
    theta = max(float(spray_angle_deg), 0.0)
    distance = max(float(spray_distance_mm), 0.0)

    total_impact_kgf = coefficient * q * math.sqrt(p)
    total_impact_n = total_impact_kgf * 9.80665

    width_mm = 0.0
    if distance > 0 and theta > 0:
        width_mm = 2.0 * distance * math.tan(math.radians(theta) / 2.0)
    elif distance > 0 and theta == 0:
        width_mm = 5.0

    width_cm = width_mm / 10.0
    average_linear_kgf_cm = total_impact_kgf / width_cm if width_cm > 0 else total_impact_kgf
    peak_linear_kgf_cm = average_linear_kgf_cm * peak_factor
    peak_linear_gf_cm = peak_linear_kgf_cm * 1000.0
    jet_velocity_m_s = math.sqrt((2.0 * p * 100_000.0) / 1000.0)

    total_design_flow_l_min = q * max(int(nozzle_qty), 1) * 1.08
    total_flow_m3_s = total_design_flow_l_min / (1000.0 * 60.0)
    diameter_mm = PIPE_INNER_DIAMETERS_MM[int(pipe_size_a)]
    diameter_m = diameter_mm / 1000.0
    pipe_area_m2 = math.pi * (diameter_m / 2.0) ** 2
    pipe_velocity_m_s = total_flow_m3_s / pipe_area_m2

    elbow_equivalent_length_m = max(int(elbow_qty), 0) * (30.0 * diameter_m)
    total_equivalent_length_m = max(float(pipe_length_m), 0.0) + elbow_equivalent_length_m
    hazen_c = 130.0
    head_loss_m = (
        10.67
        * total_flow_m3_s**1.852
        * total_equivalent_length_m
        / (hazen_c**1.852 * diameter_m**4.87)
    )
    friction_loss_bar = head_loss_m * 0.0980665
    height_loss_bar = max(float(vertical_height_m), 0.0) * 0.0980665
    total_pressure_loss_bar = max(
        0.1,
        friction_loss_bar + height_loss_bar + max(float(filter_loss_bar), 0.0),
    )

    total_required_pressure_bar = p + total_pressure_loss_bar
    hydraulic_power_kw = total_required_pressure_bar * total_design_flow_l_min / 600.0
    motor_power_kw = (hydraulic_power_kw / 0.60) * 1.15
    motor_power_hp = motor_power_kw / 0.7457

    if pipe_velocity_m_s < 1.5:
        velocity_status, velocity_tone = "권장보다 낮음", "warning"
    elif pipe_velocity_m_s <= 2.5:
        velocity_status, velocity_tone = "권장 범위", "ok"
    else:
        velocity_status, velocity_tone = "권장보다 높음", "danger"

    if peak_linear_kgf_cm < 0.02:
        impact_status = "저타력 · 린스 영역"
    elif peak_linear_kgf_cm < 0.05:
        impact_status = "중타력 · 일반 세정 영역"
    else:
        impact_status = "고타력 · 강력 세척 영역"

    return {
        "coefficient": coefficient,
        "peak_factor": peak_factor,
        "total_impact_kgf": total_impact_kgf,
        "total_impact_n": total_impact_n,
        "width_mm": width_mm,
        "average_linear_kgf_cm": average_linear_kgf_cm,
        "peak_linear_kgf_cm": peak_linear_kgf_cm,
        "peak_linear_gf_cm": peak_linear_gf_cm,
        "jet_velocity_m_s": jet_velocity_m_s,
        "total_design_flow_l_min": total_design_flow_l_min,
        "diameter_mm": diameter_mm,
        "pipe_velocity_m_s": pipe_velocity_m_s,
        "elbow_equivalent_length_m": elbow_equivalent_length_m,
        "total_equivalent_length_m": total_equivalent_length_m,
        "head_loss_m": head_loss_m,
        "friction_loss_bar": friction_loss_bar,
        "height_loss_bar": height_loss_bar,
        "filter_loss_bar": max(float(filter_loss_bar), 0.0),
        "total_pressure_loss_bar": total_pressure_loss_bar,
        "total_required_pressure_bar": total_required_pressure_bar,
        "hydraulic_power_kw": hydraulic_power_kw,
        "motor_power_kw": motor_power_kw,
        "motor_power_hp": motor_power_hp,
        "velocity_status": velocity_status,
        "velocity_tone": velocity_tone,
        "impact_status": impact_status,
    }


def section_heading(kicker: str, title: str, copy: str = "") -> None:
    copy_html = f'<div class="section-copy">{html.escape(copy)}</div>' if copy else ""
    st.markdown(
        f'<div class="section-kicker">{html.escape(kicker)}</div>'
        f'<div class="section-title">{html.escape(title)}</div>{copy_html}',
        unsafe_allow_html=True,
    )


def render_header(page_label: str, page_copy: str) -> None:
    st.markdown(
        f"""
        <div class="brand-shell">
          <div class="brand-left">
            <div class="brand-mark">FC</div>
            <div>
              <div class="brand-kicker">FLOWCORE · ENGINEERING TOOLS</div>
              <div class="brand-title">Spray Engineering Calculator</div>
              <div class="brand-sub">{html.escape(page_label)} · {html.escape(page_copy)}</div>
            </div>
          </div>
          <a class="official-logo-link" href="https://www.spray.com/ko-kr" target="_blank" rel="noopener noreferrer"
             title="스프레이시스템코리아 공식 홈페이지 열기">
            <span>SPRAYING SYSTEMS KOREA · OFFICIAL SITE</span>
            <img src="https://www.spray.com/ko-kr/-/media/spray/images/logo-spray-color-global.svg?iar=0&amp;mh=150&amp;hash=53D0DD1949C24C5AAAE0CBC733354240"
                 alt="Spraying Systems Co. 공식 로고">
          </a>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, unit: str = "", meta: str = "") -> str:
    return (
        '<div class="metric-card">'
        f'<div class="metric-label">{html.escape(label)}</div>'
        f'<div class="metric-value">{html.escape(value)}'
        f'<small>{html.escape(unit)}</small></div>'
        f'<div class="metric-meta">{html.escape(meta)}</div>'
        "</div>"
    )


def spray_diagram_svg(angle_deg: float, distance_mm: float, width_mm: float, pattern_short: str) -> str:
    """Return a small, responsive, original spray visualization."""
    spread = 8.0 if angle_deg <= 0 or distance_mm <= 0 else min(154.0, max(16.0, angle_deg / 120.0 * 154.0))
    left = 210.0 - spread
    right = 210.0 + spread
    target_y = 168.0
    return f"""
    <div class="diagram-card">
      <svg viewBox="0 0 420 190" width="100%" role="img" aria-label="분사 커버리지 개념도">
        <defs>
          <linearGradient id="sprayFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#13a2e3" stop-opacity=".82"/>
            <stop offset="76%" stop-color="#50c3ed" stop-opacity=".22"/>
            <stop offset="100%" stop-color="#e65d6a" stop-opacity=".12"/>
          </linearGradient>
          <linearGradient id="impactLine" x1="0" x2="1">
            <stop offset="0" stop-color="#13a2e3"/><stop offset=".5" stop-color="#e65d6a"/><stop offset="1" stop-color="#13a2e3"/>
          </linearGradient>
        </defs>
        <rect width="420" height="190" rx="11" fill="#f8fcff"/>
        <g opacity=".55" stroke="#dce9f2" stroke-width="1">
          <path d="M28 44H392M28 82H392M28 120H392"/>
          <path d="M80 22V168M145 22V168M275 22V168M340 22V168"/>
        </g>
        <path d="M210 32 L{left:.1f} {target_y:.1f} L{right:.1f} {target_y:.1f} Z" fill="url(#sprayFill)" stroke="#159cd5" stroke-opacity=".56"/>
        <path d="M194 17h32v13l-7 7h-18l-7-7z" fill="#082e50"/>
        <rect x="204" y="35" width="12" height="7" rx="2" fill="#13a2e3"/>
        <line x1="24" y1="168" x2="396" y2="168" stroke="#61788c" stroke-width="2"/>
        <line x1="{left:.1f}" y1="168" x2="{right:.1f}" y2="168" stroke="url(#impactLine)" stroke-width="5" stroke-linecap="round"/>
        <line x1="210" y1="50" x2="210" y2="156" stroke="#6c8396" stroke-dasharray="4 4"/>
        <text x="218" y="105" fill="#516a7e" font-size="10">H = {distance_mm:.0f} mm</text>
        <text x="210" y="184" text-anchor="middle" fill="#3f5d73" font-size="10">W = {width_mm:.1f} mm · CENTER PEAK</text>
      </svg>
      <div class="diagram-caption"><span>{html.escape(pattern_short)} · θ {angle_deg:.0f}°</span><span>개념 시각화 · 실제 액적 분포/공기 저항 미반영</span></div>
    </div>
    """


def safe_project_value(value: str, fallback: str = "-") -> str:
    cleaned = " ".join(value.strip().split())
    return cleaned or fallback


def build_pdf_report(
    project: dict[str, str],
    inputs: dict[str, Any],
    result: dict[str, float | str],
) -> bytes:
    """Generate a compact Korean-capable engineering report in memory."""
    from reportlab.lib.colors import HexColor
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont
    from reportlab.pdfgen import canvas

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    page_w, page_h = A4
    font_name = "HYSMyeongJo-Medium"
    try:
        pdfmetrics.registerFont(UnicodeCIDFont(font_name))
    except Exception:
        font_name = "Helvetica"

    navy = HexColor("#062848")
    blue = HexColor("#087CC1")
    pale = HexColor("#EAF5FB")
    line = HexColor("#D4E1EA")
    text = HexColor("#203246")
    muted = HexColor("#63788C")

    def title_bar(title: str, y: float) -> float:
        pdf.setFillColor(pale)
        pdf.roundRect(40, y - 23, page_w - 80, 26, 5, stroke=0, fill=1)
        pdf.setFillColor(navy)
        pdf.setFont(font_name, 11)
        pdf.drawString(50, y - 15, title)
        return y - 34

    def row(label: str, value: str, y: float, shaded: bool = False) -> float:
        if shaded:
            pdf.setFillColor(HexColor("#F7FAFC"))
            pdf.rect(40, y - 20, page_w - 80, 22, stroke=0, fill=1)
        pdf.setStrokeColor(line)
        pdf.line(40, y - 20, page_w - 40, y - 20)
        pdf.setFillColor(muted)
        pdf.setFont(font_name, 8.7)
        pdf.drawString(50, y - 14, label)
        pdf.setFillColor(text)
        pdf.setFont(font_name, 9.2)
        pdf.drawRightString(page_w - 50, y - 14, value)
        return y - 22

    pdf.setFillColor(navy)
    pdf.rect(0, page_h - 112, page_w, 112, stroke=0, fill=1)
    pdf.setFillColor(HexColor("#51C5EE"))
    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawString(40, page_h - 33, "FLOWCORE · INDEPENDENT ENGINEERING TOOL")
    pdf.setFillColor(HexColor("#FFFFFF"))
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(40, page_h - 60, "SPRAY ENGINEERING REPORT")
    pdf.setFont(font_name, 9)
    pdf.drawString(40, page_h - 82, "노즐 충격력 / 커버리지 / 배관 손실 / 펌프 동력 이론 분석")
    pdf.setFillColor(HexColor("#B8D7E8"))
    pdf.setFont("Helvetica", 8)
    pdf.drawRightString(page_w - 40, page_h - 34, datetime.now().strftime("%Y-%m-%d %H:%M"))

    y = page_h - 132
    y = title_bar("프로젝트 정보", y)
    for idx, (label, value) in enumerate(
        [
            ("프로젝트", safe_project_value(project.get("project_name", ""))),
            ("고객 / 현장", safe_project_value(project.get("customer", ""))),
            ("작성자", safe_project_value(project.get("engineer", ""))),
        ]
    ):
        y = row(label, value, y, idx % 2 == 0)

    y -= 8
    y = title_bar("노즐 운전 조건", y)
    operating_rows = [
        ("분사 패턴", str(inputs["pattern_name"])),
        ("단일 노즐 압력 / 유량", f'{inputs["pressure_bar"]:.2f} bar  /  {inputs["flow_l_min"]:.2f} L/min'),
        ("분사 각도 / 거리", f'{inputs["spray_angle_deg"]:.1f} deg  /  {inputs["spray_distance_mm"]:.1f} mm'),
        ("노즐 수량", f'{inputs["nozzle_qty"]} EA'),
    ]
    for idx, item in enumerate(operating_rows):
        y = row(item[0], item[1], y, idx % 2 == 0)

    y -= 8
    y = title_bar("노즐 및 분사 분석 결과", y)
    spray_rows = [
        ("중심부 최대 피크 타력", f'{result["peak_linear_kgf_cm"]:.4f} kgf/cm  ({result["peak_linear_gf_cm"]:.1f} gf/cm)'),
        ("전체 충격력", f'{result["total_impact_kgf"]:.3f} kgf  ({result["total_impact_n"]:.2f} N)'),
        ("단위 폭당 평균 타력", f'{result["average_linear_kgf_cm"]:.4f} kgf/cm'),
        ("분사 커버리지 폭", f'{result["width_mm"]:.1f} mm'),
        ("이론 분사 유속", f'{result["jet_velocity_m_s"]:.1f} m/s'),
    ]
    for idx, item in enumerate(spray_rows):
        y = row(item[0], item[1], y, idx % 2 == 0)

    y -= 8
    y = title_bar("배관 및 펌프 분석 결과", y)
    pipe_rows = [
        ("배관 조건", f'{inputs["pipe_size_a"]}A / {inputs["pipe_length_m"]:.1f} m / 90 deg elbow {inputs["elbow_qty"]} EA'),
        ("총 설계 유량 (8% 여유 포함)", f'{result["total_design_flow_l_min"]:.1f} L/min'),
        ("배관 내 유속", f'{result["pipe_velocity_m_s"]:.2f} m/s  ({result["velocity_status"]})'),
        ("마찰 / 위치 / 필터 손실", f'{result["friction_loss_bar"]:.3f} / {result["height_loss_bar"]:.3f} / {result["filter_loss_bar"]:.3f} bar'),
        ("예측 총 손실 / 총 요구 압력", f'{result["total_pressure_loss_bar"]:.2f} / {result["total_required_pressure_bar"]:.2f} bar'),
        ("소요 펌프 모터 동력", f'{result["motor_power_kw"]:.2f} kW  ({result["motor_power_hp"]:.2f} HP)'),
    ]
    for idx, item in enumerate(pipe_rows):
        y = row(item[0], item[1], y, idx % 2 == 0)

    y -= 8
    pdf.setFillColor(blue)
    pdf.setFont(font_name, 8)
    pdf.drawString(40, y, "계산 기준")
    pdf.setFillColor(muted)
    pdf.setFont(font_name, 7.2)
    notes = [
        "총 타력: F = C x Q x sqrt(P) / 분사 폭: W = 2H x tan(theta/2)",
        "배관 손실: Hazen-Williams (C=130), 엘보 등가길이 30D, 총 유량 8% 설계 여유",
        "펌프 동력: P_h = P x Q / 600, 효율 60%, 모터 안전계수 1.15",
    ]
    for note in notes:
        y -= 12
        pdf.drawString(48, y, "- " + note)

    pdf.setStrokeColor(line)
    pdf.line(40, 42, page_w - 40, 42)
    pdf.setFillColor(muted)
    pdf.setFont(font_name, 6.7)
    pdf.drawString(40, 29, "본 문서는 기술 검토용 이론 계산 결과이며 실제 성능 보증서가 아닙니다.")
    pdf.drawString(40, 18, "현장 시험과 제조사 데이터를 함께 확인하십시오.")
    pdf.setFont("Helvetica", 6.7)
    pdf.drawRightString(page_w - 40, 29, "Generated by FlowCore Spray Engineering Calculator")
    pdf.drawRightString(page_w - 40, 18, "Page 1 / 1")
    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()


def build_printable_html(
    project: dict[str, str],
    inputs: dict[str, Any],
    result: dict[str, float | str],
) -> bytes:
    """Create a standalone print view that can be saved as PDF by the browser."""
    e = html.escape
    rows = [
        ("분사 패턴", str(inputs["pattern_name"])),
        ("압력 / 단일 노즐 유량", f'{inputs["pressure_bar"]:.2f} bar / {inputs["flow_l_min"]:.2f} L/min'),
        ("분사 각도 / 거리", f'{inputs["spray_angle_deg"]:.1f}° / {inputs["spray_distance_mm"]:.1f} mm'),
        ("중심부 최대 피크 타력", f'{result["peak_linear_kgf_cm"]:.4f} kgf/cm ({result["peak_linear_gf_cm"]:.1f} gf/cm)'),
        ("전체 충격력", f'{result["total_impact_kgf"]:.3f} kgf ({result["total_impact_n"]:.2f} N)'),
        ("분사 커버리지 / 이론 유속", f'{result["width_mm"]:.1f} mm / {result["jet_velocity_m_s"]:.1f} m/s'),
        ("배관 조건", f'{inputs["pipe_size_a"]}A, {inputs["pipe_length_m"]:.1f} m, 엘보 {inputs["elbow_qty"]}개'),
        ("총 설계 유량 / 배관 유속", f'{result["total_design_flow_l_min"]:.1f} L/min / {result["pipe_velocity_m_s"]:.2f} m/s'),
        ("총 손실 / 총 요구 압력", f'{result["total_pressure_loss_bar"]:.2f} bar / {result["total_required_pressure_bar"]:.2f} bar'),
        ("펌프 모터 동력", f'{result["motor_power_kw"]:.2f} kW ({result["motor_power_hp"]:.2f} HP)'),
    ]
    table = "".join(f"<tr><th>{e(label)}</th><td>{e(value)}</td></tr>" for label, value in rows)
    doc = f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>Spray Engineering Report</title>
    <style>
    @page{{size:A4;margin:16mm}}*{{box-sizing:border-box}}body{{font-family:'Noto Sans KR','Malgun Gothic',sans-serif;color:#183047;margin:0}}
    header{{background:#062848;color:#fff;padding:24px 28px;border-radius:8px}}.k{{color:#65cff3;font-size:11px;letter-spacing:1.4px}}
    h1{{font-size:24px;margin:5px 0}}header p{{color:#c8deea;margin:0;font-size:12px}}h2{{font-size:14px;color:#087cc1;border-bottom:2px solid #dce9f1;padding-bottom:7px;margin-top:22px}}
    .meta{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px}}.meta div{{background:#f2f7fa;padding:10px;border-radius:5px;font-size:11px}}
    table{{width:100%;border-collapse:collapse;font-size:11px}}th,td{{padding:9px;border-bottom:1px solid #dce5eb}}th{{width:42%;text-align:left;color:#62788a;background:#f7fafc}}td{{text-align:right;font-weight:600}}
    .note{{margin-top:18px;padding:11px;background:#f1f8fc;border-left:3px solid #12a4e3;font-size:10px;line-height:1.6}}footer{{margin-top:18px;font-size:9px;color:#708394}}
    .print{{position:fixed;right:18px;top:18px;border:0;border-radius:6px;background:#13a2e3;color:white;padding:10px 14px;font-weight:700;cursor:pointer}}@media print{{.print{{display:none}}}}
    </style></head><body><button class="print" onclick="window.print()">인쇄 / PDF 저장</button>
    <header><div class="k">FLOWCORE · INDEPENDENT ENGINEERING TOOL</div><h1>Spray Engineering Report</h1><p>노즐 충격력 · 커버리지 · 배관 손실 · 펌프 동력 이론 분석</p></header>
    <h2>프로젝트 정보</h2><div class="meta"><div><b>프로젝트</b><br>{e(safe_project_value(project.get('project_name','')))}</div><div><b>고객 / 현장</b><br>{e(safe_project_value(project.get('customer','')))}</div><div><b>작성자</b><br>{e(safe_project_value(project.get('engineer','')))}</div></div>
    <h2>계산 결과</h2><table>{table}</table><div class="note"><b>계산 기준</b><br>Hazen-Williams C=130 · 엘보 등가길이 30D · 설계유량 8% 여유 · 펌프효율 60% · 모터 안전계수 1.15</div>
    <footer>본 리포트는 기술 검토용 이론 계산 결과이며 실제 성능을 보증하지 않습니다. 현장 시험 및 노즐·펌프 제조사의 확정 데이터를 함께 확인하십시오.<br>Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}</footer></body></html>"""
    return doc.encode("utf-8")


def render_nozzle_flow_page() -> None:
    render_header("NOZZLE FLOW", "노즐 수량과 개별 토출량으로 총 사용량을 계산합니다")
    section_heading(
        "01 · ORIGINAL CALCULATOR",
        "노즐 유량 · 약액 사용량",
        "기존 계산기의 연속 분사 계산을 그대로 유지하고, 간헐 분사 듀티와 탱크 사용시간을 확장했습니다.",
    )

    input_col, result_col = st.columns([0.92, 1.08], gap="large")
    with input_col:
        with st.container(border=True):
            st.markdown("#### 운전 조건")
            a, b = st.columns(2)
            with a:
                nozzle_count = st.number_input("노즐 수량 (EA)", 1, 1000, 6, 1)
            with b:
                single_flow = st.number_input("노즐 1개 유량 (g/min)", 0.0, 100_000.0, 30.0, 1.0)

            pulse_enabled = st.toggle("간헐(Pulse) 분사 적용", value=False)
            if pulse_enabled:
                p1, p2 = st.columns(2)
                with p1:
                    on_time = st.number_input("1회 분사 시간 (초)", 0.001, 3600.0, 0.08, 0.01, format="%.3f")
                with p2:
                    cycle_time = st.number_input("반복 주기 (초)", 0.001, 3600.0, 1.0, 0.1, format="%.3f")
                duty = min(on_time / cycle_time, 1.0)
                if on_time > cycle_time:
                    st.warning("분사 시간이 반복 주기보다 길어 듀티를 100%로 제한했습니다.")
            else:
                duty = 1.0

            c, d = st.columns(2)
            with c:
                operating_hours = st.number_input("계산 운전시간 (h)", 0.0, 10_000.0, 8.0, 0.5)
            with d:
                tank_mass = st.number_input("탱크 유효 약액량 (kg)", 0.0, 1_000_000.0, 20.0, 1.0)

    flow = calculate_nozzle_flow(nozzle_count, single_flow, duty, operating_hours, tank_mass)
    with result_col:
        st.markdown(
            f"""
            <div class="flow-hero">
              <div class="eyebrow">시간당 유효 사용량 · EFFECTIVE CONSUMPTION</div>
              <div class="big">{flow['kg_h']:,.2f} <span>kg/h</span></div>
              <div class="sub">연속 총 유량 {flow['continuous_g_min']:,.1f} g/min · 적용 듀티 {flow['duty_percent']:.1f}%</div>
            </div>
            <div class="metric-grid three">
              {metric_card('유효 총 유량', f"{flow['effective_g_min']:,.1f}", 'g/min', '듀티 반영')}
              {metric_card('선택 시간 사용량', f"{flow['period_kg']:,.2f}", 'kg', f"{operating_hours:g}시간 기준")}
              {metric_card('예상 탱크 사용시간', '∞' if math.isinf(flow['tank_hours']) else f"{flow['tank_hours']:,.2f}", 'h', f"유효 {tank_mass:g} kg")}
            </div>
            """,
            unsafe_allow_html=True,
        )
        if not pulse_enabled:
            st.caption("기존 예시값 6 EA × 30 g/min = 180 g/min = 10.80 kg/h가 동일하게 계산됩니다.")

    st.markdown('<div class="hairline"></div>', unsafe_allow_html=True)
    section_heading("02 · PRESSURE CORRECTION", "압력 변화 시 유량 환산", "동일 노즐에서 액체 유량이 압력의 제곱근에 비례한다고 가정합니다.")
    with st.container(border=True):
        p1, p2, p3 = st.columns(3)
        with p1:
            reference_flow = st.number_input("기준 유량 Q₁ (L/min)", 0.0, 100_000.0, 10.0, 0.5)
        with p2:
            reference_pressure = st.number_input("기준 압력 P₁ (bar)", 0.01, 1000.0, 3.0, 0.1)
        with p3:
            target_pressure = st.number_input("목표 압력 P₂ (bar)", 0.0, 1000.0, 5.0, 0.1)
        corrected_flow = reference_flow * math.sqrt(target_pressure / reference_pressure)
        st.markdown(
            f'<div class="formula-box">목표 유량 <b>{corrected_flow:,.3f} L/min</b> &nbsp; · &nbsp; '
            '<code>Q₂ = Q₁ × √(P₂ / P₁)</code></div>',
            unsafe_allow_html=True,
        )


def render_system_page() -> None:
    render_header("SYSTEM ANALYSIS", "충격력·분사 커버리지·배관 손실·펌프 동력을 한 화면에서 분석합니다")

    result_col, input_col = st.columns([1.14, 0.86], gap="large")
    with input_col:
        section_heading("01 · OPERATING POINT", "노즐 운전 조건")
        with st.container(border=True):
            pattern_name = st.selectbox("노즐 스프레이 패턴", list(PATTERNS), index=0)
            r1, r2 = st.columns(2)
            with r1:
                pressure_bar = st.number_input("분사 압력 (bar)", 0.1, 100.0, 3.0, 0.1)
                spray_angle_deg = st.number_input("분사 각도 (°)", 0.0, 150.0, 65.0, 1.0)
            with r2:
                flow_l_min = st.number_input("단일 노즐 유량 (L/min)", 0.1, 500.0, 10.0, 0.5)
                spray_distance_mm = st.number_input("분사 거리 (mm)", 0.0, 1000.0, 150.0, 10.0)
            pattern = PATTERNS[pattern_name]
            st.caption(f"적용 계수 C={pattern['coefficient']:.3f} · 피크 계수 ×{pattern['peak_factor']:.2f}")

    # Temporary values are completed below after the piping inputs are rendered.
    with result_col:
        section_heading("RESULT · SPRAY PERFORMANCE", "노즐 충격력 및 커버리지")
        result_placeholder = st.empty()

    st.markdown('<div class="hairline"></div>', unsafe_allow_html=True)
    section_heading(
        "02 · HYDRAULIC SYSTEM",
        "배관 손실 압력 · 펌프 모터 동력",
        "첨부 계산기의 Hazen-Williams 계수, 엘보 등가길이, 설계 여유 및 펌프 효율을 동일하게 적용합니다.",
    )
    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            nozzle_qty = st.number_input("노즐 수량 (EA)", 1, 1000, 10, 1)
            pipe_size_a = st.selectbox(
                "메인 배관 규격",
                list(PIPE_INNER_DIAMETERS_MM),
                index=2,
                format_func=lambda size: f"{size}A · 내경 {PIPE_INNER_DIAMETERS_MM[size]:.1f} mm",
            )
        with c2:
            pipe_length_m = st.number_input("배관 총 길이 (m)", 0.5, 100.0, 5.0, 1.0)
            elbow_qty = st.number_input("90° 엘보 수량 (개)", 0, 50, 4, 1)
        with c3:
            vertical_height_m = st.number_input("수직 상승 높이 (m)", 0.0, 30.0, 1.5, 0.5)
            filter_label = st.selectbox("인라인 필터", ["필터 있음 (0.25 bar)", "필터 없음 (0.00 bar)"], index=0)
            filter_loss_bar = 0.25 if filter_label.startswith("필터 있음") else 0.0

    inputs: dict[str, Any] = {
        "pattern_name": pattern_name,
        "pressure_bar": pressure_bar,
        "flow_l_min": flow_l_min,
        "spray_angle_deg": spray_angle_deg,
        "spray_distance_mm": spray_distance_mm,
        "nozzle_qty": nozzle_qty,
        "pipe_size_a": pipe_size_a,
        "pipe_length_m": pipe_length_m,
        "elbow_qty": elbow_qty,
        "vertical_height_m": vertical_height_m,
        "filter_loss_bar": filter_loss_bar,
    }
    result = calculate_system(**inputs)

    gauge = min(max(float(result["peak_linear_kgf_cm"]) / 0.08 * 100.0, 5.0), 100.0)
    with result_placeholder.container():
        st.markdown(
            f"""
            <div class="hero-result">
              <div class="hero-label">중심부 최대 피크 타력 · PEAK LINEAR IMPACT</div>
              <div class="hero-value">{result['peak_linear_kgf_cm']:.4f}<small>kgf/cm</small></div>
              <div class="hero-sub">{result['peak_linear_gf_cm']:.1f} gf/cm · {html.escape(str(result['impact_status']))}</div>
              <div class="gauge-labels"><span>저타력 · 린스</span><span>중타력 · 일반 세정</span><span>고타력 · 강력 세척</span></div>
              <div class="gauge-track"><div class="gauge-fill" style="width:{gauge:.1f}%"></div></div>
            </div>
            <div class="metric-grid spray-metrics">
              {metric_card('전체 충격력', f"{result['total_impact_kgf']:.3f}", 'kgf', f"{result['total_impact_n']:.2f} N")}
              {metric_card('단위 폭당 평균 타력', f"{result['average_linear_kgf_cm']:.4f}", 'kgf/cm', '폭 방향 평균')}
              {metric_card('분사 커버리지 폭', f"{result['width_mm']:.1f}", 'mm', '기하학적 이론 폭')}
              {metric_card('이론 분사 유속', f"{result['jet_velocity_m_s']:.1f}", 'm/s', '베르누이 기준')}
            </div>
            {spray_diagram_svg(spray_angle_deg, spray_distance_mm, float(result['width_mm']), str(pattern['short']))}
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
        <div class="metric-grid">
          {metric_card('예측 총 손실 압력', f"{result['total_pressure_loss_bar']:.2f}", 'bar', f"마찰 {result['friction_loss_bar']:.2f} + 위치 {result['height_loss_bar']:.2f} + 필터 {result['filter_loss_bar']:.2f}")}
          {metric_card('배관 내 유속', f"{result['pipe_velocity_m_s']:.2f}", 'm/s', str(result['velocity_status']))}
          {metric_card('총 설계 유량', f"{result['total_design_flow_l_min']:.1f}", 'L/min', '노즐 합계 + 8% 여유')}
          {metric_card('소요 펌프 모터 동력', f"{result['motor_power_kw']:.2f}", 'kW', f"{result['motor_power_hp']:.2f} HP · 요구압력 {result['total_required_pressure_bar']:.2f} bar")}
        </div>
        """,
        unsafe_allow_html=True,
    )
    tone = str(result["velocity_tone"])
    status_class = "" if tone == "ok" else tone
    st.markdown(
        f'<div class="status-strip {status_class}"><span><strong>배관 유속 판정 · {result["velocity_status"]}</strong><br>'
        f'현재 {result["pipe_velocity_m_s"]:.2f} m/s · 권장 검토 범위 1.5–2.5 m/s</span>'
        f'<span>등가 배관 길이 {result["total_equivalent_length_m"]:.2f} m · 수두손실 {result["head_loss_m"]:.2f} m</span></div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="hairline"></div>', unsafe_allow_html=True)
    section_heading("03 · ENGINEERING REPORT", "PDF · 인쇄 리포트", "프로젝트 정보를 넣으면 현재 계산 조건과 결과가 보고서에 반영됩니다.")
    with st.container(border=True):
        m1, m2, m3 = st.columns(3)
        with m1:
            project_name = st.text_input("프로젝트명", placeholder="예: 세정 헤더 개선 검토")
        with m2:
            customer = st.text_input("고객 / 현장", placeholder="예: A Line")
        with m3:
            engineer = st.text_input("작성자", placeholder="예: 홍길동")
        project = {"project_name": project_name, "customer": customer, "engineer": engineer}
        try:
            pdf_bytes = build_pdf_report(project, inputs, result)
            pdf_error = None
        except Exception as exc:
            pdf_bytes = b""
            pdf_error = str(exc)
        print_bytes = build_printable_html(project, inputs, result)
        b1, b2 = st.columns(2)
        with b1:
            st.download_button(
                "PDF 리포트 다운로드",
                data=pdf_bytes,
                file_name="spray_engineering_report.pdf",
                mime="application/pdf",
                width="stretch",
                disabled=bool(pdf_error),
            )
        with b2:
            st.download_button(
                "인쇄용 HTML 다운로드",
                data=print_bytes,
                file_name="spray_engineering_print_report.html",
                mime="text/html",
                width="stretch",
            )
        if pdf_error:
            st.error(f"PDF 생성 모듈을 불러오지 못했습니다: {pdf_error}")
        st.caption("인쇄용 HTML을 브라우저에서 열고 ‘인쇄 / PDF 저장’을 누르면 회사 프린터 또는 PDF로 출력할 수 있습니다.")


def render_guide_page() -> None:
    render_header("ENGINEERING BASIS", "적용 공식과 설계 가정, 사용 범위를 투명하게 확인합니다")
    section_heading("CALCULATION BASIS", "계산식 · 설계 상수")
    st.markdown(
        """
        <div class="feature-grid">
          <div class="feature-card"><div class="feature-no">01 · IMPACT</div><div class="feature-title">총 충격력</div><div class="feature-copy">F(kgf) = C × Q × √P. 패턴별 C는 부채꼴 0.024, 솔리드 스트림 0.026, 풀콘 0.018입니다.</div></div>
          <div class="feature-card"><div class="feature-no">02 · COVERAGE</div><div class="feature-title">커버리지 폭</div><div class="feature-copy">W = 2H × tan(θ/2). 실제 폭은 압력, 액적, 공기 저항과 설치 환경에 따라 달라질 수 있습니다.</div></div>
          <div class="feature-card"><div class="feature-no">03 · VELOCITY</div><div class="feature-title">이론 분사 유속</div><div class="feature-copy">v = √(2P/ρ), 물의 밀도 1,000 kg/m³를 적용한 이상 유속입니다.</div></div>
          <div class="feature-card"><div class="feature-no">04 · PIPE LOSS</div><div class="feature-title">Hazen–Williams</div><div class="feature-copy">C=130, 90° 엘보 등가길이 30D, 규격별 제공 HTML의 내경표를 그대로 사용합니다.</div></div>
          <div class="feature-card"><div class="feature-no">05 · DESIGN FLOW</div><div class="feature-title">유량 설계 여유</div><div class="feature-copy">총 설계 유량 = 단일 노즐 유량 × 수량 × 1.08로 8% 여유를 반영합니다.</div></div>
          <div class="feature-card"><div class="feature-no">06 · PUMP POWER</div><div class="feature-title">펌프 모터 동력</div><div class="feature-copy">수력동력 P×Q/600, 펌프 효율 60%, 모터 안전계수 1.15를 적용합니다.</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="hairline"></div>', unsafe_allow_html=True)
    section_heading("PIPE DATA", "배관 내경 기준표")
    pipe_rows = [
        {"호칭": f"{size}A", "내경 (mm)": diameter}
        for size, diameter in PIPE_INNER_DIAMETERS_MM.items()
    ]
    st.dataframe(pipe_rows, width="stretch", hide_index=True)

    st.markdown('<div class="hairline"></div>', unsafe_allow_html=True)
    section_heading("SCOPE & SAFETY", "사용 범위 · 주의사항")
    st.info(
        "이 계산기는 물과 유사한 비압축성 액체의 초기 기술 검토용입니다. 점도, 밀도, 온도, 노즐 마모, "
        "맥동, 밸브·티·축소관 손실 및 NPSH는 별도 검토가 필요합니다. 최종 선정 전 현장 시험과 제조사 "
        "성능곡선을 확인하십시오."
    )
    st.markdown(
        """
        <div class="independent-note"><b>상표 및 독립성 고지</b><br>
        FlowCore와 이 계산기는 독립적으로 제작된 비공식 기술 도구입니다. 특정 노즐 또는 펌프 제조사의 공식 제품, 인증 서비스, 성능 보증을 의미하지 않습니다.
        Spraying Systems Co. 로고는 사용자 요청에 따라 공식 홈페이지 링크 영역에만 표시하며, 해당 상표와 로고의 권리는 각 소유자에게 있습니다.</div>
        """,
        unsafe_allow_html=True,
    )


st.markdown(APP_CSS, unsafe_allow_html=True)

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand"><span class="mini-mark">FC</span><strong>FLOWCORE</strong><br>
        <span style="font-size:.67rem;color:#86b9d4;letter-spacing:.09em">SPRAY ENGINEERING SUITE</span></div>
        """,
        unsafe_allow_html=True,
    )
    page = st.radio(
        "계산 메뉴",
        ["통합 시스템 분석", "노즐 유량 계산", "계산 기준 · 도움말"],
        index=0,
    )
    st.divider()
    st.markdown(
        """
        <div class="sidebar-note">
          <b style="color:#eaf6fc">TECHNICAL REVIEW USE</b><br>
          입력값을 바꾸면 모든 결과가 즉시 갱신됩니다. 최종 장비 선정 전 제조사 데이터와 현장 조건을 확인하세요.
        </div>
        """,
        unsafe_allow_html=True,
    )

if page == "노즐 유량 계산":
    render_nozzle_flow_page()
elif page == "계산 기준 · 도움말":
    render_guide_page()
else:
    render_system_page()

st.markdown(
    """
    <div style="margin-top:2rem;padding-top:.8rem;border-top:1px solid #d6e2ec;color:#7b8fa0;font-size:.64rem;display:flex;justify-content:space-between;gap:1rem;flex-wrap:wrap">
      <span>FLOWCORE · Spray Engineering Calculator v2.0</span>
      <span>Independent technical reference · Not a performance warranty</span>
    </div>
    """,
    unsafe_allow_html=True,
)
