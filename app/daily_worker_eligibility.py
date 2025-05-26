import streamlit as st
from datetime import datetime, timedelta

# CSS 적용
with open("style.css", "r") as f:
    css = f.read()
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# 달력 렌더링 함수
def render_calendar(year=2025, month=5):
    # 달력 제목
    st.markdown(f'<div class="calendar-wrapper"><h3>{year}년 {month}월</h3></div>', unsafe_allow_html=True)

    # 요일 헤더
    days = ["월", "화", "수", "목", "금", "토", "일"]
    with st.container():
        cols = st.columns(7)
        for i, day in enumerate(days):
            with cols[i]:
                st.markdown(f'<div class="day-header">{day}</div>', unsafe_allow_html=True)

    # 달력 시작 요일과 날짜 수 계산
    first_day = datetime(year, month, 1)
    days_in_month = (datetime(year, month+1, 1) - timedelta(days=1)).day if month < 12 else 31
    start_weekday = first_day.weekday()  # 0: 월요일, 6: 일요일

    # 7줄(7주)로 고정
    for week in range(7):
        cols = st.columns(7)
        for day in range(7):
            with cols[day]:
                day_idx = week * 7 + day
                day_num = day_idx - start_weekday + 1
                if 1 <= day_num <= days_in_month:
                    # 유효한 날짜
                    st.markdown(
                        f'<div class="calendar-day-container">'
                        f'<div class="calendar-day-box">{day_num}</div>'
                        f'<button data-testid="stButton"></button>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                else:
                    # 비활성화된 날짜
                    st.markdown(
                        f'<div class="calendar-day-container">'
                        f'<div class="calendar-day-box disabled-day"></div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

# 달력 렌더링 호출
render_calendar()
