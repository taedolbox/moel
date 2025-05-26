import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import calendar
from streamlit.components.v1 import html

# 달력의 시작 요일 설정
calendar.setfirstweekday(calendar.SUNDAY)

# 현재 날짜 및 시간 (2025년 5월 26일 오후 8:43 KST)
current_datetime = datetime(2025, 5, 26, 20, 43)
current_time_korean = current_datetime.strftime('%Y년 %m월 %d일 %A %p %I:%M KST')

# CSS 로드
st.markdown('<link rel="stylesheet" href="/static/styles.css">', unsafe_allow_html=True)

def get_date_range(apply_date):
    """신청일을 기준으로 이전 달 초일부터 신청일까지."""
    if not isinstance(apply_date, (datetime, date)):
        raise TypeError("apply_date must be a datetime or date object")
    if isinstance(apply_date, datetime):
        apply_date = apply_date.date()
    start_date = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1).date()
    return [d.date() for d in pd.date_range(start=start_date, end=apply_date)], start_date

def render_calendar_interactive(apply_date):
    """달력을 렌더링하고 날짜 선택 기능을 제공합니다. CSS는 styles.css에서."""
    # 초기 세션 상태 설정
    if 'selected_dates' not in st.session_state:
        st.session_state.selected_dates = set()
    if 'rerun_trigger' not in st.session_state:
        st.session_state.rerun_trigger = False

    selected_dates = st.session_state.selected_dates
    current_date = current_datetime.date()

    # 달력 표시 월 범위 계산
    start_date_for_calendar = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1).date()
    end_date_for_calendar = apply_date
    months_to_display = sorted(list(set((d.year, d.month) for d in pd.date_range(start=start_date_for_calendar, end=end_date_for_calendar))))

    # 달력 컨테이너
    with st.container():
        st.markdown('<div class="calendar-wrapper">', unsafe_allow_html=True)
        for year, month in months_to_display:
            st.markdown(f'<h3>{year}년 {month}월</h3>', unsafe_allow_html=True)
            cal = calendar.monthcalendar(year, month)
            days_of_week = ["일", "월", "화", "수", "목", "금", "토"]

            # 요일 헤더 (직접 HTML로 렌더링)
            header_html = '<div class="header-wrapper">'
            for i, day_name in enumerate(days_of_week):
                color = "red" if i == 0 else "#000000"
                header_html += f'<div class="day-header" style="color: {color};">{day_name}</div>'
            header_html += '</div>'
            st.markdown(header_html, unsafe_allow_html=True)

            # 달력 본체 (직접 HTML로 7열 그리드)
            calendar_html = '<div class="calendar-grid">'
            for week in cal:
                for day in week:
                    if day == 0:
                        calendar_html += '<div class="calendar-day-container"></div>'
                        continue
                    date_obj = date(year, month, day)
                    if date_obj > apply_date:
                        calendar_html += (
                            f'<div class="calendar-day-container">'
                            f'<div class="calendar-day-box disabled-day">{day}</div>'
                            '</div>'
                        )
                        continue

                    is_selected = date_obj in selected_dates
                    is_current = date_obj == current_date
                    class_name = "calendar-day-box"
                    if is_selected:
                        class_name += " selected-day"
                    if is_current:
                        class_name += " current-day"

                    calendar_html += (
                        f'<div class="calendar-day-container">'
                        f'<div class="selection-mark"></div>'
                        f'<div class="{class_name}">{day}</div>'
                        f'</div>'
                    )

                    # 버튼을 별도로 렌더링
                    st.button("", key=f"date_{date_obj.isoformat()}", on_click=toggle_date, args=(date_obj,))
            
            calendar_html += '</div>'
            st.markdown(calendar_html, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.rerun_trigger:
        st.session_state.rerun_trigger = False
        st.rerun()

    if st.session_state.selected_dates:
        st.markdown("### ✅ 선택된 근무일자")
        st.markdown(", ".join([d.strftime("%Y-%m-%d") for d in sorted(st.session_state.selected_dates)]))

    return st.session_state.selected_dates

def toggle_date(date_obj):
    """날짜 선택 토글 및 세션 상태 업데이트."""
    if date_obj in st.session_state.selected_dates:
        st.session_state.selected_dates.remove(date_obj)
    else:
        st.session_state.selected_dates.add(date_obj)
    st.session_state.rerun_trigger = True

def daily_worker_eligibility_app():
    """일용근로자 수급자격 요건 모의계산 앱."""
    # 사이드바 토글 상태 초기화
    if 'sidebar_visible' not in st.session_state:
        st.session_state.sidebar_visible = True  # PC 라이트 기본

    # 모바일 감지: JavaScript로 화면 너비 확인
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
    screen_width = st.session_state.get('screen_width', 1000)  # 기본값: PC
    is_mobile = screen_width <= 500

    # 사이드바 토글 버튼 (모바일에서만 표시)
    if is_mobile:
        toggle_button = st.button("사이드바 토글", key="sidebar_toggle")
        if toggle_button:
            st.session_state.sidebar_visible = not st.session_state.sidebar_visible

    # 사이드바 렌더링
    if st.session_state.sidebar_visible:
        with st.sidebar:
            st.markdown("### 📋 정보")
            st.markdown("이 앱은 일용근로자 및 건설일용근로자의 수급자격 요건을 모의계산합니다.")
            st.markdown("- **조건 1**: 신청일이 속한 달의 직전 달 초일부터 신청일까지 근로일 수가 총 일수의 1/3 미만.")
            st.markdown("- **조건 2 (건설일용근로자)**: 신청일 직전 14일간 근무 사실 없음.")

    st.header("일용근로자 수급자격 요건 모의계산")

    # 현재 날짜와 시간 표시
    st.markdown(f"**오늘 날짜와 시간**: {current_time_korean}", unsafe_allow_html=True)

    # 요건 조건 설명
    st.markdown("### 📋 요건 조건")
    st.markdown("- **조건 1**: 수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지의 근로일 수가 총 일수의 1/3 미만이어야 합니다.")
    st.markdown("- **조건 2 (건설일용근로자만 해당)**: 수급자격 인정신청일 직전 14일간 근무 사실이 없어야 합니다 (신청일 제외).")
    st.markdown("---")

    # 수급자격 신청일 선택
    apply_date = st.date_input("수급자격 신청일을 선택하세요", value=current_datetime.date(), key="apply_date_input")

    # 날짜 범위 및 시작일 가져오기
    date_range_objects, start_date = get_date_range(apply_date)

    st.markdown("---")
    st.markdown("#### ✅ 근무일 선택 달력")
    selected_dates = render_calendar_interactive(apply_date)
    st.markdown("---")

    # 조건 1 계산 및 표시
    total_days = len(date_range_objects)
    worked_days = len(selected_dates)
    threshold = total_days / 3

    st.markdown(f"- 총 기간 일수: **{total_days}일**")
    st.markdown(f"- 기준 (총일수의 1/3): **{threshold:.1f}일**")
    st.markdown(f"- 선택한 근무일 수: **{worked_days}일**")

    condition1 = worked_days < threshold
    st.markdown(
        f'<div class="result-text">'
        f'<p>{"✅ 조건 1 충족: 근무일 수가 기준 미만입니다." if condition1 else "❌ 조건 1 불충족: 근무일 수가 기준 이상입니다."}</p>'
        f'</div>',
        unsafe_allow_html=True
    )

    # 조건 2 계산 및 표시 (건설일용근로자 기준)
    fourteen_days_prior_end = apply_date - timedelta(days=1)
    fourteen_days_prior_start = fourteen_days_prior_end - timedelta(days=13)
    fourteen_days_prior_range = [d.date() for d in pd.date_range(start=fourteen_days_prior_start, end=fourteen_days_prior_end)]
    no_work_14_days = all(day not in selected_dates for day in fourteen_days_prior_range)
    condition2 = no_work_14_days

    st.markdown(
        f'<div class="result-text">'
        f'<p>{"✅ 조건 2 충족: 신청일 직전 14일간(" + fourteen_days_prior_start.strftime("%Y-%m-%d") + " ~ " + fourteen_days_prior_end.strftime("%Y-%m-%d") + ") 근무내역이 없습니다." if no_work_14_days else "❌ 조건 2 불충족: 신청일 직전 14일간(" + fourteen_days_prior_start.strftime("%Y-%m-%d") + " ~ " + fourteen_days_prior_end.strftime("%Y-%m-%d") + ") 내 근무기록이 있습니다."}</p>'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown("---")

    # 조건 1 불충족 시 미래 신청일 제안
    if not condition1:
        st.markdown("### 📅 조건 1을 충족하려면 언제 신청해야 할까요?")
        found_suggestion = False
        for i in range(1, 31):
            future_date = apply_date + timedelta(days=i)
            date_range_future_objects, _ = get_date_range(future_date)
            total_days_future = len(date_range_future_objects)
            threshold_future = total_days_future / 3
            worked_days_future = sum(1 for d in selected_dates if d <= future_date)

            if worked_days_future < threshold_future:
                st.markdown(
                    f'<div class="result-text">'
                    f'<p>✅ <b>{future_date.strftime("%Y-%m-%d")}</b> 이후에 신청하면 요건을 충족할 수 있습니다.</p>'
                    f'</div>',
                    unsafe_allow_html=True
                )
                found_suggestion = True
                break
        if not found_suggestion:
            st.markdown(
                f'<div class="result-text">'
                f'<p>❗ 앞으로 30일 이내에는 요건을 충족할 수 없습니다. 근무일 수를 조정하거나 더 먼 날짜를 고려하세요.</p>'
                f'</div>',
                unsafe_allow_html=True
            )

    # 조건 2 불충족 시 미래 신청일 제안 (건설일용근로자 기준)
    if not condition2:
        st.markdown("### 📅 조건 2를 충족하려면 언제 신청해야 할까요?")
        last_worked_day = max((d for d in selected_dates if d < apply_date), default=None)
        if last_worked_day:
            suggested_date = last_worked_day + timedelta(days=15)
            st.markdown(
                f'<div class="result-text">'
                f'<p>✅ <b>{suggested_date.strftime("%Y-%m-%d")}</b> 이후에 신청하면 조건 2를 충족할 수 있습니다.</p>'
                f'</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="result-text">'
                f'<p>이미 최근 14일간 근무내역이 없으므로, 신청일을 조정할 필요는 없습니다.</p>'
                f'</div>',
                unsafe_allow_html=True
            )

    st.subheader("📌 최종 판단")
    if condition1:
        st.markdown(
            f'<div class="result-text">'
            f'<p>✅ 일반일용근로자: 신청 가능<br>'
            f'<b>수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지({start_date.strftime("%Y-%m-%d")} ~ {apply_date.strftime("%Y-%m-%d")}) 근로일 수의 합이 같은 기간 동안의 총 일수의 3분의 1 미만</b></p>'
            f'</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="result-text">'
            f'<p>❌ 일반일용근로자: 신청 불가능<br>'
            f'<b>수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지({start_date.strftime("%Y-%m-%d")} ~ {apply_date.strftime("%Y-%m-%d")}) 근로일 수의 합이 같은 기간 동안의 총 일수의 3분의 1 이상입니다.</b></p>'
            f'</div>',
            unsafe_allow_html=True
        )

    if condition1 and condition2:
        st.markdown(
            f'<div class="result-text">'
            f'<p>✅ 건설일용근로자: 신청 가능<br>'
            f'<b>수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지({start_date.strftime("%Y-%m-%d")} ~ {apply_date.strftime("%Y-%m-%d")}) 근로일 수의 합이 총 일수의 3분의 1 미만이고, 신청일 직전 14일간({fourteen_days_prior_start.strftime("%Y-%m-%d")} ~ {fourteen_days_prior_end.strftime("%Y-%m-%d")}) 근무 사실이 없음을 확인합니다.</b></p>'
            f'</div>',
            unsafe_allow_html=True
        )
    else:
        error_message = "❌ 건설일용근로자: 신청 불가능<br>"
        if not condition1:
            error_message += f"<b>수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지({start_date.strftime('%Y-%m-%d')} ~ {apply_date.strftime('%Y-%m-%d')}) 근로일 수의 합이 같은 기간 동안의 총 일수의 3분의 1 이상입니다.</b><br>"
        if not condition2:
            error_message += f"<b>신청일 직전 14일간({fourteen_days_prior_start.strftime('%Y-%m-%d')} ~ {fourteen_days_prior_end.strftime('%Y-%m-%d')}) 근무내역이 있습니다.</b>"
        st.markdown(
            f'<div class="result-text">'
            f'<p>{error_message}</p>'
            f'</div>',
            unsafe_allow_html=True
        )

if __name__ == "__main__":
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
