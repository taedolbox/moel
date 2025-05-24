import streamlit as st
import calendar
from datetime import date, timedelta

# 달력의 시작 요일을 일요일로 설정 (0=일, 1=월, ..., 6=토)
calendar.setfirstweekday(calendar.SUNDAY)

def run_daily_worker_eligibility_app():
    st.set_page_config(layout="wide") # 전체 페이지 너비를 사용하도록 설정
    st.title("일용근로자 수급자격 모의계산")
    
    # 🌟 수급자격 신청일 입력
    claim_date = st.date_input("수급자격 신청일", value=date(2025, 5, 24))

    # 🌟 조건 1 범위 (직전 달 초일부터 신청일까지)
    # 예시: 신청일이 2025-05-24 -> 직전 달은 2025-04-01부터 시작
    first_day_of_claim_month = claim_date.replace(day=1)
    calendar_start_date = (first_day_of_claim_month - timedelta(days=1)).replace(day=1)
    calendar_end_date = claim_date

    # 🌟 선택한 날짜들 저장 (세션 상태로 관리)
    if "selected_days" not in st.session_state:
        st.session_state.selected_days = set()

    # set은 직접 변경 시 Streamlit이 감지하지 못할 수 있으므로, 복사본을 사용하고 다시 할당
    selected_days = st.session_state.selected_days.copy() # set은 mutable하므로 직접 변경 대신 복사하여 사용

    def toggle_date(d):
        if d in st.session_state.selected_days:
            st.session_state.selected_days.remove(d)
        else:
            st.session_state.selected_days.add(d)
        # st.rerun() # toggle_date 함수 호출 시 Streamlit이 자동으로 rerun 감지 (불필요한 호출 방지)


    st.subheader(f"근무일 선택 (조건 1 범위: {calendar_start_date} ~ {calendar_end_date})")

    # CSS 스타일 정의
    st.markdown("""
    <style>
    /* 전체 페이지 배경 및 텍스트 색상 */
    body {
        color: #ffffff;
        background-color: #0e1117;
    }

    /* Streamlit 컨테이너 패딩 조정 */
    .main .block-container {
        padding-top: 1rem;
        padding-right: 1rem;
        padding-left: 1rem;
        padding-bottom: 1rem;
    }

    /* 컬럼(날짜 셀)의 기본 스타일 */
    div[data-testid="stHorizontalBlock"] > div {
        flex-grow: 0;
        flex-shrink: 0;
        flex-basis: calc(100% / 8 - 6px); /* 7열에 맞추고 적절한 간격 조정 */
        min-width: 40px; /* 최소 너비 조정 */
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 2px;
        margin: 0 3px; /* 열 간 마진 추가 */
    }

    /* 요일 헤더와 날짜 간격 분리 */
    .day-header-container {
        margin-bottom: 10px; /* 헤더와 날짜 간격 늘림 */
    }

    /* 날짜 원의 공통 스타일 */
    .day-circle {
        width: 38px; /* 크기 키움 */
        height: 38px; /* 크기 키움 */
        border-radius: 50%;
        text-align: center;
        line-height: 38px; /* 높이에 맞춤 */
        margin: auto; /* 중앙 정렬 */
        font-weight: bold;
        transition: all 0.2s ease-in-out; /* 부드러운 전환 효과 */
        position: relative; /* 버튼이 겹치도록 설정 */
        z-index: 2; /* 버튼보다 위에 오도록 설정 */
    }

    /* 기본 날짜 스타일 */
    .default-day {
        border: 1px solid #444;
        background-color: #1a1a1a;
        color: #ffffff;
        cursor: pointer;
    }
    .default-day:hover {
        background-color: #333;
        border-color: #777;
    }

    /* 선택된 날짜 스타일 (녹색 원) */
    .selected-day {
        border: 2px solid #4CAF50;
        background-color: #4CAF50;
        color: #ffffff;
        cursor: pointer;
    }
    .selected-day:hover {
        background-color: #5cb85c;
        border-color: #5cb85c;
    }

    /* 오늘 날짜 스타일 (파란 테두리) */
    .today-day {
        border: 2px solid #00aaff;
        background-color: #1a1a1a;
        color: #ffffff;
        cursor: pointer;
    }
    .today-day:hover {
        background-color: #333;
        border-color: #00c0ff;
    }

    /* 오늘 & 선택된 날짜 */
    .today-selected-day {
        border: 2px solid #4CAF50; /* 선택된 색 유지 */
        background-color: #4CAF50;
        color: #ffffff;
        cursor: pointer;
        outline: 2px solid #00aaff; /* 오늘 날짜임을 나타내는 추가 테두리 */
        outline-offset: 1px;
    }
    .today-selected-day:hover {
        background-color: #5cb85c;
        border-color: #5cb85c;
    }

    /* 비활성화된 날짜 */
    .disabled-day {
        border: 1px solid #333;
        background-color: #2e2e2e;
        color: #555;
        cursor: not-allowed;
    }

    /* 빈 날짜 (달력에서 해당 월이 아닌 부분) */
    .empty-day {
        width: 38px;
        height: 38px;
        margin: auto;
    }

    /* 요일 헤더 스타일 */
    .day-header {
        text-align: center;
        font-weight: bold;
        padding: 5px 0;
        font-size: 1.1em;
        color: #ffffff;
    }
    .day-header.sunday {
        color: #ff6666 !important; /* 더 밝은 빨강 */
    }
    .day-header.saturday {
        color: #66ccff !important; /* 더 밝은 파랑 */
    }

    /* 월 헤더 스타일 */
    h3 {
        background-color: #2e2e2e;
        color: #ffffff;
        text-align: center;
        padding: 10px 0;
        margin-top: 20px;
        margin-bottom: 15px;
        font-size: 1.5em;
        border-radius: 5px;
    }

    /* Streamlit 버튼을 시각적으로 숨기지만 클릭 영역은 유지 */
    .stButton > button {
        position: absolute; /* 절대 위치로 설정 */
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        opacity: 0; /* 시각적으로 숨김 */
        z-index: 3; /* div 위에 오도록 설정하여 클릭 감지 */
        cursor: pointer;
    }

    </style>
    """, unsafe_allow_html=True)

    # 달력 렌더링
    current_month_to_render = calendar_start_date

    while current_month_to_render <= calendar_end_date:
        year = current_month_to_render.year
        month = current_month_to_render.month

        # `calendar.monthcalendar`로 주별 날짜 배열 생성
        month_calendar = calendar.monthcalendar(year, month)
        
        st.markdown(f"### {year}년 {month}월")

        # 요일 헤더 (일~토)
        # 중요: 요일 헤더도 st.columns로 정렬해야 합니다.
        st.markdown('<div class="day-header-container">', unsafe_allow_html=True)
        header_cols = st.columns(7)
        weekdays = ["일", "월", "화", "수", "목", "금", "토"]
        for i, day_name in enumerate(weekdays):
            class_name = "day-header"
            if day_name == "일":
                class_name += " sunday"
            elif day_name == "토":
                class_name += " saturday"
            header_cols[i].markdown(f'<div class="{class_name}">{day_name}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # 달력 날짜 렌더링
        for week_idx, week in enumerate(month_calendar):
            # 각 주마다 새로운 컬럼 세트 생성 (가장 중요!)
            cols = st.columns(7) 
            for i, day in enumerate(week):
                # 각 날짜에 대한 HTML을 해당 컬럼에 직접 렌더링
                if day == 0:  # 빈 날짜 (이전 달 또는 다음 달)
                    cols[i].markdown(f'<div class="empty-day"></div>', unsafe_allow_html=True)
                    continue

                d = date(year, month, day)
                
                # 신청일이 오늘이라고 가정 (예시: 2025년 5월 24일)
                is_today = (d == date(2025, 5, 24))

                # 조건 1 범위 밖의 날짜는 비활성화
                is_disabled = (d < calendar_start_date or d > calendar_end_date)

                is_selected = d in selected_days
                label = str(day)

                # CSS 클래스 결정
                css_class = "day-circle"
                if is_disabled:
                    css_class += " disabled-day"
                elif is_selected and is_today:
                    css_class += " today-selected-day"
                elif is_selected:
                    css_class += " selected-day"
                elif is_today:
                    css_class += " today-day"
                else:
                    css_class += " default-day"

                # Streamlit 버튼을 이용하여 클릭 이벤트 처리
                with cols[i]:
                    if not is_disabled:
                        # Streamlit의 button 위젯은 고유한 key를 필요로 합니다.
                        # on_click 콜백 함수를 사용하여 상태를 업데이트합니다.
                        st.button(
                            label, # 버튼 라벨은 숨겨지므로 아무 값이나 가능
                            key=f"btn_{d.isoformat()}", # 고유한 키
                            on_click=toggle_date, 
                            args=(d,), # toggle_date에 전달할 인자
                            use_container_width=True # 버튼이 컬럼 너비를 채우도록
                        )
                    # 실제 시각적인 날짜 UI를 렌더링합니다. 이 div는 위의 숨겨진 버튼 위에 겹쳐집니다.
                    st.markdown(f'<div class="{css_class}">{label}</div>', unsafe_allow_html=True)
        
        # 다음 달의 첫째 날로 이동
        current_month_to_render = (current_month_to_render.replace(day=28) + timedelta(days=4)).replace(day=1)

    # ---
    st.markdown("---")

    # 결과 출력
    st.subheader("결과")
    
    # 선택된 날짜 중 조건 1 범위 내에 있는 날짜만 카운트
    # 세션 상태에서 직접 가져와야 변경된 상태를 반영합니다.
    eligible_selected_days = {d for d in st.session_state.selected_days if calendar_start_date <= d <= calendar_end_date}
    
    st.write(f"선택한 근무일 수: **{len(eligible_selected_days)}일**")

    # 예시 조건 (수급자격 요건은 실제 조건에 따라 변경 필요)
    if len(eligible_selected_days) >= 10:  
        st.success("✅ 수급자격 요건 충족 가능성이 있습니다.")
    else:
        st.error("❌ 근무일이 부족합니다. 더 많은 근무일을 선택해야 할 수 있습니다.")
    
    st.info("참고: 이 계산은 모의 계산이며, 실제 수급자격은 고용보험법 및 관련 규정에 따라 달라질 수 있습니다.")

if __name__ == "__main__":
    run_daily_worker_eligibility_app()
