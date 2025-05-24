import streamlit as st
import calendar
from datetime import date, timedelta

def run_daily_worker_eligibility_app():
    st.title("일용근로자 수급자격 모의계산")
    
    # 🌟 수급자격 신청일 입력
    claim_date = st.date_input("수급자격 신청일", value=date.today())

    # 🌟 수급자격 신청일 기준 18개월 전 구하기
    start_date = claim_date - timedelta(days=18 * 30)
    end_date = claim_date

    # 🌟 선택한 날짜들 저장
    selected_days = st.session_state.get("selected_days", [])

    def toggle_date(d):
        if d in selected_days:
            selected_days.remove(d)
        else:
            selected_days.append(d)
        st.session_state["selected_days"] = selected_days

    st.subheader(f"과거 18개월 간 근무일 선택 ({start_date} ~ {end_date})")

    current = start_date.replace(day=1)

    while current <= end_date:
        year = current.year
        month = current.month
        month_range = calendar.monthrange(year, month)[1]
        month_dates = [date(year, month, day) for day in range(1, month_range + 1)]
        month_dates = [d for d in month_dates if start_date <= d <= end_date]

        if not month_dates:
            current = (current.replace(day=28) + timedelta(days=4)).replace(day=1)
            continue

        st.markdown(f"### {year}년 {month}월")

        cols = st.columns(7)
        weekdays = ["월", "화", "수", "목", "금", "토", "일"]
        for i in range(7):
            cols[i].markdown(f"**{weekdays[i]}**")

        rows = [month_dates[i:i+7] for i in range(0, len(month_dates), 7)]

        for week in rows:
            cols = st.columns(7)
            for i, d in enumerate(week):
                label = str(d.day)
                if d in selected_days:
                    cols[i].markdown(f"<div style='background-color:#4CAF50;border-radius:50%;width:30px;height:30px;text-align:center;line-height:30px;color:white'>{label}</div>", unsafe_allow_html=True)
                else:
                    if cols[i].button(label, key=str(d)):
                        toggle_date(d)

        current = (current.replace(day=28) + timedelta(days=4)).replace(day=1)

    # 결과 출력
    st.subheader("결과")
    st.write(f"선택한 근무일 수: **{len(selected_days)}일**")
    if len(selected_days) >= 90:
        st.success("✅ 과거 18개월 간 90일 이상 근무했습니다. 수급자격 요건을 충족할 수 있습니다.")
    else:
        st.error("❌ 근로일이 부족합니다. (90일 미만)")
