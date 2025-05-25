import streamlit as st
import calendar
from datetime import datetime, date, timedelta
import pandas as pd

# 달력의 시작 요일을 일요일로 설정
calendar.setfirstweekday(calendar.SUNDAY)

# 현재 날짜 (테스트용)
current_date = date(2025, 5, 25)

def get_date_range(apply_date):
    """신청일 기준 직전 달 초일부터 신청일까지의 기간을 반환합니다."""
    start_date = (apply_date.replace(day=1) - pd.DateOffset(months=1)).date()
    return start_date, apply_date

def render_calendar(apply_date):
    """직전 달과 신청일이 속한 달의 달력을 렌더링하고 날짜 선택 기능을 제공합니다."""
    if 'selected_dates' not in st.session_state:
        st.session_state.selected_dates = set()

    selected_dates = st.session_state.selected_dates
    start_date, end_date = get_date_range(apply_date)

    # 표시할 월 목록 (직전 달과 현재 달)
    months_to_display = sorted(set((d.year, d.month) for d in pd.date_range(start=start_date, end=end_date)))

    # 간단한 CSS 스타일링
    st.markdown("""
    <style>
    .calendar-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-bottom: 20px;
    }
    .calendar-container {
        display: grid;
        grid-template-columns: repeat(7, 40px);
        gap: 5px;
        justify-content: center;
        margin: 10px 0;
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: 5px;
        background-color: #f9f9f9;
    }
    .calendar-day {
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        font-size: 14px;
        cursor: pointer;
        background-color: #ffffff;
        border: 1px solid #ddd;
    }
    .calendar-day:hover {
        background-color: #e0e0e0;
    }
    .calendar-day.selected {
        background-color: #4CAF50;
        color: #ffffff;
        border: 1px solid #4CAF50;
    }
    .calendar-day.disabled {
        background-color: #e0e0e0;
        color: #666;
        cursor: not-allowed;
    }
    .calendar-day.current {
        border: 2px solid blue;
    }
    .day-header {
        text-align: center;
        font-weight: bold;
        font-size: 14px;
        padding: 5px 0;
    }
    .day-header:first-child, .day-header:last-child {
        color: red;
    }
    h3 {
        text-align: center;
        margin: 10px 0;
        font-size: 18px;
    }
    </style>
    """, unsafe_allow_html=True)

    def toggle_date(date_obj):
        """날짜 선택/해제 함수"""
        if date_obj > apply_date:  # 신청일 이후는 선택 불가
            return
        if date_obj in selected_dates:
            selected_dates.remove(date_obj)
        else:
            selected_dates.add(date_obj)
        st.session_state.selected_dates = selected_dates
        st.rerun()

    # 각 월별 달력 렌더링
    for year, month in months_to_display:
        with st.container():
            st.markdown(f"<h3>{year}년 {month}월</h3>", unsafe_allow_html=True)
            
            # 요일 헤더
            days_of_week = ["일", "월", "화", "수", "목", "금", "토"]
            st.markdown('<div class="calendar-container">', unsafe_allow_html=True)
            for day_name in days_of_week:
                st.markdown(f'<div class="day-header">{day_name}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # 달력 날짜
            cal = calendar.monthcalendar(year, month)
            st.markdown('<div class="calendar-container">', unsafe_allow_html=True)
            for week in cal:
                for day in week:
                    if day == 0:
                        st.markdown('<div class="calendar-day"></div>', unsafe_allow_html=True)
                        continue
                    date_obj = date(year, month, day)
                    is_selected = date_obj in selected_dates
                    is_current = date_obj == current_date
                    is_disabled = date_obj > apply_date
                    class_name = "calendar-day"
                    if is_selected:
                        class_name += " selected"
                    if is_current:
                        class_name += " current"
                    if is_disabled:
                        class_name += " disabled"

                    st.markdown(
                        f'<div class="{class_name}" '
                        f'onclick="document.getElementById(\'button_{date_obj}\').click()">'
                        f'{day}</div>',
                        unsafe_allow_html=True
                    )
                    # 숨겨진 버튼으로 클릭 이벤트 처리
                    st.button("", key=f"button_{date_obj}", on_click=toggle_date, args=(date_obj,), disabled=is_disabled)
            st.markdown('</div>', unsafe_allow_html=True)

    # 선택된 날짜 출력
    if selected_dates:
        st.markdown("### 선택된 날짜")
        st.write(", ".join(sorted(d.strftime("%Y-%m-%d") for d in selected_dates)))

    return selected_dates

def main():
    """메인 함수"""
    st.title("달력 날짜 선택기")

    # 신청일 입력
    apply_date = st.date_input("신청일자를 선택하세요", value=current_date)

    # 달력 렌더링
    st.markdown("### 달력")
    selected_dates = render_calendar(apply_date)

if __name__ == "__main__":
    main()
