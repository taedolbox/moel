import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import calendar

def get_date_range(apply_date):
    start_date = apply_date.replace(month=4, day=1)
    return pd.date_range(start=start_date, end=apply_date)

def render_calendar(apply_date):
    # Inject custom CSS for compact layout and button styling
    st.markdown("""
    <style>
    /* Reduce padding and margins for calendar columns */
    div[data-testid="stHorizontalBlock"] {
        gap: 0.5rem !important; /* Reduce gap between columns */
    }
    div[data-testid="stHorizontalBlock"] > div {
        padding: 0.2rem !important; /* Reduce padding inside columns */
        margin: 0 !important; /* Remove margins */
    }
    /* Style for calendar day buttons */
    div[data-testid="stButton"] button {
        width: 40px !important;
        height: 40px !important;
        border-radius: 50% !important; /* Circular buttons */
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 0.9rem !important;
        padding: 0 !important;
        margin: 0 auto !important;
        border: 2px solid transparent !important;
        background-color: transparent !important;
        color: white !important;
    }
    /* Hover effect */
    div[data-testid="stButton"] button[kind="secondary"]:hover {
        border: 2px solid #00ff00 !important; /* Green circle on hover */
        background-color: rgba(0, 255, 0, 0.2) !important; /* Light green background */
    }
    /* Selected button style (using emoji in label, no dynamic CSS) */
    div[data-testid="stButton"] button[kind="secondary"] {
        transition: all 0.2s ease !important; /* Smooth transition */
    }
    /* Disabled (future) day style */
    div[data-testid="stButton"] button[disabled] {
        color: gray !important;
        background-color: transparent !important;
        border: 2px solid transparent !important;
    }
    /* Day header styles */
    div[data-testid="stHorizontalBlock"] span {
        font-size: 0.9rem !important;
        text-align: center !important;
    }
    /* Force horizontal layout on mobile */
    @media (max-width: 600px) {
        div[data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-wrap: nowrap !important;
            gap: 0.3rem !important;
        }
        div[data-testid="stHorizontalBlock"] > div {
            flex: 1 !important;
            min-width: 40px !important;
            padding: 0.1rem !important;
        }
        div[data-testid="stButton"] button {
            font-size: 0.8rem !important;
            width: 35px !important;
            height: 35px !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    start_date = apply_date.replace(month=4, day=1)
    end_date = apply_date

    months = sorted(set((d.year, d.month) for d in pd.date_range(start=start_date, end=end_date)))

    # Initialize selected dates in session state if not already present
    if 'selected_dates' not in st.session_state:
        st.session_state.selected_dates = set()
    selected_dates = st.session_state.selected_dates

    for year, month in months:
        st.markdown(f"### {year}년 {month}월")
        cal = calendar.monthcalendar(year, month)
        days = ["일", "월", "화", "수", "목", "금", "토"]

        # Create columns for day headers
        cols = st.columns(7, gap="small")
        for i, day in enumerate(days):
            if i == 0:
                color = "red"
            elif i == 6:
                color = "blue"
            else:
                color = "white"
            cols[i].markdown(f"<span style='color:{color}'><strong>{day}</strong></span>", unsafe_allow_html=True)

        # Create calendar grid
        for week in cal:
            cols = st.columns(7, gap="small")
            for i, day in enumerate(week):
                if day == 0:
                    cols[i].markdown(" ")
                else:
                    date_obj = date(year, month, day)  # Use date instead of datetime.date

                    if date_obj > apply_date:
                        cols[i].button(str(day), key=f"btn_{date_obj}", disabled=True)
                        continue

                    button_key = f"btn_{date_obj}"
                    
                    # Check if date is selected and modify label
                    is_selected = date_obj in selected_dates
                    label = f"✅ {day}" if is_selected else str(day)

                    # Use a function to handle the click for better state management
                    def on_button_click(clicked_date):
                        if clicked_date in st.session_state.selected_dates:
                            st.session_state.selected_dates.remove(clicked_date)
                        else:
                            st.session_state.selected_dates.add(clicked_date)

                    cols[i].button(
                        label,
                        key=button_key,
                        on_click=on_button_click,
                        args=(date_obj,),
                        help="클릭하여 근무일을 선택하거나 해제하세요"
                    )

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

    worker_type = st.radio("근로자 유형을 선택하세요", ["일반일용근로자", "건설일용근로자"])
    apply_date = st.date_input("수급자격 신청일을 선택하세요", value=datetime.today().date())  # Ensure date object

    date_range = get_date_range(apply_date)

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
        fourteen_days_prior = [apply_date - timedelta(days=i) for i in range(1, 15)]
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
        for future_date in future_dates:
            date_range_future = pd.date_range(start=future_date.replace(month=4, day=1), end=future_date)
            total_days_future = len(date_range_future)
            threshold_future = total_days_future / 3
            worked_days_future = sum(1 for d in selected_days if d <= future_date)
            if worked_days_future < threshold_future:
                st.info(f"✅ **{future_date.strftime('%Y-%m-%d')}** 이후에 신청하면 요건을 충족할 수 있습니다.")
                break
        else:
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
            st.success(f"✅ 일반일용근로자 요건 충족\n\n**수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지(2025-04-01 ~ {apply_date.strftime('%Y-%m-%d')}) 근로일 수의 합이 같은 기간 동안의 총 일수의 3분의 1 미만**")
        else:
            st.error("❌ 일반일용근로자 요건 미충족\n\n**총 일수의 3분의 1 이상 근로 사실이 확인되어 요건을 충족하지 못합니다.**")
    else:
        if condition1 or condition2:
            st.success(f"✅ 건설일용근로자 요건 충족\n\n**수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지(2025-04-01 ~ {apply_date.strftime('%Y-%m-%d')}) 근로일 수의 합이 총 일수의 3분의 1 미만임을 확인하거나, 신청일 이전 14일간({(apply_date - timedelta(days=14)).strftime('%Y-%m-%d')} ~ {apply_date.strftime('%Y-%m-%d')}) 근무 사실이 없음을 확인합니다.**")
        else:
            st.error(f"❌ 건설일용근로자 요건 미충족\n\n**총 일수의 3분의 1 이상 근로 사실이 확인되고, 신청일 이전 14일간({(apply_date - timedelta(days=14)).strftime('%Y-%m-%d')} ~ {apply_date.strftime('%Y-%m-%d')}) 내 근무기록이 존재하므로 요건을 충족하지 못합니다.**")

if __name__ == "__main__":
    daily_worker_eligibility_app()
