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
    
    # 클릭된 날짜를 저장할 임시 세션 상태 (JavaScript에서 전달받음)
    if 'clicked_date_from_js' not in st.session_state:
        st.session_state.clicked_date_from_js = None

    selected_dates = st.session_state.selected_dates
    current_date = datetime.now().date()

    # 달력 표시할 월 범위 계산 (apply_date까지 표시)
    start_date_for_calendar = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1).date()
    end_date_for_calendar = apply_date
    months_to_display = sorted(list(set((d.year, d.month) for d in pd.date_range(start=start_date_for_calendar, end=end_date_for_calendar))))

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

    /* Light Mode */
    /* 요일 헤더 기본 글자색 (라이트 모드) */
    .day-header span {{
        color: #000000 !important; /* 라이트 모드일 때 검정색 */
    }}

    /* Dark Mode (prefers-color-scheme) */
    @media (prefers-color-scheme: dark) {{
        div[data-testid="stMarkdownContainer"] h3 {{
            background-color: #2e2e2e !important; /* 다크 모드 */
            color: #ffffff !important; /* 다크 모드 */
        }}
        /* 요일 헤더 기본 글자색 (다크 모드) */
        .day-header span {{
            color: #ffffff !important; /* 다크 모드일 때 흰색 */
        }}
    }}

    /* 요일 헤더 공통 스타일 (폰트 크기 및 정렬) */
    .day-header span {{
        font-size: 1.1em !important; /* 요일 폰트 크기 */
        text-align: center !important; /* 가운데 정렬 */
        display: block !important; /* text-align을 위해 block으로 설정 */
        width: 100% !important; /* 부모 div의 너비에 맞춤 */
        font-weight: bold; /* 요일 글자 두껍게 */
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
        z-index: 1; /* 날짜 숫자 위에 오도록 */
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
    """, unsafe_allow_html=True)

    # JavaScript를 통해 클릭된 날짜를 받아올 숨겨진 st.text_input
    # 이 인풋의 `on_change` 콜백에서 `st.session_state.selected_dates`를 업데이트합니다.
    # `value`는 `st.text_input`의 현재 값을 나타냅니다.
    # 초기화 시 빈 문자열로 설정하여 불필요한 재트리거 방지
    # 이 컴포넌트는 달력 렌더링 후에 위치하므로, 자동으로 아래쪽에 표시됩니다.
    st.text_input("Hidden input for date click", key="hidden_date_input_for_js", value="", label_visibility="hidden",
                  on_change=lambda: _update_selected_dates_from_js(st.session_state.hidden_date_input_for_js))
    
    # JavaScript에서 클릭된 날짜를 받아 파이썬 상태를 업데이트할 콜백 함수
    def _update_selected_dates_from_js(date_str):
        if date_str:
            clicked_date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            if clicked_date_obj in st.session_state.selected_dates:
                st.session_state.selected_dates.discard(clicked_date_obj)
            else:
                st.session_state.selected_dates.add(clicked_date_obj)
            # `st.session_state.hidden_date_input_for_js`를 즉시 초기화하여
            # 다음 클릭을 받을 준비를 하고, 불필요한 재트리거 방지
            st.session_state.hidden_date_input_for_js = ""
            st.experimental_rerun() # 상태 변경 후 즉시 재렌더링

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
                    
                    # 클릭 시 Streamlit의 숨겨진 텍스트 인풋 값 변경 (JavaScript)
                    # `hidden_date_input_for_js`의 ID를 직접 사용하여 값을 설정하고 change 이벤트를 발생시킵니다.
                    onclick_js = f"""
                        var hiddenInput = document.getElementById('hidden_date_input_for_js');
                        if (hiddenInput) {{
                            hiddenInput.value = '{date_obj.strftime('%Y-%m-%d')}';
                            hiddenInput.dispatchEvent(new Event('change', {{ bubbles: true }})); // onchange 이벤트 강제 트리거
                        }} else {{
                            console.error('Hidden input not found!');
                        }}
                    """

                    cols[i].markdown(
                        f"""
                        <div class="{' '.join(class_names)}" onclick="{onclick_js}">
                            <span>{day}</span>
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
        last_worked_day = max((d for d in selected_days if d < apply_date), default=None)
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
