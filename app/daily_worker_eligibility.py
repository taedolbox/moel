import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import calendar
from streamlit_javascript import st_javascript # JavaScript 연동을 위함

# --- 헬퍼 함수: 날짜 범위 계산 ---
def get_date_range(apply_date):
    start_date = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1)
    return pd.date_range(start=start_date, end=apply_date), start_date

# --- JavaScript에서 호출될 Python 함수: 날짜 선택 토글 ---
def toggle_date_js(date_str):
    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    if date_obj in st.session_state.selected_dates:
        st.session_state.selected_dates.remove(date_obj)
    else:
        st.session_state.selected_dates.add(date_obj)
    st.rerun() # 상태 변경 후 앱 새로고침

# --- 캘린더 렌더링 함수 ---
def render_calendar(apply_date):
    # --- CSS 스타일 정의 (HTML 구조에 맞게 수정) ---
    st.markdown("""
    <style>
    /* 전체 블록 간격 줄이기 */
    div[data-testid="stHorizontalBlock"] {
        gap: 0.1rem !important;
    }
    div[data-testid="stHorizontalBlock"] > div {
        padding: 0 !important;
        margin: 0 !important;
    }
    /* 달력 날짜 셀 스타일 */
    .calendar-day-cell {
        display: flex;
        flex-direction: column; /* 숫자 위에 체크박스를 두기 위해 세로 배열 */
        align-items: center; /* 가운데 정렬 */
        justify-content: center;
        width: 45px !important; /* 셀 너비 조정 */
        height: 55px !important; /* 셀 높이 조정 */
        border: 1px solid #333 !important; /* 기본 테두리 */
        background-color: #1e1e1e !important;
        color: white !important;
        font-size: 1rem;
        cursor: pointer; /* 클릭 가능하도록 커서 변경 */
        border-radius: 0 !important;
        transition: all 0.2s ease;
        position: relative; /* 체크마크 절대 위치 지정을 위함 */
    }
    /* 날짜 숫자 스타일 */
    .calendar-day-number {
        font-weight: bold;
        margin-bottom: 3px; /* 체크박스와 간격 */
    }
    /* 체크박스 스타일 */
    .calendar-day-checkbox {
        width: 15px; /* 체크박스 크기 */
        height: 15px;
        accent-color: #00ff00; /* 체크박스 색상 */
        cursor: pointer;
        margin-top: 3px; /* 숫자와 간격 */
    }
    /* 비활성화된 날짜 스타일 */
    .calendar-day-cell.disabled-date {
        color: gray !important;
        background-color: #1e1e1e !important;
        cursor: not-allowed;
    }
    /* 현재 날짜 스타일 (선택 여부와 별개) */
    .calendar-day-cell.current-date {
        background-color: #0000ff !important; /* 파란색 배경 */
        color: white !important;
    }
    /* 호버 효과 */
    .calendar-day-cell:not(.disabled-date):hover {
        border: 2px solid #00ff00 !important;
        background-color: rgba(0, 255, 0, 0.2) !important;
    }
    /* 요일 헤더 스타일 */
    div[data-testid="stHorizontalBlock"] span {
        font-size: 0.9rem !important;
        text-align: center !important;
        color: white !important;
    }
    /* 월 헤더 스타일 */
    div[data-testid="stMarkdownContainer"] h3 {
        margin: 0.5rem 0 !important;
        padding: 0.2rem !important;
        background-color: #2e2e2e !important;
        text-align: center !important;
        color: white !important;
    }
    /* 모바일 반응형 */
    @media (max-width: 600px) {
        div[data-testid="stHorizontalBlock"] {
            flex-wrap: nowrap !important;
            gap: 0.1rem !important;
        }
        div[data-testid="stHorizontalBlock"] > div {
            flex: 1 !important;
            min-width: 40px !important;
            padding: 0 !important;
        }
        .calendar-day-cell {
            font-size: 0.8rem !important;
            width: 40px !important;
            height: 50px !important;
        }
        .calendar-day-checkbox {
            width: 12px;
            height: 12px;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    # --- 세션 상태 초기화 ---
    if 'selected_dates' not in st.session_state:
        st.session_state.selected_dates = set()

    selected_dates = st.session_state.selected_dates
    current_date = datetime.now().date()

    start_date = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1)
    end_date = apply_date
    months_to_display = sorted(set((d.year, d.month) for d in pd.date_range(start=start_date, end=end_date)))

    # --- 달력 렌더링 로직 ---
    for year, month in months_to_display:
        st.markdown(f"### {year}년 {month}월", unsafe_allow_html=True) # 월을 한글로 변경

        # 요일 헤더 (한글로 변경)
        days_korean = ["일", "월", "화", "수", "목", "금", "토"]
        cols = st.columns(7, gap="small")
        for i, day_name in enumerate(days_korean):
            color = "red" if i == 0 else "blue" if i == 6 else "white"
            cols[i].markdown(f"<span style='color:{color}'><strong>{day_name}</strong></span>", unsafe_allow_html=True)

        cal = calendar.monthcalendar(year, month)
        for week in cal:
            cols = st.columns(7, gap="small")
            for i, day_num in enumerate(week):
                if day_num == 0: # 빈 날짜 (이전 달/다음 달)
                    cols[i].markdown("<div class='calendar-day-cell' style='border:none; background-color:transparent;'></div>", unsafe_allow_html=True)
                else:
                    date_obj = date(year, month, day_num)
                    is_disabled = (date_obj > apply_date) # 미래 날짜 비활성화
                    is_selected = date_obj in selected_dates
                    is_current = date_obj == current_date

                    # --- HTML 구성 ---
                    classes = ["calendar-day-cell"]
                    if is_disabled:
                        classes.append("disabled-date")
                    if is_current:
                        classes.append("current-date")
                    
                    class_str = " ".join(classes)
                    date_str = date_obj.strftime('%Y-%m-%d')

                    # JavaScript 함수를 호출하기 위한 스니펫
                    onclick_js = f"window.parent.streamlit_app_callbacks.toggle_date('{date_str}');"
                    
                    # 체크박스 상태 (checked/unchecked)
                    checked_attr = "checked" if is_selected else ""
                    disabled_attr = "disabled" if is_disabled else ""

                    html_content = f"""
                    <div class='{class_str}' onclick="{'' if is_disabled else onclick_js}">
                        <span class='calendar-day-number'>{day_num}</span>
                        <input type='checkbox' class='calendar-day-checkbox' {checked_attr} {disabled_attr}
                               onclick="event.stopPropagation(); {'' if is_disabled else onclick_js}">
                    </div>
                    """
                    cols[i].markdown(html_content, unsafe_allow_html=True)
    
    # --- 선택된 근무일자 표시 (기존과 동일) ---
    if selected_dates:
        st.markdown("### ✅ 선택된 근무일자")
        st.markdown(", ".join([date.strftime("%Y-%m-%d") for date in sorted(selected_dates)]))

    return selected_dates

# --- 메인 앱 함수 ---
def daily_worker_eligibility_app():
    # 캐시 클리어 (필요시 사용, 현재는 오류 방지를 위해 제거)
    # st.cache_data.clear()
    # st.cache_resource.clear()

    st.markdown("""
<style>
div[data-testid="stRadio"] label {
    color: white !important;
    font-size: 18px !important;
}
</style>
""", unsafe_allow_html=True)

    st.header("일용근로자 수급자격 요건 모의계산")

    current_datetime = datetime.now()
    st.markdown(f"**오늘 날짜와 시간**: {current_datetime.strftime('%Y년 %m월 %d일 %A 오전 %I:%M KST')}", unsafe_allow_html=True)

    st.markdown("### 📋 요건 조건")
    st.markdown("- **조건 1**: 수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지의 근로일 수가 총 일수의 1/3 미만이어야 합니다.")
    st.markdown("- **조건 2 (건설일용근로자만 해당)**: 수급자격 인정신청일 직전 14일간 근무 사실이 없어야 합니다 (신청일 제외).")
    st.markdown("---")

    worker_type = st.radio("근로자 유형을 선택하세요", ["일반일용근로자", "건설일용근로자"])

    apply_date = st.date_input("수급자격 신청일을 선택하세요", value=datetime.now().date())
    date_range, start_date = get_date_range(apply_date)

    st.markdown("---")
    st.markdown("#### ✅ 근무일 선택 달력")
    selected_days = render_calendar(apply_date)
    st.markdown("---")

    total_days = len(date_range)
    worked_days = len(selected_days)
    threshold = total_days / 3

    st.markdown(f"- 총 기간 일수: **{total_days}일**")
    st.markdown(f"- 기준 (총일수의 1/3): **{threshold:.1f}일**")
    st.markdown(f"- 선택한 근무일 수: **{worked_days}일**")

    condition1 = worked_days < threshold
    if condition1:
        st.success("✅ 조건 1 충족: 근무일 수가 기준 미만입니다.")
    else:
        st.warning("❌ 조건 1 불충족: 근무일 수가 기준 이상입니다.")

    condition2 = False
    if worker_type == "건설일용근로자":
        fourteen_days_prior_end = apply_date - timedelta(days=1)
        fourteen_days_prior_start = fourteen_days_prior_end - timedelta(days=13)
        fourteen_days_prior = pd.date_range(start=fourteen_days_prior_start, end=fourteen_days_prior_end).date
        fourteen_days_prior_set = set(fourteen_days_prior)
        no_work_14_days = all(day not in selected_days for day in fourteen_days_prior_set)
        condition2 = no_work_14_days

        if no_work_14_days:
            st.success(f"✅ 조건 2 충족: 신청일 직전 14일간({fourteen_days_prior_start.strftime('%Y-%m-%d')} ~ {fourteen_days_prior_end.strftime('%Y-%m-%d')}) 근무내역이 없습니다.")
        else:
            st.warning(f"❌ 조건 2 불충족: 신청일 직전 14일간({fourteen_days_prior_start.strftime('%Y-%m-%d')} ~ {fourteen_days_prior_end.strftime('%Y-%m-%d')}) 내 근무기록이 존재합니다.")

    st.markdown("---")

    if not condition1:
        st.markdown("### 📅 조건 1을 충족하려면 언제 신청해야 할까요?")
        future_dates = [apply_date + timedelta(days=i) for i in range(1, 31)]
        found_suggestion = False
        for future_date in future_dates:
            date_range_future, _ = get_date_range(future_date)
            total_days_future = len(date_range_future)
            threshold_future = total_days_future / 3
            worked_days_future = sum(1 for d in selected_days if d <= future_date)
            if worked_days_future < threshold_future:
                st.info(f"✅ **{future_date.strftime('%Y-%m-%d')}** 이후에 신청하면 요건을 충족할 수 있습니다.")
                found_suggestion = True
                break
        if not found_suggestion:
            st.warning("❗앞으로 30일 이내에는 요건을 충족할 수 없습니다. 근무일 수를 조정하거나 더 먼 날짜를 고려하세요.")

    if worker_type == "건설일용근로자" and not condition2:
        st.markdown("### 📅 조건 2를 충족하려면 언제 신청해야 할까요?")
        past_worked_days = [d for d in selected_days if d < apply_date]
        last_worked_day = max(past_worked_days) if past_worked_days else None

        if last_worked_day:
            suggested_date = last_worked_day + timedelta(days=15)
            st.info(f"✅ **{suggested_date.strftime('%Y-%m-%d')}** 이후에 신청하면 조건 2를 충족할 수 있습니다.")
        else:
            st.info("이미 신청일 직전 14일간 근무내역이 없으므로, 신청일을 조정할 필요는 없습니다.")

    st.subheader("📌 최종 판단")
    if worker_type == "일반일용근로자":
        if condition1:
            st.success(f"✅ 일반일용근로자 요건 충족\n\n**수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지({start_date.strftime('%Y-%m-%d')} ~ {apply_date.strftime('%Y-%m-%d')}) 근로일 수의 합이 같은 기간 동안의 총 일수의 3분의 1 미만**")
        else:
            st.error("❌ 일반일용근로자 요건 미충족\n\n**총 일수의 3분의 1 이상 근로 사실이 확인되어 요건을 충족하지 못합니다.**")
    else: # 건설일용근로자
        fourteen_days_prior_end = apply_date - timedelta(days=1)
        fourteen_days_prior_start = fourteen_days_prior_end - timedelta(days=13)
        if condition1 or condition2:
            st.success(f"✅ 건설일용근로자 요건 충족\n\n**수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지({start_date.strftime('%Y-%m-%d')} ~ {apply_date.strftime('%Y-%m-%d')}) 근로일 수의 합이 총 일수의 3분의 1 미만임을 확인하거나, 신청일 직전 14일간({fourteen_days_prior_start.strftime('%Y-%m-%d')} ~ {fourteen_days_prior_end.strftime('%Y-%m-%d')}) 근무 사실이 없음을 확인합니다.**")
        else:
            st.error(f"❌ 건설일용근로자 요건 미충족\n\n**총 일수의 3분의 1 이상 근로 사실이 확인되고, 신청일 직전 14일간({fourteen_days_prior_start.strftime('%Y-%m-%d')} ~ {fourteen_days_prior_end.strftime('%Y-%m-%d')}) 내 근무기록이 존재하므로 요건을 충족하지 못합니다.**")
    
    # --- JavaScript 콜백 함수 등록 ---
    # 앱 로드 시 한 번만 실행되도록 조건문으로 감쌉니다.
    if 'js_callbacks_initialized' not in st.session_state:
        st_javascript(
            f"""
            if (window.parent.streamlit_app_callbacks === undefined) {{
                window.parent.streamlit_app_callbacks = {{}};
            }}
            window.parent.streamlit_app_callbacks.toggle_date = function(date_str) {{
                // 이 함수가 Python의 toggle_date_js (func_name으로 등록된)를 호출합니다.
                return window.parent.streamlit_app_callbacks.toggle_date_callback(date_str);
            }};
            """,
            key="init_js_callbacks",
            func_name="toggle_date_callback", # 이 이름으로 Python 함수가 연결됩니다.
        )
        st.session_state.js_callbacks_initialized = True
