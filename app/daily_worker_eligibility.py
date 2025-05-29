# daily_worker_eligibility.py
import streamlit as st
import datetime

# 날짜 선택 상태 저장
if 'selected_dates' not in st.session_state:
    st.session_state.selected_dates = set()

def toggle_date(date_str):
    if date_str in st.session_state.selected_dates:
        st.session_state.selected_dates.remove(date_str)
    else:
        st.session_state.selected_dates.add(date_str)

def render_calendar(year: int, month: int):
    st.markdown(f"### {year}년 {month}월")

    # CSS for grid layout and circular highlighting
    st.markdown(
        """
        <style>
        .calendar {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 4px;
            text-align: center;
            margin-bottom: 1rem;
        }
        .day {
            padding: 0.6rem 0;
            border-radius: 50%;
            cursor: pointer;
            font-weight: 500;
            background-color: #f0f0f0;
            transition: 0.2s;
        }
        .day:hover {
            background-color: #d0d0ff;
        }
        .selected {
            background-color: #4A90E2 !important;
            color: white;
        }
        @media (max-width: 600px) {
            .calendar {
                font-size: 0.8rem;
                gap: 2px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # 달력 계산
    first_day = datetime.date(year, month, 1)
    start_weekday = first_day.weekday()  # 월요일=0
    start_weekday = (start_weekday + 1) % 7  # 일요일=0 기준으로 변경
    days_in_month = (datetime.date(year + int(month / 12), (month % 12) + 1, 1) - first_day).days

    # 날짜 렌더링
    calendar_html = '<div class="calendar">'
    calendar_html += '<div></div>' * start_weekday

    for day in range(1, days_in_month + 1):
        date = datetime.date(year, month, day)
        date_str = date.isoformat()
        selected_class = "selected" if date_str in st.session_state.selected_dates else ""
        calendar_html += f'<div class="day {selected_class}" onclick="fetch(\'/?toggle={date_str}\', {{method: \'POST\'}}).then(() => window.location.reload())">{day}</div>'

    calendar_html += '</div>'
    st.markdown(calendar_html, unsafe_allow_html=True)

# URL 파라미터로부터 클릭 처리 (st.query_params 사용)
toggle_list = st.query_params.get("toggle")
toggle = toggle_list[0] if toggle_list else None
if toggle:
    toggle_date(toggle)
    st.experimental_set_query_params()  # 쿼리 파라미터 초기화

# 렌더링
render_calendar(2025, 5)

# 선택된 날짜 표시
if st.session_state.selected_dates:
    st.markdown("#### 선택한 날짜")
    selected_sorted = sorted(st.session_state.selected_dates)
    st.write(", ".join(selected_sorted))
