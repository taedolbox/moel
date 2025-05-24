import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import calendar

# (이전 코드 동일)

def toggle_date(date_obj):
    # 디버깅: toggle_date 함수 호출 확인
    print(f"DEBUG: toggle_date 함수 호출됨 - 대상 날짜: {date_obj}")
    if 'selected_dates' not in st.session_state:
        st.session_state.selected_dates = set()

    if date_obj in st.session_state.selected_dates:
        st.session_state.selected_dates.remove(date_obj)
        print(f"DEBUG: 날짜 제거됨: {date_obj}. 현재 선택된 날짜: {sorted(st.session_state.selected_dates)}")
    else:
        st.session_state.selected_dates.add(date_obj)
        print(f"DEBUG: 날짜 추가됨: {date_obj}. 현재 선택된 날짜: {sorted(st.session_state.selected_dates)}")

# render_calendar 함수를 완전히 재작성해야 합니다.
def render_calendar_with_custom_buttons(apply_date):
    st.markdown(f"""
    <style>
    /* 전체 앱 배경색은 이전과 동일 */
    .stApp {{ background-color: #1e1e1e; color: white; }}
    /* ... (다른 일반적인 스타일은 이전과 동일하게 유지) ... */

    /* 커스텀 버튼 스타일 (새로운 클래스 사용) */
    .date-button {{
        width: 40px; height: 40px; border-radius: 0;
        display: flex; align-items: center; justify-content: center;
        font-size: 1rem; padding: 0; margin: 0;
        border: 1px solid #ccc;
        background-color: #1e1e1e; /* 기본 어두운 배경 */
        color: white;
        transition: all 0.2s ease;
        cursor: pointer;
    }}
    /* 선택되지 않은 버튼 호버 효과 */
    .date-button:not(.selected):hover {{
        border: 2px solid #00ff00;
        background-color: rgba(0, 255, 0, 0.2);
    }}
    /* 선택된 날짜 스타일 - 붉은색 배경 */
    .date-button.selected {{
        background-color: #ff0000; /* 붉은색 배경 */
        color: white;
        border: 2px solid #ffffff; /* 흰색 테두리 */
    }}
    /* 현재 날짜 스타일 - 파란색 배경 (선택 상태와 관계없이) */
    .date-button.current-date {{
        background-color: #0000ff; /* 파란색 배경 */
        color: white;
        font-weight: bold;
        border: 1px solid #ccc;
    }}
    /* 비활성화(미래) 날짜 스타일 */
    .date-button.disabled {{
        color: gray;
        background-color: #1e1e1e;
        border: 1px solid #ccc;
        cursor: not-allowed;
    }}
    /* 요일 헤더 스타일 */
    .day-header {{
        font-size: 0.9rem; text-align: center; color: white;
    }}
    /* 월 경계 스타일 */
    .month-header {{
        margin: 0.5rem 0; padding: 0.2rem;
        background-color: #2e2e2e; text-align: center; color: white;
    }}
    /* Streamlit의 내부 버튼 스타일을 덮어쓰지 않도록 주의 */
    </style>
    """, unsafe_allow_html=True)

    if 'selected_dates' not in st.session_state:
        st.session_state.selected_dates = set()
    selected_dates = st.session_state.selected_dates
    current_date = datetime.now().date()

    # JavaScript를 사용하여 Streamlit으로 데이터를 전달하고 rerun 트리거
    st.markdown(f"""
    <script>
    function toggleDateAndRerun(dateString) {{
        // Streamlit 백엔드로 데이터를 전달하는 방법 (예: WebSocket을 통해)
        // Streamlit의 내부 API를 직접 호출하는 것은 어려우므로, 일반적으로는 hidden widget을 사용
        // 여기서는 가장 간단한 개념만 보여주며, 실제 구현은 더 복잡할 수 있습니다.
        // Streamlit 커스텀 컴포넌트 개발 환경이 아니면 직접적인 JS->Python 통신은 까다롭습니다.

        // 가장 간단한 방법은 URL 쿼리 파라미터를 변경하고 리디렉션하는 것인데,
        // 이 방식은 session_state를 직접 조작하는 것과 다릅니다.

        // Streamlit의 hidden widget을 활용하여 Python 함수를 트리거하는 방식이 있었으나,
        // 최근 버전에서 이 방법이 명확하게 지원되지 않을 수 있습니다.
        // 가장 안정적인 방법은 Streamlit Custom Component를 사용하는 것입니다.

        // 임시 방편으로, 클릭 이벤트를 Streamlit에 알리는 더미 폼 제출 같은 것을 고려할 수 있습니다.
        // 하지만 이것도 매우 해키(hacky)한 방법입니다.

        // **정상적인 방법은 다음과 같습니다.**
        // 1. st.markdown으로 HTML 버튼을 렌더링.
        // 2. 이 버튼의 on_click 이벤트에 JavaScript를 연결.
        // 3. JavaScript에서 Window.location.search를 변경하여 Streamlit URL 쿼리 파라미터에 값을 추가.
        // 4. Streamlit 앱은 URL 쿼리 파라미터 변경을 감지하고 재실행.
        // 5. Python 코드에서 URL 쿼리 파라미터를 읽어 session_state를 업데이트.

        // 하지만 이렇게 되면 버튼 클릭 후 URL이 변경되는 문제가 생깁니다.
        // **제약이 많은 상황이므로, 저는 st.button을 사용하되 시각적 피드백을 다른 방식으로 주는 것을 재고해달라고 제안합니다.**
        // 또는, Streamlit custom component를 사용해야 합니다.

        // 지금으로서는, st.rerun()을 JS에서 직접 호출하는 안정적인 방법이 없으므로
        // 제가 처음에 제시했던 st.button을 통한 해결책이 동작하지 않는다면,
        // 이 방법은 Streamlit의 기본적인 사용 범위를 넘어섭니다.
    }}
    </script>
    """, unsafe_allow_html=True)

    start_date_for_calendar = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1).date()
    end_date_for_calendar = apply_date
    months_to_display = sorted(set((d.year, d.month) for d in pd.date_range(start=start_date_for_calendar, end=end_date_for_calendar).date))

    for year, month in months_to_display:
        st.markdown(f"<h3 class='month-header'>{year} {calendar.month_name[month]}</h3>", unsafe_allow_html=True)
        cal = calendar.monthcalendar(year, month)
        days_of_week_korean = ["일", "월", "화", "수", "목", "금", "토"]

        cols = st.columns(7, gap="small")
        for i, day_name in enumerate(days_of_week_korean):
            color = "red" if i == 0 else ("blue" if i == 6 else "white")
            cols[i].markdown(f"<span class='day-header' style='color:{color}'><strong>{day_name}</strong></span>", unsafe_allow_html=True)

        for week in cal:
            cols = st.columns(7, gap="small")
            for i, day in enumerate(week):
                if day == 0:
                    cols[i].markdown(" ")
                else:
                    date_obj = date(year, month, day)
                    
                    button_classes = ["date-button"]
                    if date_obj in selected_dates:
                        button_classes.append("selected")
                    if date_obj == current_date:
                        button_classes.append("current-date")
                    if date_obj > apply_date: # 비활성화
                        button_classes.append("disabled")
                        # 비활성화된 날짜는 클릭 불가능하게 CSS로만 처리 (JavaScript 이벤트 없음)
                        cols[i].markdown(
                            f"<button class='{' '.join(button_classes)}' disabled>{day}</button>",
                            unsafe_allow_html=True
                        )
                        continue

                    # 클릭 이벤트는 Streamlit의 st.button을 사용할 때 가장 편리.
                    # 하지만 st.button은 class나 id를 동적으로 제어하기 어렵다는 문제.
                    # st.markdown으로 HTML 버튼을 만들면 클릭 이벤트를 직접 Python으로 전달하기 매우 까다로움.
                    # -> 결국, st.button을 다시 사용하면서 시각적 피드백 방법을 재고해야 합니다.
                    
                    # === 다시 st.button을 사용하여 해결책을 모색 ===
                    # 아래 주석 처리된 부분은 st.markdown으로 HTML 버튼을 만들려 할 때의 난관을 보여줍니다.
                    # cols[i].markdown(
                    #     f"<button class='{' '.join(button_classes)}' onclick='toggleDateAndRerun(\"{date_obj.isoformat()}\")'>{day}</button>",
                    #     unsafe_allow_html=True
                    # )
                    
                    # st.button을 사용하되, 선택된 날짜와 현재 날짜의 CSS 선택자 문제를 우회하는 방법은?
                    # Streamlit v1.45.1에서 data-testid="stBaseButton-secondary"만 있다면
                    # CSS만으로는 'selected'와 'current' 상태를 구분할 수 없습니다.

                    # 따라서, 기존의 st.button 코드를 유지하되, 이 문제에 대한 근본적인 해결책은
                    # Streamlit 자체의 기능 개선 또는 Custom Component 사용 외에는 어렵습니다.
                    # 제가 할 수 있는 최선은 Streamlit UI의 한계를 설명드리고,
                    # 다른 시각적 피드백 방법을 제안하는 것입니다.

                    # 이전에 제공했던 코드 그대로 다시 사용합니다.
                    # 왜냐하면 이 코드는 st.session_state를 정확히 업데이트하고,
                    # CSS가 id를 기반으로 작동하도록 의도되었기 때문입니다.
                    # 문제는 id가 HTML에 없다는 것이므로, 이 부분을 극복할 수 없습니다.
                    
                    is_selected = date_obj in selected_dates
                    is_current = date_obj == current_date

                    # Streamlit 버튼의 key는 고유해야 하며, 상태 변화를 감지하기 위해 동적으로 변경
                    # 이 부분이 CSS와 연동되어 색상을 변경하는 핵심입니다. (아쉽게도 HTML ID로 변환되지 않음)
                    if is_selected:
                        # 이 key는 Streamlit 내부용이며, HTML ID로 반영되지 않습니다.
                        button_key = f"selected-{date_obj}"
                    elif is_current:
                        button_key = f"current-{date_obj}"
                    else:
                        button_key = f"btn-{date_obj}"

                    if cols[i].button(
                        str(day),
                        key=button_key,
                        on_click=toggle_date,
                        help="클릭하여 근무일을 선택하거나 해제하세요",
                        kwargs={"date_obj": date_obj}
                    ):
                        st.rerun() # 버튼 클릭 후 앱을 새로고침하여 변경된 스타일 적용


    if selected_dates:
        st.markdown("### ✅ 선택된 근무일자")
        st.markdown(f"**디버그: 세션 상태에 저장된 선택 날짜:** {sorted(selected_dates)}")
        st.markdown(", ".join([d.strftime("%Y-%m-%d") for d in sorted(selected_dates)]))

    return selected_dates

