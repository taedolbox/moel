# daily_worker_eligibility.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import calendar
import json

# 달력의 시작 요일을 일요일로 설정
calendar.setfirstweekday(calendar.SUNDAY)

# 현재 날짜와 시간을 기반으로 KST 오후 XX:XX 형식을 생성 (2025년 5월 25일 오후 1:08 KST)
current_datetime = datetime(2025, 5, 25, 13, 8)  # 2025년 5월 25일 오후 1:08 KST
current_time_korean = current_datetime.strftime('%Y년 %m월 %d일 %A 오후 %I:%M KST')

def get_date_range(apply_date):
    """
    신청일을 기준으로 이전 달 초일부터 신청일까지의 날짜 범위를 반환합니다.
    반환되는 날짜들은 datetime.date 객체들의 리스트입니다.
    """
    start_date = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1).date()
    return [d.date() for d in pd.date_range(start=start_date, end=apply_date)], start_date

def render_calendar_interactive(apply_date):
    """
    달력을 렌더링하고 날짜 선택 기능을 제공합니다.
    PC와 모바일에 따라 최적화된 레이아웃을 제공합니다.
    """
    # 초기 세션 상태 설정
    # (개발/테스트 목적으로 'selected_dates'가 항상 초기화되도록 변경 가능성을 열어둡니다.
    #  현재는 기존 로직 유지하며, 필요시 '캐시 및 세션 상태 초기화' 버튼 활용)
    if 'selected_dates' not in st.session_state:
        st.session_state.selected_dates = set()
    if 'rerun_trigger' not in st.session_state:
        st.session_state.rerun_trigger = False
    if 'is_mobile' not in st.session_state:
        st.session_state.is_mobile = False
    if 'is_tablet' not in st.session_state:
        st.session_state.is_tablet = False

    selected_dates = st.session_state.selected_dates
    current_date = current_datetime.date()  # 2025년 5월 25일

    # 달력 표시할 월 범위 계산 (apply_date까지 표시)
    start_date_for_calendar = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1).date()
    end_date_for_calendar = apply_date
    months_to_display = sorted(list(set((d.year, d.month) for d in pd.date_range(start=start_date_for_calendar, end=end_date_for_calendar))))

    # 모바일 확대/축소 방지 뷰포트 설정 및 User-Agent 감지
    st.markdown(
        """
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <script>
            window.addEventListener('load', function() {
                const userAgent = navigator.userAgent.toLowerCase();
                const isMobile = /mobile|android|iphone|ipod/.test(userAgent);
                const isTablet = /ipad|android(?!.*mobile)/.test(userAgent);
                const deviceInfo = JSON.stringify({ isMobile: isMobile, isTablet: isTablet });
                console.log('Device Info:', deviceInfo);  // 디버깅용
                document.getElementById('device-type').value = deviceInfo;
                document.getElementById('device-type-form').submit();
            });
        </script>
        <form id="device-type-form" method="POST" action="#" style="display: none;">
            <input id="device-type" name="device_type" type="hidden" value="">
        </form>
        """,
        unsafe_allow_html=True
    )

    # User-Agent 정보를 처리하기 위한 폼
    with st.form(key='device_type_form'):
        device_type = st.text_input("Device Type", value="", key="device_type")
        submitted = st.form_submit_button("Submit Device Type")
        if submitted and device_type:
            try:
                device_info = json.loads(device_type)
                st.session_state.is_mobile = device_info.get("isMobile", False)
                st.session_state.is_tablet = device_info.get("isTablet", False)
                st.write(f"Device Detection: Mobile={st.session_state.is_mobile}, Tablet={st.session_state.is_tablet}")  # 디버깅용
                st.rerun()
            except json.JSONDecodeError:
                st.error("Failed to parse device type information.")

    # 사용자 정의 CSS 주입
    st.markdown("""
    <style>
    /* 기본 스타일: 모든 화면에서 중앙 정렬 */
    div[data-testid="stVerticalBlock"] > div > div > div {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        width: 100% !important;
        margin-left: 0 !important;
        padding-left: 0 !important;
    }

    /* 월별 헤더 스타일 */
    div[data-testid="stMarkdownContainer"] h3 {
        background-color: #f0f0f0 !important;
        color: #000000 !important;
        text-align: center;
        padding: 8px 0;
        margin-bottom: 15px;
        font-size: 1.5em !important;
        width: 100%;
    }

    /* 다크 모드 헤더 스타일 */
    @media (prefers-color-scheme: dark) {
        div[data-testid="stMarkdownContainer"] h3 {
            background-color: #2e2e2e !important;
            color: #ffffff !important;
        }
    }

    /* 요일 헤더 스타일 */
    .day-header {
        width: 100%;
        text-align: center;
        font-weight: bold;
        padding: 5px 0;
    }
    .day-header span {
        font-size: 1.1em !important;
        display: block;
        width: 100%;
    }

    /* 다크 모드 요일 색상 수정 */
    @media (prefers-color-scheme: dark) {
        .day-header span {
            color: #ffffff !important; /* 다크 모드에서 월~금 흰색으로 */
        }
        /* 일요일, 토요일은 여전히 빨강 */
        .day-header:first-child span, .day-header:last-child span {
            color: red !important;
        }
    }

    /* 달력 컨테이너 (PC 및 모바일 공통 7열) */
    .calendar-container {
        display: grid !important;
        grid-template-columns: repeat(7, 40px) !important; /* PC와 모바일 모두 7열로 설정 */
        gap: 0 !important;
        padding: 0 !important;
        margin: 0 auto !important;
        max-width: 280px !important; /* 40px * 7 = 280px */
    }
    .calendar-day-container {
        position: relative;
        width: 40px;
        height: 60px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: space-between;
        box-sizing: border-box;
    }
    .calendar-day-box {
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 1px solid #ddd;
        background-color: #ffffff;
        border-radius: 50%;
        font-size: 1.1em;
        color: #000000;
        box-sizing: border-box;
        user-select: none;
        white-space: nowrap;
        margin: 0;
        padding: 0;
    }
    @media (prefers-color-scheme: dark) {
        .calendar-day-box {
            border: 1px solid #444;
            background-color: #1e1e1e;
            color: #ffffff;
        }
    }
    .calendar-day-box:hover {
        background-color: #e0e0e0;
        border-color: #bbb;
    }
    @media (prefers-color-scheme: dark) {
        .calendar-day-box:hover {
            background-color: #2a2a2a;
            border-color: #666;
        }
    }
    .calendar-day-box.current-day:not(.selected-day) {
        border: 2px solid blue !important;
    }
    .calendar-day-box.selected-day {
        background-color: #4CAF50 !important;
        color: #ffffff !important;
        border: 2px solid #4CAF50 !important;
        font-weight: bold;
    }
    .calendar-day-box.disabled-day {
        border: 1px solid #555;
        background-color: #e0e0e0;
        color: #666;
        cursor: not-allowed;
    }
    @media (prefers-color-scheme: dark) {
        .calendar-day-box.disabled-day {
            background-color: #2e2e2e;
            border: 1px solid #444;
            color: #666;
        }
    }
    .selection-mark { /* PC와 모바일 공통 마크 */
        position: absolute;
        top: 2px;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background-color: #4CAF50;
        border: 1px solid #ffffff;
        display: none;
    }
    .selected-day .selection-mark {
        display: block;
    }
    button[data-testid="stButton"] {
        position: absolute;
        bottom: 0;
        width: 40px;
        height: 20px;
        background: none !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 !important;
        cursor: pointer;
        opacity: 0;
    }
    button[data-testid="stButton"]:hover {
        opacity: 0.1;
    }

    /* 모바일 기기에서의 달력 셀 크기 조정 */
    @media (max-width: 600px) {
        .calendar-container {
            grid-template-columns: repeat(7, 1fr) !important; /* 모바일에서도 7열 유지, 공간에 맞게 */
            max-width: 100% !important; /* 모바일에서 화면 너비에 맞게 */
            gap: 2px !important; /* 셀 간격 조절 */
        }
        .calendar-day-container {
            width: auto; /* 너비를 자동으로 조정 */
            height: 50px; /* 높이 조정 */
        }
        .calendar-day-box {
            width: 90%; /* 부모 컨테이너에 맞게 조정 */
            height: 90%;
            font-size: 0.9em; /* 폰트 크기 조정 */
        }
        .selection-mark {
            width: 10px;
            height: 10px;
        }
        button[data-testid="stButton"] {
            width: 100%; /* 버튼 너비를 셀에 맞게 */
            height: 100%; /* 버튼 높이를 셀에 맞게 */
        }
    }

    /* 폼 버튼 숨김 */
    button[data-testid="stFormSubmitButton"] {
        display: none;
    }
    </style>
    """, unsafe_allow_html=True)

    # 토글 함수 정의 (st.rerun()을 콜백 외부에서 호출)
    def toggle_date(date_obj):
        if date_obj in selected_dates:
            selected_dates.remove(date_obj)
        else:
            selected_dates.add(date_obj)
        st.session_state.selected_dates = selected_dates
        st.session_state.rerun_trigger = True  # 트리거 설정

    # 각 월별 달력 렌더링
    for year, month in months_to_display:
        st.markdown(f"<h3>{year}년 {month}월</h3>", unsafe_allow_html=True)
        cal = calendar.monthcalendar(year, month)
        days_of_week_korean = ["일", "월", "화", "수", "목", "금", "토"]

        # 요일 헤더 생성 (Python에서 색상 동적 삽입)
        cols = st.columns(7, gap="small")
        for i, day_name in enumerate(days_of_week_korean):
            with cols[i]:
                # 일요일(0) 또는 토요일(6)은 빨강
                if i == 0 or i == 6:
                    color = "red"
                else:
                    # 월~금은 CSS에서 다크 모드에 따라 흰색/검정색으로 설정됨
                    color = "#000000" # 라이트 모드 기본 검정
                st.markdown(
                    f'<div class="day-header"><span style="color: {color}">{day_name}</span></div>',
                    unsafe_allow_html=True
                )

        # 달력 렌더링 (PC와 모바일 모두 동일한 7열 레이아웃 적용)
        st.markdown('<div class="calendar-container">', unsafe_allow_html=True)
        for week in cal:
            for day in week:
                if day == 0:
                    st.markdown('<div class="calendar-day-container"></div>', unsafe_allow_html=True)
                    continue
                date_obj = date(year, month, day)
                if date_obj > apply_date:
                    st.markdown(
                        f'<div class="calendar-day-container">'
                        f'<div class="calendar-day-box disabled-day">{day}</div>'
                        f'<button data-testid="stButton" style="display: none;"></button>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                    continue

                is_selected = date_obj in selected_dates
                is_current = date_obj == current_date
                class_name = "calendar-day-box"
                if is_selected:
                    class_name += " selected-day"
                if is_current:
                    class_name += " current-day"

                container_key = f"date_{date_obj.isoformat()}"
                st.markdown(
                    f'<div class="calendar-day-container">'
                    f'<div class="selection-mark"></div>'
                    f'<div class="{class_name}">{day}</div>'
                    f'<button data-testid="stButton" key="{container_key}" onClick="window.parent.window.dispatchEvent(new Event(\'button_click_{container_key}\'));"></button>'
                    f'</div>',
                    unsafe_allow_html=True
                )
                if st.button("", key=container_key, on_click=toggle_date, args=(date_obj,), use_container_width=True):
                    pass
        st.markdown('</div>', unsafe_allow_html=True)

    # rerun_trigger 확인 및 페이지 새로고침
    if st.session_state.rerun_trigger:
        st.session_state.rerun_trigger = False
        st.rerun()  # 콜백 외부에서 호출

    # 현재 선택된 근무일자 목록 표시
    if st.session_state.selected_dates:
        st.markdown("### ✅ 선택된 근무일자")
        st.markdown(", ".join([d.strftime("%Y-%m-%d") for d in sorted(st.session_state.selected_dates)]))

    return st.session_state.selected_dates

def daily_worker_eligibility_app():
    """
    일용근로자 수급자격 요건 모의계산 앱의 메인 함수입니다.
    """
    st.header("일용근로자 수급자격 요건 모의계산")

    # 모든 캐시 및 세션 상태 초기화 버튼 (테스트 목적)
    if st.button("🔄 캐시 및 세션 상태 초기화", help="이전 테스트 데이터를 지우고 앱을 초기 상태로 되돌립니다."):
        st.cache_data.clear()
        st.cache_resource.clear()
        for key in list(st.session_state.keys()): # 세션 상태 키 목록을 복사하여 반복
            del st.session_state[key]
        st.rerun() # 초기화 후 앱 새로고침

    # 현재 날짜와 시간 표시
    st.markdown(f"**오늘 날짜와 시간**: {current_time_korean}", unsafe_allow_html=True)

    # 요건 조건 설명
    st.markdown("### 📋 요건 조건")
    st.markdown("- **조건 1**: 수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지의 근로일 수가 총 일수의 1/3 미만이어야 합니다.")
    st.markdown("- **조건 2 (건설일용근로자만 해당)**: 수급자격 인정신청일 직전 14일간 근무 사실이 없어야 합니다 (신청일 제외).")
    st.markdown("---")

    # 수급자격 신청일 선택 (자유롭게 선택 가능)
    apply_date = st.date_input("수급자격 신청일을 선택하세요", value=datetime.now().date(), key="apply_date_input")

    # 날짜 범위 및 시작일 가져오기
    date_range_objects, start_date = get_date_range(apply_date)

    st.markdown("---")
    st.markdown("#### ✅ 근무일 선택 달력")
    selected_dates = render_calendar_interactive(apply_date)  # 반환값을 selected_dates로 저장
    st.markdown("---")

    # 조건 1 계산 및 표시
    total_days = len(date_range_objects)
    worked_days = len(selected_dates)
    threshold = total_days / 3

    st.markdown(f"- 총 기간 일수: **{total_days}일**")
    st.markdown(f"- 기준 (총일수의 1/3): **{threshold:.1f}일**")
    st.markdown(f"- 선택한 근무일 수: **{worked_days}일**")

    condition1 = worked_days < threshold
    if condition1:
        st.success("✅ 조건 1 충족: 근무일 수가 기준 미만입니다.")
    else:
        st.warning("❌ 조건 1 불충족: 근무일 수가 기준 이상입니다.")

    # 조건 2 계산 및 표시 (건설일용근로자 기준)
    condition2 = False
    fourteen_days_prior_end = apply_date - timedelta(days=1)
    fourteen_days_prior_start = fourteen_days_prior_end - timedelta(days=13)
    fourteen_days_prior_range = [d.date() for d in pd.date_range(start=fourteen_days_prior_start, end=fourteen_days_prior_end)]
    no_work_14_days = all(day not in selected_dates for day in fourteen_days_prior_range)
    condition2 = no_work_14_days

    if no_work_14_days:
        st.success(f"✅ 조건 2 충족: 신청일 직전 14일간({fourteen_days_prior_start.strftime('%Y-%m-%d')} ~ {fourteen_days_prior_end.strftime('%Y-%m-%d')}) 근무내역이 없습니다.")
    else:
        st.warning(f"❌ 조건 2 불충족: 신청일 직전 14일간({fourteen_days_prior_start.strftime('%Y-%m-%d')} ~ {fourteen_days_prior_end.strftime('%Y-%m-%d')}) 내 근무기록이 존재합니다.")

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
                st.info(f"✅ **{future_date.strftime('%Y-%m-%d')}** 이후에 신청하면 요건을 충족할 수 있습니다.")
                found_suggestion = True
                break
        if not found_suggestion:
            st.warning("❗앞으로 30일 이내에는 요건을 충족할 수 없습니다. 근무일 수를 조정하거나 더 먼 날짜를 고려하세요.")

    # 조건 2 불충족 시 미래 신청일 제안 (건설일용근로자 기준)
    if not condition2:
        st.markdown("### 📅 조건 2를 충족하려면 언제 신청해야 할까요?")
        last_worked_day = max((d for d in selected_dates if d < apply_date), default=None)
        if last_worked_day:
            suggested_date = last_worked_day + timedelta(days=15)
            st.info(f"✅ **{suggested_date.strftime('%Y-%m-%d')}** 이후에 신청하면 조건 2를 충족할 수 있습니다.")
        else:
            st.info("이미 최근 14일간 근무내역이 없으므로, 신청일을 조정할 필요는 없습니다.")

    st.subheader("📌 최종 판단")
    # 일반일용근로자: 조건 1만 판단
    if condition1:
        st.success(f"✅ 일반일용근로자: 신청 가능\n\n**수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지({start_date.strftime('%Y-%m-%d')} ~ {apply_date.strftime('%Y-%m-%d')}) 근로일 수의 합이 같은 기간 동안의 총 일수의 3분의 1 미만**")
    else:
        st.error(f"❌ 일반일용근로자: 신청 불가능\n\n**수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지({start_date.strftime('%Y-%m-%d')} ~ {apply_date.strftime('%Y-%m-%d')}) 근로일 수의 합이 같은 기간 동안의 총 일수의 3분의 1 이상입니다.**")

    # 건설일용근로자: 조건 1과 조건 2 모두 판단
    if condition1 and condition2:
        st.success(f"✅ 건설일용근로자: 신청 가능\n\n**수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지({start_date.strftime('%Y-%m-%d')} ~ {apply_date.strftime('%Y-%m-%d')}) 근로일 수의 합이 총 일수의 3분의 1 미만이고, 신청일 직전 14일간({fourteen_days_prior_start.strftime('%Y-%m-%d')} ~ {fourteen_days_prior_end.strftime('%Y-%m-%d')}) 근무 사실이 없음을 확인합니다.**")
    else:
        error_message = "❌ 건설일용근로자: 신청 불가능\n\n"
        if not condition1:
            error_message += f"**수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지({start_date.strftime('%Y-%m-%d')} ~ {apply_date.strftime('%Y-%m-%d')}) 근로일 수의 합이 같은 기간 동안의 총 일수의 3분의 1 이상입니다.**\n\n"
        if not condition2:
            error_message += f"**신청일 직전 14일간({fourteen_days_prior_start.strftime('%Y-%m-%d')} ~ {fourteen_days_prior_end.strftime('%Y-%m-%d')}) 근무내역이 있습니다.**"
        st.error(error_message)

if __name__ == "__main__":
    daily_worker_eligibility_app()
