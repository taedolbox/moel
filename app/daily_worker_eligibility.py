# daily_worker_eligibility.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import calendar
import pytz

# 달력 시작 요일 설정
calendar.setfirstweekday(calendar.SUNDAY)

# KST 시간대 설정
KST = pytz.timezone('Asia/Seoul')
current_datetime = datetime.now(KST)
current_date = current_datetime.date()

# 스타일 삽입
st.markdown("""
<style>
.day {
    text-align: center;
    padding: 0.4em;
    border-radius: 50%;
    display: inline-block;
    width: 2.2em;
    height: 2.2em;
    line-height: 2.2em;
    cursor: pointer;
    transition: background-color 0.2s, color 0.2s, border 0.2s;
}
.day:hover {
    background-color: #f0f0f0;
}
.day.selected {
    border: 2px solid red;
    color: red;
    font-weight: bold;
}
.day.current {
    background-color: #d0ebff;
}
.day.disabled {
    color: #ccc;
    pointer-events: none;
}
.day-header {
    text-align: center;
    font-weight: bold;
    padding-bottom: 4px;
}
.weekend {
    color: #888;
}
.result-text {
    background-color: #f9f9f9;
    padding: 1em;
    border-left: 6px solid #0b74de;
    margin-top: 1em;
}
</style>
""", unsafe_allow_html=True)

def get_date_range(apply_date):
    start_date = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1).date()
    return [d.date() for d in pd.date_range(start=start_date, end=apply_date)], start_date

def render_calendar(apply_date):
    if "selected_dates" not in st.session_state:
        st.session_state.selected_dates = set()

    selected_dates = st.session_state.selected_dates
    start_date = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1).date()
    months = sorted(set((d.year, d.month) for d in pd.date_range(start=start_date, end=apply_date)))

    for year, month in months:
        st.markdown(f"### {year}년 {month}월", unsafe_allow_html=True)
        cal = calendar.monthcalendar(year, month)
        days_of_week = ["일", "월", "화", "수", "목", "금", "토"]

        cols = st.columns(7)
        for i, day in enumerate(days_of_week):
            with cols[i]:
                st.markdown(f'<div class="day-header{" weekend" if i in [0,6] else ""}">{day}</div>', unsafe_allow_html=True)

        for week in cal:
            cols = st.columns(7)
            for i, day in enumerate(week):
                with cols[i]:
                    if day == 0:
                        st.markdown(" ", unsafe_allow_html=True)
                        continue

                    d = date(year, month, day)
                    is_selected = d in selected_dates
                    is_disabled = d > apply_date
                    is_current = d == current_date

                    class_name = "day"
                    if is_selected: class_name += " selected"
                    if is_current: class_name += " current"
                    if is_disabled: class_name += " disabled"

                    clicked = st.button(str(day), key=f"{d}_btn")
                    if clicked and not is_disabled:
                        if is_selected:
                            selected_dates.discard(d)
                        else:
                            selected_dates.add(d)
                        st.session_state.selected_dates = selected_dates
                        st.rerun()

                    st.markdown(f'<div class="{class_name}">{day}</div>', unsafe_allow_html=True)

    return selected_dates

def daily_worker_eligibility_app():
    st.header("📌 일용근로자 수급자격 요건 모의계산")
    st.markdown(f"**현재 시간**: {current_datetime.strftime('%Y년 %m월 %d일 (%A) %p %I:%M')}")
    st.markdown("---")

    st.markdown("### ✅ 수급자격 신청일 선택")
    apply_date = st.date_input("수급자격 신청일을 선택하세요", value=current_date)

    st.markdown("### 📆 근무일 선택")
    selected_dates = render_calendar(apply_date)
    date_range, start_date = get_date_range(apply_date)
    worked_days = len([d for d in selected_dates if d in date_range])
    threshold = len(date_range) / 3

    st.markdown("---")
    st.markdown(f"- 총 일수: **{len(date_range)}일**")
    st.markdown(f"- 기준 (1/3): **{threshold:.1f}일**")
    st.markdown(f"- 선택된 근무일 수: **{worked_days}일**")

    condition1 = worked_days < threshold
    fourteen_range = [apply_date - timedelta(days=i) for i in range(1, 15)]
    condition2 = all(d not in selected_dates for d in fourteen_range)

    st.markdown("---")
    st.markdown("### 🔍 조건 판단 결과")

    st.markdown(f'<div class="result-text"><p>{"✅ 조건 1 충족" if condition1 else "❌ 조건 1 불충족"}</p></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="result-text"><p>{"✅ 조건 2 충족" if condition2 else "❌ 조건 2 불충족"}</p></div>', unsafe_allow_html=True)

    st.markdown("### 📅 최종 판단")
    if condition1:
        st.success("✅ 일반일용근로자 신청 가능")
    else:
        st.error("❌ 일반일용근로자 신청 불가능")

    if condition1 and condition2:
        st.success("✅ 건설일용근로자 신청 가능")
    else:
        if not condition1:
            st.error("❌ 건설일용근로자: 조건 1 불충족")
        if not condition2:
            st.error("❌ 건설일용근로자: 조건 2 불충족")

if __name__ == "__main__":
    daily_worker_eligibility_app()