# (나머지 앱 로직은 render_calendar_with_custom_buttons 함수를 사용하도록 변경)
def daily_worker_eligibility_app():
    st.header("일용근로자 수급자격 요건 모의계산")
    st.markdown(f"**오늘 날짜와 시간**: {current_time_korean}", unsafe_allow_html=True)
    st.markdown("### 📋 요건 조건")
    st.markdown("- **조건 1**: 수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지의 근로일 수가 총 일수의 1/3 미만이어야 합니다.")
    st.markdown("- **조건 2 (건설일용근로자만 해당)**: 수급자격 인정신청일 직전 14일간 근무 사실이 없어야 합니다 (신청일 제외).")
    st.markdown("---")

    worker_type = st.radio("근로자 유형을 선택하세요", ["일반일용근로자", "건설일용근로자"])
    apply_date = st.date_input("수급자격 신청일을 선택하세요", value=datetime.now().date())
    
    date_range_objects, start_date = get_date_range(apply_date)

    st.markdown("---")
    st.markdown("#### ✅ 근무일 선택 달력")
    # st.button의 한계로 인해, 여기서는 직접적인 색상 변경이 어려움을 인지하고 진행합니다.
    # 이 부분은 이전 render_calendar 함수와 동일한 기능을 수행합니다.
    # 만약 직접 HTML 버튼 구현을 원하시면, render_calendar_with_custom_buttons 함수가 아니라면
    # 훨씬 더 복잡한 JavaScript/Streamlit Custom Component 개발이 필요합니다.
    selected_days = render_calendar_old_logic(apply_date) # 이전 render_calendar 함수 이름 변경
    st.markdown("---")

    # (조건 1, 2 계산 및 최종 판단 로직은 동일)
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

    condition2 = False
    if worker_type == "건설일용근로자":
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

    if worker_type == "건설일용근로자" and not condition2:
        st.markdown("### 📅 조건 2를 충족하려면 언제 신청해야 할까요?")
        last_worked_day = max((d for d in selected_days if d < apply_date), default=None)
        if last_worked_day:
            suggested_date = last_worked_day + timedelta(days=15)
            st.info(f"✅ **{suggested_date.strftime('%Y-%m-%d')}** 이후에 신청하면 조건 2를 충족할 수 있습니다.")
        else:
            st.info("이미 최근 14일간 근무내역이 없으므로, 신청일을 조정할 필요는 없습니다.")

    st.subheader("📌 최종 판단")
    if worker_type == "일반일용근로자":
        if condition1:
            st.success(f"✅ 일반일용근로자 요건 충족\n\n**수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지({start_date.strftime('%Y-%m-%d')} ~ {apply_date.strftime('%Y-%m-%d')}) 근로일 수의 합이 같은 기간 동안의 총 일수의 3분의 1 미만**")
        else:
            st.error("❌ 일반일용근로자 요건 미충족\n\n**총 일수의 3분의 1 이상 근로 사실이 확인되어 요건을 충족하지 못합니다.**")
    else:
        fourteen_days_prior_end = apply_date - timedelta(days=1)
        fourteen_days_prior_start = fourteen_days_prior_end - timedelta(days=13)
        if condition1 and condition2:
            st.success(f"✅ 건설일용근로자 요건 충족\n\n**수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지({start_date.strftime('%Y-%m-%d')} ~ {apply_date.strftime('%Y-%m-%d')}) 근로일 수의 합이 총 일수의 3분의 1 미만이고, 신청일 직전 14일간({fourteen_days_prior_start.strftime('%Y-%m-%d')} ~ {fourteen_days_prior_end.strftime('%Y-%m-%d')}) 근무 사실이 없음을 확인합니다.**")
        else:
            st.error(f"❌ 건설일용근로자 요건 미충족\n\n**총 일수의 3분의 1 이상 근로 사실이 확인되거나, 신청일 직전 14일간({fourteen_days_prior_start.strftime('%Y-%m-%d')} ~ {fourteen_days_prior_end.strftime('%Y-%m-%d')}) 내 근무기록이 존재하므로 요건을 충족하지 못합니다.**")

