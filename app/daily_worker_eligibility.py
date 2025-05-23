import streamlit as st
from datetime import date, timedelta
import pandas as pd

st.set_page_config(page_title="일용근로자 수급자격 모의계산", layout="wide")

# ⛱️ CSS for calendar
st.markdown("""
    <style>
    div[data-testid="stButton"] button {
        width: 40px !important;
        height: 40px !important;
        border-radius: 50% !important;
        font-size: 0.9rem !important;
        padding: 0 !important;
        margin: 0 auto !important;
        background-color: transparent !important;
        color: white !important;
        border: 2px solid transparent !important;
    }
    div[data-testid="stButton"] button:hover {
        border: 2px solid #00ff00 !important;
        background-color: rgba(0, 255, 0, 0.2) !important;
    }
    div[data-testid="stButton"] button.selected-day {
        border: 2px solid white !important;
        background-color: rgba(255, 255, 255, 0.15) !important;
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🧮 일용근로자 수급자격 요건 모의계산")

# 📆 수급자격 신청일
apply_date = st.date_input("📌 수급자격 신청일을 선택하세요", date.today())

# 📌 조건 설명
start_14 = apply_date - timedelta(days=14)
end_14 = apply_date - timedelta(days=1)

st.markdown("---")
st.markdown("### 📌 수급요건 개요")
st.markdown(f"""
- **조건 1**: 신청일 기준 **직전 달의 1일 ~ 신청일까지** 전체 일수 중 **근무일 수가 1/3 미만**이어야 합니다.
- **조건 2 (건설일용)**: 신청일 **직전 14일간({start_14.strftime('%Y-%m-%d')} ~ {end_14.strftime('%Y-%m-%d')})** **근무기록이 없어야** 합니다.
""")
st.markdown("---")

# 📆 캘린더 범위 설정 (신청일 기준 지난 두 달)
start_date = (apply_date.replace(day=1) - timedelta(days=31)).replace(day=1)
end_date = apply_date

all_dates = pd.date_range(start=start_date, end=end_date)

# 세션 상태 초기화
if "selected_days" not in st.session_state:
    st.session_state.selected_days = set()

st.markdown("### 📅 근무한 날짜를 선택하세요")
calendar_by_month = all_dates.to_series().groupby(all_dates.to_series().dt.to_period("M"))

for period, dates_in_month in calendar_by_month:
    st.subheader(f"📆 {period.strftime('%Y년 %m월')}")

    # 요일 헤더
    cols = st.columns(7)
    for i, day_name in enumerate(["월", "화", "수", "목", "금", "토", "일"]):
        cols[i].markdown(f"**{day_name}**")

    week = []
    cols = st.columns(7)
    first_day_weekday = dates_in_month.iloc[0].weekday()

    for _ in range(first_day_weekday):
        cols[_].markdown("")

    for current_day in dates_in_month:
        weekday = current_day.weekday()
        if weekday == 0:
            cols = st.columns(7)

        button_label = str(current_day.day)
        key = f"{current_day.strftime('%Y-%m-%d')}"

        is_selected = key in st.session_state.selected_days
        button_style = "selected-day" if is_selected else ""

        if cols[weekday].button(button_label, key=key):
            if is_selected:
                st.session_state.selected_days.remove(key)
            else:
                st.session_state.selected_days.add(key)

        # 적용된 스타일 HTML로 표시 (선택 여부 표현)
        cols[weekday].markdown(
            f"""
            <script>
            const el = window.parent.document.querySelector('button[key="{key}"]');
            if (el) {{
                el.classList.add("{button_style}");
            }}
            </script>
            """,
            unsafe_allow_html=True,
        )

# ✔️ 결과 판단
st.markdown("---")
st.markdown("## 🧾 수급 요건 판정 결과")

selected_days = pd.to_datetime(list(st.session_state.selected_days))
selected_days = selected_days.sort_values()

# 조건 1: 직전달 1일 ~ 신청일까지
condition1_start = apply_date.replace(day=1)
condition1_end = apply_date
total_days = (condition1_end - condition1_start).days + 1

condition1_work_days = [d for d in selected_days if condition1_start <= d.date() <= condition1_end]
if len(condition1_work_days) < total_days / 3:
    st.success(f"✅ 조건 1 충족: 총 {total_days}일 중 {len(condition1_work_days)}일 근무 (< 1/3)")
else:
    st.warning(f"❌ 조건 1 불충족: 총 {total_days}일 중 {len(condition1_work_days)}일 근무 (≥ 1/3)")

# 조건 2: 신청일 직전 14일간
condition2_start = apply_date - timedelta(days=14)
condition2_end = apply_date - timedelta(days=1)
condition2_range = pd.date_range(start=condition2_start, end=condition2_end)
condition2_fail = any(d.date() in condition2_range for d in selected_days)

if not condition2_fail:
    st.success(f"✅ 조건 2 충족: 신청일 직전 14일간({condition2_start.strftime('%Y-%m-%d')} ~ {condition2_end.strftime('%Y-%m-%d')}) 근무내역이 없습니다.")
else:
    st.warning(f"❌ 조건 2 불충족: 신청일 직전 14일간({condition2_start.strftime('%Y-%m-%d')} ~ {condition2_end.strftime('%Y-%m-%d')}) 내 근무기록이 존재합니다.")

