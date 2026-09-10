# Spray Engineering Calculator

Streamlit 기반의 스프레이 엔지니어링 계산 도구입니다. 계산기를 세 단계로 나누어 순차 제작합니다.

## 현재 완성 범위

- 첫 화면: 3개 계산기 선택 카드
- 계산기 01: 노즐 분사량 계산기
  - 일류체 노즐: `Q = K × √P`
  - 이류체 노즐: 액체·공기 압력 보정 모델
  - 데이터시트 기준점 3개 선택 및 평균 K 계산
  - 목표 액체 유량과 공기 소모량 예측
  - 압력－유량 특성 곡선
- 계산기 02, 03: 제작 예정 자리만 표시

## 실행

```bash
pip install -r requirements.txt
streamlit run NozzleWeb.py
```

## Streamlit Community Cloud

GitHub 저장소의 루트에 `NozzleWeb.py`와 `requirements.txt`를 업로드한 뒤 Main file path를 `NozzleWeb.py`로 설정합니다. `.streamlit/config.toml`은 화면 테마 설정입니다.

## 참고

첨부 HTML의 노즐 분사량 계산식을 보존했습니다. 실제 노즐 선정과 운전 조건은 제조사 데이터시트 및 기술 담당자의 검토 결과를 우선 적용하십시오.

Spraying Systems Co. 로고는 사용자 요청에 따라 공식 홈페이지 연결 영역에 표시됩니다. 본 계산기는 Spraying Systems Co.의 공식 제품 또는 성능 보증 서비스가 아닌 독립적인 계산 도구입니다.
