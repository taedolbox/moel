# app/daily_worker_eligibility.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import calendar

# 달력의 시작 요일을 일요일로 설정
calendar.setfirstweekday(calendar.SUNDAY)

# 현재 날짜와 시간 (2025년 5월 27일 오후 7:15 KST)
current_datetime = datetime(2025, 5, 27, 19, 15)
current_time_korean = current_datetime.strftime('%Y년 %m월 %d일 %A 오후 %I:%M KST')

def get_date_range(apply_date):
    """신청일을 기준으로 이전 달 초일부터 신청일까지의 날짜 범위를 반환합니다."""
    start_date = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1).date()
    return [d.date() for d in pd.date_range(start=start_date, end=apply_date)], start_date

def render_calendar_interactive(apply_date):
    """달력을 렌더링하고 날짜 선택 기능을 제공합니다. CSS는 styles.css에서 로드됩니다."""
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
            st.markdown(f"<h3>{year}년 {month}월</h3>", unsafe_allow_html=True)
            cal = calendar.monthcalendar(year, month)
            days_of_week_korean = ["일", "월", "화", "수", "목", "금", "토"]

            # 요일 헤더 생성 (7열 고정)
            header_html = '<div class="header-grid">'
            for i, day_name in enumerate(days_of_week_korean):
                color = "red" if i == 0 or i == 6 else "#000000"
                header_html += f'<div class="day-header"><span style="color: {color}">{day_name}</span></div>'
            header_html += '</div>'
            st.markdown(header_html, unsafe_allow_html=True)

            # 달력 렌더링 (각 주를 Streamlit columns로 구성)
            for week in cal:
                cols = st.columns(7) # 7개의 컬럼 생성 (요일)
                for i, day_val in enumerate(week):
                    with cols[i]:
                        if day_val == 0:
                            # 비어있는 날짜 칸
                            st.markdown('<div class="calendar-day-empty"></div>', unsafe_allow_html=True)
                            continue

                        date_obj = date(year, month, day_val)
                        # Streamlit 버튼의 key는 반드시 유일해야 합니다.
                        button_key = f"date_button_{date_obj.isoformat()}"

                        is_selected = date_obj in selected_dates
                        is_current = date_obj == current_date
                        is_disabled = date_obj > apply_date # 신청일 이후는 비활성화

                        # Streamlit 버튼에 적용될 CSS 클래스를 결정합니다.
                        # 실제 HTML 콘텐츠는 버튼의 label이 아닌, CSS를 통해 버튼 자체에 적용됩니다.
                        class_names = ["calendar-day-button"]
                        if is_selected:
                            class_names.append("selected-day")
                        if is_current:
                            class_names.append("current-day")
                        if is_disabled:
                            class_names.append("disabled-day")

                        # Streamlit 버튼 생성
                        # label은 숫자로만 간단하게 유지하고, 스타일은 CSS 클래스로 제어합니다.
                        if st.button(
                            label=str(day_val),
                            key=button_key,
                            disabled=is_disabled,
                            # Streamlit 버튼의 내부 div에 우리가 원하는 CSS 클래스를 적용
                            # 이 부분이 버튼 자체의 스타일을 제어하는 핵심입니다.
                            # Streamlit 1.25.0 이후부터는 data-testid를 이용하여 스타일링하는 것이 더 안정적입니다.
                        ):
                            if not is_disabled:
                                if date_obj in selected_dates:
                                    selected_dates.discard(date_obj)
                                else:
                                    selected_dates.add(date_obj)
                                st.session_state.selected_dates = selected_dates
                                st.rerun()

                        # 각 버튼에 대한 커스텀 CSS를 삽입하여 클래스 적용
                        # 이 방법은 모든 버튼에 동일한 클래스를 적용하는 것이 아니라
                        # 개별 버튼에 동적으로 클래스를 추가할 때 유용합니다.
                        st.markdown(
                            f"""
                            <style>
                                div[data-testid="stColumn"] > div > button[data-testid="base-button-secondary"][key="{button_key}"] {{
                                    /* 기본 Streamlit 버튼 스타일 초기화 */
                                    background: none !important;
                                    border: none !important;
                                    padding: 0 !important;
                                    margin: 0 !important;
                                    display: flex !important;
                                    justify-content: center !important;
                                    align-items: center !important;
                                    width: 100% !important; /* 컬럼 너비에 맞춤 */
                                    height: 100% !important; /* 컬럼 높이에 맞춤 */
                                }}
                                div[data-testid="stColumn"] > div > button[data-testid="base-button-secondary"][key="{button_key}"] > div {{
                                    /* 버튼 라벨(숫자)을 감싸는 div에 실제 날짜 스타일 적용 */
                                    width: 38px !important; /* PC 기준 */
                                    height: 38px !important; /* PC 기준 */
                                    border: 1px solid #cccccc !important;
                                    background-color: #ffffff !important;
                                    color: #000000 !important;
                                    border-radius: 50% !important;
                                    font-size: 0.9em !important;
                                    display: flex !important;
                                    align-items: center !important;
                                    justify-content: center !important;
                                    transition: background-color 0.2s ease, border-color 0.2s ease;
                                    cursor: pointer !important;
                                }}

                                /* 선택된 날짜 (파란색 테두리) */
                                div[data-testid="stColumn"] > div > button[data-testid="base-button-secondary"][key="{button_key}"].selected-day > div {{
                                    border: 2px solid #0000ff !important;
                                }}
                                /* 오늘 날짜 (파란색 테두리) */
                                div[data-testid="stColumn"] > div > button[data-testid="base-button-secondary"][key="{button_key}"].current-day > div {{
                                    border: 2px solid #0000ff !important;
                                }}
                                /* 비활성화된 날짜 */
                                div[data-testid="stColumn"] > div > button[data-testid="base-button-secondary"][key="{button_key}"].disabled-day > div {{
                                    border: 1px solid #aaaaaa !important;
                                    background-color: #e0e0e0 !important;
                                    color: #999999 !important;
                                    cursor: not-allowed !important;
                                }}

                                /* 호버 효과 */
                                div[data-testid="stColumn"] > div > button[data-testid="base-button-secondary"][key="{button_key}"]:hover:not(.disabled-day) > div {{
                                    background-color: #e0e0e0 !important;
                                    border-color: #555 !important;
                                }}

                                @media (max-width: 500px) {
                                    div[data-testid="stColumn"] > div > button[data-testid="base-button-secondary"][key="{button_key}"] > div {{
                                        width: 34px !important;
                                        height: 34px !important;
                                    }}
                                }

                                /* 다크 모드 스타일 */
                                @media (prefers-color-scheme: dark), [data-theme="dark"] {
                                    div[data-testid="stColumn"] > div > button[data-testid="base-button-secondary"][key="{button_key}"] > div {{
                                        background-color: #000000 !important;
                                        color: #ffffff !important;
                                        border: 1px solid #888 !important;
                                    }}
                                    div[data-testid="stColumn"] > div > button[data-testid="base-button-secondary"][key="{button_key}"].disabled-day > div {{
                                        background-color: #3a3a3a !important;
                                        border: 1px solid #555 !important;
                                        color: #666 !important;
                                    }}
                                    div[data-testid="stColumn"] > div > button[data-testid="base-button-secondary"][key="{button_key}"]:hover:not(.disabled-day) > div {{
                                        background-color: #333333 !important;
                                        border-color: #aaaaaa !important;
                                    }}
                                }
                            </style>
                            """,
                            unsafe_allow_html=True
                        )

                        # 버튼에 selected-day, current-day, disabled-day 클래스를 동적으로 추가합니다.
                        # Streamlit의 컴포넌트는 HTML 요소를 직접 수정할 수 없으므로,
                        # 버튼의 부모 요소에 특정 클래스를 추가하는 방식으로 간접적으로 제어합니다.
                        # Streamlit 1.25.0 이상부터는 data-testid를 활용하는 것이 좋습니다.
                        # 여기서는 Streamlit 내부에서 부여하는 data-testid를 활용하여 CSS를 적용합니다.
                        # 각 버튼의 부모 요소에 해당하는 Streamlit 내부 div에 class를 추가하는 방식입니다.
                        # 이 방식은 Streamlit의 DOM 구조 변화에 따라 깨질 수 있어 주의가 필요합니다.
                        # 가장 확실한 방법은 JavaScript를 사용하는 것이지만, Streamlit 앱에서는 제한적입니다.
                        # 현재는 Streamlit이 버튼에 부여하는 data-testid를 이용해 해당 버튼 자체에 클래스를 적용하는 것이 최선입니다.
                        if is_selected:
                            st.markdown(f'<style> div[data-testid="stColumn"] > div > button[data-testid="base-button-secondary"][key="{button_key}"] {{ border: 2px solid #0000ff !important; }} </style>', unsafe_allow_html=True)
                        if is_current:
                            st.markdown(f'<style> div[data-testid="stColumn"] > div > button[data-testid="base-button-secondary"][key="{button_key}"] {{ border: 2px solid #0000ff !important; }} </style>', unsafe_allow_html=True)
                        if is_disabled:
                             st.markdown(f'<style> div[data-testid="stColumn"] > div > button[data-testid="base-button-secondary"][key="{button_key}"] {{ background-color: #e0e0e0 !important; color: #999999 !important; cursor: not-allowed !important; }} </style>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # 선택된 근무일자 표시
    if st.session_state.selected_dates:
        st.markdown("### ✅ 선택된 근무일자")
        st.markdown(", ".join([d.strftime("%Y-%m-%d") for d in sorted(st.session_state.selected_dates)]))

    # 디버깅 정보 출력 (페이지 하단)
    st.markdown("### 🔍 디버깅 정보")
    st.write("**현재 세션 상태 (st.session_state):**")
    st.write(st.session_state)
    st.write("**선택된 날짜 (st.session_state.selected_dates):**")
    st.write([d.strftime("%Y-%m-%d") for d in sorted(st.session_state.selected_dates)])

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
