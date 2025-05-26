import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import calendar
import os # os 모듈 임포트

# 달력의 시작 요일을 일요일로 설정
calendar.setfirstweekday(calendar.SUNDAY)

# 현재 날짜와 시간 (2025년 5월 26일 오후 3:36 KST)
current_datetime = datetime(2025, 5, 26, 15, 36)
current_time_korean = current_datetime.strftime('%Y년 %m월 %d일 %A 오후 %I:%M KST')

# --- 외부 CSS 파일 로드 함수 ---
def load_css(file_name):
    # CSS 파일의 절대 경로를 구성합니다.
    # 이 함수를 호출하는 스크립트와 styles.css가 같은 디렉토리에 있다고 가정합니다.
    css_path = os.path.join(os.path.dirname(__file__), file_name)
    try:
        with open(css_path) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"CSS 파일을 찾을 수 없습니다: {css_path}. 'styles.css'가 올바른 디렉토리에 있는지 확인하세요.")

# styles.css 로드
load_css('styles.css')

# --- 기존 함수들 ---
def get_date_range(apply_date):
    """신청일을 기준으로 이전 달 초일부터 신청일까지의 날짜 범위를 반환합니다."""
    start_date = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1).date()
    return [d.date() for d in pd.date_range(start=start_date, end=apply_date)], start_date

def render_calendar_interactive(apply_date):
    """달력을 렌더링합니다. CSS는 styles.css에서 로드됩니다."""
    # 초기 세션 상태 설정
    if 'selected_dates' not in st.session_state:
        st.session_state.selected_dates = set()

    selected_dates = st.session_state.selected_dates
    current_date = current_datetime.date()

    # 달력 표시할 월 범위 계산
    start_date_for_calendar = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1).date()
    end_date_for_calendar = apply_date
    months_to_display = sorted(list(set((d.year, d.month) for d in pd.date_range(start=start_date_for_calendar, end=end_date_for_calendar))))

    # 달력 전용 컨테이너
    with st.container():
        st.markdown('<div class="calendar-wrapper">', unsafe_allow_html=True)

        for year, month in months_to_display:
            # 월 이름은 표시하지 않음 (이전 요청에 따라)
            cal = calendar.monthcalendar(year, month)

            # 요일 헤더 (일, 월, 화, 수, 목, 금, 토)
            cols = st.columns(7, gap="small")
            for i, day_name in enumerate(["일", "월", "화", "수", "목", "금", "토"]):
                with cols[i]:
                    color = "red" if i == 0 or i == 6 else "#000000"
                    # day-header 클래스를 적용하여 CSS 스타일을 받을 수 있도록 함
                    st.markdown(
                        f'<div class="day-header" style="color: {color}; text-align: center; font-weight: bold; margin-bottom: 5px;">{day_name}</div>',
                        unsafe_allow_html=True
                    )

            # 달력 날짜 렌더링
            for week in cal:
                cols = st.columns(7, gap="small") # 각 주마다 7개의 컬럼 생성
                for i, day in enumerate(week):
                    with cols[i]:
                        if day == 0:
                            # 해당 월에 속하지 않는 날짜는 빈 공간으로 처리
                            st.markdown('<div class="calendar-day-container"></div>', unsafe_allow_html=True)
                            continue

                        date_obj = date(year, month, day)
                        is_selected = date_obj in selected_dates
                        is_current = date_obj == current_date
                        is_disabled = date_obj > apply_date # 신청일 이후의 날짜는 비활성화

                        # 각 버튼에 고유 키 생성
                        button_key = f"day_button_{year}_{month}_{day}"

                        if is_disabled:
                            # 비활성화된 날짜는 클릭 불가능하게 일반 텍스트로 렌더링
                            st.markdown(
                                f'<div class="calendar-day-container">'
                                f'<div class="calendar-day-box disabled-day">{day}</div>'
                                f'</div>',
                                unsafe_allow_html=True
                            )
                        else:
                            # 활성화된 날짜는 클릭 가능한 버튼으로 렌더링
                            # 버튼 클릭 시 선택/선택 해제 로직
                            if st.button(str(day), key=button_key, use_container_width=True):
                                if date_obj in selected_dates:
                                    selected_dates.remove(date_obj)
                                else:
                                    selected_dates.add(date_obj)
                                st.session_state.selected_dates = selected_dates # 세션 상태 업데이트
                                st.rerun() # 변경된 상태를 반영하기 위해 앱 다시 로드

                            # CSS 클래스 적용을 위한 스타일 주입 (버튼에 직접 적용)
                            button_classes = "calendar-day-box" # 기본 클래스
                            if is_selected:
                                button_classes += " selected-day"
                            if is_current and not is_selected: # 현재 날짜이면서 선택되지 않은 경우
                                button_classes += " current-day"

                            # 버튼에 적용할 CSS 스타일 주입 (동적으로 클래스 추가)
                            st.markdown(
                                f"""
                                <style>
                                    /* 특정 버튼 키를 가진 요소에 스타일 적용 */
                                    div[data-testid="column"] > button[key="{button_key}"] {{
                                        width: 35px; /* 너비 */
                                        height: 35px; /* 높이 */
                                        min-width: 35px; /* 최소 너비 */
                                        min-height: 35px; /* 최소 높이 */
                                        border-radius: 50%; /* 원형 */
                                        display: flex;
                                        align-items: center;
                                        justify-content: center;
                                        padding: 0;
                                        margin: 0 auto;
                                        box-sizing: border-box;
                                        cursor: pointer;
                                        /* 동적으로 클래스에 따라 스타일 적용 */
                                        {'background-color: #4CAF50; color: white; border: 2px solid #4CAF50;' if is_selected else ''}
                                        {'border: 2px solid blue;' if is_current and not is_selected else ''}
                                    }}
                                    /* 호버 효과 */
                                    div[data-testid="column"] > button[key="{button_key}"]:hover {{
                                        background-color: {'#45a049' if is_selected else '#e0e0e0'} !important;
                                    }}
                                </style>
                                """,
                                unsafe_allow_html=True
                            )

        st.markdown('</div>', unsafe_allow_html=True) # calendar-wrapper 닫기

    # 현재 선택된 근무일자 목록 표시
    if st.session_state.selected_dates:
        st.markdown("### ✅ 선택된 근무일자")
        st.markdown(", ".join([d.strftime("%Y-%m-%d") for d in sorted(st.session_state.selected_dates)]))

    return st.session_state.selected_dates

def daily_worker_eligibility_app():
    """일용근로자 수급자격 요건 모의계산 앱의 메인 함수입니다."""
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
        f'<p>{"✅ 조건 2 충족: 신청일 직전 14일간(" + fourteen_days_prior_start.strftime("%Y-%m-%d") + " ~ " + fourteen_days_prior_end.strftime("%Y-%m-%d") + ") 근무내역이 없습니다." if no_work_14_days else "❌ 조건 2 불충족: 신청일 직전 14일간(" + fourteen_days_prior_start.strftime("%Y-%m-%d") + " ~ " + fourteen_days_prior_end.strftime("%Y-%m-%d") + ") 내 근무기록이 존재합니다."}</p>'
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
    # 일반일용근로자: 조건 1만 판단
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

    # 건설일용근로자: 조건 1과 조건 2 모두 판단
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
    daily_worker_eligibility_app()
