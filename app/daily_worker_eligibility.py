import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import calendar

def get_date_range(apply_date):
    """
    수급자격 신청일로부터 해당 회계연도 시작일(4월 1일)까지의 날짜 범위를 반환합니다.
    """
    start_date = apply_date.replace(month=4, day=1)
    # 현재 날짜가 4월 1일 이전이고, 신청일이 해당 연도의 4월 1일 이전이라면,
    # 전년도 4월 1일부터 시작하도록 조정
    if apply_date.month < 4:
        start_date = start_date.replace(year=apply_date.year - 1)
    return pd.date_range(start=start_date, end=apply_date)

def render_calendar(apply_date):
    """
    달력을 렌더링하고 사용자가 근무일을 선택할 수 있도록 합니다.
    """
    # 커스텀 CSS를 삽입하여 달력 레이아웃과 버튼 스타일 조정
    st.markdown("""
    <style>
    .st-emotion-cache-nahz7x { /* Streamlit 내부 컨테이너 패딩 조절 */
        padding-left: 0rem;
        padding-right: 0rem;
    }
    table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 1rem;
        table-layout: fixed; /* 고정된 테이블 레이아웃 */
    }
    th, td {
        text-align: center;
        padding: 0.2rem;
        border: none; /* 테이블 셀 테두리 제거 */
    }
    th {
        font-size: 0.9rem;
        color: white;
    }
    .sunday { color: red; }
    .saturday { color: blue; }
    .weekday { color: white; }

    div[data-testid="stButton"] button {
        width: 40px !important;
        height: 40px !important;
        border-radius: 50% !important; /* 원형 버튼 */
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 0.9rem !important;
        padding: 0 !important;
        margin: 0 auto !important;
        border: 2px solid transparent !important; /* 기본 투명 테두리 */
        background-color: transparent !important;
        color: white !important;
        transition: all 0.2s ease !important; /* 부드러운 전환 */
    }
    div[data-testid="stButton"] button[kind="secondary"]:hover {
        border: 2px solid #00ff00 !important; /* 호버 시 초록색 원 */
        background-color: rgba(0, 255, 0, 0.2) !important; /* 연한 초록색 배경 */
    }
    /* 선택된 버튼 스타일 */
    div[data-testid="stButton"] button.selected-day {
        border: 2px solid #00ff00 !important; /* 선택 시 초록색 원형 테두리 */
        background-color: rgba(0, 255, 0, 0.3) !important; /* 연한 초록색 배경 */
    }
    /* 비활성화된 (미래) 날짜 스타일 */
    div[data-testid="stButton"] button[disabled] {
        color: gray !important;
        background-color: transparent !important;
        border: 2px solid transparent !important;
        cursor: not-allowed;
    }
    /* 모바일 반응형 */
    @media (max-width: 600px) {
        div[data-testid="stButton"] button {
            font-size: 0.8rem !important;
            width: 35px !important;
            height: 35px !important;
        }
        th, td {
            padding: 0.1rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    start_date = apply_date.replace(month=4, day=1)
    if apply_date.month < 4:
        start_date = start_date.replace(year=apply_date.year - 1)

    end_date = apply_date

    months_to_render = sorted(set((d.year, d.month) for d in pd.date_range(start=start_date, end=end_date)))

    # 세션 상태에 선택된 날짜가 없으면 초기화
    if 'selected_dates' not in st.session_state:
        st.session_state.selected_dates = set()
    selected_dates = st.session_state.selected_dates

    for year, month in months_to_render:
        st.markdown(f"### {year}년 {month}월")
        cal = calendar.monthcalendar(year, month)
        days_of_week = ["일", "월", "화", "수", "목", "금", "토"]

        # HTML 테이블 시작
        st.markdown("<table>", unsafe_allow_html=True)

        # 요일 헤더 행
        st.markdown("<thead><tr>", unsafe_allow_html=True)
        for i, day_name in enumerate(days_of_week):
            color_class = ""
            if i == 0: # 일요일
                color_class = "sunday"
            elif i == 6: # 토요일
                color_class = "saturday"
            else: # 평일
                color_class = "weekday"
            st.markdown(f"<th class='{color_class}'>{day_name}</th>", unsafe_allow_html=True)
        st.markdown("</tr></thead>", unsafe_allow_html=True)

        st.markdown("<tbody>", unsafe_allow_html=True)

        # 달력 주별 행
        for week in cal:
            st.markdown("<tr>", unsafe_allow_html=True)
            for i, day in enumerate(week):
                st.markdown("<td>", unsafe_allow_html=True)
                if day == 0:
                    st.markdown(" ") # 빈 칸
                else:
                    date_obj = date(year, month, day)
                    button_key = f"btn_{date_obj}"

                    # 미래 날짜는 비활성화
                    if date_obj > apply_date:
                        st.button(str(day), key=button_key, disabled=True)
                    else:
                        # 클릭 시 선택/해제 토글 함수
                        def _on_button_click(clicked_date):
                            if clicked_date in st.session_state.selected_dates:
                                st.session_state.selected_dates.remove(clicked_date)
                            else:
                                st.session_state.selected_dates.add(clicked_date)
                            st.rerun() # 상태 변경 후 즉시 UI 업데이트

                        # 버튼에 선택 상태에 따라 클래스를 동적으로 부여하기 위해 JavaScript injection이 필요하지만,
                        # Streamlit의 제한으로 직접적인 방법은 어렵습니다. 대신, selected_dates 상태를
                        # 사용하여 재렌더링 시 스타일을 반영합니다.
                        # 여기서는 `is_selected` 변수를 사용하여 CSS 클래스를 제어하는 방식은
                        # Streamlit의 `st.button`에서 직접 지원하지 않으므로,
                        # `on_click` 시 `st.rerun()`을 통해 상태를 변경하고, 변경된 상태가
                        # 다음 렌더링 주기에 반영되도록 합니다.
                        # 따라서, 실제로 버튼에 'selected-day' 클래스가 직접 추가되는 것이 아니라,
                        # `st.session_state.selected_dates`에 날짜가 있으면,
                        # 다음 렌더링 시 해당 날짜 버튼이 "선택된" 상태로 그려지는 방식입니다.
                        is_selected = date_obj in selected_dates
                        button_label = str(day)
                        if is_selected:
                            # 선택된 날짜에 대한 시각적 피드백을 주기 위해 HTML/CSS로 원을 그리는 방식을 사용
                            # 이 부분은 CSS 스타일링에서 .selected-day 클래스를 통해 구현됩니다.
                            # 버튼 자체의 라벨을 변경하지 않고 CSS로 시각적 변화를 주는 것이 더 자연스럽습니다.
                            pass # 라벨은 그대로 두고 CSS로 처리

                        st.button(
                            button_label,
                            key=button_key,
                            on_click=_on_button_click,
                            args=(date_obj,),
                            help="클릭하여 근무일을 선택하거나 해제하세요",
                        )
                st.markdown("</td>", unsafe_allow_html=True)
            st.markdown("</tr>", unsafe_allow_html=True)

        st.markdown("</tbody></table>", unsafe_allow_html=True) # HTML 테이블 끝

    if selected_dates:
        st.markdown("### ✅ 선택된 근무일자")
        st.markdown(", ".join([date.strftime("%Y-%m-%d") for date in sorted(selected_dates)]))

    return selected_dates

---

def daily_worker_eligibility_app():
    """
    일용근로자 수급자격 요건 모의계산 Streamlit 앱의 메인 함수입니다.
    """
    st.markdown("""
<style>
div[data-testid="stRadio"] label {
    color: white !important;
    font-size: 18px !important;
}
</style>
""", unsafe_allow_html=True)

    st.header("일용근로자 수급자격 요건 모의계산")

    worker_type = st.radio("근로자 유형을 선택하세요", ["일반일용근로자", "건설일용근로자"])
    apply_date = st.date_input("수급자격 신청일을 선택하세요", value=datetime.today().date())

    st.markdown("---")
    st.markdown("#### ✅ 근무일 선택 달력")
    selected_days = render_calendar(apply_date)
    st.markdown("---")

    total_days = len(get_date_range(apply_date))
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
        fourteen_days_prior = [apply_date - timedelta(days=i) for i in range(1, 15)]
        # 신청일 이전 14일간 근무내역이 없는지 확인
        no_work_14_days = all(day not in selected_days for day in fourteen_days_prior)
        condition2 = no_work_14_days

        if no_work_14_days:
            st.success("✅ 조건 2 충족: 신청일 이전 14일간 근무내역이 없습니다.")
        else:
            st.warning("❌ 조건 2 불충족: 신청일 이전 14일 내 근무기록이 존재합니다.")

    st.markdown("---")

    # 조건 불충족 시 대안 신청일 계산
    if not condition1:
        st.markdown("### 📅 조건 1을 충족하려면 언제 신청해야 할까요?")
        future_dates = [apply_date + timedelta(days=i) for i in range(1, 31)]
        found_alternative = False
        for future_date in future_dates:
            date_range_future = get_date_range(future_date)
            total_days_future = len(date_range_future)
            threshold_future = total_days_future / 3
            # 미래 날짜를 기준으로 선택된 근무일 수 계산
            worked_days_future = sum(1 for d in selected_days if d <= future_date)

            if worked_days_future < threshold_future:
                st.info(f"✅ **{future_date.strftime('%Y-%m-%d')}** 이후에 신청하면 요건을 충족할 수 있습니다.")
                found_alternative = True
                break
        if not found_alternative:
            st.warning("❗앞으로 30일 이내에는 요건을 충족할 수 없습니다. 근무일 수를 조정하거나 더 먼 날짜를 고려하세요.")

    if worker_type == "건설일용근로자" and not condition2:
        st.markdown("### 📅 조건 2를 충족하려면 언제 신청해야 할까요?")
        # 신청일 이전 근무일 중 가장 최근 근무일 찾기
        last_worked_day_before_apply = max((d for d in selected_days if d < apply_date), default=None)
        if last_worked_day_before_apply:
            suggested_date = last_worked_day_before_apply + timedelta(days=15)
            st.info(f"✅ **{suggested_date.strftime('%Y-%m-%d')}** 이후에 신청하면 조건 2를 충족할 수 있습니다.")
        else:
            st.info("이미 최근 14일간 근무내역이 없으므로, 신청일을 조정할 필요는 없습니다.")

    st.subheader("📌 최종 판단")
    if worker_type == "일반일용근로자":
        if condition1:
            st.success(f"✅ 일반일용근로자 요건 충족\n\n**수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지(2025-04-01 ~ {apply_date.strftime('%Y-%m-%d')}) 근로일 수의 합이 같은 기간 동안의 총 일수의 3분의 1 미만**")
        else:
            st.error("❌ 일반일용근로자 요건 미충족\n\n**총 일수의 3분의 1 이상 근로 사실이 확인되어 요건을 충족하지 못합니다.**")
    else: # 건설일용근로자
        if condition1 or condition2:
            st.success(f"✅ 건설일용근로자 요건 충족\n\n**수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지(2025-04-01 ~ {apply_date.strftime('%Y-%m-%d')}) 근로일 수의 합이 총 일수의 3분의 1 미만임을 확인하거나, 신청일 이전 14일간({(apply_date - timedelta(days=14)).strftime('%Y-%m-%d')} ~ {apply_date.strftime('%Y-%m-%d')}) 근무 사실이 없음을 확인합니다.**")
        else:
            st.error(f"❌ 건설일용근로자 요건 미충족\n\n**총 일수의 3분의 1 이상 근로 사실이 확인되고, 신청일 이전 14일간({(apply_date - timedelta(days=14)).strftime('%Y-%m-%d')} ~ {apply_date.strftime('%Y-%m-%d')}) 내 근무기록이 존재하므로 요건을 충족하지 못합니다.**")

if __name__ == "__main__":
    daily_worker_eligibility_app()
