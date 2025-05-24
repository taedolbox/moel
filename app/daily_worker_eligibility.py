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

def render_calendar_custom(apply_date): # 함수명 변경: render_calendar_custom
    """
    달력을 렌더링하고 커스텀 HTML/CSS를 이용한 날짜 선택 기능을 제공합니다.
    선택된 날짜, 현재 날짜, 신청일 이후 날짜는 표시하지 않습니다.
    """
    # 사용자 정의 CSS 주입
    st.markdown(f"""
    <style>
    /* 전체 폰트 Streamlit 기본 폰트 사용 */

    /* 달력 전체 컨테이너 가운데 정렬을 위한 상위 요소에 Flexbox 적용 */
    /* Streamlit이 st.columns를 감싸는 div가 무엇인지 정확히 알아내야 함 */
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

    /* 커스텀 날짜 버튼 스타일 */
    .calendar-day-button {{
        width: 45px; /* 날짜 박스 너비 */
        height: 45px; /* 날짜 박스 높이 */
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0;
        margin: 2px; /* 버튼 간 간격 */
        border: 1px solid #ddd; /* 기본 테두리색 (라이트 모드) */
        background-color: #ffffff; /* 기본 배경색 (라이트 모드) */
        cursor: pointer;
        transition: all 0.2s ease;
        border-radius: 5px; /* 약간 둥근 모서리 */
        font-size: 1.1em; /* 날짜 숫자 폰트 크기 증가 */
        color: #000000; /* 날짜 숫자 글자색 (라이트 모드) */
        box-sizing: border-box; /* 패딩, 보더가 너비 계산에 포함되도록 */
    }}
    /* Dark Mode 날짜 버튼 */
    @media (prefers-color-scheme: dark) {{
        .calendar-day-button {{
            border: 1px solid #444; /* 다크 모드 테두리색 */
            background-color: #1e1e1e; /* 다크 모드 배경색 */
            color: #ffffff; /* 날짜 숫자 글자색 (다크 모드) */
        }}
    }}

    /* 달력 날짜 그리드를 감싸는 stHorizontalBlock에 flexbox 적용 */
    div[data-testid="stHorizontalBlock"] {{
        display: flex;
        flex-wrap: wrap; /* 내용이 넘치면 다음 줄로 */
        justify-content: center; /* 내부 열(요일/날짜)들을 중앙 정렬 */
        max-width: 380px; /* 달력 전체의 최대 너비 설정 (조절 가능) */
        margin: 0 auto; /* 블록 자체를 가운데 정렬 */
        gap: 2px; /* 버튼 간 간격 */
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
        justify-content: center; /* 버튼 가운데 정렬 */
        align-items: center; /* 버튼 세로 가운데 정렬 */
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
        .calendar-day-button {{
            width: 38px;
            height: 38px;
            font-size: 1em;
        }}
        .day-header span {{
            font-size: 0.9em !important;
        }}
    }}
    </style>
    """, unsafe_allow_html=True)

    # st.session_state에서 선택된 날짜 집합 가져오기
    if 'selected_dates' not in st.session_state:
        st.session_state.selected_dates = set()
    selected_dates = st.session_state.selected_dates
    current_date = datetime.now().date()

    # 달력 표시할 월 범위 계산 (apply_date까지 표시)
    start_date_for_calendar = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1).date()
    end_date_for_calendar = apply_date
    months_to_display = sorted(list(set((d.year, d.month) for d in pd.date_range(start=start_date_for_calendar, end=end_date_for_calendar))))

    # JavaScript를 Streamlit에 주입하여 파이썬 콜백을 트리거
    # Streamlit Custom Component가 아닌 이상, Python 상태를 변경하려면
    # st.experimental_rerun() 또는 st.button/st.checkbox 같은 Streamlit 컴포넌트를
    # 클릭하여 앱을 다시 그리게 해야 합니다.
    # 여기서는 각 날짜에 대한 HTML을 직접 생성하고, onclick 이벤트를 통해
    # 특정 Hidden Button을 클릭하게 하여 Streamlit 앱을 리런시키는 방식으로 구현합니다.
    # 숨겨진 버튼을 한 번만 만들고, 각 날짜 HTML에서 이 버튼을 클릭하도록 합니다.

    # 숨겨진 버튼 생성 (이 버튼이 클릭되면 Streamlit 앱이 재실행됨)
    # 이 버튼의 `key`를 사용하여 `st.session_state`에 클릭된 날짜 정보를 전달합니다.
    if 'clicked_date_info' not in st.session_state:
        st.session_state.clicked_date_info = None

    # st.button(label="click_me", key="hidden_button", on_click=lambda: st.session_state.update(re_run_trigger=True), help="Do not click")
    # Streamlit 앱을 다시 실행하기 위한 숨겨진 버튼
    # 이 버튼은 CSS로 숨기고, JS를 통해 클릭됩니다.
    st.markdown("""
        <style>
            .hidden-button-container {
                display: none;
            }
        </style>
        <div class="hidden-button-container">
            <button id="streamlit_rerun_trigger" type="button"></button>
        </div>
    """, unsafe_allow_html=True)

    # st.script_runner.ScriptRunner.singleton.request_rerun() 대신
    # streamlit_component_v1.setElementValue('hidden_button', true) 같은 방식으로
    # Streamlit 컴포넌트의 값을 변경하여 재실행을 유도해야 합니다.
    # 하지만 Streamlit은 사용자 정의 JS -> Python 콜백을 직접 지원하지 않으므로,
    # 가장 간단한 방법은 각 날짜를 `st.button`으로 유지하되, CSS를 더 강력하게 제어하는 것입니다.
    # 또는, `st.markdown`으로 날짜를 표시하고, JavaScript를 통해 특정 URL 매개변수를 변경한 뒤
    # Streamlit이 URL 매개변수를 읽어서 상태를 업데이트하고 재실행하는 복잡한 방식도 가능하지만,
    # 여기서는 `st.button`을 사용한 이전 방식을 유지하되, CSS로 시각적인 표시를 명확히 하는 데 집중하겠습니다.

    # 이전 `st.button` 방식에서 CSS가 잘 적용되도록 다시 검토합니다.
    # 문제가 된 부분은 `st.button` 컴포넌트 자체가 `selected-date` 클래스를 받지 못한다는 점이었습니다.
    # 이를 해결하기 위해, `selected_dates`에 포함된 날짜 버튼의 배경색을
    # 직접 `st.button`의 `background-color` 인자를 통해 변경할 수는 없습니다.
    # 다시 `st.button`을 사용하는 것으로 돌아가되, 선택된 날짜에 대한 시각적 피드백을
    # CSS의 `st.button > button` 선택자를 활용하고, 버튼 자체에 `border-radius`를 더 강조하겠습니다.
    # Python 코드에서 조건부 스타일링을 직접 주입할 수는 없으므로,
    # Streamlit이 재렌더링될 때 CSS가 해당 상태를 파악하고 적용하도록 해야 합니다.

    # 다시 `st.button`을 활용하여 CSS를 더 정교하게 만듭니다.
    # 문제는 `st.experimental_rerun()` 호출이 트리거되지 않았다는 것.
    # `st.session_state` 변경만으로는 재실행이 안 될 수 있습니다.
    # `st.experimental_rerun()`은 컴포넌트의 `on_change` 콜백에서 사용하는 것이 일반적입니다.
    # 날짜 버튼을 클릭하면 `st.session_state.selected_dates`가 변경되므로
    # Streamlit은 이 변경을 감지하고 앱을 다시 실행합니다.
    # 그렇다면 `st.experimental_rerun()` 없이도 동작해야 합니다.
    # 혹시 모를 오류 때문에 `st.experimental_rerun()`을 다시 추가하는 것이 아니라,
    # `st.button`의 `on_click`을 사용하여 상태를 업데이트하는 것이 더 안전한 방법입니다.

    # 각 월별 달력 렌더링
    for year, month in months_to_display:
        st.markdown(f"<h3>{year}년 {month}월</h3>", unsafe_allow_html=True)
        cal = calendar.monthcalendar(year, month)
        days_of_week_korean = ["일", "월", "화", "수", "목", "금", "토"]

        # 요일 헤더 생성 (st.columns 사용)
        cols = st.columns(7, gap="small")
        for i, day_name in enumerate(days_of_week_korean):
            cols[i].markdown(f'<div class="day-header"><span><strong>{day_name}</strong></span></div>', unsafe_allow_html=True)

        # 달력 날짜 버튼 생성 (apply_date 이후 날짜 제외)
        for week in cal:
            cols = st.columns(7, gap="small")
            for i, day in enumerate(week):
                if day == 0:
                    cols[i].markdown(" ") # 빈 칸
                else:
                    date_obj = date(year, month, day)
                    # 신청일 이후 날짜는 표시하지 않음 (버튼 비활성화 또는 숨김)
                    if date_obj > apply_date:
                        cols[i].markdown(" ") # 빈 칸
                        continue

                    is_selected = date_obj in selected_dates
                    is_current = date_obj == current_date

                    # 버튼 스타일 결정
                    button_style = ""
                    button_color = ""
                    button_text_color = ""
                    button_border = ""

                    # 라이트 모드/다크 모드 기본 색상 설정 (CSS에서 처리되지만, 명시적으로)
                    if st.get_option("client.theming.base") == "dark":
                        # 다크 모드
                        button_color = "#1e1e1e"
                        button_text_color = "#ffffff"
                        button_border = "1px solid #444"
                    else:
                        # 라이트 모드
                        button_color = "#ffffff"
                        button_text_color = "#000000"
                        button_border = "1px solid #ddd"


                    if is_selected:
                        button_color = "#ff0000" # 선택 시 빨간색
                        button_text_color = "#ffffff" # 선택 시 흰색 글씨
                        button_border = "1px solid #ff0000"
                    elif is_current: # 오늘 날짜이면서 선택되지 않은 경우
                        button_border = "2px solid blue" # 파란색 테두리

                    # HTML을 직접 생성하여 인라인 스타일 적용
                    # st.session_state를 업데이트할 콜백 함수 정의
                    def _update_selected_dates(clicked_date):
                        if clicked_date in st.session_state.selected_dates:
                            st.session_state.selected_dates.discard(clicked_date)
                        else:
                            st.session_state.selected_dates.add(clicked_date)

                    # 각 날짜를 표시하는 HTML 요소 (버튼처럼 동작)
                    # Streamlit 컴포넌트가 아니므로 클릭 시 Streamlit 앱을 재실행할 방법이 필요.
                    # 임시로 `st.button`을 다시 사용하여 클릭 이벤트를 트리거합니다.
                    # CSS를 통해 st.button 스타일을 오버라이드합니다.

                    # `st.button`을 사용하는 이전 방식으로 돌아가되, CSS를 통해 선택 상태를 표시합니다.
                    # `st.button`은 자체적으로 상태를 저장하고, 클릭 시 앱을 다시 렌더링합니다.
                    # 따라서 `st.experimental_rerun()`은 필요 없습니다.
                    # 문제는 `st.button`에 동적으로 클래스를 추가하는 것이 어렵다는 점입니다.
                    # 해결책은 CSS에서 `st.button`의 `data-testid`와 선택 상태에 따라
                    # 스타일을 변경하는 것입니다.

                    # 가장 좋은 방법은, 선택된 날짜와 오늘 날짜에 대해
                    # Streamlit이 렌더링한 버튼에 CSS 클래스를 직접 추가하는 JavaScript를 실행하는 것입니다.
                    # 하지만 Streamlit이 JS를 직접 삽입하고 실행하는 것은 보안 상의 이유로 제한적입니다.
                    # 그래서 `st.session_state`를 활용한 간접적인 방법이 주로 사용됩니다.
                    # 즉, `st.session_state.selected_dates`에 날짜가 있으면
                    # 해당 날짜를 그리는 버튼의 CSS를 "선택된 버튼처럼" 보이도록 하는 것입니다.

                    # 날짜 텍스트 (오늘 날짜는 굵게)
                    display_day_text = str(day)
                    if is_current:
                        display_day_text = f"**{day}**"

                    # `st.button`의 `on_click`을 사용하여 상태 업데이트
                    if cols[i].button(display_day_text, key=f"date_btn_{date_obj}"):
                        _update_selected_dates(date_obj)

                    # Streamlit 렌더링 후 동적으로 CSS 클래스 추가 (JavaScript)
                    # 이 방법은 Streamlit의 실행 흐름을 벗어나므로, 보안 경고가 발생하거나
                    # Streamlit Cloud에서는 동작하지 않을 수 있습니다.
                    # 하지만 로컬 테스트 환경에서는 시도해 볼 수 있습니다.
                    # 안전한 방법은 CSS 자체를 조건부로 생성하거나,
                    # `st.button`의 `help` 인자를 활용하여 툴팁으로 표시하는 것입니다.
                    # 현재 CSS에는 `current-date`와 `selected-date` 클래스가 정의되어 있고,
                    # Streamlit이 재렌더링될 때 `selected_dates`에 따라
                    # 그 스타일이 '적용된 것처럼' 보이게 되는 것이 핵심입니다.
                    # 즉, Streamlit은 `st.session_state`가 변경되면 해당 컴포넌트를 다시 그리고,
                    # 그때 CSS가 다시 적용되므로 원하는 시각적 효과를 얻을 수 있습니다.

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
    selected_days = render_calendar_custom(apply_date) # 함수 호출 변경
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
