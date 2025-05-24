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


import streamlit as st
from datetime import date, timedelta
import calendar

def run_daily_worker_eligibility_app():
    st.title("일용근로자 수급자격 판단")

    is_construction = st.radio("건설일용근로자 여부", ["예", "아니오"]) == "예"

    st.markdown("### 1. 근무일 선택")
    st.markdown("아래 캘린더에서 과거 근무일을 클릭하여 선택하세요.")

    if "selected_days" not in st.session_state:
        st.session_state["selected_days"] = []

    selected_days = st.session_state["selected_days"]

    def toggle_date(d):
        if d in selected_days:
            selected_days.remove(d)
        else:
            selected_days.append(d)
        st.session_state["selected_days"] = selected_days

    today = date.today()
    last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
    range_start = last_month
    range_end = today

    month_range = (range_end - range_start).days + 1
    dates = [range_start + timedelta(days=i) for i in range(month_range)]

    weekdays = ["월", "화", "수", "목", "금", "토", "일"]
    st.markdown("#### " + range_start.strftime("%Y년 %m월") + " ~ " + range_end.strftime("%Y년 %m월"))

    cols = st.columns(7)
    for i in range(7):
        cols[i].markdown(f"**{weekdays[i]}**")

    rows = [dates[i:i+7] for i in range(0, len(dates), 7)]
    for week in rows:
        cols = st.columns(7)
        for i, d in enumerate(week):
            label = str(d.day)
            style = (
                f"<div class='selected'>{label}</div>" if d in selected_days
                else f"<div class='default'>{label}</div>"
            )
            if cols[i].button(label, key=str(d)):
                toggle_date(d)
            cols[i].markdown(style, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 2. 신청 가능한 날짜 판별")

    possible_dates = []
    for offset in range((today - range_start).days + 1):
        claim_day = range_start + timedelta(days=offset)
        prev_month_start = (claim_day.replace(day=1) - timedelta(days=1)).replace(day=1)
        target_range = [prev_month_start + timedelta(days=i)
                        for i in range((claim_day - prev_month_start).days + 1)]

        worked_days = [d for d in selected_days if prev_month_start <= d <= claim_day]
        condition1 = len(worked_days) < len(target_range) / 3

        if is_construction:
            last_14_days = [claim_day - timedelta(days=i) for i in range(1, 15)]
            condition2 = all(d not in selected_days for d in last_14_days)
        else:
            condition2 = True

        if condition1 and condition2:
            possible_dates.append(claim_day)

    if possible_dates:
        st.success(f"✅ 신청 가능한 가장 빠른 날짜는 **{possible_dates[0]}**입니다.")
    else:
        st.warning("❌ 조건을 만족하는 신청일이 없습니다.")

