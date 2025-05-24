import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import calendar

# 현재 날짜와 시간을 기반으로 KST 오전 XX:XX 형식을 생성
current_datetime = datetime.now()
current_time_korean = current_datetime.strftime('%Y년 %m월 %d일 %A 오전 %I:%M KST')

def get_date_range(apply_date):
    """
    신청일을 기준으로 이전 달 초일부터 신청일까지의 날짜 범위를 반환합니다.
    반환되는 날짜들은 datetime.date 객체들의 리스트입니다.
    """
    start_date = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1).date()
    # pd.date_range는 datetime 객체를 반환하므로 .date 속성을 사용하여 datetime.date로 변환
    return [d.date() for d in pd.date_range(start=start_date, end=apply_date)], start_date

def render_calendar_with_checkboxes(apply_date):
    """
    달력을 렌더링하고 체크박스를 이용한 날짜 선택 기능을 제공합니다.
    선택된 날짜, 현재 날짜, 신청일 이후의 미래 날짜에 따라 스타일이 달라집니다.
    """
    # 사용자 정의 CSS 주입
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

    /* 체크박스 컨테이너 (날짜 숫자를 포함하는 부분) */
    div[data-testid="stCheckbox"] {{
        width: 40px !important; /* 버튼과 동일한 너비 */
        height: 40px !important; /* 버튼과 동일한 높이 */
        display: flex !important;
        align-items: center !important;
        justify-content: center !important; /* 숫자를 중앙에 배치 */
        padding: 0 !important;
        margin: 0 !important;
        border: 1px solid #ccc !important; /* 기본 테두리 */
        background-color: #1e1e1e !important; /* 기본 어두운 배경 */
        transition: all 0.2s ease !important;
        cursor: pointer; /* 클릭 가능한 커서 */
    }}
    
    /* 체크박스 라벨 전체 (아이콘과 텍스트 포함) */
    div[data-testid="stCheckbox"] label {{
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%; /* 부모 div에 꽉 차게 */
        height: 100%; /* 부모 div에 꽉 차게 */
        margin: 0 !important; /* 기본 마진 제거 */
    }}

    /* 체크마크 아이콘 (체크박스 자체) */
    div[data-testid="stCheckbox"] label div[data-testid="stDecoration"] {{
        display: none !important; /* 체크마크 아이콘 숨기기 */
    }}

    /* 물음표 아이콘 (help 텍스트) - help 인자 제거로 더 이상 필요 없지만 혹시 몰라 유지 */
    div[data-testid="stCheckbox"] label span[data-baseweb="tooltip"] {{
        display: none !important; /* 물음표 아이콘 숨기기 */
    }}

    /* 체크박스 라벨 텍스트 스타일 (날짜 숫자) */
    div[data-testid="stCheckbox"] label div[data-testid="stMarkdownContainer"] p {{
        color: white !important; /* 기본 텍스트 색상 */
        font-size: 1rem !important; /* 폰트 크기 조정 */
        line-height: 1; /* 줄 높이 조정하여 텍스트가 중앙에 오도록 */
        margin: 0 !important; /* p 태그 기본 마진 제거 */
        padding: 0 !important;
        text-align: center; /* 텍스트 중앙 정렬 */
        width: 100%; /* 텍스트 컨테이너가 공간을 다 차지하도록 */
        display: flex; /* 내부 텍스트를 flex로 만들어서 중앙 정렬 */
        align-items: center;
        justify-content: center;
        height: 100%; /* p 태그가 부모 div에 꽉 차도록 */
    }}
    
    /* 선택된 날짜 (체크박스 체크 상태) */
    div[data-testid="stCheckbox"] input[type="checkbox"]:checked + label {{
        background-color: #ff0000 !important; /* 붉은색 배경 */
        border: 2px solid #ffffff !important; /* 흰색 테두리 */
        box-sizing: border-box; /* 패딩, 보더가 너비/높이에 포함되도록 */
    }}
    div[data-testid="stCheckbox"] input[type="checkbox"]:checked + label p {{
        color: white !important; /* 선택된 날짜의 텍스트 색상 */
    }}

    /* 현재 날짜 스타일 - 텍스트 bold 처리 (파이썬에서 처리) */
    /* 별도의 테두리 스타일은 제거하고, 기본 체크박스 스타일에 맡깁니다. */
    
    /* 신청일 이후 미래 날짜 스타일 (흐리게/반전 효과) */
    div[data-testid="stCheckbox"] input[type="checkbox"]:disabled + label {{
        color: #888888 !important; /* 텍스트 회색 (더 흐리게) */
        background-color: #2a2a2a !important; /* 배경 약간 더 밝게 */
        border: 1px solid #555555 !important; /* 테두리 더 흐리게 */
        cursor: not-allowed !important; /* 비활성화 커서 */
        opacity: 0.5; /* 투명도 더 낮게 (더 흐리게) */
    }}
    div[data-testid="stCheckbox"] input[type="checkbox"]:disabled + label p {{
        color: #888888 !important; /* 텍스트 회색 */
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
        div[data-testid="stCheckbox"] {{ /* 체크박스 크기 조정 */
            font-size: 0.8rem !important;
            width: 35px !important;
            height: 35px !important;
        }}
        div[data-testid="stCheckbox"] label div[data-testid="stMarkdownContainer"] p {{
            font-size: 0.8rem !important;
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

    # st.session_state에서 선택된 날짜 집합 가져오기
    if 'selected_dates' not in st.session_state:
        st.session_state.selected_dates = set()
    selected_dates = st.session_state.selected_dates
    current_date = datetime.now().date() # 오늘 날짜

    # 각 월별 달력 렌더링
    for year, month in months_to_display:
        st.markdown(f"### {year} {calendar.month_name[month]}", unsafe_allow_html=True)
        cal = calendar.monthcalendar(year, month) # 특정 월의 달력 데이터 (주 단위)
        days_of_week_korean = ["일", "월", "화", "수", "목", "금", "토"]

        # 요일 헤더 (일, 월, 화...) 생성
        cols = st.columns(7, gap="small")
        for i, day_name in enumerate(days_of_week_korean):
            # 일요일은 빨간색, 토요일은 파란색, 나머지는 흰색
            color = "red" if i == 0 else ("blue" if i == 6 else "white")
            cols[i].markdown(f"<span style='color:{color}'><strong>{day_name}</strong></span>", unsafe_allow_html=True)

        # 달력 날짜 체크박스 생성
        for week in cal:
            cols = st.columns(7, gap="small")
            for i, day in enumerate(week):
                if day == 0: # 해당 월에 속하지 않는 빈 칸
                    cols[i].markdown(" ")
                else:
                    date_obj = date(year, month, day) # 현재 날짜 객체 생성

                    is_selected = date_obj in selected_dates
                    is_current = date_obj == current_date
                    is_future = date_obj > apply_date # 신청일 이후의 미래 날짜

                    # 체크박스 상태가 변경될 때 호출될 콜백 함수
                    def on_checkbox_change(current_date_obj_for_callback):
                        if st.session_state[f"chk_{current_date_obj_for_callback}"]:
                            # 체크박스가 체크되면, session_state에 추가
                            if current_date_obj_for_callback not in st.session_state.selected_dates:
                                st.session_state.selected_dates.add(current_date_obj_for_callback)
                                print(f"DEBUG: 날짜 추가됨: {current_date_obj_for_callback}. 현재 선택된 날짜: {sorted(st.session_state.selected_dates)}")
                        else:
                            # 체크박스가 체크 해제되면, session_state에서 제거
                            if current_date_obj_for_callback in st.session_state.selected_dates:
                                st.session_state.selected_dates.remove(current_date_obj_for_callback)
                                print(f"DEBUG: 날짜 제거됨: {current_date_obj_for_callback}. 현재 선택된 날짜: {sorted(st.session_state.selected_dates)}")

                    # 체크박스 텍스트에 bold 적용 (현재 날짜)
                    display_day_text = str(day)
                    if is_current:
                        display_day_text = f"**{day}**" # Streamlit markdown으로 텍스트를 bold 처리

                    cols[i].checkbox(
                        display_day_text, # bold 텍스트 사용
                        key=f"chk_{date_obj}", # 고유 키
                        value=is_selected, # 현재 선택 상태를 체크박스에 반영
                        on_change=on_checkbox_change, # 상태 변경 시 호출될 함수
                        args=(date_obj,), # on_change 함수에 날짜 객체 전달
                        disabled=is_future # 신청일 이후 날짜는 비활성화
                        # help 인자 제거됨
                    )
                    
    # 현재 선택된 근무일자 목록을 표시
    if st.session_state.selected_dates:
        st.markdown("### ✅ 선택된 근무일자")
        st.markdown(", ".join([d.strftime("%Y-%m-%d") for d in sorted(st.session_state.selected_dates)]))

    return st.session_state.selected_dates # 선택된 날짜 집합 반환

def daily_worker_eligibility_app():
    """
    일용근로자 수급자격 요건 모의계산 앱의 메인 함수입니다.
    사용자 입력, 조건 계산, 결과 표시를 담당합니다.
    """
    st.header("일용근로자 수급자격 요건 모의계산")

    # 현재 날짜와 시간 표시
    st.markdown(f"**오늘 날짜와 시간**: {current_time_korean}", unsafe_allow_html=True)

    # 요건 조건 설명
    st.markdown("### 📋 요건 조건")
    st.markdown("- **조건 1**: 수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지의 근로일 수가 총 일수의 1/3 미만이어야 합니다.")
    st.markdown("- **조건 2 (건설일용근로자만 해당)**: 수급자격 인정신청일 직전 14일간 근무 사실이 없어야 합니다 (신청일 제외).")
    st.markdown("---")

    # 근로자 유형 선택 라디오 버튼
    worker_type = st.radio("근로자 유형을 선택하세요", ["일반일용근로자", "건설일용근로자"])

    # 수급자격 신청일 선택
    apply_date = st.date_input("수급자격 신청일을 선택하세요", value=datetime.now().date())
    
    # 신청일을 기준으로 날짜 범위 및 시작일 가져오기
    date_range_objects, start_date = get_date_range(apply_date)

    st.markdown("---")
    st.markdown("#### ✅ 근무일 선택 달력")
    # 달력 렌더링 및 선택된 날짜 목록 가져오기 (이제 체크박스 버전 사용)
    selected_days = render_calendar_with_checkboxes(apply_date)
    st.markdown("---")

    # 조건 1 계산 및 표시
    total_days = len(date_range_objects) # 조건 1 계산에 사용될 전체 기간 일수
    worked_days = len(selected_days) # 사용자가 선택한 근무일 수
    threshold = total_days / 3 # 조건 1의 기준 (총 일수의 1/3)

    st.markdown(f"- 총 기간 일수: **{total_days}일**")
    st.markdown(f"- 기준 (총일수의 1/3): **{threshold:.1f}일**")
    st.markdown(f"- 선택한 근무일 수: **{worked_days}일**")

    condition1 = worked_days < threshold
    if condition1:
        st.success("✅ 조건 1 충족: 근무일 수가 기준 미만입니다.")
    else:
        st.warning("❌ 조건 1 불충족: 근무일 수가 기준 이상입니다.")

    # 조건 2 계산 및 표시 (건설일용근로자에게만 해당)
    condition2 = False
    if worker_type == "건설일용근로자":
        # 신청일 직전 14일 기간 계산 (신청일 제외)
        fourteen_days_prior_end = apply_date - timedelta(days=1)
        fourteen_days_prior_start = fourteen_days_prior_end - timedelta(days=13)
        # 해당 14일 기간 내의 모든 날짜들을 datetime.date 객체로 생성
        fourteen_days_prior_range = [d.date() for d in pd.date_range(start=fourteen_days_prior_start, end=fourteen_days_prior_end)]
        
        # 14일 기간 내에 근무 기록이 없는지 확인
        no_work_14_days = all(day not in selected_days for day in fourteen_days_prior_range)
        condition2 = no_work_14_days

        if no_work_14_days:
            st.success(f"✅ 조건 2 충족: 신청일 직전 14일간({fourteen_days_prior_start.strftime('%Y-%m-%d')} ~ {fourteen_days_prior_end.strftime('%Y-%m-%d')}) 근무내역이 없습니다.")
        else:
            st.warning(f"❌ 조건 2 불충족: 신청일 직전 14일간({fourteen_days_prior_start.strftime('%Y-%m-%d')} ~ {fourteen_days_prior_end.strftime('%Y-%m-%d')}) 내 근무기록이 존재합니다.")

    st.markdown("---")

    # 조건 1 불충족 시, 조건을 충족할 수 있는 미래 신청일 제안
    if not condition1:
        st.markdown("### 📅 조건 1을 충족하려면 언제 신청해야 할까요?")
        found_suggestion = False
        # 현재 신청일로부터 최대 30일까지 미래 날짜 탐색
        for i in range(1, 31):
            future_date = apply_date + timedelta(days=i)
            date_range_future_objects, _ = get_date_range(future_date)
            total_days_future = len(date_range_future_objects)
            threshold_future = total_days_future / 3
            # 미래 날짜까지의 선택된 근무일만 고려
            worked_days_future = sum(1 for d in selected_days if d <= future_date)

            if worked_days_future < threshold_future:
                st.info(f"✅ **{future_date.strftime('%Y-%m-%d')}** 이후에 신청하면 요건을 충족할 수 있습니다.")
                found_suggestion = True
                break # 제안을 찾으면 루프 종료
        if not found_suggestion:
            st.warning("❗앞으로 30일 이내에는 요건을 충족할 수 없습니다. 근무일 수를 조정하거나 더 먼 날짜를 고려하세요.")

    # 조건 2 불충족 시 (건설일용근로자만), 조건을 충족할 수 있는 미래 신청일 제안
    if worker_type == "건설일용근로자" and not condition2:
        st.markdown("### 📅 조건 2를 충족하려면 언제 신청해야 할까요?")
        # 신청일 이전의 마지막 근무일 찾기
        last_worked_day = max((d for d in selected_days if d < apply_date), default=None)
        if last_worked_day:
            suggested_date = last_worked_day + timedelta(days=15) # 마지막 근무일 + 14일 무근무 + 1일 (신청 가능일)
            st.info(f"✅ **{suggested_date.strftime('%Y-%m-%d')}** 이후에 신청하면 조건 2를 충족할 수 있습니다.")
        else:
            st.info("이미 최근 14일간 근무내역이 없으므로, 신청일을 조정할 필요는 없습니다.")

    st.subheader("📌 최종 판단")
    # 최종 수급자격 요건 충족 여부 판단 및 메시지 표시
    if worker_type == "일반일용근로자":
        if condition1:
            st.success(f"✅ 일반일용근로자 요건 충족\n\n**수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지({start_date.strftime('%Y-%m-%d')} ~ {apply_date.strftime('%Y-%m-%d')}) 근로일 수의 합이 같은 기간 동안의 총 일수의 3분의 1 미만**")
        else:
            st.error("❌ 일반일용근로자 요건 미충족\n\n**총 일수의 3분의 1 이상 근로 사실이 확인되어 요건을 충족하지 못합니다.**")
    else: # 건설일용근로자
        fourteen_days_prior_end = apply_date - timedelta(days=1)
        fourteen_days_prior_start = fourteen_days_prior_end - timedelta(days=13)
        if condition1 and condition2: # 건설일용근로자는 두 조건을 모두 충족해야 함
            st.success(f"✅ 건설일용근로자 요건 충족\n\n**수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지({start_date.strftime('%Y-%m-%d')} ~ {apply_date.strftime('%Y-%m-%d')}) 근로일 수의 합이 총 일수의 3분의 1 미만이고, 신청일 직전 14일간({fourteen_days_prior_start.strftime('%Y-%m-%d')} ~ {fourteen_days_prior_end.strftime('%Y-%m-%d')}) 근무 사실이 없음을 확인합니다.**")
        else:
            st.error(f"❌ 건설일용근로자 요건 미충족\n\n**총 일수의 3분의 1 이상 근로 사실이 확인되거나, 신청일 직전 14일간({fourteen_days_prior_start.strftime('%Y-%m-%d')} ~ {fourteen_days_prior_end.strftime('%Y-%m-%d')}) 내 근무기록이 존재하므로 요건을 충족하지 못합니다.**")

# 앱 실행 진입점
if __name__ == "__main__":
    daily_worker_eligibility_app()
