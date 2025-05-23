import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import calendar

def get_date_range(apply_date):
    # Start from the first day of the previous month
    start_date = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1)
    return pd.date_range(start=start_date, end=apply_date), start_date

def toggle_date(date_obj):
    # 이 함수는 session_state를 올바르게 업데이트합니다.
    if date_obj in st.session_state.selected_dates:
        st.session_state.selected_dates.remove(date_obj)
    else:
        st.session_state.selected_dates.add(date_obj)

def render_calendar(apply_date):
    # CSS 스타일을 여기에 직접 삽입합니다.
    # 각 버튼의 ID를 직접 타겟팅하여 스타일을 적용합니다.
    # st.button의 key가 "date_btn_YYYY-MM-DD"일 때, Streamlit은 대략 "st-b-key-date_btn_YYYY-MM-DD" 형태의 ID를 생성합니다.
    # 이 ID를 CSS에서 정확히 타겟팅해야 합니다.
    
    # 세션 상태에 'selected_dates'가 없으면 초기화합니다.
    if 'selected_dates' not in st.session_state:
        st.session_state.selected_dates = set()

    selected_dates = st.session_state.selected_dates
    current_date = datetime.now().date()

    # 동적으로 생성할 스타일 규칙들을 담을 리스트
    dynamic_styles = []

    # 기본 CSS는 변경하지 않고 유지합니다.
    # 특정 날짜에 대한 스타일 오버라이드를 동적으로 주입합니다.
    st.markdown("""
    <style>
    /* Reduce padding and margins for calendar columns */
    div[data-testid="stHorizontalBlock"] {
        gap: 0.1rem !important;
    }
    div[data-testid="stHorizontalBlock"] > div {
        padding: 0 !important;
        margin: 0 !important;
    }
    /* Style for calendar day buttons */
    div[data-testid="stButton"] button {
        width: 40px !important;
        height: 40px !important;
        border-radius: 0 !important; /* Square buttons */
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 1rem !important;
        padding: 0 !important;
        margin: 0 !important;
        border: 1px solid #ccc !important; /* Default light border */
        background-color: #1e1e1e !important; /* Default dark background */
        color: white !important;
        transition: all 0.2s ease !important; /* Smooth transition for hover */
    }
    /* Hover effect for unselected buttons */
    div[data-testid="stButton"] button:not([data-selected="true"]):not([disabled]):hover { /* data-selected 속성 사용 */
        border: 2px solid #00ff00 !important;
        background-color: rgba(0, 255, 0, 0.2) !important;
    }
    /* Disabled (future) day style */
    div[data-testid="stButton"] button[disabled] {
        color: gray !important;
        background-color: #1e1e1e !important;
        border: 1px solid #ccc !important;
    }
    /* Day header styles */
    div[data-testid="stHorizontalBlock"] span {
        font-size: 0.9rem !important;
        text-align: center !important;
        color: white !important;
    }
    /* Force horizontal layout on mobile */
    @media (max-width: 600px) {
        div[data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-wrap: nowrap !important;
            gap: 0.1rem !important;
        }
        div[data-testid="stHorizontalBlock"] > div {
            flex: 1 !important;
            min-width: 35px !important;
            padding: 0 !important;
        }
        div[data-testid="stButton"] button {
            font-size: 0.8rem !important;
            width: 35px !important;
            height: 35px !important;
        }
    }
    /* Month boundary styling */
    div[data-testid="stMarkdownContainer"] h3 {
        margin: 0.5rem 0 !important;
        padding: 0.2rem !important;
        background-color: #2e2e2e !important; /* Slightly lighter than app background */
        text-align: center !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

    start_date = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1)
    end_date = apply_date
    months = sorted(set((d.year, d.month) for d in pd.date_range(start=start_date, end=end_date)))

    for year, month in months:
        st.markdown(f"### {year} {calendar.month_name[month]}", unsafe_allow_html=True)
        cal = calendar.monthcalendar(year, month)
        days = ["Sun", "Mon", "Tue", "Wen", "Thu", "Fri", "Sat"]

        cols = st.columns(7, gap="small")
        for i, day in enumerate(days):
            color = "red" if i == 0 else "blue" if i == 6 else "white"
            cols[i].markdown(f"<span style='color:{color}'><strong>{day}</strong></span>", unsafe_allow_html=True)

        for week in cal:
            cols = st.columns(7, gap="small")
            for i, day in enumerate(week):
                if day == 0:
                    cols[i].markdown(" ")
                else:
                    date_obj = date(year, month, day)
                    # **버튼 키는 항상 고정되어야 합니다.**
                    button_key = f"date_btn_{date_obj.strftime('%Y-%m-%d')}"
                    
                    is_selected = date_obj in selected_dates
                    is_current = date_obj == current_date

                    # **동적 CSS를 여기에 추가하여 선택된/현재 날짜 버튼의 스타일을 직접 오버라이드합니다.**
                    # Streamlit이 생성하는 버튼의 실제 ID는 "st-b-key-" + key 값입니다.
                    actual_html_id = f"st-b-key-{button_key}"

                    if is_selected:
                        dynamic_styles.append(f"""
                            button[id="{actual_html_id}"] {{
                                background-color: #00ff00 !important; /* Green background for selected dates */
                                color: white !important;
                                border: 2px solid #0000ff !important; /* Blue border for selected dates */
                            }}
                        """)
                    # 현재 날짜 스타일은 선택된 날짜보다 우선순위가 낮도록 하거나,
                    # 선택된 날짜와 겹치지 않도록 조건을 추가해야 합니다.
                    # 여기서는 선택되지 않은 경우에만 현재 날짜 스타일을 적용하도록 합니다.
                    elif is_current: # is_selected가 아닐 때만 적용
                        dynamic_styles.append(f"""
                            button[id="{actual_html_id}"] {{
                                background-color: #0000ff !important; /* Blue background for current date */
                                color: white !important;
                                font-weight: bold !important;
                                border: 1px solid #ccc !important;
                            }}
                        """)
                        
                    # 버튼 렌더링
                    if cols[i].button(
                        str(day),
                        key=button_key, # 고정된 키 사용
                        on_click=toggle_date,
                        help="클릭하여 근무일을 선택하거나 해제하세요",
                        kwargs={"date_obj": date_obj},
                        disabled=(date_obj > apply_date) # 미래 날짜는 비활성화
                    ):
                        st.rerun()

    # 모든 동적 스타일 규칙을 한 번에 삽입합니다.
    if dynamic_styles:
        st.markdown(f"<style>{' '.join(dynamic_styles)}</style>", unsafe_allow_html=True)

    if selected_dates:
        st.markdown("### ✅ 선택된 근무일자")
        st.markdown(", ".join([date.strftime("%Y-%m-%d") for date in sorted(selected_dates)]))

    return selected_dates

def daily_worker_eligibility_app():
    st.markdown("""
<style>
div[data-testid="stRadio"] label {
    color: white !important;
    font-size: 18px !important;
}
</style>
""", unsafe_allow_html=True)

    st.header("일용근로자 수급자격 요건 모의계산")

    # Display current date and time in Korean
    current_datetime = datetime.now()
    st.markdown(f"**오늘 날짜와 시간**: {current_datetime.strftime('%Y년 %m월 %d일 %A 오전 %I:%M KST')}", unsafe_allow_html=True)

    # Display conditions at the top
    st.markdown("### 📋 요건 조건")
    st.markdown("- **조건 1**: 수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지의 근로일 수가 총 일수의 1/3 미만이어야 합니다.")
    st.markdown("- **조건 2 (건설일용근로자만 해당)**: 수급자격 인정신청일 직전 14일간 근무 사실이 없어야 합니다 (신청일 제외).")
    st.markdown("---")

    worker_type = st.radio("근로자 유형을 선택하세요", ["일반일용근로자", "건설일용근로자"])

    apply_date = st.date_input("수급자격 신청일을 선택하세요", value=datetime.now().date())
    date_range, start_date = get_date_range(apply_date)

    st.markdown("---")
    st.markdown("#### ✅ 근무일 선택 달력")
    selected_days = render_calendar(apply_date)
    st.markdown("---")

    total_days = len(date_range)
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
        fourteen_days_prior = pd.date_range(start=fourteen_days_prior_start, end=fourteen_days_prior_end).date
        # Ensure 'selected_days' elements are date objects for comparison
        fourteen_days_prior_set = set(fourteen_days_prior)
        no_work_14_days = all(day not in selected_days for day in fourteen_days_prior_set)
        condition2 = no_work_14_days

        if no_work_14_days:
            st.success(f"✅ 조건 2 충족: 신청일 직전 14일간({fourteen_days_prior_start.strftime('%Y-%m-%d')} ~ {fourteen_days_prior_end.strftime('%Y-%m-%d')}) 근무내역이 없습니다.")
        else:
            st.warning(f"❌ 조건 2 불충족: 신청일 직전 14일간({fourteen_days_prior_start.strftime('%Y-%m-%d')} ~ {fourteen_days_prior_end.strftime('%Y-%m-%d')}) 내 근무기록이 존재합니다.")

    st.markdown("---")

    if not condition1:
        st.markdown("### 📅 조건 1을 충족하려면 언제 신청해야 할까요?")
        future_dates = [apply_date + timedelta(days=i) for i in range(1, 31)]
        found_suggestion = False
        for future_date in future_dates:
            date_range_future, _ = get_date_range(future_date)
            total_days_future = len(date_range_future)
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
        past_worked_days = [d for d in selected_days if d < apply_date]
        last_worked_day = max(past_worked_days) if past_worked_days else None

        if last_worked_day:
            suggested_date = last_worked_day + timedelta(days=15)
            st.info(f"✅ **{suggested_date.strftime('%Y-%m-%d')}** 이후에 신청하면 조건 2를 충족할 수 있습니다.")
        else:
            st.info("이미 신청일 직전 14일간 근무내역이 없으므로, 신청일을 조정할 필요는 없습니다.")

    st.subheader("📌 최종 판단")
    if worker_type == "일반일용근로자":
        if condition1:
            st.success(f"✅ 일반일용근로자 요건 충족\n\n**수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지({start_date.strftime('%Y-%m-%d')} ~ {apply_date.strftime('%Y-%m-%d')}) 근로일 수의 합이 같은 기간 동안의 총 일수의 3분의 1 미만**")
        else:
            st.error("❌ 일반일용근로자 요건 미충족\n\n**총 일수의 3분의 1 이상 근로 사실이 확인되어 요건을 충족하지 못합니다.**")
    else: # 건설일용근로자
        fourteen_days_prior_end = apply_date - timedelta(days=1)
        fourteen_days_prior_start = fourteen_days_prior_end - timedelta(days=13)
        if condition1 or condition2:
            st.success(f"✅ 건설일용근로자 요건 충족\n\n**수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지({start_date.strftime('%Y-%m-%d')} ~ {apply_date.strftime('%Y-%m-%d')}) 근로일 수의 합이 총 일수의 3분의 1 미만임을 확인하거나, 신청일 직전 14일간({fourteen_days_prior_start.strftime('%Y-%m-%d')} ~ {fourteen_days_prior_end.strftime('%Y-%m-%d')}) 근무 사실이 없음을 확인합니다.**")
        else:
            st.error(f"❌ 건설일용근로자 요건 미충족\n\n**총 일수의 3분의 1 이상 근로 사실이 확인되고, 신청일 직전 14일간({fourteen_days_prior_start.strftime('%Y-%m-%d')} ~ {fourteen_days_prior_end.strftime('%Y-%m-%d')}) 내 근무기록이 존재하므로 요건을 충족하지 못합니다.**")

if __name__ == "__main__":
    daily_worker_eligibility_app()
