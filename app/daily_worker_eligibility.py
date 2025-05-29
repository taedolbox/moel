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
current_datetime = datetime(2025, 5, 28, 8, 44, tzinfo=KST)
current_time_korean = current_datetime.strftime('%Y년 %m월 %d일 %A 오전 %I:%M KST')

# 스타일시트 로드
with open("static/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def get_date_range(apply_date):
    start_date = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1).date()
    return [d.date() for d in pd.date_range(start=start_date, end=apply_date)], start_date

def render_calendar(apply_date):
    if 'selected_dates' not in st.session_state:
        st.session_state.selected_dates = set()

    selected_dates = st.session_state.selected_dates
    current_date = current_datetime.date()
    start_date = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1).date()
    months = sorted(set((d.year, d.month) for d in pd.date_range(start=start_date, end=apply_date)))

    for year, month in months:
        st.markdown(f"### {year}년 {month}월", unsafe_allow_html=True)
        cal = calendar.monthcalendar(year, month)
        days_of_week = ["일", "월", "화", "수", "목", "금", "토"]

        with st.container():
            cols = st.columns(7, gap="small")
            for i, day in enumerate(days_of_week):
                with cols[i]:
                    class_name = "day-header"
                    if i == 0 or i == 6:
                        class_name += " weekend"
                    st.markdown(f'<div class="{class_name}">{day}</div>', unsafe_allow_html=True)

        for week in cal:
            with st.container():
                cols = st.columns(7, gap="small")
                for i, day in enumerate(week):
                    with cols[i]:
                        if day == 0:
                            st.empty()
                            continue
                        date_obj = date(year, month, day)
                        is_selected = date_obj in selected_dates
                        is_current = date_obj == current_date
                        is_disabled = date_obj > apply_date

                        class_name = "day"
                        if is_selected:
                            class_name += " selected"
                        if is_current:
                            class_name += " current"
                        if is_disabled:
                            class_name += " disabled"

                        checkbox_key = f"date_{date_obj}"
                        checkbox_id = f"id_{checkbox_key}"

                        if not is_disabled:
                            checkbox_value = st.checkbox(
                                "", key=checkbox_key, value=is_selected, label_visibility="hidden"
                            )
                            st.markdown(
                                f'''
                                <label for="{checkbox_id}">
                                    <input type="checkbox" id="{checkbox_id}" style="display:none;" {'checked' if is_selected else ''}>
                                    <div class="{class_name}" data-date="{date_obj}">{day}</div>
                                </label>
                                ''',
                                unsafe_allow_html=True
                            )
                            if checkbox_value != is_selected:
                                if checkbox_value:
                                    selected_dates.add(date_obj)
                                else:
                                    selected_dates.discard(date_obj)
                                st.session_state.selected_dates = selected_dates
                                st.rerun()
                        else:
                            st.markdown(f'<div class="{class_name}">{day}</div>', unsafe_allow_html=True)

    return st.session_state.selected_dates

def daily_worker_eligibility_app():
    st.header("일용근로자 수급자격 요건 모의계산")
    st.markdown(f"**오늘 날짜와 시간**: {current_time_korean}", unsafe_allow_html=True)

    st.markdown("### \ud83d\udccb \uc694\uac74 \uc870\uac74")
    st.markdown("- **\uc870\uac74 1**: ...")  # 생략된 본문은 앞서 제공한 코드와 동일
    # 이하 생략 (기존 코드 그대로 유지)

if __name__ == "__main__":
    daily_worker_eligibility_app()
