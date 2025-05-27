# daily_worker_eligibility.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import calendar

# 달력의 시작 요일을 일요일로 설정
calendar.setfirstweekday(calendar.SUNDAY)

# 현재 날짜와 시간
current_datetime = datetime(2025, 5, 27, 21, 7)
current_time_korean = current_datetime.strftime('%Y년 %m월 %d일 %A 오후 %I:%M KST')

def render_calendar(apply_date):
    if 'selected_dates' not in st.session_state:
        st.session_state.selected_dates = set()

    selected_dates = st.session_state.selected_dates
    current_date = current_datetime.date()
    start_date = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1).date()
    months = sorted(set((d.year, d.month) for d in pd.date_range(start=start_date, end=apply_date)))

    for year, month in months:
        st.markdown(f"### {year}년 {month}월")
        cal = calendar.monthcalendar(year, month)
        days_of_week = ["일", "월", "화", "수", "목", "금", "토"]

        # 요일 헤더
        cols = st.columns(7)
        for i, day in enumerate(days_of_week):
            with cols[i]:
                st.markdown(f'<span style="color: {"red" if i == 0 or i == 6 else "black"}">{day}</span>', unsafe_allow_html=True)

        # 날짜 렌더링
        for week in cal:
            cols = st.columns(7)
            for i, day in enumerate(week):
                if day == 0:
                    with cols[i]:
                        st.empty()
                    continue
                date_obj = date(year, month, day)
                is_selected = date_obj in selected_dates
                is_current = date_obj == current_date
                is_disabled = date_obj > apply_date

                with cols[i]:
                    if is_disabled:
                        st.markdown(f'<div class="day disabled">{day}</div>', unsafe_allow_html=True)
                    else:
                        if st.checkbox("", key=f"date_{date_obj}", value=is_selected):
                            selected_dates.add(date_obj)
                        else:
                            selected_dates.discard(date_obj)
                        st.session_state.selected_dates = selected_dates
                        st.markdown(
                            f'<div class="day{' selected' if is_selected else ''}{' current' if is_current else ''}">{day}</div>',
                            unsafe_allow_html=True
                        )

        st.markdown("---")

    if selected_dates:
        st.markdown("### ✅ 선택된 근무일자")
        st.write(", ".join([d.strftime("%Y-%m-%d") for d in sorted(selected_dates)]))

def daily_worker_eligibility_app():
    st.header("일용근로자 수급자격 요건 모의계산")
    st.markdown(f"**오늘 날짜와 시간**: {current_time_korean}")

    apply_date = st.date_input("수급자격 신청일을 선택하세요", value=current_datetime.date())
    render_calendar(apply_date)

if __name__ == "__main__":
    daily_worker_eligibility_app()
