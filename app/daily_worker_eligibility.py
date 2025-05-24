import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import calendar

# 달력의 시작 요일을 일요일로 설정
calendar.setfirstweekday(calendar.SUNDAY)

# 현재 날짜와 시간을 기반으로 KST 오후 XX:XX 형식을 생성
current_datetime = datetime.now()
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
    달력을 렌더링하고 HTML/CSS/JS를 이용한 날짜 선택 기능을 제공합니다.
    선택된 날짜, 현재 날짜, 신청일 이후 날짜는 표시하지 않습니다.
    """
    # 초기 세션 상태 설정
    if 'selected_dates' not in st.session_state:
        st.session_state.selected_dates = set()
    
    # 클릭된 날짜를 저장할 임시 세션 상태
    if 'clicked_date_from_js' not in st.session_state:
        st.session_state.clicked_date_from_js = None

    selected_dates = st.session_state.selected_dates
    current_date = datetime.now().date()

    # 달력 표시할 월 범위 계산 (apply_date까지 표시)
    start_date_for_calendar = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1).date()
    end_date_for_calendar = apply_date
    months_to_display = sorted(list(set((d.year, d.month) for d in pd.date_range(start=start_date_for_calendar, end=end_date_for_calendar))))

    # JavaScript를 통해 클릭된 날짜를 받아 파이썬 상태를 업데이트할 콜백 함수
    def _update_selected_dates_from_js_callback():
        # st.session_state.clicked_date_from_js 값은 JavaScript에서 설정됩니다.
        if st.session_state.clicked_date_from_js:
            clicked_date_str = st.session_state.clicked_date_from_js
            clicked_date_obj = datetime.strptime(clicked_date_str, '%Y-%m-%d').date()
            if clicked_date_obj in st.session_state.selected_dates:
                st.session_state.selected_dates.discard(clicked_date_obj)
            else:
                st.session_state.selected_dates.add(clicked_date_obj)
            st.session_state.clicked_date_from_js = None # 처리 후 초기화

    # 숨겨진 Streamlit 버튼을 위한 플레이스홀더
    # 이 버튼은 JavaScript에 의해 클릭되어 파이썬 콜백을 트리거합니다.
    # 클릭된 날짜는 `st.session_state.clicked_date_from_js`에 임시로 저장됩니다.
    hidden_button_placeholder = st.empty()
    with hidden_button_placeholder.container():
        # 실제 버튼은 아니지만, JavaScript가 클릭할 수 있는 `st.button` 요소를 만듭니다.
        # `key`는 필수이며, `on_click` 콜백 함수를 가집니다.
        # `label`은 UI에 표시되므로 숨겨야 합니다.
        st.button(
            label="TriggerDateClick",
            key="trigger_date_click_button",
            on_click=_update_selected_dates_from_js_callback,
            # CSS로 이 버튼을 완전히 숨김
            help="Internal button to trigger date selection logic",
        )
        st.markdown("""
            <style>
            /* 숨겨진 버튼을 위한 CSS */
            div[data-testid="stButton"] button[data-testid="stFormSubmitButton"] {
                display: none; /* 버튼 자체를 숨김 */
            }
            </style>
        """, unsafe_allow_html=True)


    # 사용자 정의 CSS 주입
    st.markdown(f"""
    <style>
    /* 전체 폰트 Streamlit 기본 폰트 사용 */

    /* 달력 전체 컨테이너 가운데 정렬을 위한 상위 요소에 Flexbox 적용 */
    div[data-testid="stVerticalBlock"] > div:nth-child(2) > div:nth-child(2) {{
        display: flex;
        flex-direction: column;
        align-items: center; /* 수평 가운데 정렬 */
        width: 100%; /* 부모 너비 채우기 */
    }}

    /* 월별 헤더 스타일 */
    div[data-testid="stMarkdownContainer"] h3 {{
        background-color: #f0f0f0 !important; /* 라이트 모드 */
        color: #000000 !important; /* 라이트 모드 */
        text-align: center; /* 월별 헤더 가운데 정렬 */
        padding: 8px 0; /* 패딩 증가 */
        margin-bottom: 15px; /* 아래 여백 증가 */
        font-size: 1.5em !important; /* 월별 헤더 폰트 크기 증가 */
    }}

    /* Dark Mode (prefers-color-scheme) */
    @media (prefers-color-scheme: dark) {{
        div[data-testid="stMarkdownContainer"] h3 {{
            background-color: #2e2e2e !important; /* 다크 모드 */
            color: #ffffff !important; /* 다크 모드 */
        }}
    }}

    /* 요일 헤더 공통 스타일 (폰트 크기 및 정렬) */
    .day-header span {{
        font-size: 1.1em !important; /* 요일 폰트 크기 */
        text-align: center !important; /* 가운데 정렬 */
        display: block !important; /* text-align을 위해 block으로 설정 */
        width: 100% !important; /* 부모 div의 너비에 맞춤 */
        font-weight: bold; /* 요일 글자 두껍게 */
        color: var(--text-color); /* 기본 텍스트 색상 (라이트/다크 모드 따라감) */
        padding: 5px 0; /* 요일 패딩 추가 */
    }}

    /* 요일 헤더 특정 요일 색상 (라이트/다크 모드 공통) */
    /* 일요일 빨간색 */
    .day-header:nth-child(1) span {{
        color: red !important;
    }}
    /* 토요일 파란색 */
    .day-header:nth-child(7) span {{
        color: blue !important;
    }}

    /* 커스텀 날짜 박스 스타일 (클릭 영역) */
    .calendar-day-box {{
        width: 45px; /* 날짜 박스 너비 */
        height: 45px; /* 날짜 박스 높이 */
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0;
        margin: 2px; /* 박스 간 간격 */
        border: 1px solid var(--border-color); /* 기본 테두리색 */
        background-color: var(--background-color-body); /* 기본 배경색 */
        cursor: pointer;
        transition: all 0.1s ease; /* 부드러운 전환 효과 */
        border-radius: 5px; /* 약간 둥근 모서리 */
        font-size: 1.1em; /* 날짜 숫자 폰트 크기 증가 */
        color: var(--text-color); /* 날짜 숫자 글자색 */
        box-sizing: border-box; /* 패딩, 보더가 너비 계산에 포함되도록 */
        user-select: none; /* 텍스트 선택 방지 */
        position: relative; /* ::after 가상 요소를 위한 position 설정 */
    }}

    /* 호버 시 효과 */
    .calendar-day-box:hover {{
        background-color: var(--secondary-background-color); /* 호버 시 Streamlit 보조 배경색 */
        border-color: var(--text-color); /* 호버 시 글자색과 유사한 테두리 */
    }}
    
    /* 오늘 날짜 스타일 (선택되지 않았을 때만 적용) */
    .calendar-day-box.current-day {{
        border: 2px solid blue !important; /* 오늘 날짜 파란색 테두리 */
    }}

    /* 선택된 날짜에 대한 원형 표시 */
    .calendar-day-box.selected-day::after {{
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 30px; /* 원의 크기 */
        height: 30px; /* 원의 크기 */
        background-color: rgba(255, 0, 0, 0.4); /* 빨간색 40% 투명도 */
        border-radius: 50%; /* 원형으로 만듦 */
        z-index: 1; /* 날짜 숫자 아래에 오도록 */
    }}

    /* 선택된 날짜의 숫자 글자색 */
    .calendar-day-box.selected-day span {{
        position: relative; /* z-index가 작동하도록 */
        z-index: 2; /* 원형 위에 글자가 오도록 */
        color: #ffffff !important; /* 선택된 날짜 글자색 흰색 */
    }}

    /* 달력 날짜 그리드를 감싸는 stHorizontalBlock에 flexbox 적용 */
    div[data-testid="stHorizontalBlock"] {{
        display: flex;
        flex-wrap: wrap; /* 내용이 넘치면 다음 줄로 */
        justify-content: center; /* 내부 열(요일/날짜)들을 중앙 정렬 */
        max-width: 380px; /* 달력 전체의 최대 너비 설정 (조절 가능) */
        margin: 0 auto; /* 블록 자체를 가운데 정렬 */
        gap: 2px; /* 박스 간 간격 */
    }}
    /* stHorizontalBlock 내의 각 열 (날짜/요일) */
    div[data-testid="stHorizontalBlock"] > div {{
        flex-grow: 0; /* 늘어나지 않음 */
        flex-shrink: 0; /* 줄어들지 않음 */
        flex-basis: calc(100% / 7 - 4px); /* 7개 열이 대략적으로 균등하게, gap 고려 */
        min-width: 45px; /* 너무 작아지지 않도록 최소 너비 설정 */
        padding: 0 !important;
        margin: 0 !important;
        box-sizing: border-box; /* 패딩, 보더가 너비 계산에 포함되도록 */
        display: flex; /* 내부 요소 정렬을 위해 flexbox 사용 */
        justify-content: center; /* 박스 가운데 정렬 */
        align-items: center; /* 박스 세로 가운데 정렬 */
    }}

    /* 모바일 반응형 조절 */
    @media (max-width: 600px) {{
        div[data-testid="stHorizontalBlock"] {{
            max-width: 100%; /* 모바일에서는 너비 100% */
        }}
        div[data-testid="stHorizontalBlock"] > div {{
            flex-basis: calc(100% / 7 - 2px); /* 모바일에서는 간격 약간 줄여서 7개 열 맞춤 */
            min-width: 38px !important; /* 모바일 최소 너비 */
        }}
        .calendar-day-box {{
            width: 38px;
            height: 38px;
            font-size: 1em;
        }}
        .day-header span {{
            font-size: 0.9em !important;
        }}
        .calendar-day-box.selected-day::after {{
            width: 25px; /* 모바일에서 원 크기 조절 */
            height: 25px; /* 모바일에서 원 크기 조절 */
        }}
    }}
    </style>

    <script>
    // 날짜 박스 클릭 핸들러
    function handleDateClick(dateString) {{
        // Streamlit의 숨겨진 버튼을 찾아서 클릭 이벤트를 트리거합니다.
        // Streamlit 컴포넌트의 실제 DOM ID는 동적으로 생성되므로, `data-testid`를 사용합니다.
        // `st.button`의 `data-testid`는 "stFormSubmitButton"입니다.
        const hiddenButton = document.querySelector('button[data-testid="stFormSubmitButton"]');
        
        if (hiddenButton) {{
            // 클릭된 날짜를 세션 상태에 전달하기 위해 임시 변수에 저장
            // 이 방법은 Streamlit이 현재 세션 상태를 업데이트하는 가장 일반적인 방법입니다.
            // Streamlit의 `setComponentValue`는 더 이상 직접 호출되지 않습니다.
            // 대신, `st.session_state`에 직접 값을 설정하고 `st.experimental_rerun()`을 호출하여
            // 파이썬 함수를 트리거합니다.

            // 숨겨진 버튼의 `aria-label`을 활용하여 데이터 전달 (Streamlit 1.25+ 버전)
            // St.button의 on_click 콜백은 `args`를 통해 파라미터를 받을 수 있습니다.
            // 그러나 JS에서 파이썬 함수에 직접 파라미터를 넘기는 것은 불가능합니다.
            // 따라서 `st.session_state`를 우회적으로 사용해야 합니다.
            
            // `st.session_state`에 직접 값을 설정하는 것은 JS에서 불가능하므로,
            // Streamlit의 `Custom Components API`를 사용하거나,
            // 아니면 `st.text_input` 또는 `st.button`의 `on_click`을 통해
            // 파이썬으로 값을 전달하는 방법을 사용합니다.
            
            // 가장 안정적인 방법은 `st.text_input`의 `on_change`입니다.
            const hiddenInput = document.getElementById('hidden_date_input_for_js');
            if (hiddenInput) {{
                hiddenInput.value = dateString;
                hiddenInput.dispatchEvent(new Event('change', {{ bubbles: true }})); // onchange 이벤트 강제 트리거
            }}
        }} else {{
            console.warn('Hidden Streamlit button not found. Date click might not register.');
        }}
    }}
    </script>
    """, unsafe_allow_html=True)

    # 클릭된 날짜 정보 처리
    # 이 부분은 `st.text_input`의 `on_change` 콜백에서 이미 처리되므로, 직접 호출할 필요가 없습니다.
    # 하지만, `st.session_state.clicked_date_from_js`가 있다면 이를 활용하여 selected_dates를 업데이트합니다.
    if st.session_state.clicked_date_from_js:
        _update_selected_dates_from_js_callback()


    # 각 월별 달력 렌더링
    for year, month in months_to_display:
        st.markdown(f"<h3>{year}년 {month}월</h3>", unsafe_allow_html=True)
        cal = calendar.monthcalendar(year, month)
        days_of_week_korean = ["일", "월", "화", "수", "목", "금", "토"]

        # 요일 헤더 생성 (st.columns 사용)
        cols = st.columns(7, gap="small")
        for i, day_name in enumerate(days_of_week_korean):
            cols[i].markdown(f'<div class="day-header"><span><strong>{day_name}</strong></span></div>', unsafe_allow_html=True)

        # 달력 날짜 박스 생성 (apply_date 이후 날짜 제외)
        for week in cal:
            cols = st.columns(7, gap="small")
            for i, day in enumerate(week):
                if day == 0:
                    cols[i].markdown(" ") # 빈 칸
                else:
                    date_obj = date(year, month, day)
                    # 신청일 이후 날짜는 표시하지 않음 (빈 칸)
                    if date_obj > apply_date:
                        cols[i].markdown(" ")
                        continue

                    is_selected = date_obj in selected_dates
                    is_current = date_obj == current_date
                    
                    class_names = ["calendar-day-box"]
                    if is_selected:
                        class_names.append("selected-day")
                    if is_current:
                        class_names.append("current-day")
                    
                    # 날짜 텍스트 (오늘 날짜는 굵게)
                    display_day_text = str(day)
                    if is_current:
                        display_day_text = f"**{day}**"

                    # 클릭 시 JavaScript 함수 호출
                    onclick_js = f"handleDateClick('{date_obj.strftime('%Y-%m-%d')}');"

                    cols[i].markdown(
                        f"""
                        <div class="{' '.join(class_names)}" onclick="{onclick_js}">
                            <span>{display_day_text}</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
    
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
    selected_days = render_calendar_interactive(apply_date) # 함수 호출 변경
    st.markdown("---")

    # 조건 1 계산 및 표시
    total_days = len(date_range_objects)
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

    # 조건 2 계산 및 표시 (건설일용근로자 기준)
    condition2 = False
    fourteen_days_prior_end = apply_date - timedelta(days=1)
    fourteen_days_prior_start = fourteen_days_prior_end - timedelta(days=13)
    fourteen_days_prior_range = [d.date() for d in pd.date_range(start=fourteen_days_prior_start, end=fourteen_days_prior_end)]
    no_work_14_days = all(day not in selected_days for day in fourteen_days_prior_range)
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
            worked_days_future = sum(1 for d in selected_days if d <= future_date)

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
