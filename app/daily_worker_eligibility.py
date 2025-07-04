import streamlit as st
from datetime import datetime, timedelta
import json
from eligibility_logic import check_conditions  # 별도 파일에서 함수 임포트

def daily_worker_eligibility_app():
    st.markdown("<span style='font-size:22px; font-weight:600;'>🏗️ 일용직 신청 가능 시점 판단</span>", unsafe_allow_html=True)

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

    calendar_groups = {}
    for date in cal_dates:
        ym = date.strftime("%Y-%m")
        calendar_groups.setdefault(ym, []).append(date)

    # 달력 UI 코드(생략 가능, 기존과 동일하게 작성)

    # 선택된 날짜를 근무일로 처리 (MM/DD 형식)
    selected_dates = st.session_state.selected_dates_list

    # calendar_dates를 YYYY-MM-DD 문자열 리스트로 변환
    calendar_dates_str = [d.strftime("%Y-%m-%d") for d in cal_dates]

    # 조건 판단 함수 호출
    results = check_conditions(selected_dates, calendar_dates_str, input_date)

    # 결과 출력 (예시)
    st.markdown("---")
    st.write(f"총 기간 일수: {results['total_days']}일")
    st.write(f"1/3 기준: {results['threshold']:.1f}일")
    st.write(f"근무일 수: {results['worked_days']}일")

    if results['cond1']:
        st.success("✅ 조건 1 충족: 근무일 수가 기준 미만입니다.")
    else:
        st.error("❌ 조건 1 불충족: 근무일 수가 기준 이상입니다.")

    if results['no_work_14_days']:
        st.success(f"✅ 조건 2 충족: 신청일 직전 14일간({results['fourteen_days_start']} ~ {results['fourteen_days_end']}) 무근무")
    else:
        st.error(f"❌ 조건 2 불충족: 신청일 직전 14일간({results['fourteen_days_start']} ~ {results['fourteen_days_end']}) 내 근무기록이 존재합니다.")

        st.info(f"📅 조건 2를 충족하려면 오늘 이후에 근로제공이 없는 경우 {results['next_possible_date']} 이후에 신청하면 조건 2를 충족할 수 있습니다.")

    # 최종 판단
    general_ok = "✅ 신청 가능" if results['cond1'] else "❌ 신청 불가능"
    construction_ok = "✅ 신청 가능" if (results['cond1'] or results['no_work_14_days']) else "❌ 신청 불가능"

    st.markdown("### 📌 최종 판단")
    st.write(f"✅ 일반일용근로자: {general_ok}")
    st.write(f"수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지({calendar_dates_str[0]} ~ {calendar_dates_str[-1]}) 근로일 수의 합이 같은 기간 총 일수의 3분의 1 미만")
    st.write(f"✅ 건설일용근로자: {construction_ok}")

