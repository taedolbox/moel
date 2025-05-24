import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import calendar

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

def render_calendar_with_checkboxes(apply_date):
    """
    달력을 렌der링하고 체크박스를 이용한 날짜 선택 기능을 제공합니다.
    선택된 날짜, 현재 날짜, 신청일 이후 날짜에 따라 스타일이 달라집니다.
    """
    # 사용자 정의 CSS 주입
    st.markdown(f"""
    <style>
    /* 전체 앱 배경색을 어둡게 설정 */
    .stApp {{
        background-color: #1e1e1e;
        color: white;
    }}
    /* 라디오 버튼 텍스트 색상 */
    div[data-testid="stRadio"] label {{
        color: white !important;
        font-size: 18px !important;
    }}
    /* 헤더 및 텍스트 색상 */
    h1, h2, h3, h4, h5, h6, .stMarkdown, .stText {{
        color: white;
    }}
    div[data-testid="stMarkdownContainer"] p {{
        color: white;
    }}
    /* Streamlit Input 위젯 라벨 색상 */
    .stDateInput label, .stSelectbox label {{
        color: white !important;
    }}
    /* 알림 박스 텍스트 색상 */
    .st-dg, .st-ck, .st-cf {{
        color: black !important;
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
        width: 60px !important;
        height: 40px !important; /* 직사각형으로 세로 길게 */
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 0 !important;
        margin: 0 !important;
        border: 1px solid #ffffff !important; /* 신청일 이전: 흰색 테두리 */
        background-color: #1e1e1e !important;
        transition: all 0.2s ease !important;
        cursor: pointer;
    }}
    /* 체크박스 라벨 전체 */
    div[data-testid="stCheckbox"] label {{
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        height: 100%;
        margin: 0 !important;
    }}
    /* 체크마크 아이콘 숨기기 */
    div[data-testid="stCheckbox"] label div[data-testid="stDecoration"] {{
        display: none !important;
    }}
    /* 체크박스 라벨 텍스트 스타일 */
    div[data-testid="stCheckbox"] label div[data-testid="stMarkdownContainer"] p {{
        color: white !important;
        font-size: 1rem !important;
        line-height: 1;
        margin: 0 !important;
        padding: 0 !important;
        text-align: center;
        width: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
    }}
    /* 선택된 날짜 */
    div[data-testid="stCheckbox"] input[type="checkbox"]:checked + label {{
        background-color: #ff0000 !important;
        border: 2px solid #ffffff !important;
        box-sizing: border-box;
    }}
    div[data-testid="stCheckbox"] input[type="checkbox"]:checked + label p {{
        color: white !important;
    }}
    /* 신청일 이후 날짜 스타일 */
    div[data-testid="stCheckbox"] input[type="checkbox"]:disabled + label {{
        color: #1e1e1e !important; /* 숫자 색상을 배경색과 동일하게 */
        background-color: #1e1e1e !important; /* 배경색 */
        border: 1px solid #1e1e1e !important; /* 테두리를 배경색과 동일하게 */
        cursor: not-allowed !important;
        opacity: 1 !important; /* 투명도 유지 */
    }}
    div[data-testid="stCheckbox"] input[type="checkbox"]:disabled + label p {{
        color: #1e1e1e !important;
    }}
    /* 요일 헤더 스타일 */
    div[data-testid="stHorizontalBlock"] span {{
        font-size: 0.9rem !important;
        text-align: center !important;
        color: white !important;
    }}
    /* 모바일 반응형 */
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
        div[data-testid="stCheckbox"] {{
            width: 50px !important;
            height: 50px !important; /* 모바일에서도 직사각형 */
        }}
        div[data-testid="stCheckbox"] label div[data-testid="stMarkdownContainer"] p {{
            font-size: 0.8rem !important;
        }}
    }}
    /* 월 경계 스타일 */
    div[data-testid="stMarkdownContainer"] h3 {{
        margin: 0.5rem 0 !important;
        padding: 0.2rem !important;
        background-color: #2e2e2e !important;
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
    current_date = datetime.now().date()

    # 각 월별 달력 렌der링
    for year, month in months_to_display:
        st.markdown(f"### {year}년 {month}월", unsafe_allow_html=True)  # 한글화: "2025 May" → "2025년 5월"
        cal = calendar.monthcalendar(year, month)
        days_of_week_korean = ["일", "월", "화", "수", "목", "금", "토"]

        # 요일 헤더 생성
        cols = st.columns(7, gap="small")
        for i, day_name in enumerate(days_of_week_korean):
            color = "red" if i == 0 else ("blue" if i == 6 else "white")
            cols[i].markdown(f"<span style='color:{color}'><strong>{day_name}</strong></span>", unsafe_allow_html=True)

        # 달력 날짜 체크박스 생성
        for week in cal:
            cols = st.columns(7, gap="small")
            for i, day in enumerate(week):
                if day == 0:
                    cols[i].markdown(" ")
                else:
                    date_obj = date(year, month, day)
                    is_selected = date_obj in selected_dates
                    is_current = date_obj == current_date
                    # 신청일 이후를 비활성화
                    is_disabled = date_obj > apply_date

                    def on_checkbox_change(current_date_obj_for_callback):
                        if st.session_state[f"chk_{current_date_obj_for_callback}"]:
                            st.session_state.selected_dates.add(current_date_obj_for_callback)
                            print(f"DEBUG: 날짜 추가됨: {current_date_obj_for_callback}. 현재 선택된 날짜: {sorted(st.session_state.selected_dates)}")
                        else:
                            st.session_state.selected_dates.discard(current_date_obj_for_callback)
                            print(f"DEBUG: 날짜 제거됨: {current_date_obj_for_callback}. 현재 선택된 날짜: {sorted(st.session_state.selected_dates)}")

                    display_day_text = str(day)
                    if is_current:
                        display_day_text = f"**{day}**"

                    cols[i].checkbox(
                        display_day_text,
                        key=f"chk_{date_obj}",
                        value=is_selected,
                        on_change=on_checkbox_change,
                        args=(date_obj,),
                        disabled=is_disabled
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

    # 수급자격 신청일 선택 (자유롭게 선택 가능, 정상 유지)
    apply_date = st.date_input("수급자격 신청일을 선택하세요", value=datetime.now().date())

    # 날짜 범위 및 시작일 가져오기
    date_range_objects, start_date = get_date_range(apply_date)

    st.markdown("---")
    st.markdown("#### ✅ 근무일 선택 달력")
    selected_days = render_calendar_with_checkboxes(apply_date)
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
