import streamlit as st
from datetime import datetime, timedelta
from app.eligibility_logic import check_conditions  # 조건 판단 함수

def daily_worker_eligibility_app():
    st.markdown("🏗️ 일용직 신청 가능 시점 판단")

    today_kst = datetime.utcnow() + timedelta(hours=9)
    input_date = st.date_input("📅 기준 날짜 선택", today_kst.date())

    first_day_prev_month = (input_date.replace(day=1) - timedelta(days=1)).replace(day=1)
    last_day = input_date

    cal_dates = []
    current = first_day_prev_month
    while current <= last_day:
        cal_dates.append(current.strftime("%m/%d"))
        current += timedelta(days=1)

    selected_dates = st.multiselect(
        "근무한 날짜 선택 (mm/dd)", 
        options=cal_dates, 
        default=st.session_state.get('selected_dates_list', [])
    )
    st.session_state['selected_dates_list'] = selected_dates

    # 선택된 날짜가 변경될 때마다 결과 바로 계산
    # 전체 달력 날짜 full 포맷
    cal_dates_full = []
    current = first_day_prev_month
    while current <= last_day:
        cal_dates_full.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)

    # 선택된 날짜(mm/dd)를 YYYY-MM-DD로 변환 (연도 조정 포함)
    selected_full_dates = []
    for sel in selected_dates:
        month_day = datetime.strptime(sel, "%m/%d")
        full_date = datetime(year=input_date.year, month=month_day.month, day=month_day.day)
        if full_date > input_date:
            full_date = full_date.replace(year=input_date.year - 1)
        selected_full_dates.append(full_date.strftime("%Y-%m-%d"))

    fourteen_days_prior_start = (input_date - timedelta(days=14)).strftime("%Y-%m-%d")
    fourteen_days_prior_end = (input_date - timedelta(days=1)).strftime("%Y-%m-%d")

    # 조건 판단 결과 표시
    result = check_conditions(
        selected_full_dates,
        cal_dates_full,
        fourteen_days_prior_start,
        fourteen_days_prior_end
    )
    st.markdown("---")
    st.markdown(result, unsafe_allow_html=True)

