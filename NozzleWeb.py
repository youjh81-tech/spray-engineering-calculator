import streamlit as st

# 웹페이지 기본 설정
st.set_page_config(
    page_title="Spray Engineering Calculator",
    page_icon="💧",
    layout="centered"
)

# 제목
st.title("💧 Spray Engineering Calculator")
st.subheader("Nozzle Flow Calculator")

st.write("노즐 수량과 유량을 입력하면 총 사용량을 계산합니다.")

# 입력
nozzle_count = st.number_input(
    "노즐 개수 (EA)",
    min_value=1,
    value=4,
    step=1
)

flow = st.number_input(
    "노즐 1개당 유량 (g/min)",
    min_value=0.0,
    value=30.0,
    step=1.0
)

# 계산
total_flow = nozzle_count * flow
hourly_flow = total_flow * 60 / 1000

# 결과
st.divider()

st.subheader("계산 결과")

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "총 유량",
        f"{total_flow:,.1f} g/min"
    )

with col2:
    st.metric(
        "시간당 사용량",
        f"{hourly_flow:,.2f} kg/h"
    )

st.divider()

st.caption("Spray Engineering Calculator v1.0")