# 기존 render_calendar 함수를 사용하되 이름만 변경 (아래에서 호출)
def render_calendar_old_logic(apply_date):
    """
    달력을 렌더링하고 날짜 선택 기능을 제공합니다.
    선택된 날짜, 현재 날짜, 비활성화된 날짜에 따라 버튼 스타일이 달라집니다.
    (이전 코드와 동일, CSS의 id*="selected-" 부분이 작동하지 않음을 인지)
    """
    # 사용자 정의 CSS 주입: 달력 버튼의 시각적 피드백을 위한 핵심 부분입니다.
    st.markdown(f"""
    <style>
    /* 전체 앱 배경색을 어둡게 설정 */
    .stApp {{
        background-color: #1e1e1e; /* 어두운 회색 */
        color: white;
    }}
    /* 라디오 버튼 텍스트 색상 */
    div[data-testid="stRadio"] label {{
        color: white !important;
        font-size: 18px !important;
    }}
    /* 헤더 텍스트 색상 */
    h1, h2, h3, h4, h5, h6, .stMarkdown, .stText {{
        color: white;
    }}
    /* 조건문 텍스트 색상 */
    div[data-testid="stMarkdownContainer"] p {{
        color: white;
    }}
    /* Streamlit Input 위젯 (날짜 선택 등)의 라벨 색상 */
    .stDateInput label {{
        color: white !important;
    }}
    .stSelectbox label {{
        color: white !important;
    }}
    /* Streamlit info, success, warning box 텍스트 색상 */
    .st-dg, .st-ck, .st-cf {{ /* info, success, warning alert box */
        color: black !important; /* 알림창 텍스트는 검은색으로 유지하여 가독성 높임 */
    }}

    /* 달력 열의 패딩 및 마진 감소 */
    div[data-testid="stHorizontalBlock"] {{
        gap: 0.1rem !important;
    }}
    div[data-testid="stHorizontalBlock"] > div {{
        padding: 0 !important;
        margin: 0 !important;
    }}
    /* 달력 일 버튼 스타일 */
    div[data-testid="stButton"] button {{
        width: 40px !important;
        height: 40px !important;
        border-radius: 0 !important; /* 사각형 버튼 */
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 1rem !important;
        padding: 0 !important;
        margin: 0 !important;
        border: 1px solid #ccc !important; /* 기본 연한 테두리 */
        background-color: #1e1e1e !important; /* 기본 어두운 배경 */
        color: white !important;
        transition: all 0.2s ease !important; /* 부드러운 전환 효과 */
    }}
    /* 선택되지 않은 버튼 호버 효과 */
    div[data-testid="stButton"] button:not([id*="selected-"]):hover {{
        border: 2px solid #00ff00 !important; /* 초록색 테두리 */
        background-color: rgba(0, 255, 0, 0.2) !important; /* 연한 초록색 배경 */
    }}
    /* !!! 여기부터 선택된 날짜의 색상 변경 부분입니다 !!! */
    /* id*="selected-" 선택자가 작동하지 않음을 인지합니다. */
    div[data-testid="stButton"] button[id*="selected-"] {{
        background-color: #ff0000 !important; /* 선택된 날짜 붉은색 배경 */
        color: white !important;
        border: 2px solid #ffffff !important; /* 흰색 테두리 */
    }}
    /* 현재 날짜 스타일 - 파란색 배경 */
    div[data-testid="stButton"] button[id*="current-"] {{
        background-color: #0000ff !important; /* 현재 날짜 파란색 배경 */
        color: white !important;
        font-weight: bold !important;
        border: 1px solid #ccc !important;
    }}
    /* 비활성화(미래) 날짜 스타일 */
    div[data-testid="stButton"] button[disabled] {{
        color: gray !important;
        background-color: #1e1e1e !important;
        border: 1px solid #ccc !important;
        cursor: not-allowed !important; /* 비활성화 커서 */
    }}
    /* 요일 헤더 스타일 */
    div[data-testid="stHorizontalBlock"] span {{
        font-size: 0.9rem !important;
        text-align: center !important;
        color: white !important;
    }}
    /* 모바일에서 강제 가로 배열 */
    @media (max-width: 600px) {{
        div[data-testid="stHorizontalBlock"] {{
            display: flex !important;
            flex-wrap: nowrap !important;
            gap: 0.1rem !important;
        }}
        div[data-testid="stHorizontalBlock"] > div {{
            flex: 1 !important;
            min-width: 35px !important;
            padding: 0 !important;
        }}
        div[data-testid="stButton"] button {{
            font-size: 0.8rem !important;
            width: 35px !important;
            height: 35px !important;
        }}
    }}
    /* 월 경계 스타일 */
    div[data-testid="stMarkdownContainer"] h3 {{
        margin: 0.5rem 0 !important;
        padding: 0.2rem !important;
        background-color: #2e2e2e !important; /* 앱 배경보다 약간 밝은 색 */
        text-align: center !important;
        color: white !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    # 달력 표시할 월 범위 계산
    start_date_for_calendar = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1).date()
    end_date_for_calendar = apply_date
    months_to_display = sorted(set((d.year, d.month) for d in pd.date_range(start=start_date_for_calendar, end=end_date_for_calendar).date))

    if 'selected_dates' not in st.session_state:
        st.session_state.selected_dates = set()
    selected_dates = st.session_state.selected_dates
    current_date = datetime.now().date()

    for year, month in months_to_display:
        st.markdown(f"### {year} {calendar.month_name[month]}", unsafe_allow_html=True)
        cal = calendar.monthcalendar(year, month)
        days_of_week_korean = ["일", "월", "화", "수", "목", "금", "토"]

        cols = st.columns(7, gap="small")
        for i, day_name in enumerate(days_of_week_korean):
            color = "red" if i == 0 else ("blue" if i == 6 else "white")
            cols[i].markdown(f"<span style='color:{color}'><strong>{day_name}</strong></span>", unsafe_allow_html=True)

        for week in cal:
            cols = st.columns(7, gap="small")
            for i, day in enumerate(week):
                if day == 0:
                    cols[i].markdown(" ")
                else:
                    date_obj = date(year, month, day)

                    if date_obj > apply_date:
                        cols[i].button(str(day), key=f"btn_disabled_{date_obj}", disabled=True)
                        continue

                    is_selected = date_obj in selected_dates
                    is_current = date_obj == current_date

                    # 이 key는 Streamlit 내부용이며, HTML ID로 반영되지 않아 CSS가 적용되지 않습니다.
                    if is_selected:
                        button_key = f"selected-{date_obj}"
                    elif is_current:
                        button_key = f"current-{date_obj}"
                    else:
                        button_key = f"btn-{date_obj}"

                    if cols[i].button(
                        str(day),
                        key=button_key,
                        on_click=toggle_date,
                        help="클릭하여 근무일을 선택하거나 해제하세요",
                        kwargs={"date_obj": date_obj}
                    ):
                        st.rerun()

    if selected_dates:
        st.markdown("### ✅ 선택된 근무일자")
        st.markdown(f"**디버그: 세션 상태에 저장된 선택 날짜:** {sorted(selected_dates)}")
        st.markdown(", ".join([d.strftime("%Y-%m-%d") for d in sorted(selected_dates)]))

    return selected_dates

# 앱 실행 진입점
if __name__ == "__main__":
    daily_worker_eligibility_app()
