# app/daily_worker_eligibility.py

import streamlit as st
from datetime import datetime, timedelta
import json
from app.eligibility_logic import check_conditions

def daily_worker_eligibility_app():
    st.markdown(
        "<h3>🏗️ 일용직 신청 가능 시점 판단</h3>", unsafe_allow_html=True
    )

    if 'selected_dates_list' not in st.session_state:
        st.session_state.selected_dates_list = []

    today_kst = datetime.utcnow() + timedelta(hours=9)
    input_date = st.date_input("📅 기준 날짜 선택", today_kst.date())

    first_day_prev_month = (input_date.replace(day=1) - timedelta(days=1)).replace(day=1)
    last_day = input_date
    cal_dates = []
    current_date = first_day_prev_month
    while current_date <= last_day:
        cal_dates.append(current_date)
        current_date += timedelta(days=1)

    calendar_dates_json = json.dumps([d.strftime("%Y-%m-%d") for d in cal_dates])
    fourteen_days_prior_end = (input_date - timedelta(days=1)).strftime("%Y-%m-%d")
    fourteen_days_prior_start = (input_date - timedelta(days=14)).strftime("%Y-%m-%d")

    st.write(f"선택된 날짜들: {st.session_state.selected_dates_list}")

    # 결과 버튼
    if st.button("✅ 조건 판단하기"):
        result = check_conditions(
            st.session_state.selected_dates_list,
            cal_dates,
            fourteen_days_prior_start,
            fourteen_days_prior_end
        )
        st.markdown(result)

    st.markdown(f"""
    <script>
    const CALENDAR_DATES = {calendar_dates_json};

    window.addEventListener("message", (event) => {{
        const selected = JSON.parse(event.data);
        window.parent.postMessage({{ selected_dates: selected }}, '*');
    }});
    </script>
    """, unsafe_allow_html=True)

    # 달력은 네 기존 JS로 유지
    st.write("달력은 여기에 표시!")

    # 테스트용 직접 입력
    selected = st.text_input("테스트용 선택된 날짜 (mm/dd, 쉼표 구분)", "")
    if selected:
        st.session_state.selected_dates_list = [d.strip() for d in selected.split(",")]


