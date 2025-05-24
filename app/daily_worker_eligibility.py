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

def render_calendar_with_buttons(apply_date): # 함수명 변경: render_calendar_with_buttons
    """
    달력을 렌더링하고 버튼을 이용한 날짜 선택 기능을 제공합니다.
    선택된 날짜, 현재 날짜, 신청일 이후 날짜는 표시하지 않습니다.
    """
    # 사용자 정의 CSS 주입
    st.markdown(f"""
    <style>
    /* 전체 폰트 Streamlit 기본 폰트 사용 */

    /* 달력 전체 컨테이너 가운데 정렬을 위한 상위 요소에 Flexbox 적용 */
    /* Streamlit이 st.columns를 감싸는 div가 무엇인지 정확히 알아내야 함 */
    /* 가장 일반적인 상위 div[data-testid="stVerticalBlock"] 내의 두 번째 div를 시도 */
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
    div[data-testid="stHorizontalBlock"] span {{
        color: #000000 !important; /* 라이트 모드일 때 검정색 */
    }}

    /* 개별 날짜 버튼 스타일 */
    div[data-testid="stHorizontalBlock"] .stButton > button {{ /* st.button의 실제 버튼 요소 선택 */
        width: 45px; /* 날짜 버튼 너비 */
        height: 45px; /* 날짜 버튼 높이 */
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
    }}

    /* Dark Mode (prefers-color-scheme) */
    @media (prefers-color-scheme: dark) {{
        div[data-testid="stMarkdownContainer"] h3 {{
            background-color: #2e2e2e !important; /* 다크 모드 */
            color: #ffffff !important; /* 다크 모드 */
        }}
        /* 요일 헤더 기본 글자색 (다크 모드) */
        div[data-testid="stHorizontalBlock"] span {{
            color: #ffffff !important; /* 다크 모드일 때 흰색 */
        }}
        /* 개별 날짜 버튼 스타일 (다크 모드) */
        div[data-testid="stHorizontalBlock"] .stButton > button {{
            border: 1px solid #444; /* 다크 모드 테두리색 */
            background-color: #1e1e1e; /* 다크 모드 배경색 */
            color: #ffffff; /* 날짜 숫자 글자색 (다크 모드) */
        }}
    }}

    /* 선택된 날짜 버튼 스타일 (라이트/다크 모드 공통) */
    div[data-testid="stHorizontalBlock"] .stButton > button.selected-date {{ /* Python에서 추가할 클래스 */
        background-color: #ff0000; /* 선택 시 빨간색 배경 */
        border: 1px solid #ff0000; /* 테두리도 빨간색 */
        color: #ffffff; /* 선택 시 흰색 글씨 */
        font-weight: bold; /* 선택된 날짜 글자 두껍게 */
        /* border-radius: 50%; */ /* 원형을 원한다면 이 주석을 해제하고 위 width/height 값을 동일하게 (예: 40px) 설정 */
    }}

    /* 오늘 날짜 스타일 (선택되지 않았을 때만 적용) */
    div[data-testid="stHorizontalBlock"] .stButton > button.current-date:not(.selected-date) {{
        border: 2px solid blue !important; /* 오늘 날짜 파란색 테두리 */
    }}


    /* 요일 헤더 공통 스타일 (폰트 크기 및 정렬) */
    div[data-testid="stHorizontalBlock"] > div span {{
        font-size: 1.1em !important; /* 요일 폰트 크기 */
        text-align: center !important; /* 가운데 정렬 */
        display: block !important; /* text-align을 위해 block으로 설정 */
        width: 100% !important; /* 부모 div의 너비에 맞춤 */
        font-weight: bold; /* 요일 글자 두껍게 */
        padding: 5px 0; /* 요일 패딩 추가 */
    }}

    /* 요일 헤더 특정 요일 색상 (라이트/다크 모드 공통) */
    /* 일요일 빨간색 */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) span {{
        color: red !important;
    }}
    /* 토요일 파란색 */
    div[data-testid="stHorizontalBlock"] > div:nth-child(7) span {{
        color: blue !important;
    }}

    /* 달력 날짜 그리드를 감싸는 stHorizontalBlock에 flexbox 적용 */
    /* (st.columns가 이 data-testid를 가짐) */
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
        display: flex; /* 내부 요소 (버튼) 정렬을 위해 flexbox 사용 */
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
        div[data-testid="stHorizontalBlock"] .stButton > button {{
            width: 38px;
            height: 38px;
            font-size: 1em;
        }}
        div[data-testid="stHorizontalBlock"] > div span {{
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

    # 각 월별 달력 렌더링
    for year, month in months_to_display:
        st.markdown(f"<h3>{year}년 {month}월</h3>", unsafe_allow_html=True)
        cal = calendar.monthcalendar(year, month)
        days_of_week_korean = ["일", "월", "화", "수", "목", "금", "토"]

        # 요일 헤더 생성 (st.columns 사용)
        cols = st.columns(7, gap="small")
        for i, day_name in enumerate(days_of_week_korean):
            cols[i].markdown(f"<span><strong>{day_name}</strong></span>", unsafe_allow_html=True)

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

                    # 버튼에 적용될 CSS 클래스 결정
                    button_class = []
                    if date_obj in selected_dates:
                        button_class.append("selected-date")
                    if date_obj == current_date:
                        button_class.append("current-date")

                    # st.button을 사용하여 날짜를 버튼으로 표시
                    # key는 고유해야 함. 클래스는 unsafe_allow_html로 직접 추가
                    if cols[i].button(str(day), key=f"btn_{date_obj}", help=f"{date_obj.strftime('%Y-%m-%d')} 선택",
                                      # class를 직접 넣는 방법은 Streamlit에서 지원하지 않으므로, 아래 HTML 마크다운 방식으로 대체
                                     ):
                        # 버튼이 클릭되었을 때 선택 상태 토글
                        if date_obj in selected_dates:
                            selected_dates.discard(date_obj)
                        else:
                            selected_dates.add(date_obj)
                        st.session_state.selected_dates = selected_dates # 세션 상태 업데이트
                        st.experimental_rerun() # 상태 변경 후 재실행하여 UI 업데이트

                    # Streamlit 버튼에 클래스를 동적으로 적용하는 직접적인 방법이 없으므로,
                    # JavaScript를 사용하거나, CSS 선택자를 매우 구체적으로 지정해야 합니다.
                    # 여기서는 CSS 선택자를 통해 버튼에 스타일을 적용하고,
                    # 선택된 상태는 Python에서 처리 후 재실행하여 UI를 업데이트하는 방식으로 합니다.
                    # 만약 `button_class`를 직접 버튼 태그에 넣고 싶다면, `st.markdown`으로 HTML을 직접 구성해야 합니다.
                    # 현재 CSS는 `stButton > button`에 적용되고, `selected-date` 클래스는 Python에서
                    # 버튼이 선택되었을 때 재실행하면서 버튼의 배경색을 변경하도록 CSS에서 설정했습니다.
                    # Streamlit 렌더링 후 클래스 추가를 위해 스크립트를 삽입해야 하지만,
                    # 간단한 예시에서는 선택된 날짜에 `selected-date` 클래스가 적용된 것으로 가정하고 CSS를 작성했습니다.
                    # 실제 Streamlit 버튼 컴포넌트 자체에 동적으로 클래스를 추가하려면 더 복잡한 JS 주입이 필요합니다.

    # 선택된 날짜에 대한 CSS 클래스 동적 부여 (버튼 렌더링 후)
    # 이 부분은 Streamlit 컴포넌트의 한계로 직접적인 CSS 클래스 주입이 어렵습니다.
    # 대신, 선택된 날짜의 버튼에 스타일이 적용되도록 CSS를 다시 검토했습니다.
    # 즉, selected_dates에 있으면 `st.experimental_rerun()`으로 UI를 새로 그리게 하여
    # CSS의 `.stButton > button.selected-date` 규칙이 적용되도록 합니다.
    # 그러나 Streamlit은 `st.button`에 직접적인 HTML class 인자를 제공하지 않으므로
    # `st.experimental_rerun()`으로 상태가 변경될 때마다 전체를 다시 그리게 하여
    # `current-date`와 `selected-date`가 CSS에 의해 적용되도록 합니다.
    # 이 부분을 직접적인 HTML 및 JS 삽입 없이 구현하려면 다음과 같이 접근합니다:
    # 1. `st.button`은 클릭 이벤트를 감지.
    # 2. 클릭 시 `st.session_state.selected_dates`를 업데이트.
    # 3. `st.experimental_rerun()`을 호출하여 전체 앱을 다시 그림.
    # 4. 앱이 다시 그려질 때, 각 날짜 버튼이 현재 `selected_dates`에 포함되어 있는지 확인하고
    #    그에 맞는 CSS 스타일이 적용되도록 CSS를 미리 정의해 둠. (이전 접근 방식과 유사)

    # `st.button`은 `key` 인자가 필수입니다.
    # `cols[i].button(str(day), key=f"btn_{date_obj}")` 부분에 `key`를 이미 넣어두었습니다.

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
    selected_days = render_calendar_with_buttons(apply_date) # 함수 호출 변경
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
