import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import calendar
from streamlit.components.v1 import html

# CSS 파일 로드
def load_css():
    with open("style.css", "r") as f:
        css = f"<style>{f.read()}</style>"
        st.markdown(css, unsafe_allow_html=True)

# 달력 렌더링 함수
def render_calendar(year, month, selected_date):
    # 달력 제목
    month_name = f"{year}년 {month}월"
    st.markdown(f'<div class="calendar-wrapper"><h3>{month_name}</h3></div>', unsafe_allow_html=True)

    # 요일 헤더
    cols = st.columns(7)
    days = ["월", "화", "수", "목", "금", "토", "일"]
    for col, day in zip(cols, days):
        col.markdown(f'<div class="day-header">{day}</div>', unsafe_allow_html=True)

    # 달력 데이터 준비
    cal = calendar.monthcalendar(year, month)
    today = datetime.now().date()

    for week in cal:
        cols = st.columns(7)
        for day_idx, day in enumerate(week):
            with cols[day_idx]:
                if day == 0:  # 빈 날짜
                    st.markdown('<div class="calendar-day-container"></div>', unsafe_allow_html=True)
                    continue
                date = datetime(year, month, day).date()
                # 자격 확인 더미 로직 (예: 특정 날짜는 비활성화)
                is_disabled = date < today  # 과거 날짜 비활성화
                # 클래스 설정
                classes = []
                if date == selected_date:
                    classes.append("selected-day")
                if date == today:
                    classes.append("current-day")
                if is_disabled:
                    classes.append("disabled-day")
                class_str = " ".join(classes)
                # 숫자 표시
                st.markdown(
                    f'<div class="calendar-day-container">'
                    f'<div class="calendar-day-box {class_str}">'
                    f'<div class="selection-mark"></div>'
                    f'{day}</div></div>',
                    unsafe_allow_html=True
                )
                # 선택 버튼 (숫자 라벨 포함)
                st.button(
                    f"{day}",
                    key=f"day_{year}_{month}_{day}",
                    on_click=select_date,
                    args=(date,),
                    disabled=is_disabled,
                    help=f"Select {day}"
                )

# 날짜 선택 콜백
def select_date(date):
    st.session_state.selected_date = date

# 근로자 자격 확인 더미 함수
def check_eligibility(date):
    # 예: 특정 날짜에 따라 자격 여부 결정
    if date.weekday() in [5, 6]:  # 주말은 자격 없음
        return "주말 근무 불가"
    return "근무 가능"

# 메인 앱
def main():
    load_css()
    st.title("일별 근로자 자격 확인")

    # 세션 상태 초기화
    if "selected_date" not in st.session_state:
        st.session_state.selected_date = datetime.now().date()

    # 연도와 월 선택
    col1, col2 = st.columns(2)
    with col1:
        year = st.number_input("연도", min_value=2020, max_value=2030, value=2025)
    with col2:
        month = st.number_input("월", min_value=1, max_value=12, value=5)

    # 달력 렌더링
    render_calendar(year, month, st.session_state.selected_date)

    # 선택된 날짜와 자격 표시
    selected_date = st.session_state.selected_date
    st.write(f"선택된 날짜: {selected_date}")
    eligibility = check_eligibility(selected_date)
    st.write(f"자격 상태: {eligibility}")

if __name__ == "__main__":
    main()
    # JavaScript로 화면 너비 업데이트
    screen_width_script = """
    <script>
        function updateScreenWidth() {
            window.parent.window.dispatchEvent(new CustomEvent('screen_width_event', { detail: window.innerWidth }));
        }
        window.addEventListener('resize', updateScreenWidth);
        updateScreenWidth();
    </script>
    """
    html(screen_width_script)

    def update_screen_width():
        if 'screen_width_event' in st.session_state:
            st.session_state.screen_width = st.session_state.screen_width_event

    st.session_state.screen_width_event = st.experimental_get_query_params().get("screen_width", [1000])[0]
    update_screen_width()

    daily_worker_eligibility_app()
